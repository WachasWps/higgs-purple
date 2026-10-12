"""Lay dubbed lines onto the original timeline, mix over the background stem, and mux onto the video.

Each line keeps close to its original cue but may flow into following gaps; one uniform tempo
(<= MAX_RATE) is applied to the whole voice track so the delivery stays consistent.

Usage: .venv/bin/python assemble.py <script.json> <clips_dir> <out.mp4>
Clips are expected as <clips_dir>/line_<id>.wav.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import librosa
import numpy as np
import pyloudnorm as pyln
import soundfile as sf

SR = 44100
ROOT = Path(__file__).parent
VIDEO = ROOT / "source/morning-glow.mp4"
BED = ROOT / "analysis/stems/htdemucs/audio_orig/no_vocals.wav"
ORIG_VOX = ROOT / "analysis/stems/htdemucs/audio_orig/vocals.wav"

MAX_PAUSE = 0.12  # longest pause kept inside a line (TTS comma pauses run ~0.3 s)
LEAD = 0.15       # a line may start this much before its original cue
GAP = 0.10        # minimum breath between lines
MAX_DRIFT = 1.0   # a line may start at most this late vs. its original cue
MAX_RATE = 1.25   # beyond this, speech starts to sound rushed


def tighten(y):
    """Trim edges and shorten internal pauses longer than MAX_PAUSE (shorter gaps are left untouched)."""
    iv = librosa.effects.split(y, top_db=35)
    keep = int(MAX_PAUSE * SR)
    parts = [y[iv[0][0]: iv[0][1]]]
    for (_, prev_end), (b, e) in zip(iv[:-1], iv[1:]):
        gap = y[prev_end:b]
        if len(gap) > keep:  # keep the gap's edges so word tails/onsets aren't clipped
            gap = np.concatenate([gap[: keep // 2], gap[-(keep - keep // 2):]])
        parts += [gap, y[b:e]]
    return np.concatenate(parts)


def atempo(y, rate):
    """Time-compress without changing pitch."""
    if abs(rate - 1.0) < 1e-3:
        return y
    with tempfile.TemporaryDirectory() as tmp:
        tmp_in, tmp_out = Path(tmp) / "in.wav", Path(tmp) / "out.wav"
        sf.write(tmp_in, y, SR)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp_in, "-filter:a", f"atempo={rate:.4f}", tmp_out], check=True)
        out, _ = librosa.load(tmp_out, sr=SR, mono=True)
    return out


def layout(lines, durs, rate):
    placed, t = [], 0.0
    for i, (line, d) in enumerate(zip(lines, durs)):
        start = max(line["start"], 0.05) if i == 0 else max(line["start"] - LEAD, t + GAP)
        placed.append(start)
        t = start + d / rate
    drift = max(s - l["start"] for s, l in zip(placed, lines))
    return placed, t, drift


def plan_layout(script_path, clips_dir, video):
    """Where every line lands in the final mix (deterministic; shared by main() and caption timing)."""
    lines = json.loads(Path(script_path).read_text())["lines"]
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video],
                           capture_output=True, text=True, check=True)
    end_limit = float(probe.stdout) - 0.35
    clips = [tighten(librosa.load(Path(clips_dir) / f"line_{l['id']}.wav", sr=SR, mono=True)[0]) for l in lines]
    durs = [len(c) / SR for c in clips]
    rate = 1.0
    while True:
        starts, end, drift = layout(lines, durs, rate)
        if (end <= end_limit and drift <= MAX_DRIFT) or rate >= MAX_RATE:
            break
        rate = round(rate + 0.01, 2)
    return lines, clips, durs, starts, rate, end, drift, end_limit


def write_layout(clips_dir, lines, clips, starts, rate):
    """layout.json: final-timeline start/end of each line + its speech bursts (for word-level captions)."""
    out = []
    for l, clip, start in zip(lines, clips, starts):
        speech = [[round(start + a / SR / rate, 3), round(start + b / SR / rate, 3)]
                  for a, b in librosa.effects.split(clip, top_db=35)]
        out.append({"id": l["id"], "speaker": l.get("speaker"), "start": round(start, 3),
                    "end": round(start + len(clip) / SR / rate, 3), "speech": speech})
    (Path(clips_dir) / "layout.json").write_text(json.dumps({"rate": rate, "lines": out}, indent=1))


def main(script_path, clips_dir, out_path, video=VIDEO, bed_path=BED, orig_vox=ORIG_VOX):
    lines, clips, durs, starts, rate, end, drift, end_limit = plan_layout(script_path, clips_dir, video)
    write_layout(clips_dir, lines, clips, starts, rate)

    bed, _ = librosa.load(bed_path, sr=SR, mono=False)
    voice = np.zeros(bed.shape[1], dtype=np.float32)
    for clip, start in zip(clips, starts):
        y = atempo(clip, rate)
        a = int(start * SR)
        b = min(a + len(y), len(voice))
        voice[a:b] += y[: b - a]

    # Match the original voice loudness so the voice/background balance is unchanged.
    meter = pyln.Meter(SR)
    orig, _ = librosa.load(orig_vox, sr=SR, mono=True)
    voice = pyln.normalize.loudness(voice, meter.integrated_loudness(voice), meter.integrated_loudness(orig))

    mix = bed + voice[None, :]
    peak = np.abs(mix).max()
    if peak > 0.89:  # -1 dBFS ceiling for social platforms
        mix *= 0.89 / peak
    mix_path = Path(out_path).with_suffix(".wav")
    sf.write(mix_path, mix.T, SR)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", video, "-i", mix_path, "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out_path],
        check=True,
    )

    mix_path.unlink()
    print(f"uniform tempo x{rate:.2f}  |  voice ends at {end:.2f}s  |  max late start {drift:+.2f}s")
    print("line  orig_cue  new_start  shift   length")
    for l, s, d in zip(lines, starts, durs):
        print(f"{l['id']:>4}  {l['start']:8.2f}  {s:9.2f}  {s - l['start']:+5.2f}  {d / rate:6.2f}s")
    if end > end_limit or drift > MAX_DRIFT:
        print("WARNING: script still too long for the picture even at max tempo; shorten lines.")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
