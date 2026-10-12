import json, sys
root = "/Users/wachas/Documents/higgs-purple/dub/work/"
ids = "00b304b4 02bad3b3 23850d94 291827ba 33c29291 390113f1 3d01d9fc 46d965c9 51440b1f 595689d8 5fd50ab8 655a1328 65a0c520 715b1b5c".split()
R = [
 ("எஸ்பிஎஃப் ஃபிஃப்டி, பிஏ ட்ரிபிள் ப்ளஸ்", "SPF 50 PA+++"),
 ("எஸ்பிஎஃப் ஃபிஃப்டி பிஏ ட்ரிபிள் ப்ளஸ்", "SPF 50 PA+++"),
 ("எஸ்பிஎஃப் ஃபிப்டி பிஏ ட்ரிபிள் ப்ளஸ்", "SPF 50 PA+++"),
 ("டெர்ம்டாக்", "DERMDOC"),
 ("டூ பர்சன்ட்", "2%"),
 ("ஃபோர் பர்சென்ட்", "4%"),
 ("நாலு பர்சென்ட்", "4%"),
 ("நாலு பர்சன்ட்", "4%"),
 ("கோஜிக் ஆசிட்", "Kojic Acid"),
 ("நியாசினமைட்", "Niacinamide"),
 ("ஆல்ஃபா அர்புடினும்", "Alpha Arbutin-னும்"),
 ("ஆல்ஃபா அர்புடின்", "Alpha Arbutin"),
 ("க்ளோ ஃப்யூஷன் ஃபார்முலா", "Glow Fusion Formula"),
 ("க்ளோ ஃப்யூஷன்ல", "Glow Fusion-ல"),
 ("க்ளோ ஃப்யூஷன்", "Glow Fusion"),
 ("நைட் க்ரீம்ல", "Night Cream-ல"),
 ("நைட் க்ரீம்", "Night Cream"),
 ("சன்ஸ்கிரீன ", "Sunscreen-ன "),
 ("சன்ஸ்கிரீன்", "Sunscreen"),
 ("சன்ஸ்க்ரீன்ல", "Sunscreen-ல"),
 ("யூவிஏ யூவிபி", "UVA UVB"),
 ("த்ரீ எக்ஸ்பர்ட்", "3Xpert"),
 ("கே என் சி", "KNC"),
 ("யூவி ரேஸ்", "UV ரேஸ்"),
]
for i in ids:
    p = json.load(open(root + i + "/plan.json"))
    out = {}
    for l in p["lines"]:
        if l.get("keep_original") or not l.get("ta", "").strip():
            continue
        t = l["ta"]
        for a, b in R:
            t = t.replace(a, b)
        out[str(l["id"])] = t
        if t != l["ta"]:
            print(i, l["id"], "|", l["ta"], "->", t)
    json.dump({"language": "ta", "lines": out}, open(root + i + "/captions_ta.json", "w"), ensure_ascii=False, indent=1)
