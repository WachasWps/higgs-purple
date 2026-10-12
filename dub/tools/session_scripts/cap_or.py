import json, re, sys
from pathlib import Path
W = Path("/Users/wachas/Documents/higgs-purple/dub/work")
IDS = "71e0977a 74495eba 7558fbf1 784c77c5 7ea55172 89697c77 906fbf3c bd3b8af7 c51221b6 caf29456 cd5a6fe8 ce849d3f dad2130b e7e42eaf f7ce58d4".split()
R = [
 ("ଏସପିଏଫ ଫିଫ୍ଟି, ପିଏ ଟ୍ରିପଲ ପ୍ଲସ", "SPF 50 PA+++"),
 ("ଏସପିଏଫ ଫିଫ୍ଟି ପିଏ ଟ୍ରିପଲ ପ୍ଲସ", "SPF 50 PA+++"),
 ("ୟୁଭିଏ", "UVA"), ("ୟୁଭିବି", "UVB"),
 ("ଟୁ ପର୍ସେଣ୍ଟ", "2%"), ("ଫୋର ପର୍ସେଣ୍ଟ", "4%"), ("ଫୋର ପରସେଣ୍ଟ", "4%"), ("ଚାରି ପର୍ସେଣ୍ଟ", "4%"),
 ("କୋଜିକ ଏସିଡ୍", "Kojic Acid"), ("କୋଜିକ ଏସିଡ", "Kojic Acid"), ("କୋଜିକ", "Kojic"),
 ("ନିଆସିନାମାଇଡ୍", "Niacinamide"), ("ନିଆସିନାମାଇଡ", "Niacinamide"),
 ("ଆଲଫା ଆରବୁଟିନ", "Alpha Arbutin"), ("ଆଲଫା ଆର୍ବୁଟିନ୍", "Alpha Arbutin"), ("ଆଲଫା ଆର୍ବୁଟିନ", "Alpha Arbutin"),
 ("ଗ୍ଲୋ ଫ୍ୟୁଜନ ଫର୍ମୁଲା", "Glow Fusion Formula"), ("ଗ୍ଲୋ ଫିଉଜନ", "Glow Fusion"),
 ("ଥ୍ରୀ ଏକ୍ସପର୍ଟ", "3Xpert"),
 ("ନାଇଟ୍ କ୍ରିମରେ", "Night Cream-ରେ"), ("ନାଇଟ କ୍ରିମ୍", "Night Cream"), ("ନାଇଟ କ୍ରିମ", "Night Cream"),
 ("କେ ଏନ ସି", "KNC"), ("ଡର୍ମଡକ", "DERMDOC"), ("ସନସ୍କ୍ରିନ", "Sunscreen"),
]
SUS = re.compile("ପର୍ସେଣ୍ଟ|ପରସେଣ୍ଟ|ଏସପିଏଫ|ପିଏ|କ୍ରିମ|ନାଇଟ|ଡର୍ମ|ଫର୍ମୁଲା|ଅଲ|ୟୁଭି|ହନେ|ସାଇନ|ଆରବୁ|ଆର୍ବୁ|ଫ୍ୟୁଜ|ଫିଉଜ|ଏକ୍ସପର୍ଟ|ଫିଫ୍ଟି|ଟ୍ରିପଲ")
for i in IDS:
    plan = json.loads((W/i/"plan.json").read_text())
    out = {}
    for l in plan["lines"]:
        s = l.get("or", "")
        if l.get("keep_original") or not s.strip(): continue
        t = s
        for a, b in R: t = t.replace(a, b)
        out[str(l["id"])] = t
        flag = " <<CHECK" if SUS.search(t) else ""
        if t != s or flag: print(f"{i}:{l['id']}  {s}\n    -> {t}{flag}")
    (W/i/"captions_or.json").write_text(json.dumps({"language": "or", "lines": out}, ensure_ascii=False, indent=1) + "\n")
