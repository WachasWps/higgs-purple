import json, sys
from pathlib import Path
W = Path("/Users/wachas/Documents/higgs-purple/dub/work")
# (id, line) -> caption override; all other lines copied verbatim from plan ta
O = {
 "71e0977a": {"4": "மூணு டார்கெட்டட் இன்கிரீடியன்ட்ஸ் பவர், ஒரே Night Cream-ல.",
              "5": "DERMDOC கே என் சி Night Cream. ஒவ்வொரு நைட்டும் வொர்த்!"},
 "74495eba": {"3": "SPF 50 PA+++, UVA, UVB ரெண்டுலருந்தும் காப்பாத்தும்!",
              "5": "இந்தியன் ஸ்கின்னுக்காகவே, 4% Niacinamide-டோட!"},
 "7558fbf1": {"3": "என் பவர், 2% Kojic Acid, கூட Niacinamide, Alpha Arbutin!",
              "4": "சேர்ந்து, நாங்கதான் Glow Fusion Formula!",
              "8": "DERMDOC Night Cream, ஓவர்நைட் பிரைட்னர்!"},
 "784c77c5": {"1": "டார்க் ஸ்பாட்ஸ ட்ராக் பண்ணேன், இந்த Night Cream தான் மெயின் ஸ்டெப்.",
              "2": "DERMDOC 2% Kojic Acid!",
              "5": "Kojic Acid, Niacinamide, Alpha Arbutin, ஸ்பாட்ஸ் குறைவா தெரிய உதவும்."},
 "7ea55172": {"6": "4% Niacinamide, ப்ரைட்டா ஆக ஹெல்ப்!",
              "7": "SPF 50 PA+++, வெயிலுக்கு ரெடி!"},
 "89697c77": {"4": "நீ தூங்கு, 3Xpert ஃபார்முலா வொர்க்!",
              "9": "DERMDOC Kojic க்ரீம், ஸ்லீப் டு க்ளோ!"},
 "906fbf3c": {"3": "3Xpert ஃபார்முலா, மூணு ப்ரைட்டனிங் ஆக்டிவ்ஸ்!",
              "8": "DERMDOC 2% Kojic Night Cream. தூங்கு, க்ளோ!"},
 "bd3b8af7": {"2": "நான் 2% Kojic Acid. டார்க் ஸ்பாட், பிக்மென்டேஷன் என் வேலை.",
              "5": "ரிச் க்ரீம். தடவு, ஊறட்டும், தினமும். DERMDOC 2% Kojic Acid Night Cream."},
 "c51221b6": {"2": "இனி ஊருக்கே உன் Sunscreen தெரியும்!",
              "3": "தப்பான Sunscreen, மச்சி!",
              "7": "க்ளோவ பாருங்க, Sunscreen-ன இல்ல!"},
 "caf29456": {"6": "கூட 4% Niacinamide, நேச்சுரல் ஸ்கின் டோன் மாறாம, ப்ரைட்டா, ஈவனா தெரியும்.",
              "7": "SPF 50 PA+++, டேடைம் ப்ரொடெக்ஷன் கவர்!"},
 "cd5a6fe8": {"3": "Glow Fusion-ல Kojic Acid, Niacinamide, Alpha Arbutin.",
              "4": "Night Cream டெக்ஸ்சர் செம்ம ரிச்!",
              "9": "DERMDOC Night Cream, ப்ரைட்னிங்!"},
 "ce849d3f": {},
 "dad2130b": {"1": "பர்பிள் Sunscreen-னா? பர்பிளா ஆயிடுவேன்னு நெனச்சேன்!",
              "5": "4% Niacinamide, SPF 50 PA+++."},
 "e7e42eaf": {"3": "UVA-வும் UVB-யும்? ப்ளாக்ட்!"},
 "f7ce58d4": {"6": "மூணு டார்கெட்டட் இன்கிரீடியன்ட்ஸ். ஒரே பவர்ஃபுல் Night Cream.",
              "7": "DERMDOC 2% Kojic Acid Night Cream."},
}
for vid, ov in O.items():
    plan = json.loads((W/vid/"plan.json").read_text())
    lines = {}
    for l in plan["lines"]:
        if l.get("keep_original") or not l.get("ta", "").strip():
            continue
        lid = str(l["id"])
        lines[lid] = ov.get(lid, l["ta"].strip())
    assert set(ov) <= set(lines), (vid, set(ov) - set(lines))
    (W/vid/"captions_ta.json").write_text(json.dumps({"language": "ta", "lines": lines}, ensure_ascii=False, indent=1) + "\n")
print("written", len(O))
