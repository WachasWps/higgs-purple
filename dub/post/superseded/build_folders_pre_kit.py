"""Build Final_Deliverables/ from deliver_music/ (copies; originals stay).

Final_Deliverables/<Category>/<Product>/<Language>/<file>.mp4   (AI_General_Ads: <Product>/<file>_English.mp4)
General Ads ship in ENGLISH ONLY (client decision 2026-10-09): their Indic dubs and the old Hinglish cuts are skipped.
"""
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "deliver_music"
OUT = ROOT / "Final_Deliverables"
CAT = {"personification": "1_Ingredient_Personified", "product_avatar": "2_Product_Avatar", "ugc": "3_UGC_Ads",
       "product_ad": "4_AI_General_Ads"}
PROD = {"uv_sunscreen": "Purple_Sunscreen_PS", "kojic_night_cream": "KNC"}
SHORT = {"uv_sunscreen": "PS", "kojic_night_cream": "KNC"}
LANG = {"Bengali": "Bengali_WB", "Tamil": "Tamil_TN", "Telugu": "Telugu_APTS", "Malayalam": "Malayalam_KL", "Odia": "Odia_Od"}


TITLE_FIX = {"a5c00002": "forgot-your-night-skincare", "ce849d3f": "personification-no-more-greasy-sunscreen"}   # slug was just "ugc"


def clean(s):
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    n, per = 0, {}
    for f in sorted(SRC.glob("*/*.mp4")):
        lang_dir, vid = f.parent.name, f.stem.split("_")[-1]
        meta = json.loads((ROOT / "work" / vid / "meta.json").read_text())
        g = json.loads((ROOT / "work" / vid / "graphics.json").read_text())
        prod = g["product"]
        title = clean(re.sub(r"^\d+_(?:PS_|KNC_)?(?:kojic-night-cream_|uv-sunscreen_|dermdoc_)?", "", f.stem[: -len(vid) - 1]))
        if lang_dir == "Hinglish_Ads":   # old cut, superseded by the rebuilt English ad
            continue
        if lang_dir == "English":
            title = clean(re.sub(r"^(?:product[-_]ad[-_]?)+", "", title, flags=re.I)) or vid
            dst = OUT / "4_AI_General_Ads" / PROD[prod] / f"{SHORT[prod]}_General-Ad_{title}_English.mp4"
        else:
            plan = json.loads((ROOT / "work" / vid / "plan.json").read_text())
            if plan["style"] == "product_ad":   # general ads: English only
                continue
            cat = CAT[plan["style"]]
            style_name = {"1_Ingredient_Personified": "Ingredient-Personified", "2_Product_Avatar": "Product-Avatar", "3_UGC_Ads": "UGC",
                          "4_AI_General_Ads": "General-Ad"}[cat]
            title = clean(re.sub(r"^(?:kojic-night-cream|uv-sunscreen|dermdoc)[-_]?(?:personification|product[-_]avatar|ugc|product[-_]ad)?[-_]?", "", title, flags=re.I)) or vid
            title = TITLE_FIX.get(vid, title)
            dst = OUT / cat / PROD[prod] / LANG[lang_dir] / f"{SHORT[prod]}_{style_name}_{title}_{lang_dir}.mp4"
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():  # same title twice in a folder: disambiguate with the id
            dst = dst.with_name(dst.stem + f"_{vid}.mp4")
        shutil.copy2(f, dst)
        per[dst.parent.relative_to(OUT)] = per.get(dst.parent.relative_to(OUT), 0) + 1
        n += 1
    for k in sorted(per):
        print(f"{per[k]:3d}  {k}")
    print(f"TOTAL {n} files -> {OUT}")


if __name__ == "__main__":
    main()
