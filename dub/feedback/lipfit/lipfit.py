"""Lip-fit re-assembly (no lip-sync model): put each dubbed line's speech where her lips actually move.

Lip windows = her original voice (work/<id>/stems/vocals.wav, VAD) on her own on-camera shots.  Per line:
  - lip bursts inside the line's slot [start, max_end] are the target; on a cutaway-only slot the slot is the target
  - the dub clip is split at its own pauses into phrases; if phrases and bursts can be paired, phrase i is stretched
    onto burst i, else the whole line is stretched onto [first onset, last offset]
  - tempo per piece is kept in [MIN_RATE, MAX_RATE]; a too-long line spills into the slot's cutaway time (lips hidden)
Writes out/<id>_<lang>.mp4 (same mix as assemble.py) and layout.json (captions follow the new timing).
usage: .venv/bin/python feedback/lipfit/lipfit.py [<id> ...]
"""
import json
import sys
from pathlib import Path

import librosa
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "feedback" / "lipfit"))
import assemble as AS  # noqa: E402
import analyze as AN  # noqa: E402

SR = AS.SR
LANGS = AN.LANGS
MIN_RATE, MAX_RATE = 0.88, 1.32
EDGE = 0.04   # start this much after the mouth opens (sound lags picture is less noticeable than leads)


def phrases(y, gap=0.18):
    iv = librosa.effects.split(y, top_db=35, frame_length=1024, hop_length=256)
    out = [list(iv[0])]
    for a, b in iv[1:]:
        if (a - out[-1][1]) / SR >= gap:
            out.append([a, b])
        else:
            out[-1][1] = b
    return [(a, b) for a, b in out if (b - a) / SR > 0.08]


def fit_piece(y, t0, t1):
    """Stretch y onto [t0, t1] within the tempo limits; returns (audio, start, end)."""
    d = len(y) / SR
    r = float(np.clip(d / max(t1 - t0, 0.05), MIN_RATE, MAX_RATE))
    z = AS.atempo(y, r)
    return z, t0, t0 + len(z) / SR


def plan_line(y, slot, lips, me):
    s0, s1 = slot
    bursts = [(max(a, s0), min(b, s1)) for a, b in lips if min(b, s1) - max(a, s0) > 0.1]
    if not bursts:
        return [fit_piece(y, s0, s1 - 0.08)]
    ph = phrases(y)
    w0, w1 = bursts[0][0] + EDGE, bursts[-1][1]
    need = len(y) / SR / MAX_RATE
    if need > w1 - w0:   # too long for the mouth: spill into hidden (cutaway) time of this slot, after first
        hidden_after = s1 - 0.08 - w1 if not any(a < s1 - 0.08 and b > w1 for a, b in me) else 0
        hidden_before = w0 - s0 if not any(a < w0 and b > s0 for a, b in me) else 0
        w1 = min(w1 + hidden_after, w0 + need) if hidden_after > 0 else w1
        if need > w1 - w0 and hidden_before > 0:
            w0 = max(s0, w1 - need)
        return [fit_piece(y, w0, w1)]
    if 1 < len(bursts) == len(ph):
        out = []
        for (a, b), (t0, t1) in zip(ph, bursts):
            seg = y[max(0, a - 400): b + 600]
            out.append(fit_piece(seg, t0 + EDGE, t1))
        if all(o[2] <= nb[0] + EDGE + 0.05 for o, nb in zip(out, bursts[1:])):
            return out
    return [fit_piece(y, w0, w1)]


def run(vid):
    lips, me = AN.lips(vid), AN.me_shots(vid)
    wd = ROOT / "work" / vid
    for lang in LANGS:
        clips_dir = ROOT / "out" / f"{vid}_{lang}"
        lines = json.loads((clips_dir / "script.json").read_text())["lines"]
        bed, _ = librosa.load(wd / "stems" / "no_vocals.wav", sr=SR, mono=False)
        voice = np.zeros(bed.shape[1], dtype=np.float32)
        layout, prev_end = [], 0.0
        for i, l in enumerate(lines):
            y, _ = librosa.load(clips_dir / f"line_{l['id']}.wav", sr=SR, mono=True)
            y = AS.tighten(y)
            nxt = lines[i + 1]["start"] if i + 1 < len(lines) else l["max_end"]
            slot = (max(l["start"] - 0.1, prev_end + 0.06), max(l["max_end"], min(nxt, l["max_end"] + 0.3)))
            pieces = plan_line(y, slot, lips, me)
            speech = []
            for z, t0, t1 in pieces:
                a = int(t0 * SR)
                b = min(a + len(z), len(voice))
                voice[a:b] += z[: b - a]
                iv = librosa.effects.split(z, top_db=35)
                speech += [[round(t0 + p / SR, 3), round(t0 + q / SR, 3)] for p, q in iv]
            prev_end = pieces[-1][2]
            layout.append({"id": l["id"], "speaker": l.get("speaker"), "start": round(pieces[0][1], 3),
                           "end": round(prev_end, 3), "speech": speech})
        (clips_dir / "layout.json").write_text(json.dumps({"rate": 1.0, "lipfit": True, "lines": layout}, indent=1))
        meter = AS.pyln.Meter(SR)
        orig, _ = librosa.load(wd / "stems" / "vocals.wav", sr=SR, mono=True)
        voice = AS.pyln.normalize.loudness(voice, meter.integrated_loudness(voice), meter.integrated_loudness(orig))
        mix = bed + voice[None, :]
        mix *= min(1.0, 0.89 / np.abs(mix).max())
        out = ROOT / "out" / f"{vid}_{lang}.mp4"
        wav = out.with_suffix(".wav")
        AS.sf.write(wav, mix.T, SR)
        AS.subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wd / "source.mp4"), "-i", str(wav), "-map", "0:v",
                           "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)], check=True)
        wav.unlink()
        sp = [tuple(x) for l in layout for x in l["speech"]]
        sp_me = AN.inter(sp, me)
        print(f"{vid} {lang}: lips w/o voice {AN.total(lips) - AN.total(AN.inter(lips, sp)):4.1f}s | "
              f"voice over closed lips {AN.total(sp_me) - AN.total(AN.inter(sp_me, lips)):4.1f}s", flush=True)


if __name__ == "__main__":
    for v in sys.argv[1:] or AN.IDS:
        run(v)
