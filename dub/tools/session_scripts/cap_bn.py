import json, sys
from pathlib import Path
W = Path("/Users/wachas/Documents/higgs-purple/dub/work")
OV = {
 "71e0977a": {"4": "তিনটে টার্গেটেড ইনগ্রেডিয়েন্টের পাওয়ার, একটাই Night Cream-এ।",
              "5": "DERMDOC কে এন সি Night Cream। প্রতিটা রাত কাজে লাগাও!"},
 "74495eba": {"3": "SPF 50 PA+++, UVA আর UVB থেকে প্রোটেক্ট করে।",
              "5": "ইন্ডিয়ান স্কিনের জন্য, 4% Niacinamide!"},
 "7558fbf1": {"3": "আমার জোর 2% Kojic Acid, Niacinamide আর Alpha Arbutin!",
              "4": "একসাথে আমরাই Glow Fusion Formula!",
              "8": "DERMDOC Night Cream, ওভারনাইট ব্রাইটেনার!"},
 "784c77c5": {"2": "DERMDOC 2% Kojic Acid!",
              "5": "Kojic Acid, Niacinamide, Alpha Arbutin, স্পট কম দেখাতে হেল্প!"},
 "7ea55172": {"6": "4% Niacinamide, গ্লোতে হেল্প!",
              "7": "SPF 50 PA+++, রোদ সামলাবে!"},
 "89697c77": {"4": "3Xpert ফর্মুলা, ঘুমেও কাজ করে!",
              "9": "DERMDOC Kojic Night Cream। স্লিপ টু গ্লো!"},
 "906fbf3c": {"3": "3Xpert মানে তিন ব্রাইটেনিং অ্যাক্টিভ!",
              "8": "DERMDOC 2% Kojic Night Cream। স্লিপ টু গ্লো!"},
 "bd3b8af7": {"2": "আমি 2% Kojic Acid, টার্গেট ডার্ক স্পট, পিগমেন্টেশন।",
              "5": "রিচ ক্রিম। লাগাও, মিশুক, রোজ লাগাও। DERMDOC 2% Kojic Acid Night Cream।"},
 "c51221b6": {"2": "এবার সবাই তোর Sunscreen দেখবে!",
              "3": "ভুল Sunscreen, ভায়া!",
              "7": "গ্লো দেখো, Sunscreen নয়!"},
 "caf29456": {"6": "সাথে 4% Niacinamide, ন্যাচারাল টোন না বদলেই স্কিন আরও ব্রাইট আর ইভেন।",
              "7": "আর SPF 50 PA+++, ডে প্রোটেকশন কভার্ড।"},
 "cd5a6fe8": {"3": "Glow Fusion-এ Kojic Acid, Niacinamide, Alpha Arbutin।",
              "9": "DERMDOC Night Cream, ব্রাইটনিং!"},
 "ce849d3f": {},
 "dad2130b": {"1": "পার্পল Sunscreen? ভাবলাম পার্পল হয়ে যাব!",
              "5": "4% Niacinamide, SPF 50 PA+++!"},
 "e7e42eaf": {"3": "UVA আর UVB? ব্লকড!"},
 "f7ce58d4": {"6": "তিনটে টার্গেটেড ইনগ্রেডিয়েন্ট। একটা পাওয়ারফুল Night Cream।",
              "7": "DERMDOC 2% Kojic Acid Night Cream।"},
}
for vid, ov in OV.items():
    plan = json.loads((W/vid/"plan.json").read_text())
    lines = {}
    ids = set()
    for l in plan["lines"]:
        if l.get("keep_original") or not l.get("bn", "").strip(): continue
        lid = str(l["id"]); ids.add(lid)
        lines[lid] = ov.get(lid, l["bn"])
    assert set(ov) <= ids, (vid, set(ov) - ids)
    (W/vid/"captions_bn.json").write_text(json.dumps({"language": "bn", "lines": lines}, ensure_ascii=False, indent=1) + "\n")
print("written", len(OV))
