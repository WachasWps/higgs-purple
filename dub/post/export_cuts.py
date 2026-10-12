"""Text-free shot cuts of the 10 English General Ads, for the client to re-edit (text/captions are added back later).

usage: python3 post/export_cuts.py [<id> ...]        -> General_Ads_Cuts/<NN>_<PS|KNC>_<title>/
Per ad: 00_full_clean.mp4 (whole picture, no text/logo/audio), Cut_NN_<source>.mp4 per shot (frame-accurate, from
work/<id>/source_fixed.mp4), 99_end_card.mp4 (the 5 s brand outro) and cuts.csv (shot timings on the ad timeline).
"""
import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "feedback"))
sys.path.insert(0, str(ROOT / "post"))
import assemble_fix as A  # noqa: E402
import render_post as R  # noqa: E402

ADS = "4010f985 c01adcce fe7174d4 fb3fa838 ce52c347 a9be56d9 426b77bb eab38211 e9528636 b4c787e1".split()
OUT = ROOT / "General_Ads_Cuts"
ENC = ["-an", "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p", "-movflags", "+faststart"]


def run(cmd):
    subprocess.run([R.FFMPEG, "-v", "error", "-y", *cmd], check=True)


def export(v):
    shots, *_ = A.plan_shots(v)
    pic = ROOT / "work" / v / "source_fixed.mp4"
    name = R.out_path(v, "en").stem.rsplit("_", 1)[0]
    d = OUT / name
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    run(["-i", str(pic), *ENC, str(d / "00_full_clean.mp4")])
    rows = []
    for i, s in enumerate(shots, 1):
        a, b = float(s["start"]), float(s["end"])
        what = str(s.get("replace_with") or "original").replace("GRAPHIC_", "").lower()
        fn = f"Cut_{i:02d}_{what}.mp4"
        run(["-i", str(pic), "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", *ENC, str(d / fn)])
        rows.append([fn, f"{a:.2f}", f"{b:.2f}", f"{b - a:.2f}"])
    g = json.loads((ROOT / "work" / v / "graphics.json").read_text())
    if not g.get("no_outro"):
        run(["-i", str(R.outro_for(g.get("product") or "uv_sunscreen")), "-t", f"{R.OUTRO_DUR}", "-vf",
             f"scale={R.W}:{R.H}:force_original_aspect_ratio=increase,crop={R.W}:{R.H},setsar=1,fps={R.FPS}",
             *ENC, str(d / "99_end_card.mp4")])
    with open(d / "cuts.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cut", "start (s)", "end (s)", "length (s)"])
        w.writerows(rows)
    return f"{v}: {name} — {len(rows)} cuts"


if __name__ == "__main__":
    for v in sys.argv[1:] or ADS:
        try:
            print(export(v), flush=True)
        except Exception as ex:
            print(f"{v}: FAILED {ex!r}", flush=True)
