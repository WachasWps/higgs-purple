"""Usage: tiles.py <id> <k1,k2,...>  -> zoomed tiles with y-grid lines (0.12 .. 0.88) into scratchpad."""
import sys
from PIL import Image, ImageDraw
vid, ks = sys.argv[1], [int(k) for k in sys.argv[2].split(",")]
SP = "/Users/wachas/Documents/higgs-purple/dub/tools"
sh = Image.open(f"/Users/wachas/Documents/higgs-purple/dub/post/sheets/{vid}.png").convert("RGB")
tw, th = sh.width // 5, sh.height // 4
S = 1.6
out = Image.new("RGB", (int(tw * S) * len(ks) + 6 * len(ks), int(th * S)), "black")
for i, k in enumerate(ks):
    t = sh.crop(((k % 5) * tw, (k // 5) * th, (k % 5 + 1) * tw, (k // 5 + 1) * th)).resize((int(tw * S), int(th * S)))
    d = ImageDraw.Draw(t)
    for y in (0.12, 0.16, 0.30, 0.50, 0.68, 0.88):
        yy = int(y * t.height)
        d.line([(0, yy), (t.width, yy)], fill=(255, 0, 0) if y in (0.12, 0.88) else (0, 255, 0), width=1)
        d.text((2, yy - 11), f"{y}", fill=(255, 255, 0))
    d.text((4, 4), f"t={k}", fill=(255, 255, 0))
    out.paste(t, (i * (int(tw * S) + 6), 0))
out.save(f"{SP}/{vid}_t{'-'.join(map(str, ks))}.png")
print(f"{SP}/{vid}_t{'-'.join(map(str, ks))}.png")
