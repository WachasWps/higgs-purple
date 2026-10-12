import sys, glob
from PIL import Image, ImageDraw
prefix, out = sys.argv[1], sys.argv[2]
per = int(sys.argv[3]) if len(sys.argv) > 3 else 4
files = sorted(glob.glob(f"/Users/wachas/Documents/higgs-purple/dub/post/preview/{prefix}_*.png"))
w, h = 540, 960
for k in range(0, len(files), per):
    chunk = files[k:k+per]
    im = Image.new("RGB", (w*len(chunk), h), "black")
    for i, f in enumerate(chunk):
        a = Image.open(f).convert("RGB").resize((w, h), Image.LANCZOS)
        d = ImageDraw.Draw(a); d.rectangle([w-150, h-30, w, h], fill="black"); d.text((w-145, h-25), f.split("_")[-1], fill="yellow")
        im.paste(a, (i*w, 0))
    im.save(f"{out}_{k//per}.png")
    print(f"{out}_{k//per}.png", [f.split('/')[-1] for f in chunk])
