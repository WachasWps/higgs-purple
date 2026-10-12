"""Add subtle original (synthesized, copyright-free) background music + SFX to deliver/ videos, audio-only (video copied).

Music: product-specific ambient bed (sunscreen = bright/airy, night cream = warm/calm), ducked under the voice.
SFX: soft pops / whooshes / shimmer at each on-screen text from work/<id>/graphics.json, plus an outro swoosh + ding.
Usage: nice -n 10 .venv/bin/python post/add_audio.py [--ids id ...] [--jobs 3] [--force]
Output: deliver_music/<same folder>/<same name>.mp4
"""
import json
import subprocess
import sys
import wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from scipy.signal import butter, fftconvolve, lfilter

ROOT = Path(__file__).resolve().parent.parent
SR = 48000
FF = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
FP = "/opt/homebrew/opt/ffmpeg-full/bin/ffprobe"
CACHE = ROOT / "post" / "audio"


def note(n):  # MIDI -> Hz
    return 440.0 * 2 ** ((n - 69) / 12)


def lowpass(x, fc, order=2):
    b, a = butter(order, fc / (SR / 2))
    return lfilter(b, a, x, axis=0)


def reverb(x, secs=1.6, seed=3):
    rng = np.random.default_rng(seed)
    n = int(SR * secs)
    ir = rng.standard_normal((n, 2)) * np.exp(-np.linspace(0, 6, n))[:, None]
    ir = lowpass(ir, 3500)
    ir /= np.abs(ir).sum(0, keepdims=True) * 0.18
    wet = np.stack([fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], 1)
    return 0.55 * x + 0.75 * wet


def music(kind, secs=48.0):
    """Rhythmic, melodic bed (no sustained drone): e-piano arpeggio/chords + bass + soft drums. Normalised to -25 LUFS."""
    import pyloudnorm as pyln
    rng = np.random.default_rng(11)
    n = int(secs * SR)
    keys = np.zeros((n, 2)); low = np.zeros(n); drums = np.zeros((n, 2))
    tt = lambda d: np.arange(int(d * SR)) / SR

    def add(buf, snd, at, pan=0.5):
        a0 = int(at * SR)
        if a0 < 0 or a0 >= n:
            return
        sn = snd[: n - a0]
        if buf.ndim == 1:
            buf[a0: a0 + len(sn)] += sn
        else:
            buf[a0: a0 + len(sn), 0] += sn * (1 - pan)
            buf[a0: a0 + len(sn), 1] += sn * pan

    def ep(m, d, vel, k=3.2):
        f, t = note(m), tt(d)
        sig = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t) * np.exp(-t * 8) + 0.12 * np.sin(6 * np.pi * f * t) * np.exp(-t * 12)
        return sig * (1 - np.exp(-t * 500)) * np.exp(-t * k) * vel

    def bass(m, d, vel):
        f, t = note(m), tt(d)
        return (np.sin(2 * np.pi * f * t) + 0.2 * np.sin(4 * np.pi * f * t)) * (1 - np.exp(-t * 300)) * np.exp(-t * 3.2) * vel

    def kick(vel):
        t = tt(0.32)
        return (np.sin(2 * np.pi * np.cumsum(45 + 95 * np.exp(-t * 32)) / SR) * np.exp(-t * 9)) * vel

    def hat(vel):
        t = tt(0.05); x = rng.standard_normal(len(t)); x = x - lowpass(x, 7000)
        return x * np.exp(-t * 110) * vel

    def clap(vel):
        t = tt(0.22); x = rng.standard_normal(len(t))
        x = lfilter(*butter(2, [900 / (SR / 2), 5500 / (SR / 2)], "band"), x)
        return (x * np.exp(-t * 20) + 0.5 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 35)) * vel

    def rim(vel):
        t = tt(0.06)
        return (np.sin(2 * np.pi * 1650 * t) + 0.4 * rng.standard_normal(len(t))) * np.exp(-t * 85) * vel

    def pump(buf, beat):   # house-style sidechain pump on every beat (energy without loudness)
        t = (np.arange(len(buf)) / SR) % beat
        g = 0.55 + 0.45 * (1 - np.exp(-t / (beat * 0.22)))
        return buf * (g[:, None] if buf.ndim == 2 else g)

    # Client: previous beds "too slow, boring, make the video seem long" -> upbeat four-on-the-floor grooves.
    if kind == "uv_sunscreen":   # bright dance-pop: C - G - Am - F, 124 BPM, 16th pluck arp + offbeat bass
        bpm = 124
        bars = [(48, [60, 64, 67, 72]), (43, [59, 62, 67, 71]), (45, [60, 64, 69, 72]), (41, [60, 65, 69, 72])]
        beat = 60 / bpm
        for bar in range(int(secs / (4 * beat)) + 1):
            root, ch = bars[bar % 4]
            t0 = bar * 4 * beat
            for i, idx in enumerate([0, 2, 1, 3, 2, 0, 3, 1, 0, 2, 1, 3, 2, 3, 1, 2]):   # 16th-note pluck arpeggio
                v = (0.75 if i % 4 == 0 else 0.5 if i % 2 == 0 else 0.38) * (0.85 + 0.15 * rng.random())
                add(keys, ep(ch[idx] + 12, 0.22, v, 9.0), t0 + i * beat / 4 + rng.normal(0, 0.002), 0.3 + 0.4 * (i % 4) / 3)
            for b_ in (0, 2):                                                   # chord stabs
                for j, m in enumerate(ch[:3]):
                    add(keys, ep(m, 0.35, 0.32, 7.0), t0 + (b_ + 0.5) * beat + j * 0.01, 0.4 + 0.1 * j)
            for k in range(4):                                                  # offbeat house bass
                add(low, bass(root, 0.2, 0.85), t0 + (k + 0.5) * beat)
            for k in range(4):
                add(drums, kick(0.95), t0 + k * beat, 0.5)
                if k in (1, 3):
                    add(drums, clap(0.42), t0 + k * beat, 0.5)
            for h in range(16):
                add(drums, hat(0.2 if h % 4 == 2 else 0.09), t0 + h * beat / 4, 0.62 if h % 2 else 0.4)
        mix = pump(keys, beat) * 0.6 + pump(low, beat)[:, None] * 0.6 + drums * 0.55
    else:                        # night but lively chill-house: Am - F - C - G, 118 BPM
        bpm = 118
        bars = [(45, [57, 60, 64, 69]), (41, [57, 60, 65, 69]), (48, [55, 60, 64, 67]), (43, [55, 59, 62, 67])]
        beat = 60 / bpm
        for bar in range(int(secs / (4 * beat)) + 1):
            root, ch = bars[bar % 4]
            t0 = bar * 4 * beat
            for b_ in (0, 1.5, 2.5):                                            # syncopated rolled chords
                for j, m in enumerate(ch):
                    add(keys, ep(m, 0.6, 0.42 * (0.9 + 0.1 * rng.random()), 5.0), t0 + b_ * beat + j * 0.018, 0.3 + 0.13 * j)
            for i, idx in enumerate([3, 1, 2, 3, 1, 2, 0, 2]):                  # 8th-note bell arp
                add(keys, ep(ch[idx] + 12, 0.3, 0.26, 7.0), t0 + i * beat / 2, 0.6)
            for k in range(4):
                add(low, bass(root + (12 if k == 3 else 0), 0.22, 0.8), t0 + (k + 0.5) * beat)
            for k in range(4):
                add(drums, kick(0.8), t0 + k * beat, 0.5)
                if k in (1, 3):
                    add(drums, rim(0.4), t0 + k * beat, 0.5)
                    add(drums, clap(0.22), t0 + k * beat, 0.5)
            for h in range(8):
                add(drums, hat(0.16 if h % 2 else 0.06), t0 + h * beat / 2 + (0.01 if h % 2 else 0), 0.55)
        mix = pump(keys, beat) * 0.55 + pump(low, beat)[:, None] * 0.6 + drums * 0.55
    mix = reverb(mix, 1.1, seed=5) * 0.9 + mix * 0.2          # a little space
    mix = lowpass(mix, 9000)
    meter = pyln.Meter(SR)
    mix = pyln.normalize.loudness(mix, meter.integrated_loudness(mix), -25.0)
    pk = np.abs(mix).max()
    if pk > 0.9:
        mix *= 0.9 / pk
    return mix.astype(np.float32)


def sweep(noise, f0, f1, order=2):
    """Noise with a lowpass cutoff gliding f0 -> f1 (chunked, filter state carried)."""
    out, n, k = np.zeros_like(noise), len(noise), 24
    zi = None
    for i in range(k):
        fc = f0 * (f1 / f0) ** (i / (k - 1))
        bb, aa = butter(order, min(fc, SR / 2 - 100) / (SR / 2))
        sl = slice(i * n // k, (i + 1) * n // k)
        if zi is None:
            zi = np.zeros(max(len(aa), len(bb)) - 1)
        out[sl], zi = lfilter(bb, aa, noise[sl], zi=zi * 0 if i == 0 else zi)
    return out


def sfx_bank():
    tt = lambda d: np.arange(int(d * SR)) / SR
    rng = np.random.default_rng(1)
    nz = lambda x, db: (x / (np.abs(x).max() + 1e-9) * 10 ** (db / 20)).astype(np.float32)
    bell = lambda f, d, k=7: (np.sin(2 * np.pi * f * tt(d)) + 0.35 * np.sin(2 * np.pi * 2.01 * f * tt(d))) * np.exp(-tt(d) * k)

    t = tt(0.16)  # pop: blip + click + soft thump
    pop = np.sin(2 * np.pi * (1100 + 700 * np.exp(-t * 70)) * t) * np.exp(-t * 38)
    pop[:int(0.004 * SR)] += rng.standard_normal(int(0.004 * SR)) * 0.5
    pop += 0.9 * np.sin(2 * np.pi * 130 * t) * np.exp(-t * 45)

    t = tt(0.55)  # whoosh: rising filtered noise, bell-shaped
    env = np.sin(np.pi * np.clip(t / 0.55, 0, 1)) ** 1.6
    whoosh = sweep(rng.standard_normal(len(t)), 350, 6500) * env
    t = tt(0.4)   # out-whoosh: falling, softer
    out_w = sweep(rng.standard_normal(len(t)), 5200, 400) * (np.sin(np.pi * np.clip(t / 0.4, 0, 1)) ** 2)

    t = tt(0.9)   # hook impact: sub hit + air
    hit = np.sin(2 * np.pi * (62 + 50 * np.exp(-t * 14)) * t) * np.exp(-t * 5.5)
    hit += 0.35 * lowpass(rng.standard_normal(len(t)), 1800) * np.exp(-t * 9)

    spark = np.zeros(int(1.3 * SR))  # claim sparkle: 4 rising bell notes
    for i, f in enumerate((1047, 1319, 1568, 2093)):
        b = bell(f, 1.0, 5.5)
        a0 = int(i * 0.055 * SR)
        spark[a0:a0 + len(b)] += b * (0.7 + 0.1 * i)
    t = tt(0.5)   # tag sparkle: 2 notes
    tag = np.zeros(len(t))
    for i, f in enumerate((1568, 2349)):
        b = bell(f, 0.4, 9)
        a0 = int(i * 0.05 * SR)
        tag[a0:a0 + len(b)] += b

    t = tt(0.22)  # hud: two short digital blips
    hud = np.zeros(len(t))
    for i, a0 in enumerate((0.0, 0.09)):
        n = int(0.04 * SR)
        hud[int(a0 * SR):int(a0 * SR) + n] += np.sin(2 * np.pi * (2300 + 500 * i) * tt(0.04)) * np.hanning(n)
    t = tt(1.2)   # outro ding: warm bell
    ding = bell(1318, 1.2, 3.2) + 0.5 * bell(1976, 1.2, 4.0)
    t = tt(0.6)   # outro swoosh
    sw = sweep(rng.standard_normal(len(t)), 300, 7000) * (np.sin(np.pi * np.clip(t / 0.6, 0, 1)) ** 1.5)
    return {"pop": nz(pop, -13), "whoosh": nz(whoosh, -15), "out": nz(out_w, -19), "hit": nz(hit, -11),
            "spark": nz(spark, -15), "tag": nz(tag, -16), "hud": nz(hud, -19), "ding": nz(ding, -14),
            "swoosh": nz(sw, -15)}


def place(track, snd, at, pan=0.5):
    a = int(at * SR)
    if a < 0 or a >= len(track):
        return
    s = snd[: len(track) - a]
    track[a: a + len(s), 0] += s * (1 - pan) * 1.4
    track[a: a + len(s), 1] += s * pan * 1.4


def build(vid, dur, bank):
    g = json.loads((ROOT / "work" / vid / "graphics.json").read_text())
    n = int(dur * SR)
    sfx = np.zeros((n, 2), np.float32)
    for i, e in enumerate(g["elements"]):
        t, s, en = e["type"], e["start"], e["end"]
        pan = 0.35 + 0.3 * ((i * 0.61) % 1)
        if t == "hook_mono":
            place(sfx, bank["hit"], s)
            place(sfx, bank["whoosh"], s - 0.2, 0.5)
        elif t == "claim_bold":
            place(sfx, bank["whoosh"], s - 0.25, pan)
            place(sfx, bank["spark"], s + 0.05, 0.55)
            place(sfx, bank["out"], en - 0.3, pan)
        elif t == "pill" and not e.get("mask"):
            place(sfx, bank["pop"], s + 0.02, pan)
            place(sfx, bank["whoosh"], s - 0.12, pan)
            place(sfx, bank["out"], en - 0.25, pan)
        elif t == "label":
            txt = " ".join(e.get("lines", [])).upper()
            if txt in ("BEFORE", "AFTER"):
                place(sfx, bank["whoosh"], s - 0.15, 0.3 if txt == "BEFORE" else 0.7)
                place(sfx, bank["pop"], s + 0.02, 0.3 if txt == "BEFORE" else 0.7)
            else:
                place(sfx, bank["pop"], s + 0.02, pan)
                place(sfx, bank["tag"], s + 0.06, pan)
        elif t == "hud":
            place(sfx, bank["hud"], s + 0.05, 0.5)
        elif t == "blur":
            place(sfx, bank["out"], s, 0.5)
    for t in g.get("cut_sfx", []):   # a swoosh on every cut (re-cut UGCs: creator <-> product / wheel / B-A)
        place(sfx, bank["swoosh"], t - 0.25, 0.5)
        place(sfx, bank["tag"], t + 0.02, 0.5)
    if not g.get("no_outro"):
        out_start = dur - 5.0
        place(sfx, bank["swoosh"], out_start - 0.2)
        place(sfx, bank["ding"], out_start + 1.1, 0.6)
        place(sfx, bank["spark"], out_start + 1.1, 0.45)
    return g.get("product", "uv_sunscreen"), sfx


def write_wav(path, x):
    x = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(x.tobytes())


def process(src, out_root, beds, bank, force):
    rel = src.relative_to(ROOT / "deliver")
    dst = out_root / rel
    if dst.exists() and not force:
        return f"skip {rel}"
    dst.parent.mkdir(parents=True, exist_ok=True)
    vid = src.stem.split("_")[-1]
    dur = float(subprocess.run([FP, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(src)],
                               capture_output=True, text=True).stdout)
    product, sfx = build(vid, dur, bank)
    bed = beds[product][: int(dur * SR)].copy()
    if json.loads((ROOT / "work" / vid / "graphics.json").read_text()).get("own_music"):
        bed *= 0.0   # the footage already carries its own soundtrack (user-supplied ads): SFX only
    fi, fo = int(0.8 * SR), int(1.8 * SR)
    bed[:fi] *= np.linspace(0, 1, fi)[:, None]
    bed[-fo:] *= np.linspace(1, 0, fo)[:, None]
    tmp = out_root / "_tmp"
    tmp.mkdir(exist_ok=True)
    wm, ws = tmp / f"{src.stem}_{rel.parent.name}_m.wav", tmp / f"{src.stem}_{rel.parent.name}_s.wav"
    write_wav(wm, bed)
    write_wav(ws, sfx)
    # music ducks under the voice (sidechain); base level ~ -14 dB, ducked further while speech plays
    fc = ("[0:a]aresample=48000,asplit=2[v][sc];"
          "[1:a]volume=1.0[m0];[m0][sc]sidechaincompress=threshold=0.03:ratio=3:attack=30:release=600:makeup=1[md];"
          "[2:a]volume=1.0[fx];"
          "[v][md][fx]amix=inputs=3:normalize=0:duration=first:dropout_transition=0,alimiter=limit=0.89:level=disabled[a]")
    r = subprocess.run(["nice", "-n", "10", FF, "-v", "error", "-y", "-i", str(src), "-i", str(wm), "-i", str(ws),
                        "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac",
                        "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(dst)],
                       capture_output=True, text=True)
    wm.unlink(missing_ok=True)
    ws.unlink(missing_ok=True)
    return f"{'ok  ' if r.returncode == 0 else 'FAIL'} {rel} {r.stderr[-120:] if r.returncode else ''}"


def main():
    args = sys.argv[1:]
    force = "--force" in args
    jobs = int(args[args.index("--jobs") + 1]) if "--jobs" in args else 3
    ids = args[args.index("--ids") + 1:] if "--ids" in args else None
    ids = [i for i in (ids or []) if not i.startswith("--")] or None
    CACHE.mkdir(parents=True, exist_ok=True)
    beds = {}
    for k in ("uv_sunscreen", "kojic_night_cream"):
        f = CACHE / f"bed_{k}.npy"
        if not f.exists():
            np.save(f, music(k))
        beds[k] = np.load(f)
    bank = sfx_bank()
    files = sorted((ROOT / "deliver").glob("*/*.mp4"))
    if ids:
        files = [f for f in files if f.stem.split("_")[-1] in ids]
    out_root = ROOT / "deliver_music"
    with ThreadPoolExecutor(jobs) as ex:
        for msg in ex.map(lambda f: process(f, out_root, beds, bank, force), files):
            print(msg, flush=True)
    print(f"DONE {len(files)} files -> {out_root}")


if __name__ == "__main__":
    main()
