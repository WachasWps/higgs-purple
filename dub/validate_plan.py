"""Validate a dub plan.json against DIRECTOR_BRIEF.md. Prints OK or a list of errors.

Usage: python3 validate_plan.py work/<id>/plan.json
"""
import json
import math
import sys

LANGS = {"bn": (0x0980, 0x09FF), "ta": (0x0B80, 0x0BFF), "te": (0x0C00, 0x0C7F), "ml": (0x0D00, 0x0D7F),
         "or": (0x0B00, 0x0B7F)}
PUNCT = set(",.?!।")
JOINERS = {"‌", "‍"}
ROLES = {"creator", "narrator", "product_mascot", "meme", "villain", "hero", "sidekick", "other"}
FX = {"none", "cartoon", "villain", "villain_f"}  # villain_f: female villain (client: female VO only)
TAGS = {None, "happy", "sad", "angry", "disgust", "fear", "surprise"}
# Measured Indic-Mio speech rate per language (chars/s): bn 11.9, or 11.3, te 13.3, ml 14.9, ta 15.3.
# Total budget = rate x ~1.1 headroom (tempo/pauses); per-line cap allows lines to flow into gaps.
CPS_TOTAL = {"bn": 13.0, "or": 12.5, "te": 14.5, "ml": 15.5, "ta": 15.5}
CPS_LINE = {k: round(v * 17 / 14.5, 1) for k, v in CPS_TOTAL.items()}


def count(text):
    return sum(1 for c in text if not c.isspace() and c not in PUNCT and c not in JOINERS)


def main(path):
    errs = []
    p = json.load(open(path))
    cast = {c["id"]: c for c in p.get("cast", [])}
    if not cast:
        errs.append("cast is empty")
    for c in cast.values():
        if c.get("role") not in ROLES:
            errs.append(f"cast {c['id']}: role must be one of {sorted(ROLES)}")
        if c.get("fx") not in FX:
            errs.append(f"cast {c['id']}: fx must be one of {sorted(FX)}")
        refs = c.get("ref_ranges") or []
        total = sum(b - a for a, b in refs)
        if total < 1.5:
            errs.append(f"cast {c['id']}: ref_ranges total {total:.1f}s < 1.5s")
        if any(b <= a for a, b in refs):
            errs.append(f"cast {c['id']}: a ref range has end <= start")
        if not -6 <= c.get("pitch_semitones", 0) <= 6:
            errs.append(f"cast {c['id']}: pitch_semitones must be within -6..6")
    lines = p.get("lines", [])
    if not lines:
        errs.append("no lines")
    totals = {k: [0, 0.0] for k in LANGS}
    prev_start = -1
    for l in lines:
        lid = l.get("id")
        if l.get("speaker") not in cast:
            errs.append(f"line {lid}: speaker '{l.get('speaker')}' not in cast")
        if l.get("tag") not in TAGS:
            errs.append(f"line {lid}: tag '{l.get('tag')}' invalid")
        if not (l["start"] < l["end"] <= l["max_end"] + 0.3):
            errs.append(f"line {lid}: need start < end <= max_end (+0.3 tolerance)")
        if l["start"] < prev_start:
            errs.append(f"line {lid}: lines must be in time order")
        prev_start = l["start"]
        if l.get("keep_original"):
            continue
        slot = l["max_end"] - l["start"]
        for k, (lo, hi) in LANGS.items():
            t = l.get(k, "")
            if not t.strip():
                errs.append(f"line {lid} [{k}]: empty")
                continue
            bad = sorted({c for c in t if not (lo <= ord(c) <= hi or c.isspace() or c in PUNCT or c in JOINERS)})
            if bad:
                errs.append(f"line {lid} [{k}]: characters outside {k} script/allowed punctuation: {''.join(bad)!r}")
            n = count(t)
            budget = math.floor(slot * CPS_LINE[k])
            totals[k][0] += n
            totals[k][1] += slot
            if n > budget:
                errs.append(f"line {lid} [{k}]: {n} chars > budget {budget} (slot {slot:.2f}s) — shorten")
    for k, (n, sec) in totals.items():
        if n > math.floor(sec * CPS_TOTAL[k]):
            errs.append(f"[{k}] total {n} chars > {math.floor(sec * CPS_TOTAL[k])} for {sec:.1f}s of slots — shorten some lines")
    import os
    ok_marker = path.replace("plan.json", "plan.ok")
    if errs:
        if os.path.exists(ok_marker):
            os.remove(ok_marker)
        print("\n".join(errs))
        sys.exit(1)
    open(path.replace("plan.json", "plan.ok"), "w").write("ok")  # dubbing engine only picks up validated plans
    print("OK  " + "  ".join(f"{k}:{n}/{math.floor(s * CPS_TOTAL[k])}" for k, (n, s) in totals.items()))


if __name__ == "__main__":
    main(sys.argv[1])
