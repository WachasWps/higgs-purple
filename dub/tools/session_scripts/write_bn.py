import json, sys
from pathlib import Path
W = Path("/Users/wachas/Documents/higgs-purple/dub/work")
# overrides: id -> {line_id: caption}; all other lines copied verbatim from plan bn text
O = {
 "00b304b4": {"4": "UV রে আমি সামলাব!"},
 "02bad3b3": {
   "2": "রাতে DERMDOC 2% Kojic Acid Night Cream।",
   "3": "এতে Kojic, Niacinamide আর Alpha Arbutin।",
   "6": "Glow Fusion Formula রাতভর কাজ করে।"},
 "23850d94": {"6": "DERMDOC KNC Night Cream। নাইট ক্লাস ছুটি!"},
 "291827ba": {"3": "প্রমাণ নম্বর এক, UVA আর UVB প্রোটেকশন!"},
 "33c29291": {
   "1": "এই Sunscreen পাড়াসুদ্ধ সবাইকে দেখাবো!",
   "2": "ভুল শেড। ভুল Sunscreen।",
   "5": "4% Niacinamide ব্রাইট করতে হেল্প করে।",
   "6": "আর SPF 50 PA+++ দেয় প্রোটেকশন!"},
 "390113f1": {},
 "3d01d9fc": {
   "1": "জানলার আলোয় বুঝলাম Sunscreen কী নেই।",
   "6": "4% Niacinamide ব্রাইট, ইভেন ফিনিশ।",
   "7": "SPF 50 PA+++, এটাই আমার গ্লো!"},
 "46d965c9": {
   "2": "তাই নাইট রিসেট শুরু এই Night Cream-এ।",
   "3": "DERMDOC 2% Kojic Acid!",
   "6": "Glow Fusion তিনটে ব্রাইটনিং অ্যাক্টিভ।"},
 "51440b1f": {
   "6": "ইন্ডিয়ান স্কিনের জন্য, 4% Niacinamide ব্রাইট ফিনিশ।",
   "7": "আর SPF 50 PA+++, রোজকার প্রোটেকশন, ঠিক যেটা দরকার।"},
 "595689d8": {
   "3": "আমার 3Xpert ফর্মুলা, অন!",
   "4": "Kojic Acid ডার্ক স্পটের লুক টার্গেট করে।",
   "5": "Niacinamide, ইভেন!",
   "6": "আর Alpha Arbutin-ও ব্রাইটেনিং টিমে!"},
 "5fd50ab8": {"2": "রিল্যাক্স। পার্পল টিন্ট, SPF 50 PA+++, আর 4% Niacinamide।"},
 "655a1328": {
   "5": "4% Niacinamide ব্রাইট হতে হেল্প করে।",
   "6": "SPF 50 PA+++ প্রোটেক্ট করে!"},
 "65a0c520": {
   "7": "4% Niacinamide।",
   "8": "আর SPF 50 PA+++।"},
 "715b1b5c": {
   "2": "Glow Fusion নাইট প্যাট্রোল, হাজির!",
   "3": "Kojic Acid, টার্গেট ডার্ক স্পট!",
   "4": "Niacinamide, ব্রাইট ইভন টোনে সাপোর্ট!",
   "5": "Alpha Arbutin, ব্রাইটেনিং টিমে এসো!",
   "9": "DERMDOC Glow Fusion, ওভারনাইট ব্রাইটেনার!"},
}
for vid, ov in O.items():
    plan = json.loads((W/vid/"plan.json").read_text())
    lines = {}
    for l in plan["lines"]:
        if l.get("keep_original") or not l.get("bn", "").strip():
            continue
        lid = str(l["id"])
        lines[lid] = ov.get(lid, l["bn"].strip())
    assert set(ov) <= set(lines), (vid, set(ov) - set(lines))
    (W/vid/"captions_bn.json").write_text(json.dumps({"language": "bn", "lines": lines}, ensure_ascii=False, indent=1) + "\n")
print("written", len(O))
