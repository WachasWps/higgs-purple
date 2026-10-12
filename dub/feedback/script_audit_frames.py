"""Per-shot frames + overlapping script lines for the script audit (feedback/script_audit/<id>/)."""
import json, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
FF = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
OUT = ROOT / "feedback" / "script_audit"
ADS = "4010f985 c01adcce fe7174d4 fb3fa838 ce52c347 a9be56d9 426b77bb eab38211 e9528636 b4c787e1".split()
ids = sorted({p.stem for p in (ROOT / "feedback" / "edl_v2").glob("*.json")} | set(ADS))
for v in ids:
    if v in ADS:
        shots = [dict(n=r["n"], start=r["start"], end=r["end"], what=r["source"]) for r in json.loads((ROOT/"feedback/edl"/f"{v}.json").read_text())["rebuild"]["shots"]]
    else:
        shots = [dict(n=s["n"], start=s["start"], end=s["end"], what=s.get("replace_with") or "original footage") for s in json.loads((ROOT/"feedback/edl_v2"/f"{v}.json").read_text())["shots"]]
    plan = json.loads((ROOT/"work"/v/"plan.json").read_text())
    d = OUT / v; d.mkdir(parents=True, exist_ok=True)
    for s in shots:
        for k, frac in enumerate((0.25, 0.75)):
            t = s["start"] + (s["end"] - s["start"]) * frac
            f = d / f"s{s['n']:02d}_{k}.jpg"
            subprocess.run([FF, "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(ROOT/"work"/v/"source_fixed.mp4"), "-frames:v", "1", "-vf", "scale=270:-2", str(f)], check=True)
        s["frames"] = [f"s{s['n']:02d}_0.jpg", f"s{s['n']:02d}_1.jpg"]
        s["lines"] = [dict(id=l["id"], start=l["start"], end=l["end"], speaker=l["speaker"], en=l["en"]) for l in plan["lines"] if l["start"] < s["end"] and l["end"] > s["start"]]
    (d / "manifest.json").write_text(json.dumps(dict(video=v, style=plan.get("style"), cast=[{k: c.get(k) for k in ("id", "name", "description")} for c in plan.get("cast", [])],
        lines=[dict(id=l["id"], start=l["start"], end=l["end"], speaker=l["speaker"], en=l["en"]) for l in plan["lines"]], shots=shots), indent=1, ensure_ascii=False))
    print(v, len(shots), "shots")
