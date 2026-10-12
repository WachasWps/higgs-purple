"""Multi-character dubbing engine on an NVIDIA GPU: CUDA port of dubplan.py (same behaviour, same outputs).

- Every cast member's voice is cloned from their own ref_ranges in the original (Demucs) vocals (MioCodec on CUDA).
- All takes for all lines in all pending languages are sampled by Indic-Mio (TAKES samples per prompt), on vLLM or,
  where vLLM can't run (e.g. V100), on transformers with batched left-padded sampling. Both use the same prompts,
  sampling (T=0.8, top-p 0.9), per-line token budgets and speech-token extraction.
- Takes are checked lazily with a faster-whisper back-transcription (stop at the first good take), with per-language
  GOOD/RETRY CER marks and one retry round; Odia is read by Bengali ASR, a Latin-script answer counts as heard.
- Character finishing: pitch matched to the original character (+ plan offset), plus `cartoon` / `villain` fx.
- `keep_original` lines reuse the original sound (laughs, screams, jingles). Mixing is the unchanged assemble.py.

Throughput design (one GPU: L40S / A100 / V100): ONE engine process that voices many videos per GPU pass.
  A video is small GPU work (~40 prompts for a 0.6B LM, ~80 short codec decodes + Whisper reads), so throughput is
  decided by batch size and by keeping the GPU busy while the CPU does pitch tracking and mixing:
  * GROUP videos are claimed together. All their lines x languages x takes are sampled together (vLLM: ONE generate()
    call with continuous batching; transformers: budget-sorted batches of BATCH prompts x TAKES). The lazy QA runs in
    rounds (take k of every still-open line); each round is one batch of codec decodes plus batched faster-whisper
    passes across all videos and languages.
  * The CPU stage (pyin pitch-match + ffmpeg fx in a spawned process pool, assemble.main on a thread pool) runs in
    the background while the GPU moves on to the next group. The backlog is capped to keep memory bounded.
  * One copy of every model and one CUDA context: no time-slicing between processes, no duplicated weights / KV,
    and all spare cores go to the pyin/ffmpeg work. (On a 16 GB V100 this is also the only layout that fits.)
  --workers N runs N such engines on the same GPU (dub.lock keeps them apart). Each vLLM gets ~0.18 of the GPU,
  and the engines start one after another so each sizes its KV cache from the memory that is really free. Use it
  only on big cards when nvidia-smi shows the GPU idling (< ~60 %) because one engine's Python loop is the limit.

Usage: python vm/dubplan_cuda.py work/ out/ [--watch N] [--reverse] [--group 8] [--workers 1] [--gpu-util 0.4]
           [--backend auto|vllm|transformers] [--only id1,id2,... | --ids-file ids.txt] [--jobs N]
           (--watch: wait for N validated plans to appear; --only/--ids-file: just these videos)
       python vm/dubplan_cuda.py --selftest work/ [--backend ...]   (smoke test; exits non-zero on failure)
Env: DTYPE, CODEC_DTYPE, WHISPER_COMPUTE (see cudacfg.py), BATCH (transformers prompts per batch, default 24),
     ASR_BATCH (Whisper windows per GPU batch; default 16, 8 below compute capability 8.0)
Outputs: out/<id>_<lang>.mp4 (skips any that already exist), out/<id>_<lang>/{line_*.wav, script.json, qa.json}
"""
import bisect
import gc
import json
import multiprocessing as mp
import os
import subprocess
import sys
import time
import unicodedata
import warnings
import zlib
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path

warnings.filterwarnings("ignore")
import librosa
import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # dub/: the unchanged assemble.py
import assemble
import cudacfg

# torch / vLLM / transformers / faster-whisper / MioCodec are imported in Engine.__init__: the CPU pool's *spawned*
# workers re-import this module, and they only need numpy + librosa.
torch = None

LANGS = ["bn", "ta", "te", "ml", "or"]
TAKES = 3
# Whisper is much weaker on Malayalam (and reads Odia via Bengali), so their pass marks are looser.
GOOD_CER = {"bn": 0.20, "ta": 0.25, "te": 0.25, "ml": 0.45, "or": 0.35}
RETRY_CER = {"bn": 0.40, "ta": 0.45, "te": 0.45, "ml": 0.65, "or": 0.55}
SPEECH_OFFSET, CODEBOOK, TPS = 151669, 12800, 25
TTS, CODEC = "SPRINGLab/Indic-Mio", "Aratako/MioCodec-25Hz-24kHz"
STOP_IDS = [151645, 151643]  # <|im_end|>, <|endoftext|>: Indic-Mio's generation_config eos ids (151643 = its pad)
WHISPER = os.environ.get("WHISPER_MODEL", "large-v3-turbo")  # faster-whisper alias of mobiuslabsgmbh/faster-whisper-large-v3-turbo
DEVICE = "cuda"
ASR = {"bn": ("bn", "এটা একটা বাংলা ভিডিও।"), "ta": ("ta", "இது ஒரு தமிழ் வீடியோ."),
       "te": ("te", "ఇది ఒక తెలుగు వీడియో."), "ml": ("ml", "ഇതൊരു മലയാളം വീഡിയോ ആണ്."),
       "or": ("bn", "এটা একটা বাংলা ভিডিও।")}  # Whisper has no Odia: read it with Bengali ASR (aligned Unicode)
FX = {"none": "", "cartoon": "treble=g=3:f=3200", "villain": "bass=g=4:f=120,aecho=0.8:0.6:35:0.18"}
GROUP = 8        # videos per GPU pass
ASR_CHUNK = 64   # clips per batched-Whisper call
VLLM_DTYPES = {"bf16": "bfloat16", "fp16": "float16", "fp32": "float32"}


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


def compression_ratio(text):
    """Whisper's own repetition test (gzip ratio of the UTF-8 text), used by its temperature fallback."""
    b = text.encode("utf-8")
    return len(b) / len(zlib.compress(b)) if b else 0.0


def median_f0(y, sr):
    if len(y) < sr // 5:
        return None
    f0, _, _ = librosa.pyin(librosa.resample(y, orig_sr=sr, target_sr=16000), fmin=60, fmax=700, sr=16000)
    f0 = f0[~np.isnan(f0)]
    return float(np.median(f0)) if len(f0) > 10 else None


def finish(wav, sr, voice):
    """Match the character's original pitch, add character fx. (CPU: runs in the process pool.)"""
    shift = voice.get("pitch_semitones", 0)
    f0 = median_f0(wav, sr)
    if voice["f0"] and f0:
        diff = 12 * np.log2(voice["f0"] / f0)
        if voice["fx"] != "none" or abs(diff) > 2:
            shift += diff
    shift = float(np.clip(shift, -7, 7))
    filters = []
    if abs(shift) > 0.7:
        r = 2 ** (shift / 12)
        filters.append(f"asetrate={sr * r:.0f},aresample={sr},atempo={1 / r:.5f}")
    if FX.get(voice["fx"]):
        filters.append(FX[voice["fx"]])
    if not filters:
        return wav
    p = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(sr), "-ac", "1", "-i", "pipe:0",
                        "-af", ",".join(filters), "-f", "f32le", "pipe:1"],
                       input=wav.astype(np.float32).tobytes(), capture_output=True, check=True)
    return np.frombuffer(p.stdout, dtype=np.float32)


def fx_spec(voice):
    """The picklable part of a voice that finish() needs (waits for its pitch from the CPU pool)."""
    f0 = voice["f0"]
    return {"f0": f0.result() if hasattr(f0, "result") else f0, "fx": voice["fx"],
            "pitch_semitones": voice.get("pitch_semitones", 0)}


def better(c, fit, best):
    """dubplan.py's ranking: intelligibility in 0.08-CER buckets first, then timing fit."""
    return best is None or (round(c / 0.08), fit) < (round(best[0] / 0.08), best[1])


def one_thread():
    """Pool workers get one BLAS/OpenMP thread each: the pool itself fills the cores."""
    global _LIMITS
    try:
        from threadpoolctl import threadpool_limits
        _LIMITS = threadpool_limits(1)
    except ImportError:
        pass


class VllmTTS:
    """Indic-Mio on vLLM (offline LLM): n samples per prompt, per-prompt max_tokens, continuous batching."""
    name = "vllm"

    def __init__(self, dtype, gpu_util, max_seqs):
        from vllm import LLM, SamplingParams
        from vllm.inputs import TokensPrompt
        self.SamplingParams, self.TokensPrompt, self.dtype = SamplingParams, TokensPrompt, dtype
        self.lm = LLM(model=TTS, dtype=VLLM_DTYPES[dtype], gpu_memory_utilization=gpu_util, max_model_len=2048,
                      max_num_seqs=max_seqs, enable_prefix_caching=True, seed=int.from_bytes(os.urandom(3), "little"))
        self.tok = self.lm.get_tokenizer()

    def generate(self, prompts, budgets, takes):
        """-> per prompt: `takes` lists of generated token ids."""
        params = [self.SamplingParams(n=takes, temperature=0.8, top_p=0.9, stop_token_ids=STOP_IDS, max_tokens=b,
                                      detokenize=False) for b in budgets]
        res = self.lm.generate([self.TokensPrompt(prompt_token_ids=p) for p in prompts], params, use_tqdm=False)
        return [[list(o.token_ids) for o in r.outputs] for r in res]


class HfTTS:
    """Indic-Mio on transformers (GPUs vLLM refuses, e.g. V100): SDPA attention, left-padded batches of BATCH prompts
    x `takes` samples. A batch runs to its largest budget and each sample is then cut at EOS and at its own line's
    budget, which is the same as a per-sample max_tokens. fp16 falls back to fp32 if it overflows (probe or sampling)."""
    name = "transformers"

    def __init__(self, dtype):
        from transformers import AutoTokenizer
        self.tok = AutoTokenizer.from_pretrained(TTS)
        self.pad = self.tok.pad_token_id if self.tok.pad_token_id is not None else STOP_IDS[1]
        self.batch = int(os.environ.get("BATCH", 24))
        torch.manual_seed(int.from_bytes(os.urandom(4), "little"))
        self.dtype, self.lm = dtype, self._load(dtype)
        if dtype != "fp32" and not self._finite():
            print(f"Indic-Mio overflows in {dtype} on this GPU: using fp32", flush=True)
            self._to_fp32()

    def _load(self, dtype):
        import transformers
        from packaging.version import Version
        from transformers import AutoModelForCausalLM
        td = cudacfg.torch_dtype(dtype)
        kw = "dtype" if Version(transformers.__version__) >= Version("4.56") else "torch_dtype"  # renamed in 4.56
        lm = AutoModelForCausalLM.from_pretrained(TTS, attn_implementation="sdpa", **{kw: td})
        return lm.to(device=DEVICE, dtype=td).eval()

    def _to_fp32(self):
        del self.lm
        gc.collect()
        torch.cuda.empty_cache()
        self.dtype, self.lm = "fp32", self._load("fp32")

    def _finite(self):
        """Quick probe: greedy-decode a short line, then check every logit over prompt + output is finite."""
        ids = self.tok.apply_chat_template([{"role": "user", "content": "এটা একটা পরীক্ষা। <happy>"}],
                                           add_generation_prompt=True)
        x = torch.tensor([list(ids["input_ids"] if hasattr(ids, "keys") else ids)], device=DEVICE)
        with torch.no_grad():
            y = self.lm.generate(x, attention_mask=torch.ones_like(x), do_sample=False, max_new_tokens=48,
                                 pad_token_id=self.pad)
            return bool(torch.isfinite(self.lm(y).logits.float()).all())

    def _batch(self, prompts, max_new, takes):
        n = max(map(len, prompts))
        ids = torch.full((len(prompts), n), self.pad, dtype=torch.long)
        mask = torch.zeros_like(ids)
        for r, p in enumerate(prompts):  # left padding: every prompt ends where generation starts
            ids[r, n - len(p):] = torch.tensor(p)
            mask[r, n - len(p):] = 1
        with torch.no_grad():
            gen = self.lm.generate(input_ids=ids.to(DEVICE), attention_mask=mask.to(DEVICE), do_sample=True,
                                   temperature=0.8, top_p=0.9, top_k=0, repetition_penalty=1.0,
                                   max_new_tokens=max_new, num_return_sequences=takes,
                                   eos_token_id=STOP_IDS, pad_token_id=self.pad)
        return gen[:, n:].tolist()  # rows: prompt 0 take 0..takes-1, prompt 1 take 0.., ...

    @staticmethod
    def _cut(seq, budget):
        seq = seq[:budget]
        for k, t in enumerate(seq):
            if t in STOP_IDS:
                return seq[:k]
        return seq

    def generate(self, prompts, budgets, takes):
        """-> per prompt: `takes` lists of generated token ids."""
        out = [None] * len(prompts)
        order = sorted(range(len(prompts)), key=lambda i: budgets[i])  # similar budgets share a batch
        for s in range(0, len(order), self.batch):
            idx = order[s: s + self.batch]
            args = ([prompts[i] for i in idx], max(budgets[i] for i in idx), takes)
            try:
                seqs = self._batch(*args)
            except RuntimeError as e:  # fp16 overflow surfaces as inf/nan probabilities in sampling
                if self.dtype == "fp32" or not any(w in str(e) for w in ("inf", "nan")):
                    raise
                print(f"Indic-Mio overflowed in {self.dtype} while sampling: switching to fp32", flush=True)
                self._to_fp32()
                seqs = self._batch(*args)
            for j, i in enumerate(idx):
                out[i] = [self._cut(q, budgets[i]) for q in seqs[j * takes: (j + 1) * takes]]
        torch.cuda.empty_cache()  # hand the KV memory back: CTranslate2 (Whisper) allocates outside torch's cache
        return out


def make_tts(backend, dtype, gpu_util, max_seqs):
    """auto: vLLM if it is installed and accepts this GPU, else transformers (setup.sh skips vLLM below cc 8.0)."""
    if backend not in ("auto", "vllm", "transformers"):
        raise ValueError(f"--backend must be auto, vllm or transformers (got {backend!r})")
    if backend != "transformers":
        try:
            return VllmTTS(dtype, gpu_util, max_seqs)
        except Exception as e:  # not installed, or refuses this GPU / dtype
            if backend == "vllm":
                raise
            print(f"vLLM unavailable ({e!r:.300}); using transformers", flush=True)
            gc.collect()
            torch.cuda.empty_cache()
    return HfTTS(dtype)


class Engine:
    def __init__(self, backend="auto", gpu_util=0.40, max_seqs=512, jobs=None, threads=8):
        global torch
        t = time.time()
        import torch
        from faster_whisper import BatchedInferencePipeline, WhisperModel
        from miocodec import MioCodecModel
        # TTS first: vLLM sizes its KV cache from the GPU memory it sees free at start-up.
        self.tts = make_tts(backend, cudacfg.dtype_name(), gpu_util, max_seqs)
        self.tok = self.tts.tok
        self.tts_tokens, self.tts_seconds = 0, 0.0
        self.codec_dtype = cudacfg.codec_dtype()
        cudacfg.patch_codec(self.codec_dtype)
        self.codec = MioCodecModel.from_pretrained(CODEC).eval().to(DEVICE)
        self.sr = self.codec.config.sample_rate
        self.whisper_compute = cudacfg.whisper_compute()
        self.whisper = WhisperModel(WHISPER, device=DEVICE, compute_type=self.whisper_compute)
        self.batched = BatchedInferencePipeline(model=self.whisper)
        self.asr_batch_size = int(os.environ.get("ASR_BATCH", 16 if cudacfg.compute_cap() >= (8, 0) else 8))
        list(self.whisper.transcribe(np.zeros(16000, dtype=np.float32), language="bn")[0])  # warm-up
        # spawn, not fork: this process holds CUDA (+ vLLM threads). Workers start lazily and import light modules.
        self.cpu = ProcessPoolExecutor(jobs or max(2, (os.cpu_count() or 8) - 3),
                                       mp_context=mp.get_context("spawn"), initializer=one_thread)
        self.io = ThreadPoolExecutor(threads)
        print(f"models ready in {time.time() - t:.1f}s | {self.describe()}", flush=True)

    def describe(self):
        cc = ".".join(map(str, cudacfg.compute_cap()))
        return (f"GPU cc {cc} | TTS {self.tts.name} {self.tts.dtype} | codec {self.codec_dtype} | "
                f"whisper {self.whisper_compute}")

    def close(self):
        self.io.shutdown()
        self.cpu.shutdown()

    def voices(self, plan, vocals_path):
        vox, _ = librosa.load(vocals_path, sr=self.sr, mono=True)
        out = {}
        for c in plan["cast"]:
            ref = np.concatenate([vox[int(a * self.sr): int(b * self.sr)] for a, b in c["ref_ranges"]])[: 10 * self.sr]
            with torch.no_grad():  # same (1, samples) call as dubplan.py
                emb = self.codec.encode(torch.tensor(ref)[None].to(DEVICE), return_content=False).global_embedding
            out[c["id"]] = {"emb": emb, "f0": self.cpu.submit(median_f0, ref, self.sr), **c}  # pitch: a CPU future
        return out, vox

    def sample(self, items, takes):
        """items: [(key, lang, line)] -> {(key, lang, id): [codes, ...]}. Everything in `items` is sampled together."""
        prompts, budgets, owners = [], [], []
        for key, lang, l in items:
            text = l[lang] + (f" <{l['tag']}>" if l.get("tag") else "")
            ids = self.tok.apply_chat_template([{"role": "user", "content": text}], add_generation_prompt=True)
            prompts.append(list(ids["input_ids"] if hasattr(ids, "keys") else ids))
            budgets.append(int(min(600, TPS * (l["max_end"] - l["start"]) * 3 + 40)))
            owners.append((key, lang, l["id"]))
        res = {}
        if not prompts:
            return res
        t0 = time.time()
        outs = self.tts.generate(prompts, budgets, takes)
        self.tts_seconds += time.time() - t0
        for owner, seqs in zip(owners, outs):
            for toks in seqs:
                self.tts_tokens += len(toks)
                codes = [t - SPEECH_OFFSET for t in toks if SPEECH_OFFSET <= t < SPEECH_OFFSET + CODEBOOK]
                if len(codes) >= 5:
                    res.setdefault(owner, []).append(codes)
        return res

    def render(self, codes, emb):
        with torch.no_grad():
            wav = self.codec.decode(global_embedding=emb, content_token_indices=torch.tensor(codes, device=DEVICE))
        return wav.squeeze().float().cpu().numpy()

    def asr_batch(self, audios, lang, hint):
        """One batched faster-whisper pass over many 16 kHz clips -> texts. Clips are laid end to end, each in its own
        >15 s window: faster-whisper merges consecutive windows while their total stays <= 30 s, so >15 s windows
        keep every clip in a Whisper pass of its own (no shared context), exactly like separate transcribe() calls."""
        texts = []
        for s in range(0, len(audios), ASR_CHUNK):
            part = [a[: int(29.5 * 16000)] for a in audios[s: s + ASR_CHUNK]]
            starts, t = [], 0.0
            for a in part:
                starts.append(t)
                t += max(15.1, len(a) / 16000 + 0.1)
            buf = np.zeros(int(t * 16000) + 16000, dtype=np.float32)
            for a0, a in zip(starts, part):
                buf[int(a0 * 16000): int(a0 * 16000) + len(a)] = a
            clips = [{"start": a, "end": b} for a, b in zip(starts, starts[1:] + [t])]
            segs, _ = self.batched.transcribe(buf, language=lang, initial_prompt=hint, beam_size=1, temperature=0.0,
                                              vad_filter=False, clip_timestamps=clips, without_timestamps=True,
                                              batch_size=self.asr_batch_size)
            heard = [""] * len(part)
            for seg in segs:
                heard[max(bisect.bisect_right(starts, seg.start + 1e-3) - 1, 0)] += seg.text
            texts += [h.strip() for h in heard]
        return texts

    def asr_one(self, audio, lang, hint):
        """dubplan.py's exact check: temperature fallback, then a second opinion without the hint if Whisper loops."""
        heard = ""
        for opts in ({"initial_prompt": hint}, {}):
            segs, _ = self.whisper.transcribe(audio, language=lang, beam_size=1, temperature=(0.0, 0.3, 0.6),
                                              compression_ratio_threshold=1.8, condition_on_previous_text=False,
                                              vad_filter=False, **opts)
            heard = "".join(s.text for s in segs).strip()
            if not looped(heard):
                break
        return heard

    def check_many(self, reqs):
        """[(wav, lang, line)] -> [(cer, fit, heard)], scored exactly like dubplan.py's check()."""
        audio = [np.concatenate([np.zeros(4000, np.float32), librosa.resample(w, orig_sr=self.sr, target_sr=16000),
                                 np.zeros(8000, np.float32)]) for w, _, _ in reqs]  # silence around clips steadies Whisper
        heard = [""] * len(reqs)
        by_asr = defaultdict(list)
        for i, (_, lang, _) in enumerate(reqs):
            by_asr[ASR[lang]].append(i)
        for (asr_lang, hint), idx in by_asr.items():
            for i, text in zip(idx, self.asr_batch([audio[i] for i in idx], asr_lang, hint)):
                heard[i] = text
        out = []
        for i, (wav, lang, l) in enumerate(reqs):
            # batched decoding has no temperature fallback: redo decoder failures one by one, as dubplan.py would
            if looped(heard[i]) or compression_ratio(heard[i]) > 1.8:
                heard[i] = self.asr_one(audio[i], *ASR[lang])
            speech, _ = librosa.effects.trim(wav, top_db=35)
            fit = max(0.0, len(speech) / self.sr / (l["max_end"] - l["start"]) - 1.0)
            letters = [c for c in heard[i] if c.isalpha()]
            if letters and sum(c.isascii() for c in letters) / len(letters) > 0.5:
                out.append((0.15, fit, heard[i]))  # ASR spelled the (loanword-heavy) line in English: recognisable
            else:
                out.append((cer(asr_view(l[lang], lang), heard[i]), fit, heard[i]))
        return out

    def pick(self, items, pool, emb, best=None, lazy=True):
        """Best take per item -> {(key, lang, id): (cer, fit, heard, wav)}. As in dubplan.py, takes are checked in
        order and (lazy) a line stops at its first good take. Here that runs in rounds, take k of every still-open
        line at once, so each round's renders and Whisper reads are batched across lines, languages and videos."""
        best = dict(best or {})
        open_items, k = list(items), 0
        while open_items:
            batch = [(it, pool[(it[0], it[1], it[2]["id"])][k]) for it in open_items
                     if k < len(pool.get((it[0], it[1], it[2]["id"]), []))]
            if not batch:
                break
            wavs = [self.render(codes, emb(key, l)) for (key, _, l), codes in batch]
            scores = self.check_many([(w, lang, l) for w, ((_, lang, l), _) in zip(wavs, batch)])
            open_items = []
            for ((key, lang, l), _), wav, (c, fit, heard) in zip(batch, wavs, scores):
                if better(c, fit, best.get((key, lang, l["id"]))):
                    best[(key, lang, l["id"])] = (c, fit, heard, wav)
                if not (lazy and c <= GOOD_CER[lang] and fit < 0.6):
                    open_items.append((key, lang, l))
            k += 1
        return best

    def process_group(self, wds, out_root):
        """GPU stage for a group of videos. Returns the futures of their CPU stage (finish + write + assemble)."""
        t0 = time.time()
        jobs = {}
        for wd in wds:
            try:
                plan = json.loads((wd / "plan.json").read_text())
                todo = [lang for lang in LANGS if not (out_root / f"{wd.name}_{lang}.mp4").exists()]
                if not todo:
                    continue
                voices, vox = self.voices(plan, wd / "stems" / "vocals.wav")
                spoken = [l for l in plan["lines"] if not l.get("keep_original")]
                missing = {l["speaker"] for l in spoken} - set(voices)
                if missing:
                    raise KeyError(f"speakers not in cast: {sorted(missing)}")
                jobs[wd.name] = {"wd": wd, "lines": plan["lines"], "spoken": spoken, "todo": todo,
                                 "voices": voices, "vox": vox}
            except Exception as e:  # one bad plan must not stop the group
                print(f"[{wd.name}] FAILED: {e!r}", flush=True)
        if not jobs:
            return []
        emb = lambda vid, l: jobs[vid]["voices"][l["speaker"]]["emb"]
        items = [(vid, lang, l) for vid, j in jobs.items() for lang in j["todo"] for l in j["spoken"]]
        chosen = self.pick(items, self.sample(items, TAKES), emb)
        retry = [(vid, lang, l) for vid, lang, l in items
                 if chosen.get((vid, lang, l["id"])) is None or chosen[(vid, lang, l["id"])][0] > RETRY_CER[lang]]
        if retry:
            chosen = self.pick(retry, self.sample(retry, TAKES), emb, best=chosen)
        print(f"[group {' '.join(jobs)}] {len(items)} lines voiced in {time.time() - t0:.0f}s, retried {len(retry)}",
              flush=True)
        return [self.io.submit(self.write, j, chosen, out_root, sum(r[0] == vid for r in retry), t0)
                for vid, j in jobs.items()]

    def write(self, job, chosen, out_root, retried, t0):
        """CPU stage for one video: finish every chosen take (process pool), write clips + QA, mix each language."""
        wd, lines, vox = job["wd"], job["lines"], job["vox"]
        vid = wd.name
        try:
            fx = {cid: fx_spec(v) for cid, v in job["voices"].items()}
            for lang in job["todo"]:
                for l in job["spoken"]:
                    if chosen.get((vid, lang, l["id"])) is None:
                        raise RuntimeError(f"no usable take for line {l['id']} [{lang}]")
            done = {(lang, l["id"]): self.cpu.submit(finish, chosen[(vid, lang, l["id"])][3], self.sr, fx[l["speaker"]])
                    for lang in job["todo"] for l in job["spoken"]}
            report = {lang: [] for lang in job["todo"]}
            stems = wd / "stems"
            for lang in job["todo"]:
                clips = out_root / f"{vid}_{lang}"
                clips.mkdir(parents=True, exist_ok=True)
                for l in lines:
                    if l.get("keep_original"):
                        sf.write(clips / f"line_{l['id']}.wav", vox[int(l["start"] * self.sr): int(l["end"] * self.sr)],
                                 self.sr)
                        continue
                    c, fit, heard, _ = chosen[(vid, lang, l["id"])]
                    sf.write(clips / f"line_{l['id']}.wav", done[(lang, l["id"])].result(), self.sr)
                    report[lang].append({"id": l["id"], "speaker": l["speaker"], "cer": round(c, 2), "heard": heard})
                (clips / "script.json").write_text(json.dumps({"language": lang, "lines": lines}, ensure_ascii=False))
                (clips / "qa.json").write_text(json.dumps(report[lang], ensure_ascii=False, indent=1))
                assemble.main(clips / "script.json", clips, str(out_root / f"{vid}_{lang}.mp4"), wd / "source.mp4",
                              stems / "no_vocals.wav", stems / "vocals.wav")
            worst = max((r["cer"] for rs in report.values() for r in rs), default=0)
            print(f"[{vid}] {len(job['todo'])} langs in {time.time() - t0:.0f}s | worst line CER {worst:.2f} | "
                  f"retried {retried}", flush=True)
        except Exception as e:
            print(f"[{vid}] FAILED: {e!r}", flush=True)


def opt(args, name, default):
    return type(default)(args[args.index(name) + 1]) if name in args else default


def spawn_workers(n, argv, out_root):
    """--workers N: N engines on one GPU, started one after another (each vLLM sizes its KV cache from free memory)."""
    procs = []
    for i in range(n):
        ready = out_root / f".worker{i}.ready"
        ready.unlink(missing_ok=True)
        procs.append(subprocess.Popen([sys.executable, str(Path(__file__).resolve()), *argv, "--worker", str(i)]))
        while not ready.exists() and procs[-1].poll() is None:
            time.sleep(3)
    sys.exit(max(p.wait() for p in procs))


SELFTEST = {"bn": "আজ আমার ত্বক একদম ঝকঝকে লাগছে।", "ta": "இன்னைக்கு என் ஸ்கின் ரொம்ப பளபளப்பா இருக்கு.",
            "te": "ఈరోజు నా స్కిన్ చాలా మెరుస్తోంది.", "ml": "ഇന്ന് എന്റെ സ്കിൻ നല്ല തിളക്കമുണ്ട്.",
            "or": "ଆଜି ମୋ ସ୍କିନ୍ ବହୁତ ଚମକୁଛି।"}


def selftest(work, backend):
    """Smoke test: Indic-Mio emits speech tokens, MioCodec renders them, batched Whisper reads them back. Prints the
    backend, dtypes, sample durations and TTS tokens/s; exits 1 if a language gets no speech or none is intelligible."""
    vocals = next(iter(sorted(work.glob("*/stems/vocals.wav"))), None)
    if vocals is None:
        print("SELFTEST FAILED: needs one work/<id>/stems/vocals.wav as the reference voice (run prep first)", flush=True)
        sys.exit(1)
    eng = Engine(backend=backend)
    voices, _ = eng.voices({"cast": [{"id": "ref", "ref_ranges": [[0.0, 10.0]], "fx": "none"}]}, vocals)
    line = {"id": 1, "speaker": "ref", "start": 0.0, "end": 3.0, "max_end": 3.5, "tag": "happy", **SELFTEST}
    items = [("selftest", lang, line) for lang in LANGS]
    pool = eng.sample(items, TAKES)
    best = eng.pick(items, pool, lambda key, l: voices["ref"]["emb"], lazy=False)
    out = work.resolve().parent / "selftest"
    out.mkdir(exist_ok=True)
    silent, intelligible, durs = [], [], {}
    for lang in LANGS:
        n, b = len(pool.get(("selftest", lang, 1), [])), best.get(("selftest", lang, 1))
        if b is None:
            silent.append(lang)
            print(f"{lang}: no speech tokens in any take", flush=True)
            continue
        durs[lang] = len(librosa.effects.trim(b[3], top_db=35)[0]) / eng.sr
        intelligible += [lang] if b[0] <= RETRY_CER[lang] else []
        sf.write(out / f"{lang}.wav", finish(b[3], eng.sr, fx_spec(voices["ref"])), eng.sr)
        print(f"{lang}: {n}/{TAKES} takes with speech, {durs[lang]:.2f}s, best CER {b[0]:.2f} "
              f"(good <= {GOOD_CER[lang]}), heard: {b[2]}", flush=True)
    eng.close()
    rate = eng.tts_tokens / max(eng.tts_seconds, 1e-6)
    print(f"SELFTEST {eng.describe()} | TTS {len(items)} lines x {TAKES} takes: {eng.tts_tokens} tokens in "
          f"{eng.tts_seconds:.1f}s = {rate:.0f} tok/s | 1-line sample (bn) {durs.get('bn', 0):.2f}s | "
          f"intelligible {len(intelligible)}/{len(LANGS)} | wavs in {out}/", flush=True)
    if silent or not intelligible:
        print(f"SELFTEST FAILED: no speech in {silent or '-'}; intelligible: {intelligible or 'none'}", flush=True)
        sys.exit(1)
    print("SELFTEST OK", flush=True)


def main(*argv):
    if argv[:1] == ("--selftest",):
        rest = argv[1:]
        work = Path(rest[0] if rest and not rest[0].startswith("--") else "work")
        return selftest(work, opt(list(rest), "--backend", "auto"))
    work, out_root, *args = argv
    work, out_root = Path(work), Path(out_root)
    out_root.mkdir(exist_ok=True)
    workers = opt(args, "--workers", 1)
    if workers > 1 and "--worker" not in args:
        return spawn_workers(workers, argv, out_root)
    expect = opt(args, "--watch", 0)
    reverse = "--reverse" in args  # a second engine works from the other end of the list
    only = cudacfg.ids_filter(args)  # an explicit subset (work split between the Mac and the VM)
    group = opt(args, "--group", GROUP if workers == 1 else GROUP // 2)
    eng = Engine(backend=opt(args, "--backend", "auto"),
                 gpu_util=opt(args, "--gpu-util", 0.40 if workers == 1 else 0.18),
                 max_seqs=512 if workers == 1 else 256,
                 jobs=opt(args, "--jobs", max(2, (os.cpu_count() or 8) // workers - 3)), threads=max(4, group))
    if only is not None:
        print(f"restricted to {len(only)} video ids", flush=True)
    flag = out_root / f".worker{opt(args, '--worker', 0)}.ready"
    if "--worker" in args:
        flag.touch()
    done, pending = set(), []
    while True:
        ready = sorted((p.parent for p in work.glob("*/plan.json")
                        if p.parent.name not in done and (p.parent / "plan.ok").exists()
                        and (only is None or p.parent.name in only)), reverse=reverse)
        claimed = []
        for wd in ready:
            try:  # claim the video so two engines never work on the same one
                os.close(os.open(wd / "dub.lock", os.O_CREAT | os.O_EXCL | os.O_WRONLY))
            except FileExistsError:
                done.add(wd.name)
                continue
            claimed.append(wd)
            if len(claimed) == group:
                break
        if claimed:
            done.update(wd.name for wd in claimed)
            try:
                pending += eng.process_group(claimed, out_root)
            except Exception as e:  # one bad group must not stop the batch
                print(f"[{' '.join(wd.name for wd in claimed)}] FAILED: {e!r}", flush=True)
            while len(pending) > 2 * group:  # cap the CPU-stage backlog (memory-safe)
                pending.pop(0).result()
            continue
        if len(done) >= expect:
            break
        time.sleep(20)
    for f in pending:
        f.result()
    eng.close()
    flag.unlink(missing_ok=True)
    print(f"DUB DONE: {len(done)} videos", flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:])
