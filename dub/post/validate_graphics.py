"""Validate work/<id>/graphics.json against post/GRAPHICS_BRIEF.md. Prints OK or errors."""
import json
import sys
from pathlib import Path

TYPES = {"hook_mono", "pill", "claim_bold", "label", "hud", "blur"}
SPLIT_LABELS = ("BEFORE", "AFTER", "INSTANT GLOW")   # before/after split-screen labels (top / under the after image)


def split_label(e):
    ls = [str(x).strip().upper() for x in e.get("lines") or []]
    return len(ls) == 1 and ls[0].startswith(SPLIT_LABELS)
POS = {"top", "upper", "center", "lower"}
ANIM = {"pop", "fade", "slide_up", "type", None}
BANNED = ("WHITEN", "FAIR")


def main(path):
    p = Path(path)
    g = json.loads(p.read_text())
    meta = json.loads((p.parent / "meta.json").read_text())
    dur = meta.get("duration", 20.0)
    errs = []
    if g.get("product") not in ("uv_sunscreen", "kojic_night_cream"):
        errs.append("product must be uv_sunscreen or kojic_night_cream")
    if not 0.78 <= g.get("caption_y", 0.90) <= 0.93:
        errs.append("caption_y must be within 0.78..0.93")
    for m in g.get("caption_moves", []):  # temporarily lift captions over baked-in bottom text
        if not (isinstance(m.get("start"), (int, float)) and isinstance(m.get("end"), (int, float))
                and 0 <= m["start"] < m["end"] <= dur + 0.05 and 0.55 <= m.get("y", 0) <= 0.93):
            errs.append(f"caption_moves entry {m}: need 0<=start<end<=duration and 0.55<=y<=0.93")
    texts = []
    for i, e in enumerate(g.get("elements", [])):
        t = e.get("type")
        tag = f"element {i} ({t})"
        if t not in TYPES:
            errs.append(f"{tag}: type must be one of {sorted(TYPES)}")
            continue
        s, en = e.get("start"), e.get("end")
        if not (isinstance(s, (int, float)) and isinstance(en, (int, float)) and 0 <= s < en <= dur + 0.05):
            errs.append(f"{tag}: need 0 <= start < end <= duration ({dur:.2f})")
            continue
        if e.get("anim") not in ANIM:
            errs.append(f"{tag}: anim must be one of pop/fade/slide_up/type")
        if t == "blur":
            b = e.get("box") or {}
            if not (all(isinstance(b.get(k), (int, float)) for k in ("x0", "x1", "y0", "y1"))
                    and 0 <= b["x0"] < b["x1"] <= 1 and 0 <= b["y0"] < b["y1"] <= 1):
                errs.append(f"{tag}: blur needs box with 0<=x0<x1<=1, 0<=y0<y1<=1")
            continue
        if t == "hud":
            if e.get("variant") not in ("corners", "scan"):
                errs.append(f"{tag}: hud variant must be corners or scan")
            continue
        is_mask = bool(e.get("mask"))
        if not is_mask and not 1.0 <= en - s <= 4.0:
            errs.append(f"{tag}: on screen {en - s:.1f}s (keep 1.0–4.0 s)")
        lines = e.get("lines") or []
        if not 1 <= len(lines) <= (3 if is_mask else 2):
            errs.append(f"{tag}: 1–2 lines (masks: up to 3)")
        for ln in lines + ([e["sub"]] if e.get("sub") else []):
            if ln != ln.upper() and t != "label":
                errs.append(f"{tag}: '{ln}' must be UPPERCASE")
            if any(b in ln.upper() for b in BANNED):
                errs.append(f"{tag}: banned claim wording in '{ln}'")
        for ln in lines:
            if len(ln.split()) > (5 if is_mask else 3):
                errs.append(f"{tag}: '{ln}' has too many words")
        if e.get("sub") and len(e["sub"].split()) > 5:
            errs.append(f"{tag}: sub line longer than 5 words")
        mk = e.get("mask")
        if mk is not None and not (t == "pill" and all(isinstance(mk.get(k), (int, float)) for k in ("x0", "x1", "y0", "y1"))
                                   and 0 <= mk["x0"] < mk["x1"] <= 1 and 0 <= mk["y0"] < mk["y1"] <= 1):
            errs.append(f"{tag}: mask must be on a pill with 0<=x0<x1<=1, 0<=y0<y1<=1")
        if t == "label":
            if not all(isinstance(e.get(k), (int, float)) for k in ("x", "y")):
                errs.append(f"{tag}: label needs explicit x,y (0..1)")
            elif not (0.05 <= e["x"] <= 0.95 and 0.12 <= e["y"] <= (0.97 if split_label(e) else 0.85)):
                errs.append(f"{tag}: label x/y outside safe area (x 0.05–0.95, y 0.12–0.85; "
                            f"before/after split labels up to 0.97 — captions are moved to the divider then)")
        elif e.get("position") not in POS and not all(isinstance(e.get(k), (int, float)) for k in ("x", "y")):
            errs.append(f"{tag}: position must be one of {sorted(POS)} (or explicit x,y)")
        texts.append((s, en, "label" if is_mask else t, i))  # masks may overlap other supers
    # no two non-label text elements overlapping in time
    main_ = sorted((s, en, i) for s, en, t, i in texts if t != "label")
    for (s1, e1, i1), (s2, e2, i2) in zip(main_, main_[1:]):
        if s2 < e1 - 0.05:
            errs.append(f"elements {i1} and {i2} overlap in time ({s2:.2f} < {e1:.2f})")
    # the before/after labels (BEFORE / AFTER / INSTANT GLOW) form ONE comparison element
    n_txt = len(texts) - max(0, sum(1 for e in g["elements"] if isinstance(e, dict) and e.get("type") == "label" and split_label(e)) - 1)
    if not 1 <= n_txt <= 8:
        errs.append(f"{n_txt} text elements (use 1–8; typically 3–5)")
    if errs:
        print("\n".join(errs))
        sys.exit(1)
    print(f"OK  {len(texts)} text elements")


if __name__ == "__main__":
    main(sys.argv[1])
