"""Resumable prep for dubbing on an NVIDIA GPU: CUDA port of prep.py. Skips whatever already exists.

Usage: python vm/prep_cuda.py work/ [--gens gens_a.json [gens_b.json ...]] [--only id1,id2 | --ids-file f] [--jobs N]
  --gens (optional): first fetch every completed video in those generation-history files into
                     work/<id8>/{source.mp4, prompt.txt, meta.json, frames/f_01..f_08.jpg}
  --only / --ids-file: restrict fetching and prep to these video ids
  --stems-only: skip transcription (for videos whose plan.json already exists)
Env: WHISPER_COMPUTE, DTYPE / CODEC_DTYPE (see cudacfg.py; V100 has no bf16)
For every work/<id8>/ that has source.mp4 it then produces, like prep.py:
  stems/{vocals,no_vocals}.wav   htdemucs two-stems on CUDA (model loaded once for all videos; audio decode and
                                 wav encode overlap on a thread pool)
  transcript.json                faster-whisper large-v3-turbo fp16 with word timings, per-segment pitch (pyin on a
                                 process pool) and the voice-cluster hint (MioCodec speaker embeddings, CUDA)
"""
import itertools
import json
import multiprocessing as mp
import os
import shutil
import subprocess
import sys
import urllib.request
import warnings
from collections import deque
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path

warnings.filterwarnings("ignore")
import librosa
import numpy as np
import soundfile as sf

import cudacfg

# torch / demucs / faster-whisper / MioCodec are imported inside the GPU stages: the pitch workers are *spawned*
# processes that re-import this module, and they only need numpy + librosa.
WHISPER = os.environ.get("WHISPER_MODEL", "large-v3-turbo")  # faster-whisper alias of mobiuslabsgmbh/faster-whisper-large-v3-turbo
CODEC = "Aratako/MioCodec-25Hz-24kHz"
DEVICE = "cuda"


def valid_wav(p):
    try:
        return p.exists() and sf.info(p).frames > 0
    except Exception:
        return False


def ffmpeg_audio(src, sr, channels):
    """Decode a file's audio to float32 (channels, samples)."""
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-vn", "-ac", str(channels), "-ar", str(sr),
                        "-f", "f32le", "pipe:1"], capture_output=True, check=True)
    return np.frombuffer(p.stdout, dtype=np.float32).reshape(-1, channels).T.copy()


def duration(src):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src],
                         capture_output=True, text=True, check=True).stdout
    return float(out)


def one_thread():
    """Pool workers get one BLAS/OpenMP thread each: the pool itself fills the cores."""
    global _LIMITS
    try:
        from threadpoolctl import threadpool_limits
        _LIMITS = threadpool_limits(1)
    except ImportError:
        pass


def prefetch(io, load, wds, ahead=4):
    """Yield (wd, load(wd)) in order while the next few inputs load on the thread pool; load failures are logged."""
    it, q = iter(wds), deque()
    for wd in itertools.islice(it, ahead):
        q.append((wd, io.submit(load, wd)))
    while q:
        wd, fut = q.popleft()
        for nxt in itertools.islice(it, 1):
            q.append((nxt, io.submit(load, nxt)))
        try:
            data = fut.result()
        except Exception as e:
            print(f"[{wd.name}] FAILED to load: {e!r}", flush=True)
            continue
        yield wd, data


def fetch_one(wd, g):
    try:
        wd.mkdir(parents=True, exist_ok=True)
        src = wd / "source.mp4"
        if not src.exists():
            part = wd / "source.part"
            req = urllib.request.Request(g["results"]["rawUrl"], headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=120) as r, open(part, "wb") as f:
                shutil.copyfileobj(r, f, 1 << 20)
            part.rename(src)
        if not (wd / "prompt.txt").exists():
            (wd / "prompt.txt").write_text((g.get("params") or {}).get("prompt", ""))
        dur = duration(src)
        if not (wd / "meta.json").exists():
            (wd / "meta.json").write_text(json.dumps({"id": g["id"], "createdAt": g.get("createdAt", 0),
                                                      "duration": round(dur, 2)}))
        frames = wd / "frames"
        frames.mkdir(exist_ok=True)
        for k in range(1, 9):  # 8 frames across the video for the dub directors
            if not (frames / f"f_{k:02d}.jpg").exists():
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{dur * (k - 0.5) / 8:.2f}", "-i", src,
                                "-frames:v", "1", "-vf", "scale=360:-2", "-q:v", "3", frames / f"f_{k:02d}.jpg"],
                               check=True)
        return True
    except Exception as e:
        print(f"[{wd.name}] fetch FAILED: {e!r}", flush=True)
        return False


def fetch(work, gens_paths, io, only=None):
    """Create work/<id8>/ for every completed video in the generation-history JSON files (same layout as the Mac)."""
    entries = {}
    for p in gens_paths:
        for g in json.loads(Path(p).read_text()):
            if g.get("type") == "video" and g.get("status") == "completed" and (g.get("results") or {}).get("rawUrl") \
                    and (only is None or g["id"][:8] in only):
                entries[g["id"][:8]] = g
    ok = sum(f.result() for f in [io.submit(fetch_one, work / k, g) for k, g in sorted(entries.items())])
    print(f"fetched {ok}/{len(entries)} videos", flush=True)


def save_stems(wd, vocals, rest, sr):
    from demucs.api import save_audio  # same writer + defaults as the demucs CLI (16-bit, rescale on clip)
    tmp = wd / "stems.tmp"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir()
    save_audio(vocals, str(tmp / "vocals.wav"), samplerate=sr)
    save_audio(rest, str(tmp / "no_vocals.wav"), samplerate=sr)
    shutil.rmtree(wd / "stems", ignore_errors=True)
    tmp.rename(wd / "stems")


def separate_all(wds, io):
    todo = [wd for wd in wds if not (valid_wav(wd / "stems" / "vocals.wav") and valid_wav(wd / "stems" / "no_vocals.wav"))]
    if not todo:
        return
    import torch
    from demucs.api import Separator
    # = `demucs --two-stems=vocals -n htdemucs` defaults, but the model is loaded once and stays on the GPU.
    sep = Separator("htdemucs", device=DEVICE, shifts=1, overlap=0.25, split=True, jobs=0, progress=False)
    sr = sep.samplerate
    saves = []
    for wd, mix in prefetch(io, lambda wd: ffmpeg_audio(wd / "source.mp4", sr, 2), todo):
        try:
            with torch.no_grad():
                _, res = sep.separate_tensor(torch.from_numpy(mix), sr)
                vocals = res.pop("vocals")
                rest = sum(res.values())  # two-stems "add": no_vocals = drums + bass + other
            saves.append(io.submit(save_stems, wd, vocals, rest, sr))
        except Exception as e:
            print(f"[{wd.name}] separation FAILED: {e!r}", flush=True)
    for f in saves:
        f.result()
    del sep
    torch.cuda.empty_cache()


def segment_pitch(x):
    f0, _, _ = librosa.pyin(x, fmin=70, fmax=600, sr=16000)
    f0 = f0[~np.isnan(f0)]
    return round(float(np.median(f0))) if len(f0) else None


def write_transcript(wd, language, segments, f0s, embs):
    try:
        segs = []
        for i, (s, f0) in enumerate(zip(segments, f0s)):
            segs.append({"seg": i, "start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
                         "f0_median_hz": f0.result() if f0 is not None else None,
                         "words": [[w.word.strip(), round(w.start, 2), round(w.end, 2)] for w in (s.words or [])]})
        # Speaker hint: greedy cosine clustering of segment voice embeddings (short segments stay unassigned).
        cents, labels = [], []
        for e in embs:
            if e is None:
                labels.append(None)
                continue
            e = e / np.linalg.norm(e)
            sims = [float(e @ c / np.linalg.norm(c)) for c in cents]
            if sims and max(sims) > 0.80:
                k = int(np.argmax(sims))
                cents[k] = cents[k] + e
            else:
                cents.append(e.copy())
                k = len(cents) - 1
            labels.append(f"voice_{chr(65 + k)}")
        for s, lab in zip(segs, labels):
            s["voice_cluster_hint"] = lab
        (wd / "transcript.json").write_text(json.dumps({"language": language, "segments": segs},
                                                       ensure_ascii=False, indent=1))
        print(f"{wd.name}: {len(segs)} segments, lang={language}, voices~{len(cents)}", flush=True)
    except Exception as e:
        print(f"[{wd.name}] transcript FAILED: {e!r}", flush=True)


def transcribe_all(wds, io, cpu):
    todo = [wd for wd in wds if not (wd / "transcript.json").exists() and valid_wav(wd / "stems" / "vocals.wav")]
    if not todo:
        return
    import torch
    from faster_whisper import WhisperModel
    from miocodec import MioCodecModel
    asr = WhisperModel(WHISPER, device=DEVICE, compute_type=cudacfg.whisper_compute())
    cudacfg.patch_codec(cudacfg.codec_dtype())  # MioCodec hard-codes bf16 autocast; V100 has no bf16
    codec = MioCodecModel.from_pretrained(CODEC).eval().to(DEVICE)
    load = lambda wd: (ffmpeg_audio(wd / "source.mp4", 16000, 1)[0],
                       librosa.load(wd / "stems" / "vocals.wav", sr=16000, mono=True)[0])
    writes = []
    for wd, (mix, vocals) in prefetch(io, load, todo):
        try:
            # Sequential (not Batched) pipeline, no VAD: segments keep Whisper's own boundaries, as with mlx_whisper.
            # The batched pipeline would merge them into ~30 s chunks, and directors rely on per-segment pitch.
            segments, info = asr.transcribe(mix, word_timestamps=True, condition_on_previous_text=False, vad_filter=False)
            segments = list(segments)
            f0s, embs = [], []
            for s in segments:
                x = vocals[int(s.start * 16000): int(s.end * 16000)]
                f0s.append(cpu.submit(segment_pitch, x) if len(x) > 1600 else None)
                emb = None
                if len(x) >= 12000:
                    w = torch.tensor(librosa.resample(x, orig_sr=16000, target_sr=codec.config.sample_rate))[None].to(DEVICE)
                    with torch.no_grad():
                        emb = codec.encode(w, return_content=False).global_embedding.flatten().float().cpu().numpy()
                embs.append(emb)
            writes.append(io.submit(write_transcript, wd, info.language, segments, f0s, embs))
        except Exception as e:
            print(f"[{wd.name}] transcription FAILED: {e!r}", flush=True)
    for f in writes:
        f.result()


def main(work, *args):
    work = Path(work)
    work.mkdir(exist_ok=True)
    jobs = int(args[args.index("--jobs") + 1]) if "--jobs" in args else max(2, (os.cpu_count() or 8) - 2)
    only = cudacfg.ids_filter(args)
    io = ThreadPoolExecutor(8)
    if "--gens" in args:
        fetch(work, list(itertools.takewhile(lambda a: not a.startswith("--"), args[args.index("--gens") + 1:])), io,
              only)
    wds = sorted(p.parent for p in work.glob("*/source.mp4") if only is None or p.parent.name in only)
    separate_all(wds, io)
    print(f"separated {len(wds)}", flush=True)
    if "--stems-only" not in args:  # --stems-only: plans already exist, dubbing only needs the stems
        # spawn, not fork: this process already holds a CUDA context
        with ProcessPoolExecutor(jobs, mp_context=mp.get_context("spawn"), initializer=one_thread) as cpu:
            transcribe_all(wds, io, cpu)
    io.shutdown()
    print("PREP DONE", flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:])
