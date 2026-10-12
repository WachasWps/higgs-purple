"""Lip windows (her original speech on her own on-camera shots) vs. where each dubbed line actually sounds."""
import json, sys
import numpy as np, soundfile as sf
IDS = ["d6c1e78e", "b876bd3c", "a135c7dc", "751fe1db", "010ea465"]
LANGS = ["bn", "ta", "te", "ml", "or"]

def me_shots(v):
    sh = json.load(open(f"feedback/edl_v2/{v}.json"))["rebuild"]["shots"]
    return [(s["start"], s["end"]) for s in sh if s["source"].startswith(f"USR_{v}_")]

def vad(path, hop=0.02, thr_db=-38, min_gap=0.25, min_len=0.15):
    y, sr = sf.read(path, dtype="float32")
    y = y.mean(1) if y.ndim > 1 else y
    h = int(sr * hop); n = len(y) // h
    e = 20 * np.log10(np.sqrt((y[: n * h].reshape(n, h) ** 2).mean(1)) + 1e-9)
    on = e > max(thr_db, e.max() - 35)
    segs, i = [], 0
    while i < n:
        if on[i]:
            j = i
            while j < n and on[j]: j += 1
            segs.append([i * hop, j * hop]); i = j
        else: i += 1
    out = []
    for s in segs:
        if out and s[0] - out[-1][1] < min_gap: out[-1][1] = s[1]
        else: out.append(s)
    return [s for s in out if s[1] - s[0] >= min_len]

def inter(a, b):
    out = []
    for s, e in a:
        for S, E in b:
            lo, hi = max(s, S), min(e, E)
            if hi > lo: out.append((lo, hi))
    return out

def total(x): return sum(e - s for s, e in x)

def lips(v):
    return inter(vad(f"work/{v}/stems/vocals.wav"), me_shots(v))

if __name__ == "__main__":
    for v in sys.argv[1:] or IDS:
        L = lips(v); me = me_shots(v)
        print(f"== {v} lip windows:", " ".join(f"{s:.2f}-{e:.2f}" for s, e in L))
        for lang in LANGS:
            lay = json.load(open(f"out/{v}_{lang}/layout.json"))
            sp = [tuple(x) for l in lay["lines"] for x in l["speech"]]
            sp_me = inter(sp, me)
            silent_lips = total(L) - total(inter(L, sp))
            dub_still = total(sp_me) - total(inter(sp_me, L))
            print(f"   {lang} rate {lay['rate']}: lips moving w/o voice {silent_lips:4.1f}s | voice over closed lips {dub_still:4.1f}s")
