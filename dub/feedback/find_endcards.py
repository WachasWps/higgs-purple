"""For every ad, find where a baked 'Available on purplle' end card starts (OCR the last 12 s of the picture source)."""
import json, subprocess, sys, tempfile
from pathlib import Path
from ocrmac import ocrmac
from PIL import Image
FF = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"; FP = "/opt/homebrew/opt/ffmpeg-full/bin/ffprobe"
ROOT = Path(__file__).resolve().parent.parent
res = {}
GENERAL = {"a9be56d9","426b77bb","eab38211","e9528636","b4c787e1","c01adcce","fe7174d4","fb3fa838","ce52c347","4010f985"}
for gp in sorted(ROOT.glob("work/*/graphics.json")):
    v = gp.parent.name
    if v in GENERAL: continue
    src = gp.parent / "source_fixed.mp4"
    if not src.exists(): continue
    d = float(subprocess.run([FP, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(src)], capture_output=True, text=True).stdout)
    t0 = max(0, d - 12)
    with tempfile.TemporaryDirectory() as td:
        subprocess.run([FF, "-v", "error", "-ss", f"{t0}", "-i", str(src), "-vf", "fps=4,scale=540:-1", f"{td}/f%04d.png"], check=True)
        hits = []
        for i, f in enumerate(sorted(Path(td).glob("f*.png"))):
            txt = " ".join(t for t, c, b in ocrmac.OCR(str(f)).recognize()).lower()
            if "available on" in txt or "purplle" in txt:
                hits.append(round(t0 + i / 4, 2))
    first = hits[0] if hits else None
    # card = the contiguous run of hits that reaches the end
    if hits:
        run = [hits[-1]]
        for h in reversed(hits[:-1]):
            if run[-1] - h <= 0.5: run.append(h)
            else: break
        first = run[-1]
    g = json.loads(gp.read_text())
    res[v] = {"dur": round(d, 2), "card_start": first, "no_outro": bool(g.get("no_outro"))}
    print(v, res[v], flush=True)
(ROOT / "feedback" / "endcards.json").write_text(json.dumps(res, indent=1))
