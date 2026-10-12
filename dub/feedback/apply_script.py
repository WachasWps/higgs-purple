"""Apply the approved shot-matched script (feedback/script_audit/final_changes.json + translations.json):
update plan.json (en + 5 langs), captions_<lang>.json, and write redub.json for the dubbed videos."""
import json, shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
A = ROOT / "feedback" / "script_audit"
ADS = set("4010f985 c01adcce fe7174d4 fb3fa838 ce52c347 a9be56d9 426b77bb eab38211 e9528636 b4c787e1".split())
fc = json.loads((A / "final_changes.json").read_text())
tr = {(t["video"], t["id"]): t for t in json.loads((A / "translations.json").read_text())}
for v, ls in fc.items():
    wd = ROOT / "work" / v
    bak = ROOT / "feedback" / "plan_backup" / f"{v}.plan.pre_script2.json"
    if not bak.exists(): shutil.copy2(wd / "plan.json", bak)
    plan = json.loads((wd / "plan.json").read_text()); L = {l["id"]: l for l in plan["lines"]}
    for c in ls:
        L[c["id"]]["en"] = c["new"]
        if v not in ADS:
            t = tr[(v, c["id"])]
            for k in ("bn", "ta", "te", "ml", "or"):
                L[c["id"]][k] = t[k]
                cf = wd / f"captions_{k}.json"
                if cf.exists():
                    cj = json.loads(cf.read_text()); cj.setdefault("lines", {})[str(c["id"])] = t[k]; cf.write_text(json.dumps(cj, ensure_ascii=False, indent=1))
    (wd / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    if v not in ADS:
        (wd / "redub.json").write_text(json.dumps({"lines": [c["id"] for c in ls]}))
        (wd / "redub.ok").unlink(missing_ok=True)
    print(v, "updated", [c["id"] for c in ls])
