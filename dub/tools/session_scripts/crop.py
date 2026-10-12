import sys
from PIL import Image
# crop.py out.png x0 y0 x1 y1 file1 file2 ...  (fractions) -> side by side
out = sys.argv[1]; x0, y0, x1, y1 = map(float, sys.argv[2:6]); files = sys.argv[6:]
ims = []
for f in files:
    im = Image.open(f).convert("RGB"); W, H = im.size
    ims.append(im.crop((int(x0*W), int(y0*H), int(x1*W), int(y1*H))))
w = sum(i.width for i in ims) + 8*(len(ims)-1); h = max(i.height for i in ims)
s = Image.new("RGB", (w, h), "red"); x = 0
for i in ims:
    s.paste(i, (x, 0)); x += i.width + 8
if s.width > 2000:
    s = s.resize((2000, int(s.height * 2000 / s.width)))
s.save(out); print(out, s.size)
