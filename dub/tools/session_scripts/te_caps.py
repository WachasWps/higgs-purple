import json, sys
from pathlib import Path
W = Path("/Users/wachas/Documents/higgs-purple/dub/work")
Z = "‌"
DD = "డెర్మ్‌డాక్"
NC = "నైట్ క్రీమ్"
SUBS = {
 "71e0977a": {4: [(NC + Z + "లో", "Night Cream-లో")],
              5: [(DD, "DERMDOC"), ("కె ఎన్ సి", "KNC"), (NC, "Night Cream")]},
 "74495eba": {3: [("ఎస్‌పీఎఫ్ ఫిఫ్టీ, పీఏ ట్రిపుల్ ప్లస్", "SPF 50 PA+++"), ("యూవీఏ", "UVA"), ("యూవీబీ", "UVB")],
              5: [("ఫోర్ పర్సెంట్", "4%"), ("నియాసినమైడ్" + Z + "తో", "Niacinamide-తో")]},
 "7558fbf1": {3: [("టూ పర్సెంట్", "2%"), ("కోజిక్ యాసిడ్", "Kojic Acid"), ("నియాసినమైడ్", "Niacinamide"), ("ఆల్ఫా అర్బుటిన్", "Alpha Arbutin")],
              4: [("గ్లో ఫ్యూజన్ ఫార్ములా", "Glow Fusion Formula")],
              8: [(DD, "DERMDOC"), (NC, "Night Cream")]},
 "784c77c5": {1: [("నైట్ క్రీమే", "Night Cream-మే")],
              2: [(DD, "DERMDOC"), ("టూ పర్సెంట్", "2%"), ("కోజిక్ ఆసిడ్", "Kojic Acid")],
              5: [("కోజిక్ ఆసిడ్", "Kojic Acid"), ("నియాసినమైడ్", "Niacinamide"), ("ఆల్ఫా ఆర్బుటిన్", "Alpha Arbutin")]},
 "7ea55172": {6: [("ఫోర్ పర్సెంట్", "4%"), ("నియాసినమైడ్", "Niacinamide")],
              7: [("ఎస్‌పిఎఫ్ ఫిఫ్టీ పిఏ ట్రిపుల్ ప్లస్", "SPF 50 PA+++")]},
 "89697c77": {4: [("త్రీ ఎక్స్‌పర్ట్", "3Xpert")],
              9: [(DD, "DERMDOC"), ("కోజిక్", "Kojic")]},
 "906fbf3c": {3: [("త్రీ ఎక్స్‌పర్ట్", "3Xpert")],
              8: [(DD, "DERMDOC"), ("టూ పర్సెంట్", "2%"), ("కోజిక్", "Kojic"), (NC, "Night Cream")]},
 "bd3b8af7": {2: [("టూ పర్సెంట్", "2%"), ("కోజిక్ యాసిడ్", "Kojic Acid")],
              5: [(DD, "DERMDOC"), ("టూ పర్సెంట్", "2%"), ("కోజిక్ యాసిడ్", "Kojic Acid"), (NC, "Night Cream")]},
 "c51221b6": {2: [("సన్‌స్క్రీన్", "Sunscreen")], 3: [("సన్‌స్క్రీన్", "Sunscreen")], 7: [("సన్‌స్క్రీన్", "Sunscreen")]},
 "caf29456": {6: [("నాలుగు పర్సెంట్", "4%"), ("నియాసినమైడ్", "Niacinamide")],
              7: [("ఎస్‌పీఎఫ్ ఫిఫ్టీ పీఏ ట్రిపుల్ ప్లస్", "SPF 50 PA+++")]},
 "cd5a6fe8": {3: [("గ్లో ఫ్యూజన్" + Z + "లో", "Glow Fusion-లో"), ("కోజిక్ యాసిడ్", "Kojic Acid"), ("నియాసినమైడ్", "Niacinamide"), ("ఆల్ఫా ఆర్బుటిన్", "Alpha Arbutin")],
              4: [("నైట్ క్రీం", "Night Cream")],
              9: [(DD, "DERMDOC"), ("నైట్ క్రీం", "Night Cream")]},
 "ce849d3f": {},
 "dad2130b": {1: [("సన్‌స్క్రీనా", "Sunscreen-నా")],
              5: [("నాలుగు పర్సెంట్", "4%"), ("నియాసినమైడ్", "Niacinamide"), ("ఎస్‌పీఎఫ్ ఫిఫ్టీ పీఏ ట్రిపుల్ ప్లస్", "SPF 50 PA+++")]},
 "e7e42eaf": {3: [("యూవీఏ", "UVA"), ("యూవీబీ", "UVB")]},
 "f7ce58d4": {2: [("కె ఎన్ సి", "KNC")], 6: [(NC, "Night Cream")],
              7: [(DD, "DERMDOC"), ("టూ పర్సెంట్", "2%"), ("కోజిక్ యాసిడ్", "Kojic Acid"), (NC, "Night Cream")]},
}
for vid, subs in SUBS.items():
    plan = json.loads((W / vid / "plan.json").read_text())
    lines = {}
    for l in plan["lines"]:
        if l.get("keep_original") or not l.get("te", "").strip():
            continue
        t = l["te"]
        for old, new in subs.get(l["id"], []):
            assert old in t, (vid, l["id"], old, t)
            t = t.replace(old, new)
        lines[str(l["id"])] = t
    assert set(map(str, subs)) <= set(lines), vid
    (W / vid / "captions_te.json").write_text(json.dumps({"language": "te", "lines": lines}, ensure_ascii=False, indent=1) + "\n")
print("written", len(SUBS))
