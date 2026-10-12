"""Validate work/<id>/captions_<L>.json against the dubbed line text (CAPTIONS_BRIEF.md)."""
import json, re, sys
from pathlib import Path

BLOCK = {"bn": (0x0980, 0x09FF), "ta": (0x0B80, 0x0BFF), "te": (0x0C00, 0x0C7F), "ml": (0x0D00, 0x0D7F), "or": (0x0B00, 0x0B7F)}
LATIN_OK = {w.lower() for w in """DERMDOC Honest Science Niacinamide Kojic Acid Alpha Arbutin Glow Fusion Formula 3Xpert
Night Cream Ultra Violet Sunscreen SPF PA+++ PA UVA UVB UV KNC Instant""".split()}  # "Instant Glow" (client wording)
PUNCT = set(",.?!।-'’ +&%")


def main(path):
    p = Path(path)
    cap = json.loads(p.read_text())
    L = cap["language"]
    lo, hi = BLOCK[L]
    plan = json.loads((p.parent / "plan.json").read_text())
    want = {str(l["id"]): l.get(L, "") for l in plan["lines"] if not l.get("keep_original") and l.get(L, "").strip()}
    errs = []
    for lid, src in want.items():
        t = cap["lines"].get(lid)
        if not t:
            errs.append(f"line {lid}: missing")
            continue
        for ch in t:
            if not (lo <= ord(ch) <= hi or ch.isspace() or ch in PUNCT or ch.isdigit() or ch.isascii() or ch in "‌‍"):
                errs.append(f"line {lid}: character {ch!r} outside {L} script / Latin / digits")
                break
        for w in re.findall(r"[A-Za-z0-9][A-Za-z0-9+]*", t):
            if w.isdigit():
                continue
            if w.lower() not in LATIN_OK and w.lower().rstrip("s") not in LATIN_OK:
                errs.append(f"line {lid}: English word '{w}' is not an allowed ingredient/brand term")
        src_words = set(re.findall(r"[^\s,.?!।]+", src))
        for m in re.finditer(r"[^\sA-Za-z0-9,.?!।%+\-]+", t):
            w = m.group()
            if m.start() > 0 and t[m.start() - 1] == "-" and len(w) <= 6:
                continue  # grammatical suffix glued to an English term, e.g. Niacinamide-এ
            if not any(w in s for s in src_words):
                errs.append(f"line {lid}: regional word '{w}' not in the dubbed line")
    extra = set(cap["lines"]) - set(want)
    if extra:
        errs.append(f"unexpected line ids {sorted(extra)}")
    if errs:
        print("\n".join(errs[:20])); sys.exit(1)
    print(f"OK  {len(want)} lines")


if __name__ == "__main__":
    main(sys.argv[1])
