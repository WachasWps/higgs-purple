"""Client: "Keep VO voice female only" / "Male VO voice is very scary".
Recast every male or pitched-down character to a female reference voice and queue its lines in work/<id>/redub.json.

usage: apply_voices.py [--dry]
"""
import json
import sys
import warnings
from pathlib import Path

import librosa
import numpy as np

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
FEMALE = {   # reference clips (all real female voices from our own source videos)
    "narrator": {"ref_file": "work/71e0977a/stems/vocals.wav", "ref_ranges": [[9.32, 12.54], [13.68, 16.56]], "fx": "none"},
    "hero": {"ref_file": "work/51440b1f/stems/vocals.wav", "ref_ranges": [[0.0, 5.5], [5.62, 10.5]], "fx": "cartoon"},
    "villain": {"ref_file": "work/46d965c9/stems/vocals.wav", "ref_ranges": [[0.0, 2.46], [2.68, 4.5], [13.44, 17.56]],
                "fx": "villain_f"},
}


def median_f0(y, sr):
    f, _, _ = librosa.pyin(y, fmin=60, fmax=500, sr=sr)
    f = f[~np.isnan(f)]
    return float(np.median(f)) if len(f) else None


def kind(c):
    role = (c.get("role") or "").lower()
    if "villain" in role or c.get("fx") == "villain":
        return "villain"
    if c["id"] == "narrator" or "narrat" in role or "voiceover" in (c.get("description") or "").lower():
        return "narrator"
    return "hero"


def main(dry):
    total = 0
    for pf in sorted((ROOT / "work").glob("*/plan.json")):
        wd = pf.parent
        plan = json.loads(pf.read_text())
        y, sr = librosa.load(wd / "stems" / "vocals.wav", sr=16000)
        recast = []
        for c in plan["cast"]:
            if c.get("ref_file") or not c.get("ref_ranges"):
                continue
            seg = np.concatenate([y[int(a * sr): int(b * sr)] for a, b in c["ref_ranges"]])
            f0 = median_f0(seg, sr)
            eff = f0 * 2 ** (c.get("pitch_semitones", 0) / 12) if f0 else None
            if (eff and eff < 165) or c.get("pitch_semitones", 0) <= -2:
                k = kind(c)
                c.update({**FEMALE[k], "pitch_semitones": -1 if k == "villain" else 0,
                          "recast": f"female {k} (was f0≈{round(eff or 0)} Hz)"})
                recast.append(c["id"])
        if not recast:
            continue
        ids = [l["id"] for l in plan["lines"] if l["speaker"] in recast and not l.get("keep_original")]
        total += len(ids)
        print(f"{wd.name}: recast {recast} -> {len(ids)} lines")
        if dry:
            continue
        pf.write_text(json.dumps(plan, ensure_ascii=False, indent=1))
        rd = wd / "redub.json"
        cur = json.loads(rd.read_text())["lines"] if rd.exists() else []
        rd.write_text(json.dumps({"lines": sorted(set(cur) | set(ids))}))
    print(f"TOTAL {total} lines queued for re-dub (x5 languages)")


if __name__ == "__main__":
    main("--dry" in sys.argv)
