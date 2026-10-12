import json, sys
from pathlib import Path
ROOT = Path("/Users/wachas/Documents/higgs-purple/dub/work")
# per-video exact replacements (old -> new), applied in order to the dubbed ml text
R = {
 "71e0977a": {4: [("നൈറ്റ് ക്രീമിൽ", "Night Cream-ൽ")],
              5: [("ഡെർമ്ഡോക്", "DERMDOC"), ("കെ എൻ സി", "KNC"), ("നൈറ്റ് ക്രീം", "Night Cream")]},
 "74495eba": {3: [("എസ്പിഎഫ് ഫിഫ്റ്റി, പിഎ ട്രിപ്പിൾ പ്ലസ്", "SPF 50 PA+++"), ("യുവിഎ", "UVA"), ("യുവിബി", "UVB")],
              5: [("ഫോർ പേഴ്സന്റ് നിയാസിനമൈഡുമായി", "4% Niacinamide-മായി")]},
 "7558fbf1": {3: [("ടു പേഴ്സന്റ് കോജിക് ആസിഡ്", "2% Kojic Acid"), ("നിയാസിനാമൈഡും", "Niacinamide-ഡും"), ("ആൽഫ ആർബുട്ടിനും", "Alpha Arbutin-നും")],
              4: [("ഗ്ലോ ഫ്യൂഷൻ ഫോർമുല", "Glow Fusion Formula")],
              8: [("ഡെർമ്ഡോക്", "DERMDOC"), ("നൈറ്റ് ക്രീം", "Night Cream")]},
 "784c77c5": {1: [("നൈറ്റ് ക്രീമാണ്", "Night Cream-മാണ്")],
              2: [("ഡെർമ്ഡോക്", "DERMDOC"), ("ടു പെർസെന്റ് കോജിക് ആസിഡ്", "2% Kojic Acid")],
              5: [("കോജിക് ആസിഡ്", "Kojic Acid"), ("നിയാസിനമൈഡ്", "Niacinamide"), ("ആൽഫ ആർബുട്ടിൻ", "Alpha Arbutin")]},
 "7ea55172": {6: [("ഫോർ പേഴ്സന്റ് നിയാസിനമൈഡ്", "4% Niacinamide")],
              7: [("എസ്പിഎഫ് ഫിഫ്റ്റി പിഎ ട്രിപ്പിൾ പ്ലസ്", "SPF 50 PA+++")]},
 "89697c77": {4: [("ത്രീ എക്സ്പർട്", "3Xpert")],
              9: [("ഡെർമ്ഡോക്", "DERMDOC"), ("കോജിക്", "Kojic")]},
 "906fbf3c": {3: [("ത്രീ എക്സ്പേർട്ട്", "3Xpert")],
              8: [("ഡെർമ്ഡോക്", "DERMDOC"), ("ടു പേഴ്സന്റ് കോജിക് നൈറ്റ് ക്രീം", "2% Kojic Night Cream")]},
 "bd3b8af7": {2: [("ടു പെർസന്റ് കോജിക് ആസിഡ്", "2% Kojic Acid")],
              5: [("ഡെർമ്ഡോക്", "DERMDOC"), ("ടു പെർസന്റ് കോജിക് ആസിഡ് നൈറ്റ് ക്രീം", "2% Kojic Acid Night Cream")]},
 "c51221b6": {2: [("സൺസ്ക്രീൻ", "Sunscreen")],
              3: [("സൺസ്ക്രീൻ", "Sunscreen")],
              7: [("സൺസ്ക്രീനല്ല", "Sunscreen-നല്ല")]},
 "caf29456": {6: [("നാല് പെർസെന്റ് നിയാസിനമൈഡ്", "4% Niacinamide")],
              7: [("എസ്പിഎഫ് ഫിഫ്റ്റി പിഎ ട്രിപ്പിൾ പ്ലസ്", "SPF 50 PA+++")]},
 "cd5a6fe8": {3: [("ഗ്ലോ ഫ്യൂഷനിൽ", "Glow Fusion-ൽ"), ("കോജിക് ആസിഡ്", "Kojic Acid"), ("നിയാസിനമൈഡ്", "Niacinamide"), ("ആൽഫ ആർബുട്ടിൻ", "Alpha Arbutin")],
              4: [("നൈറ്റ് ക്രീം", "Night Cream")],
              9: [("ഡെർമ്ഡോക്", "DERMDOC")]},
 "ce849d3f": {},
 "dad2130b": {1: [("സൺസ്ക്രീനോ", "Sunscreen-നോ")],
              5: [("നാല് പെർസെന്റ് നിയാസിനമൈഡും", "4% Niacinamide-ഡും"), ("എസ്പിഎഫ് ഫിഫ്റ്റി പിഎ ട്രിപ്പിൾ പ്ലസും", "SPF 50 PA+++-സും")]},
 "e7e42eaf": {3: [("യുവിഎയും", "UVA-യും"), ("യുവിബിയും", "UVB-യും")]},
 "f7ce58d4": {2: [("കെ എൻ സി", "KNC")],
              6: [("നൈറ്റ് ക്രീം", "Night Cream")],
              7: [("ഡെർമ്ഡോക്", "DERMDOC"), ("ടു പേഴ്സന്റ് കോജിക് ആസിഡ് നൈറ്റ് ക്രീം", "2% Kojic Acid Night Cream")]},
}
bad = 0
for vid, reps in R.items():
    plan = json.loads((ROOT / vid / "plan.json").read_text())
    lines = {}
    for l in plan["lines"]:
        t = l.get("ml", "")
        if l.get("keep_original") or not t.strip():
            continue
        for old, new in reps.get(l["id"], []):
            if t.count(old) != 1:
                print(f"!! {vid} line {l['id']}: '{old}' found {t.count(old)}x"); bad += 1
            t = t.replace(old, new)
        lines[str(l["id"])] = t
    missing = set(reps) - {int(k) for k in lines}
    if missing: print("!! unused rep lines", vid, missing); bad += 1
    (ROOT / vid / "captions_ml.json").write_text(json.dumps({"language": "ml", "lines": lines}, ensure_ascii=False, indent=1) + "\n")
print("bad", bad)
