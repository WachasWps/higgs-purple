import sys, subprocess
from PIL import Image, ImageDraw
vid = sys.argv[1]; ts = [float(t) for t in sys.argv[2:]]
src = f"/Users/wachas/Documents/higgs-purple/dub/work/{vid}/source.mp4"
FF = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
d = "/Users/wachas/Documents/higgs-purple/dub/tools/fr"
ims = []
for t in ts:
    out = f"{d}/{vid}_{t:.2f}.png"
    subprocess.run(["nice", "-n", "10", FF, "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{t}", "-i", src, "-frames:v", "1", "-vf", "scale=270:480", out], check=True)
    ims.append((t, Image.open(out).convert("RGB")))
cols = min(len(ims), 8)
rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (cols * 270, rows * 480))
dr = ImageDraw.Draw(sheet)
for i, (t, im) in enumerate(ims):
    x, y = (i % cols) * 270, (i // cols) * 480
    sheet.paste(im, (x, y))
    dr.rectangle([x, y + 455, x + 60, y + 480], fill="red"); dr.text((x + 4, y + 460), f"{t:.2f}", fill="white")
sheet.save(f"{d}/{vid}_src_sheet.png"); print(f"{d}/{vid}_src_sheet.png")
