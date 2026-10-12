# usage: fine.py CLIP "s-e,s-e,..." [step] [width] [suffix]
import subprocess, sys, os, io
from PIL import Image, ImageDraw, ImageFont
FF="/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
SRC="/Users/wachas/Documents/higgs-purple/dub/feedback/user_clips"
OUT="/Users/wachas/Documents/higgs-purple/dub/tools/catalog"
clip=sys.argv[1]; wins=sys.argv[2].split(",")
step=float(sys.argv[3]) if len(sys.argv)>3 else 0.1
W=int(sys.argv[4]) if len(sys.argv)>4 else 120
suffix=sys.argv[5] if len(sys.argv)>5 else "_f"
def grab(t):
    r=subprocess.run([FF,"-v","error","-ss",f"{t:.3f}","-i",f"{SRC}/{clip}.mp4","-frames:v","1","-vf",f"scale={W}:-2","-f","image2pipe","-vcodec","png","-"],capture_output=True)
    if not r.stdout: return None
    return Image.open(io.BytesIO(r.stdout)).convert("RGB")
rows=[]
font=ImageFont.load_default()
for w in wins:
    s,e=map(float,w.split("-"))
    t=s; ims=[]
    while t<=e+1e-6:
        im=grab(t)
        if im:
            d=ImageDraw.Draw(im); d.rectangle([0,0,34,11],fill=(0,0,0)); d.text((1,0),f"{t:.2f}",fill=(255,255,0),font=font)
            ims.append(im)
        t+=step
    if not ims: continue
    h=ims[0].height
    row=Image.new("RGB",(len(ims)*(W+2),h),(0,0,0))
    for i,im in enumerate(ims): row.paste(im,(i*(W+2),0))
    rows.append(row)
mw=max(r.width for r in rows); th=sum(r.height+3 for r in rows)
canvas=Image.new("RGB",(mw,th),(40,40,40)); y=0
for r in rows: canvas.paste(r,(0,y)); y+=r.height+3
canvas.save(f"{OUT}/{clip}{suffix}.jpg",quality=80)
print(clip,canvas.size)
