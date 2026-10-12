"""Expose finished dubs as dub/final/<Language>/<NN>_<title>.mp4 (hard links, no extra disk). Skips broken files."""
import json, re, subprocess
from pathlib import Path
ROOT = Path(__file__).parent
LANG = {"bn": "Bengali", "ta": "Tamil", "te": "Telugu", "ml": "Malayalam", "or": "Odia"}

def title(wd):
    p = (wd / "prompt.txt").read_text() if (wd / "prompt.txt").exists() else ""
    m = re.search(r'(?:TITLE:|titled|—)\s*[“"]([^”"]{3,60})[”"]', p) or re.search(r'[“"]([^”"]{4,40})[”"]', p)
    t = m.group(1) if m else ""
    plan = json.loads((wd / "plan.json").read_text()) if (wd / "plan.json").exists() else {}
    style = plan.get("style", "ad")
    product = "kojic-night-cream" if "KOJIC" in p.upper() else "uv-sunscreen" if "VIOLET" in p.upper() else "dermdoc"
    slug = re.sub(r"[^a-z0-9]+", "-", (t or style).lower()).strip("-")[:40]
    return f"{product}_{style}_{slug}"

ids = sorted(p.parent for p in (ROOT / "work").glob("*/plan.json")
             if json.loads((p.parent / "meta.json").read_text()).get("kind") != "ad")  # ads deliver separately
meta = {wd.name: json.loads((wd / "meta.json").read_text())["createdAt"] if (wd / "meta.json").exists() else 0 for wd in ids}
order = {vid: i + 1 for i, vid in enumerate(sorted(meta, key=meta.get))}
n = 0
for wd in ids:
    for code, name in LANG.items():
        src = ROOT / "out" / f"{wd.name}_{code}.mp4"
        if not src.exists():
            continue
        ok = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src],
                            capture_output=True, text=True).stdout.strip()
        if not ok or float(ok) < 5:
            continue  # incomplete/broken render; the engine will redo it
        dst = ROOT / "final" / name / f"{order[wd.name]:02d}_{title(wd)}_{wd.name}.mp4"
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            dst.unlink()
        dst.hardlink_to(src)
        n += 1
print(f"final/: {n} videos  ({', '.join(f'{v}: {len(list((ROOT/'final'/v).glob(chr(42)+'.mp4')))}' for v in LANG.values() if (ROOT/'final'/v).exists())})")
