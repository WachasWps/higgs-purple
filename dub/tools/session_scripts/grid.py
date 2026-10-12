import sys
from PIL import Image, ImageDraw, ImageFont
# grid.py out.png x0 y0 x1 y1 step img1 [img2...]: crop region, draw labelled grid every `step` (fractions), side-by-side
out = sys.argv[1]; x0, y0, x1, y1, st = map(float, sys.argv[2:7]); files = sys.argv[7:]
f = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 16)
tiles = []
for fn in files:
    im = Image.open(fn).convert("RGB"); W, H = im.size
    c = im.crop((int(x0*W), int(y0*H), int(x1*W), int(y1*H))); d = ImageDraw.Draw(c)
    k = 0
    v = round(x0 / st) * st
    while v <= x1 + 1e-9:
        px = (v - x0) * W
        if px >= 0:
            d.line([(px, 0), (px, c.height)], fill=(255, 255, 0), width=1); d.text((px + 2, 2), f"{v:.3f}", fill=(255, 255, 0), font=f)
        v += st
    v = round(y0 / st) * st
    while v <= y1 + 1e-9:
        py = (v - y0) * H
        if py >= 0:
            d.line([(0, py), (c.width, py)], fill=(0, 255, 255), width=1); d.text((2, py + 2), f"{v:.3f}", fill=(0, 255, 255), font=f)
        v += st
    tiles.append(c)
w = sum(t.width for t in tiles) + 6 * (len(tiles) - 1); h = max(t.height for t in tiles)
s = Image.new("RGB", (w, h), "red"); x = 0
for t in tiles:
    s.paste(t, (x, 0)); x += t.width + 6
if s.width > 2000:
    s = s.resize((2000, int(s.height * 2000 / s.width)))
s.save(out); print(out, s.size)
