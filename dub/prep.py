"""Resumable, one-video-at-a-time prep for dubbing (stays inside the Mac's limits via guard.py).

Usage: nice -n 10 .venv/bin/python prep.py work/
For every work/<id8>/ that has source.mp4, produces (skipping whatever already exists):
  stems/{vocals,no_vocals}.wav, transcript.json (segments, word timings, pitch, voice-cluster hint), meta.json
"""
import guard  # noqa: F401  (must be first: caps threads)

import json
import shutil
import subprocess
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
import librosa
import mlx_whisper
import numpy as np
import soundfile as sf
import torch
from miocodec import MioCodecModel

guard.cap_torch()
WHISPER = "mlx-community/whisper-large-v3-turbo"
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"


def valid_wav(p):
    try:
        return p.exists() and sf.info(p).frames > 0
    except Exception:
        return False


def separate(wd, work):
    stems = wd / "stems"
    if valid_wav(stems / "vocals.wav") and valid_wav(stems / "no_vocals.wav"):
        return
    leftover = work / "_demucs" / "htdemucs" / wd.name  # finished output from the interrupted run
    if valid_wav(leftover / "vocals.wav") and valid_wav(leftover / "no_vocals.wav"):
        shutil.rmtree(stems, ignore_errors=True)
        shutil.move(str(leftover), str(stems))
        return
    wav = wd / f"{wd.name}.wav"
    if not valid_wav(wav):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wd / "source.mp4", "-vn", "-ac", "2", "-ar", "44100", wav],
                       check=True)
    subprocess.run([sys.executable, "-m", "demucs", "--two-stems=vocals", "-n", "htdemucs", "-d", DEVICE, "-j", "1",
                    "-o", str(work / "_demucs"), str(wav)], check=True, capture_output=True)
    shutil.rmtree(stems, ignore_errors=True)
    shutil.move(str(leftover), str(stems))


def transcribe(wd, codec):
    if (wd / "transcript.json").exists():
        return
    wav = wd / f"{wd.name}.wav"
    if not valid_wav(wav):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wd / "source.mp4", "-vn", "-ac", "2", "-ar", "44100", wav],
                       check=True)
    vocals, _ = librosa.load(wd / "stems" / "vocals.wav", sr=16000, mono=True)
    r = mlx_whisper.transcribe(str(wav), path_or_hf_repo=WHISPER, word_timestamps=True,
                               condition_on_previous_text=False)
    segs, embs = [], []
    for i, s in enumerate(r["segments"]):
        x = vocals[int(s["start"] * 16000): int(s["end"] * 16000)]
        f0 = np.array([])
        if len(x) > 1600:
            f0, _, _ = librosa.pyin(x, fmin=70, fmax=600, sr=16000)
            f0 = f0[~np.isnan(f0)]
        emb = None
        if len(x) >= 12000:
            w = torch.tensor(librosa.resample(x, orig_sr=16000, target_sr=codec.config.sample_rate))[None].to(DEVICE)
            with torch.no_grad():
                emb = codec.encode(w, return_content=False).global_embedding.flatten().float().cpu().numpy()
        embs.append(emb)
        segs.append({"seg": i, "start": round(s["start"], 2), "end": round(s["end"], 2), "text": s["text"].strip(),
                     "f0_median_hz": round(float(np.median(f0))) if len(f0) else None,
                     "words": [[w["word"].strip(), round(w["start"], 2), round(w["end"], 2)] for w in s.get("words", [])]})
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
    (wd / "transcript.json").write_text(json.dumps({"language": r.get("language"), "segments": segs},
                                                   ensure_ascii=False, indent=1))
    wav.unlink()  # the stems + source are all we need later
    print(f"{wd.name}: {len(segs)} segments, lang={r.get('language')}, voices~{len(cents)}", flush=True)


def main(work):
    work = Path(work)
    wds = sorted(p.parent for p in work.glob("*/source.mp4"))
    for wd in wds:
        guard.wait_for_headroom(wd.name)
        separate(wd, work)
    print(f"separated {len(wds)}", flush=True)
    codec = MioCodecModel.from_pretrained("Aratako/MioCodec-25Hz-24kHz").eval().to(DEVICE)
    for wd in wds:
        guard.wait_for_headroom(wd.name)
        transcribe(wd, codec)
    print("PREP DONE", flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
