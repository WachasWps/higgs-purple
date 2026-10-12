"""Apply specs.py to work/<id>/ (plan, captions, graphics, redub_text.json).

usage: python3 apply.py check <id>...   -> build + validate in scratch only
       python3 apply.py write <id>...   -> same, then atomically write into work/<id>/ and validate there
"""
import contextlib
import copy
import io
import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

DUB = Path("/Users/wachas/Documents/higgs-purple/dub")
SCR = Path(__file__).resolve().parent / "stage"
sys.path.insert(0, str(DUB))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_plan as VP  # noqa: E402
from specs import SPECS  # noqa: E402

VP.FX = set(VP.FX) | {"villain_f"}   # recast step introduced fx "villain_f" (supported by dubplan.py); cast is off-limits
LANGS = ["bn", "ta", "te", "ml", "or"]
REPL = {
    "bn": [("ইনস্ট্যান্ট গ্লো", "Instant Glow"), ("ফোর পার্সেন্ট নায়াসিনামাইড", "4% Niacinamide"),
           ("ফোর পারসেন্ট নায়াসিনামাইড", "4% Niacinamide"), ("সানস্ক্রিন", "Sunscreen")],
    "ta": [("இன்ஸ்டன்ட் க்ளோ", "Instant Glow")],
    "te": [("ఇన్‌స్టంట్ గ్లో", "Instant Glow"), ("సన్‌స్క్రీన్", "Sunscreen")],
    "ml": [("ഇൻസ്റ്റന്റ് ഗ്ലോ", "Instant Glow")],
    "or": [("ଇନଷ୍ଟାଣ୍ଟ ଗ୍ଲୋ", "Instant Glow"), ("ଫୋର ପର୍ସେଣ୍ଟ ନିଆସିନାମାଇଡ", "4% Niacinamide"),
           ("ସନସ୍କ୍ରିନକୁ", "Sunscreen-କୁ"), ("ସନସ୍କ୍ରିନ", "Sunscreen")],
}
LEFTOVER = ["ইনস্ট্যান্ট", "இன்ஸ்டன்ட்", "ఇన్‌స్టంట్", "ഇൻസ്റ്റന്റ്", "ଇନଷ୍ଟାଣ୍ଟ", "সানস্ক্রিন", "சன்ஸ்க்ரீன",
            "సన్‌స్క్రీన్", "സൺസ്ക്രീ", "ସନସ୍କ୍ରିନ", "নায়াসিনামাইড", "ନିଆସିନାମାଇଡ"]


def atomic_write(path, text):
    tmp = path.with_name(path.name + ".tmp_textpass")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def run_plan_validator(plan_path):
    buf = io.StringIO()
    code = 0
    with contextlib.redirect_stdout(buf):
        try:
            VP.main(str(plan_path))
        except SystemExit as e:
            code = e.code or 0
    return code, buf.getvalue().strip()


def caption_for(lang, text):
    for a, b in REPL[lang]:
        text = text.replace(a, b)
    return text


def build(vid):
    spec = SPECS[vid]
    wd = DUB / "work" / vid
    plan = json.loads((wd / "plan.json").read_text())
    new = copy.deepcopy(plan)
    lines = {l["id"]: l for l in new["lines"]}
    changed = {}
    for lid, edits in spec["plan"].items():
        l = lines[lid]
        for k, v in edits.items():
            if l.get(k) != v:
                l[k] = v
                changed.setdefault(lid, set()).add(k)
    caps = {}
    for L in LANGS:
        c = json.loads((wd / f"captions_{L}.json").read_text())
        for lid, ks in changed.items():
            if L in ks or lid in spec.get("caps", {}):
                c["lines"][str(lid)] = spec.get("caps", {}).get(lid, {}).get(L) or caption_for(L, lines[lid][L])
        caps[L] = c
    meta = json.loads((wd / "meta.json").read_text())
    old_g = json.loads((wd / "graphics.json").read_text())
    g = {"video_id": vid, "product": old_g.get("product", "uv_sunscreen"), "caption_y": spec["gfx"]["caption_y"],
         "elements": spec["gfx"]["elements"], "notes": spec["gfx"]["notes"]}
    if spec["gfx"].get("caption_moves"):
        g["caption_moves"] = spec["gfx"]["caption_moves"]
    return plan, new, changed, caps, g, meta


def report(vid, plan, new, changed, caps):
    old = {l["id"]: l for l in plan["lines"]}
    for l in new["lines"]:
        if l["id"] not in changed:
            continue
        slot = l["max_end"] - l["start"]
        print(f"  L{l['id']} [{l['start']}-{l['max_end']}] {sorted(changed[l['id']])}  en: {l['en']}")
        for L in LANGS:
            if L in changed[l["id"]]:
                n, b = VP.count(l[L]), math.floor(slot * VP.CPS_LINE[L])
                print(f"     {L} {n:>3}/{b:<3} {l[L]}")
                print(f"            cap: {caps[L]['lines'][str(l['id'])]}")
                left = [w for w in LEFTOVER if w in caps[L]["lines"][str(l["id"])]]
                if left:
                    print(f"            !! regional term left in caption: {left}")


def validate_dir(d, vid):
    out = []
    code, msg = run_plan_validator(d / "plan.json")
    out.append(("plan", code, msg))
    for L in LANGS:
        r = subprocess.run([sys.executable, str(DUB / "post" / "validate_captions.py"), str(d / f"captions_{L}.json")],
                           capture_output=True, text=True)
        out.append((f"captions_{L}", r.returncode, (r.stdout + r.stderr).strip()))
    r = subprocess.run([sys.executable, str(DUB / "post" / "validate_graphics.py"), str(d / "graphics.json")],
                       capture_output=True, text=True)
    out.append(("graphics", r.returncode, (r.stdout + r.stderr).strip()))
    return out


def dump(obj):
    return json.dumps(obj, ensure_ascii=False, indent=1) + "\n"


def main(mode, ids):
    for vid in ids:
        plan, new, changed, caps, g, meta = build(vid)
        print(f"===== {vid}  changed lines: {sorted(changed)}")
        report(vid, plan, new, changed, caps)
        st = SCR / vid
        if st.exists():
            shutil.rmtree(st)
        st.mkdir(parents=True)
        (st / "plan.json").write_text(dump(new))
        (st / "meta.json").write_text(json.dumps(meta))
        for L in LANGS:
            (st / f"captions_{L}.json").write_text(dump(caps[L]))
        (st / "graphics.json").write_text(dump(g))
        res = validate_dir(st, vid)
        for name, code, msg in res:
            print(f"  [stage] {name}: {'OK' if code == 0 else 'FAIL'}  {msg if code else msg.splitlines()[0] if msg else ''}")
        plan_ok = res[0][1] == 0 and all(c == 0 for n, c, m in res if n.startswith("captions"))
        if mode != "write":
            continue
        if not plan_ok:
            print(f"  !! {vid}: plan/captions not valid in stage, NOT writing")
            continue
        wd = DUB / "work" / vid
        atomic_write(wd / "plan.json", dump(new))
        for L in LANGS:
            atomic_write(wd / f"captions_{L}.json", dump(caps[L]))
        atomic_write(wd / "graphics.json", dump(g))
        rt = wd / "redub_text.json"
        prev = json.loads(rt.read_text())["lines"] if rt.exists() else []
        atomic_write(rt, json.dumps({"lines": sorted(set(prev) | set(changed))}) + "\n")
        for name, code, msg in validate_dir(wd, vid):
            print(f"  [work ] {name}: {'OK' if code == 0 else 'FAIL'}  {msg}")
        print(f"  redub_text.json -> {rt.read_text().strip()}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
