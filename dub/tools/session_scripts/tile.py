import sys, glob
from PIL import Image, ImageDraw, ImageFont
vid, lang = sys.argv[1], sys.argv[2]
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 4
tw = int(sys.argv[4]) if len(sys.argv) > 4 else 450
files = sorted(glob.glob(f"/Users/wachas/Documents/higgs-purple/dub/post/preview/{vid}_{lang}_*.png"))
th = int(tw * 16 / 9)
rows = (len(files) + cols - 1) // cols
sheet = Image.new("RGB", (cols * tw, rows * th), "black")
d = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 28)
except Exception:
    font = None
for i, f in enumerate(files):
    im = Image.open(f).convert("RGB").resize((tw, th), Image.LANCZOS)
    x, y = (i % cols) * tw, (i // cols) * th
    sheet.paste(im, (x, y))
    t = f.rsplit("_", 1)[1].replace(".png", "")
    d.rectangle([x, y + th - 40, x + 110, y + th], fill="red")
    d.text((x + 6, y + th - 36), t, fill="white", font=font)
out = f"/Users/wachas/Documents/higgs-purple/dub/tools/{vid}_{lang}_sheet.png"
sheet.save(out)
print(out, len(files))
