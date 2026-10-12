"""Backfill out/<id>_<lang>/layout.json for renders made before assemble.py wrote it."""
import sys, warnings
from pathlib import Path
warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import assemble

root = Path(__file__).resolve().parent.parent
done = skipped = 0
for d in sorted((root / "out").glob("????????_??")):
    vid = d.name.split("_")[0]
    if not (d / "script.json").exists() or not list(d.glob("line_*.wav")):
        skipped += 1
        continue
    if (d / "layout.json").exists() and "--force" not in sys.argv:
        continue
    lines, clips, durs, starts, rate, end, drift, lim = assemble.plan_layout(d / "script.json", d, root / "work" / vid / "source.mp4")
    assemble.write_layout(d, lines, clips, starts, rate)
    done += 1
print(f"layouts written: {done}, skipped (no clips, e.g. Kaggle renders): {skipped}")
