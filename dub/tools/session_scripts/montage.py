import sys
from PIL import Image, ImageDraw, ImageFont
out = sys.argv[1]; files = sys.argv[2:]
tw, th = 432, 768
cols = min(4, len(files)); rows = (len(files)+cols-1)//cols
M = Image.new("RGB", (cols*tw + (cols-1)*6, rows*th + (rows-1)*6), (255,0,255))
d = ImageDraw.Draw(M)
for i, f in enumerate(files):
    im = Image.open(f).convert("RGB").resize((tw, th), Image.LANCZOS)
    x, y = (i%cols)*(tw+6), (i//cols)*(th+6)
    M.paste(im, (x, y))
    lab = f.rsplit("_",1)[-1].replace(".png","")
    d.rectangle([x, y+th-30, x+90, y+th], fill=(255,0,0)); d.text((x+4, y+th-26), lab, fill=(255,255,255))
M.save(out)
print(out, M.size)
