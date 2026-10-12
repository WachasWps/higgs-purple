"""Multi-character dubbing engine: voices work/<id>/plan.json in bn/ta/te/ml/or, one video at a time.

- Every cast member's voice is cloned from their own ref_ranges in the original (Demucs) vocals.
- All takes for all lines in all pending languages are sampled in batched MLX passes (Indic-Mio).
- Takes are checked lazily with an MLX Whisper back-transcription (stop at the first good take).
- Character finishing: pitch matched to the original character (+ plan offset), plus `cartoon` / `villain` fx.
- `keep_original` lines reuse the original sound (laughs, screams, jingles).
- guard.py keeps it inside the Mac's limits: 4 CPU threads, pauses on memory/thermal pressure,
  a short cool-down between videos, and it is meant to run under `nice`.

Usage: nice -n 10 .venv/bin/python dubplan.py work/ out/ [--watch N]   (--watch: wait for N plans to appear)
Outputs: out/<id>_<lang>.mp4 (skips any that already exist), out/<id>_<lang>/qa.json
"""
import guard  # noqa: F401  (first: caps threads)

import json
import os
import subprocess
import sys
import time
import unicodedata
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
import librosa
import mlx.core as mx
import mlx_whisper
import numpy as np
import soundfile as sf
import torch
from miocodec import MioCodecModel
from mlx_lm import batch_generate, load
from mlx_lm.sample_utils import make_sampler

import assemble

guard.cap_torch()
mx.set_cache_limit(512 * 1024 ** 2)  # don't let MLX hoard freed GPU buffers
LANGS = ["bn", "ta", "te", "ml", "or"]
TAKES, CHUNK = 3, 16  # 16-sequence batches keep MLX peaks small on a 16 GB Mac
# Whisper is much weaker on Malayalam (and reads Odia via Bengali), so their pass marks are looser.
GOOD_CER = {"bn": 0.20, "ta": 0.25, "te": 0.25, "ml": 0.45, "or": 0.35}
RETRY_CER = {"bn": 0.40, "ta": 0.45, "te": 0.45, "ml": 0.65, "or": 0.55}
SPEECH_OFFSET, CODEBOOK, TPS = 151669, 12800, 25
WHISPER = "mlx-community/whisper-large-v3-turbo"
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
COOLDOWN_S = 10
ASR = {"bn": ("bn", "এটা একটা বাংলা ভিডিও।"), "ta": ("ta", "இது ஒரு தமிழ் வீடியோ."),
       "te": ("te", "ఇది ఒక తెలుగు వీడియో."), "ml": ("ml", "ഇതൊരു മലയാളം വീഡിയോ ആണ്."),
       "or": ("bn", "এটা একটা বাংলা ভিডিও।")}  # Whisper has no Odia: read it with Bengali ASR (aligned Unicode)
FX = {"none": "", "cartoon": "treble=g=3:f=3200", "villain": "bass=g=4:f=120,aecho=0.8:0.6:35:0.18",
      "villain_f": "bass=g=3:f=180,aecho=0.8:0.5:28:0.14"}  # female villain: menace without a deep pitch-down


def asr_view(text, lang):
    if lang == "or":
        return "".join(chr(ord(c) - 0x180) if 0x0B00 <= ord(c) <= 0x0B7F else c for c in text)
    return text


def cer(ref, hyp):
    norm = lambda s: [c for c in unicodedata.normalize("NFC", s) if c.isalnum()]
    r, h = norm(ref), norm(hyp)[: 2 * max(len(norm(ref)), 1)]  # cap runaway ASR loops
    d = list(range(len(h) + 1))
    for i in range(1, len(r) + 1):
        prev, d[0] = d[0], i
        for j in range(1, len(h) + 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (r[i - 1] != h[j - 1]))
    return min(d[len(h)] / max(len(r), 1), 1.0)


def looped(text):
    """Whisper stuck repeating itself (a decoder failure, not evidence about the audio)."""
    words = text.split()
    runs = sum(1 for a, b in zip(words, words[1:]) if a == b)
    return runs >= 3 or any(text.count(c * 6) for c in set(text) if c.isalpha())


def median_f0(y, sr):
    if len(y) < sr // 5:
        return None
    f0, _, _ = librosa.pyin(librosa.resample(y, orig_sr=sr, target_sr=16000), fmin=60, fmax=700, sr=16000)
    f0 = f0[~np.isnan(f0)]
    return float(np.median(f0)) if len(f0) > 10 else None


class Engine:
    def __init__(self):
        t = time.time()
        self.lm, self.tok = load("SPRINGLab/Indic-Mio")
        self.codec = MioCodecModel.from_pretrained("Aratako/MioCodec-25Hz-24kHz").eval().to(DEVICE)
        self.sr = self.codec.config.sample_rate
        self.sampler = make_sampler(temp=0.8, top_p=0.9)
        mlx_whisper.transcribe(np.zeros(16000, dtype=np.float32), path_or_hf_repo=WHISPER)
        print(f"models ready in {time.time() - t:.1f}s", flush=True)

    def voices(self, plan, vocals_path):
        vox, _ = librosa.load(vocals_path, sr=self.sr, mono=True)
        out, ext = {}, {}
        for c in plan["cast"]:
            src = vox
            if c.get("ref_file"):  # voice borrowed from another clip (e.g. client: "keep VO voice female only")
                if c["ref_file"] not in ext:
                    ext[c["ref_file"]], _ = librosa.load(Path(__file__).resolve().parent / c["ref_file"], sr=self.sr, mono=True)
                src = ext[c["ref_file"]]
            ref = np.concatenate([src[int(a * self.sr): int(b * self.sr)] for a, b in c["ref_ranges"]])[: 10 * self.sr]
            with torch.no_grad():
                emb = self.codec.encode(torch.tensor(ref)[None].to(DEVICE), return_content=False).global_embedding
            out[c["id"]] = {"emb": emb, "f0": median_f0(ref, self.sr), **c}
        return out, vox

    def sample(self, items, takes):
        """items: [(lang, line)] -> {(lang, id): [wav, ...]}"""
        prompts, owners, budgets = [], [], []
        for lang, l in items:
            text = l[lang] + (f" <{l['tag']}>" if l.get("tag") else "")
            ids = self.tok.apply_chat_template([{"role": "user", "content": text}], add_generation_prompt=True)
            for _ in range(takes):
                prompts.append(ids)
                owners.append((lang, l))
                budgets.append(int(min(600, TPS * (l["max_end"] - l["start"]) * 3 + 40)))
        res = {}
        for i in range(0, len(prompts), CHUNK):
            r = batch_generate(self.lm, self.tok, prompts[i:i + CHUNK], max_tokens=budgets[i:i + CHUNK],
                               sampler=self.sampler, return_token_ids=True)
            for (lang, l), toks in zip(owners[i:i + CHUNK], r.token_ids):
                codes = [t - SPEECH_OFFSET for t in list(toks) if SPEECH_OFFSET <= t < SPEECH_OFFSET + CODEBOOK]
                if len(codes) >= 5:
                    res.setdefault((lang, l["id"]), []).append(codes)
            mx.clear_cache()
        return res

    def render(self, codes, emb):
        with torch.no_grad():
            wav = self.codec.decode(global_embedding=emb, content_token_indices=torch.tensor(codes, device=DEVICE))
        return wav.squeeze().float().cpu().numpy()

    def check(self, wav, lang, l):
        asr_lang, hint = ASR[lang]
        audio = np.concatenate([np.zeros(4000, np.float32), librosa.resample(wav, orig_sr=self.sr, target_sr=16000),
                                np.zeros(8000, np.float32)])  # a little silence around short clips steadies Whisper
        heard = ""
        for opts in ({"initial_prompt": hint}, {}):  # second opinion without the hint if Whisper loops
            heard = mlx_whisper.transcribe(audio, path_or_hf_repo=WHISPER, language=asr_lang,
                                           temperature=(0.0, 0.3, 0.6), compression_ratio_threshold=1.8,
                                           condition_on_previous_text=False, **opts)["text"].strip()
            if not looped(heard):
                break
        speech, _ = librosa.effects.trim(wav, top_db=35)
        fit = max(0.0, len(speech) / self.sr / (l["max_end"] - l["start"]) - 1.0)
        letters = [c for c in heard if c.isalpha()]
        if letters and sum(c.isascii() for c in letters) / len(letters) > 0.5:
            return 0.15, fit, heard  # ASR spelled the (loanword-heavy) line in English: it was recognisable
        return cer(asr_view(l[lang], lang), heard), fit, heard

    def finish(self, wav, voice):
        """Match the character's original pitch, add character fx."""
        shift = voice.get("pitch_semitones", 0)
        f0 = median_f0(wav, self.sr)
        if voice["f0"] and f0:
            diff = 12 * np.log2(voice["f0"] / f0)
            if abs(diff) > 6:  # a pitch tracker octave error on one side, not a real 6+ semitone gap
                diff -= 12 * np.sign(diff)
            diff = float(np.clip(diff, -5, 5))
            if voice["fx"] != "none" or abs(diff) > 2:
                shift += diff
        shift = float(np.clip(shift, -7, 7))
        filters = []
        if abs(shift) > 0.7:
            r = 2 ** (shift / 12)
            filters.append(f"asetrate={self.sr * r:.0f},aresample={self.sr},atempo={1 / r:.5f}")
        if FX.get(voice["fx"]):
            filters.append(FX[voice["fx"]])
        if not filters:
            return wav
        p = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(self.sr), "-ac", "1", "-i", "pipe:0",
                            "-af", ",".join(filters), "-f", "f32le", "pipe:1"],
                           input=wav.astype(np.float32).tobytes(), capture_output=True, check=True)
        return np.frombuffer(p.stdout, dtype=np.float32)

    def process(self, wd, out_root):
        t0 = time.time()
        plan = json.loads((wd / "plan.json").read_text())
        vid = wd.name
        todo = [lang for lang in LANGS if not (out_root / f"{vid}_{lang}.mp4").exists()]
        if not todo:
            return
        voices, vox = self.voices(plan, wd / "stems" / "vocals.wav")
        lines = plan["lines"]
        spoken = [l for l in lines if not l.get("keep_original")]
        mx.random.seed(abs(hash(vid)) % (2 ** 31))

        pool = self.sample([(lang, l) for lang in todo for l in spoken], TAKES)
        chosen, report = {}, {lang: [] for lang in todo}
        retry = []
        for lang in todo:
            for l in spoken:
                best = None
                for codes in pool.get((lang, l["id"]), []):
                    wav = self.render(codes, voices[l["speaker"]]["emb"])
                    c, fit, heard = self.check(wav, lang, l)
                    if best is None or (round(c / 0.08), fit) < (round(best[0] / 0.08), best[1]):
                        best = (c, fit, heard, wav)
                    if c <= GOOD_CER[lang] and fit < 0.6:
                        break
                chosen[(lang, l["id"])] = best
                if best is None or best[0] > RETRY_CER[lang]:
                    retry.append((lang, l))
        if retry:
            extra = self.sample(retry, TAKES)
            for lang, l in retry:
                best = chosen.get((lang, l["id"]))
                for codes in extra.get((lang, l["id"]), []):
                    wav = self.render(codes, voices[l["speaker"]]["emb"])
                    c, fit, heard = self.check(wav, lang, l)
                    if best is None or (round(c / 0.08), fit) < (round(best[0] / 0.08), best[1]):
                        best = (c, fit, heard, wav)
                    if c <= GOOD_CER[lang] and fit < 0.6:
                        break
                chosen[(lang, l["id"])] = best

        stems = wd / "stems"
        for lang in todo:
            clips = out_root / f"{vid}_{lang}"
            clips.mkdir(parents=True, exist_ok=True)
            for l in lines:
                if l.get("keep_original"):
                    sf.write(clips / f"line_{l['id']}.wav", vox[int(l["start"] * self.sr): int(l["end"] * self.sr)], self.sr)
                    continue
                c, fit, heard, wav = chosen[(lang, l["id"])]
                sf.write(clips / f"line_{l['id']}.wav", self.finish(wav, voices[l["speaker"]]), self.sr)
                report[lang].append({"id": l["id"], "speaker": l["speaker"], "cer": round(c, 2), "heard": heard})
            (clips / "script.json").write_text(json.dumps({"language": lang, "lines": lines}, ensure_ascii=False))
            (clips / "qa.json").write_text(json.dumps(report[lang], ensure_ascii=False, indent=1))
            assemble.main(clips / "script.json", clips, str(out_root / f"{vid}_{lang}.mp4"), wd / "source.mp4",
                          stems / "no_vocals.wav", stems / "vocals.wav")
        mx.clear_cache()
        if DEVICE == "mps":
            torch.mps.empty_cache()
        worst = max((r["cer"] for rs in report.values() for r in rs), default=0)
        print(f"[{vid}] {len(todo)} langs in {time.time() - t0:.0f}s | worst line CER {worst:.2f} | "
              f"retried {len(retry)}", flush=True)


def main(work, out_root, *args):
    work, out_root = Path(work), Path(out_root)
    out_root.mkdir(exist_ok=True)
    expect = int(args[args.index("--watch") + 1]) if "--watch" in args else 0
    reverse = "--reverse" in args  # a second engine works from the other end of the list
    eng, done = Engine(), set()
    while True:
        ready = sorted((p.parent for p in work.glob("*/plan.json")
                        if p.parent.name not in done and (p.parent / "plan.ok").exists()), reverse=reverse)
        for wd in ready:
            try:  # claim the video so two engines never work on the same one
                os.close(os.open(wd / "dub.lock", os.O_CREAT | os.O_EXCL | os.O_WRONLY))
            except FileExistsError:
                done.add(wd.name)
                continue
            guard.wait_for_headroom(wd.name)
            try:
                eng.process(wd, out_root)
            except Exception as e:  # one bad plan must not stop the batch
                print(f"[{wd.name}] FAILED: {e!r}", flush=True)
            done.add(wd.name)
            time.sleep(COOLDOWN_S)
            if (out_root / ".restart").exists():  # pick up code changes between videos
                (out_root / ".restart").unlink()
                print("restart requested", flush=True)
                sys.exit(3)
        if len(done) >= expect:
            break
        time.sleep(20)
    print(f"DUB DONE: {len(done)} videos", flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:])
