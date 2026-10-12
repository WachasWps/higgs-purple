"""Fast batch dubber. Loads Indic-Mio (MLX), MioCodec and Whisper (MLX) once, then runs many jobs.

For each job, all takes of all lines are sampled in ONE batched MLX pass, decoded in the
creator's voice, checked with a Whisper back-transcription, and the best take per line is
kept (one retry round for lines that come back unintelligible). Mixing runs on a thread pool
so the GPU moves straight on to the next job.

Usage: .venv/bin/python dubfast.py jobs.json
jobs.json: [{"script": "script_ta.json", "video": "source/x.mp4", "stems": "<dir with vocals.wav + no_vocals.wav>",
             "out": "out/x_ta.mp4"}, ...]
"""
import hashlib
import json
import sys
import time
import unicodedata
import warnings
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

warnings.filterwarnings("ignore")
import librosa
import mlx.core as mx
import mlx_whisper
import numpy as np
import soundfile as sf
import torch
from miocodec import MioCodecModel, load_audio
from mlx_lm import batch_generate, load
from mlx_lm.sample_utils import make_sampler

import assemble

TAKES = 3
RETRY_CER = 0.25
SPEECH_OFFSET, CODEBOOK, TOKENS_PER_S = 151669, 12800, 25
WHISPER = "mlx-community/whisper-large-v3-turbo"
ASR_LANG = {"bn": "bn", "ta": "ta", "te": "te", "ml": "ml", "hi": "hi", "mr": "mr", "kn": "kn", "gu": "gu", "pa": "pa",
            "or": "bn"}  # Whisper has no Odia; Odia is read by Bengali ASR (close phonology, aligned Unicode blocks)
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"


def asr_view(text, lang):
    """Map the target text into the script the ASR will answer in."""
    if lang == "or":  # Odia U+0B00..0B7F sits exactly 0x180 above Bengali U+0980..09FF
        return "".join(chr(ord(c) - 0x180) if 0x0B00 <= ord(c) <= 0x0B7F else c for c in text)
    return text


def cer(ref, hyp):
    norm = lambda s: [c for c in unicodedata.normalize("NFC", s) if c.isalnum()]
    r, h = norm(ref), norm(hyp)
    d = list(range(len(h) + 1))
    for i in range(1, len(r) + 1):
        prev, d[0] = d[0], i
        for j in range(1, len(h) + 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (r[i - 1] != h[j - 1]))
    return d[len(h)] / max(len(r), 1)


class Dubber:
    def __init__(self):
        t = time.time()
        self.lm, self.tok = load("SPRINGLab/Indic-Mio")
        self.codec = MioCodecModel.from_pretrained("Aratako/MioCodec-25Hz-24kHz").eval().to(DEVICE)
        self.sr = self.codec.config.sample_rate
        self.sampler = make_sampler(temp=0.8, top_p=0.9)
        self.spk_cache = {}
        mlx_whisper.transcribe(np.zeros(16000, dtype=np.float32), path_or_hf_repo=WHISPER)  # warm-up / download
        print(f"models ready in {time.time() - t:.1f}s", flush=True)

    def speaker(self, vocals_path):
        if vocals_path not in self.spk_cache:
            ref = load_audio(vocals_path, sample_rate=self.sr)[..., : 10 * self.sr].to(DEVICE)
            with torch.no_grad():
                self.spk_cache[vocals_path] = self.codec.encode(ref, return_content=False).global_embedding
        return self.spk_cache[vocals_path]

    def sample(self, lines, lang, spk, takes, take_dir, offset):
        """One batched pass: `takes` samples for every line. Returns {line_id: [(cer, overflow, dur, heard, path)]}."""
        prompts, owners, budgets = [], [], []
        for l in lines:
            text = l[lang] + (f" <{l['tag']}>" if l.get("tag") else "")
            ids = self.tok.apply_chat_template([{"role": "user", "content": text}], add_generation_prompt=True)
            slot = l["max_end"] - l["start"]
            for k in range(takes):
                prompts.append(ids)
                owners.append((l, offset + k))
                budgets.append(int(min(600, TOKENS_PER_S * slot * 3 + 40)))  # cap runaway babble
        resp = batch_generate(self.lm, self.tok, prompts, max_tokens=budgets, sampler=self.sampler,
                              return_token_ids=True)
        out = {}
        for (l, k), toks in zip(owners, resp.token_ids):
            codes = [t - SPEECH_OFFSET for t in list(toks) if SPEECH_OFFSET <= t < SPEECH_OFFSET + CODEBOOK]
            if len(codes) < 5:
                continue
            with torch.no_grad():
                wav = self.codec.decode(global_embedding=spk,
                                        content_token_indices=torch.tensor(codes, device=DEVICE))
            wav = wav.squeeze().float().cpu().numpy()
            path = take_dir / f"line_{l['id']}_take{k}.wav"
            sf.write(path, wav, self.sr)
            speech, _ = librosa.effects.trim(wav, top_db=35)
            dur = len(speech) / self.sr
            heard = mlx_whisper.transcribe(
                librosa.resample(wav, orig_sr=self.sr, target_sr=16000), path_or_hf_repo=WHISPER,
                language=ASR_LANG.get(lang, lang), temperature=0.0, condition_on_previous_text=False,
            )["text"].strip()
            slot = l["max_end"] - l["start"]
            out.setdefault(l["id"], []).append(
                (cer(asr_view(l[lang], lang), heard), max(0.0, dur / slot - 1.0), dur, heard, path))
        return out

    def run(self, job):
        t0 = time.time()
        script = json.loads(Path(job["script"]).read_text())
        lang, lines = script["language"], script["lines"]
        clips_dir = Path(job["out"]).with_suffix("")  # out/x_ta/ holds the kept clips + takes
        take_dir = clips_dir / "takes"
        take_dir.mkdir(parents=True, exist_ok=True)
        stems = Path(job["stems"])
        spk = self.speaker(str(stems / "vocals.wav"))
        mx.random.seed(int(hashlib.md5(job["out"].encode()).hexdigest()[:8], 16))

        cands = self.sample(lines, lang, spk, TAKES, take_dir, 0)
        weak = [l for l in lines if min((c[0] for c in cands.get(l["id"], [])), default=1.0) > RETRY_CER]
        if weak:
            for lid, extra in self.sample(weak, lang, spk, TAKES, take_dir, TAKES).items():
                cands.setdefault(lid, []).extend(extra)

        report = []
        for l in lines:
            best = min(cands[l["id"]], key=lambda c: (round(c[0] / 0.08), c[1]))
            sf.write(clips_dir / f"line_{l['id']}.wav", sf.read(best[4])[0], self.sr)
            report.append({"id": l["id"], "cer": round(best[0], 2), "dur": round(best[2], 2), "heard": best[3]})
        (clips_dir / "qa.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))
        print(f"[{Path(job['out']).name}] voice done in {time.time() - t0:.1f}s | "
              f"worst line CER {max(r['cer'] for r in report):.2f} | retried {len(weak)} line(s)", flush=True)
        return clips_dir


def main(jobs_path):
    jobs = json.loads(Path(jobs_path).read_text())
    dubber = Dubber()
    t = time.time()
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = []
        for job in jobs:
            clips_dir = dubber.run(job)
            stems = Path(job["stems"])
            futures.append(pool.submit(assemble.main, job["script"], clips_dir, job["out"], job["video"],
                                       stems / "no_vocals.wav", stems / "vocals.wav"))
        for f in futures:
            f.result()
    print(f"ALL {len(jobs)} jobs done in {time.time() - t:.1f}s", flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
