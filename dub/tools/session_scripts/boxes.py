import sys, json
from PIL import Image, ImageDraw
# boxes.py out.png img x0 y0 x1 y1 [x0 y0 x1 y1 ...]  draws boxes + 5% grid, crops to region of interest
out, img = sys.argv[1], sys.argv[2]; v = list(map(float, sys.argv[3:]))
im = Image.open(img).convert("RGB"); W, H = im.size; d = ImageDraw.Draw(im)
for i in range(1, 20):
    d.line([(i*W/20, 0), (i*W/20, H)], fill=(255,255,0) if i % 2 == 0 else (120,120,0), width=1)
    d.line([(0, i*H/20), (W, i*H/20)], fill=(255,255,0) if i % 2 == 0 else (120,120,0), width=1)
for k in range(0, len(v), 4):
    x0, y0, x1, y1 = v[k:k+4]
    d.rectangle([x0*W, y0*H, x1*W, y1*H], outline=(255,0,0), width=3)
im.resize((W*2//3, H*2//3)).save(out); print(out)
