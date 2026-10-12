import subprocess, io, sys
from PIL import Image, ImageDraw
FF="/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
S="/Users/wachas/Documents/higgs-purple/dub/feedback/user_clips"
# args: out W "clip@t[@crop x,y,w,h as fractions]" ...
out=sys.argv[1]; W=int(sys.argv[2]); tiles=[]
for spec in sys.argv[3:]:
    p=spec.split("@"); c=p[0]; t=float(p[1])
    vf=f"scale={W}:-2"
    if len(p)>2:
        x,y,w,h=map(float,p[2].split(","))
        vf=f"crop=iw*{w}:ih*{h}:iw*{x}:ih*{y},scale={W}:-2"
    r=subprocess.run([FF,"-v","error","-ss",str(t),"-i",f"{S}/{c}.mp4","-frames:v","1","-vf",vf,"-f","image2pipe","-vcodec","png","-"],capture_output=True)
    im=Image.open(io.BytesIO(r.stdout)).convert("RGB")
    d=ImageDraw.Draw(im); d.rectangle([0,0,70,11],fill=(0,0,0)); d.text((1,0),f"{c}@{t}",fill=(255,255,0))
    tiles.append(im)
H=max(t.height for t in tiles); can=Image.new("RGB",(sum(t.width+3 for t in tiles),H),(40,40,40)); x=0
for t in tiles: can.paste(t,(x,0)); x+=t.width+3
can.save(out,quality=85); print(can.size)
