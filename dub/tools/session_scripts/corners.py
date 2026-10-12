import subprocess, io
from PIL import Image, ImageDraw
FF="/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"; FP="/opt/homebrew/opt/ffmpeg-full/bin/ffprobe"
S="/Users/wachas/Documents/higgs-purple/dub/feedback/user_clips"
tiles=[]
for i in range(1,32):
    c=f"U{i:02d}"
    d=float(subprocess.check_output([FP,"-v","error","-show_entries","format=duration","-of","csv=p=0",f"{S}/{c}.mp4"]).decode())
    # bottom-right 22% x 12% region scaled to 140 wide
    r=subprocess.run([FF,"-v","error","-ss",f"{d*0.45:.2f}","-i",f"{S}/{c}.mp4","-frames:v","1","-vf","crop=iw*0.25:ih*0.1:iw*0.75:ih*0.9,scale=140:-2","-f","image2pipe","-vcodec","png","-"],capture_output=True)
    im=Image.open(io.BytesIO(r.stdout)).convert("RGB")
    ImageDraw.Draw(im).text((2,1),c,fill=(255,0,0))
    tiles.append(im)
cols=8; w=142; h=max(t.height for t in tiles)+2
rows=(len(tiles)+cols-1)//cols
can=Image.new("RGB",(cols*w,rows*h),(0,0,0))
for k,t in enumerate(tiles): can.paste(t,((k%cols)*w,(k//cols)*h))
can.save("catalog/corners.jpg",quality=85)
