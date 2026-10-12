import cv2,numpy as np,sys,shutil,subprocess
from pathlib import Path
FF="/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
def hp(g): g=g.astype(np.float32); return g-cv2.GaussianBlur(g,(0,0),3)
# region (x0,y0,x1,y1) per shot kind
REG={'cap':(956,1850,1078,1912),'tube':(956,1868,1078,1920)}
JOBS={'d6c1e78e':[('cap',12.767,14.967),('tube',18.367,20.667)],
      'b876bd3c':[('cap',18.367,20.567),('tube',26.933,29.233)],
      'a135c7dc':[('cap',20.333,22.533)],'010ea465':[('cap',21.933,24.133)]}
def read_frames(p,a,b):
    c=cv2.VideoCapture(str(p)); i=0; out=[]
    while True:
        ok,f=c.read()
        if not ok or i/30>b: break
        if i/30>=a: out.append(f)
        i+=1
    return out
# static masks from d6c1e78e averaged high-pass (watermark static, content moves)
src0=Path('work/d6c1e78e/source_fixed.pregrok.mp4')
if not src0.exists(): src0=Path('work/d6c1e78e/source_fixed.mp4')
MASK={}
for k,(a,b) in {'cap':(12.8,14.9),'tube':(19.5,20.6)}.items():
    x0,y0,x1,y1=REG[k]; fs=read_frames(src0,a,b)
    acc=np.mean([hp(cv2.cvtColor(f[y0:y1,x0:x1],cv2.COLOR_BGR2GRAY)) for f in fs],0)
    m=(np.abs(acc)>2.5).astype(np.uint8)
    m[:,:8]=0;m[:,-8:]=0;m[:6]=0
    n,lab,st,_=cv2.connectedComponentsWithStats(m)
    keep=np.zeros_like(m)
    for j in range(1,n):
        if st[j,4]>=6: keep[lab==j]=1
    m=cv2.dilate(keep,np.ones((7,7),np.uint8))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
    if k=='tube': m[:15]=0
    MASK[k]=m; cv2.imwrite(f'{sys.argv[1]}/mask_{k}.png',m*255)
    ys,xs=np.where(m); print(k,'mask bbox',xs.min()+x0,ys.min()+y0,xs.max()+x0,ys.max()+y0)
rng=np.random.default_rng(0)
for vid in sys.argv[2:]:
    wd=Path('work')/vid; bk=wd/'source_fixed.pregrok.mp4'
    if not bk.exists(): shutil.copy(wd/'source_fixed.mp4',bk)
    cap=cv2.VideoCapture(str(bk)); fps=cap.get(5); W,H=int(cap.get(3)),int(cap.get(4))
    tmp=wd/'source_fixed.tmp.mp4'
    p=subprocess.Popen([FF,"-v","error","-y","-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",f"{fps}","-i","-","-i",str(bk),
        "-map","0:v","-map","1:a?","-c:v","libx264","-crf","15","-pix_fmt","yuv420p","-c:a","copy","-shortest",str(tmp)],stdin=subprocess.PIPE)
    i=0;n=0
    while True:
        ok,f=cap.read()
        if not ok: break
        t=i/fps
        for k,a,b in JOBS[vid]:
            if a-1/fps-1e-3<=t<=b+1e-3:
                x0,y0,x1,y1=REG[k]; roi=f[y0:y1,x0:x1].copy(); m=MASK[k]
                if k=='tube':
                    g=cv2.cvtColor(roi,cv2.COLOR_BGR2GRAY).astype(np.float32)
                    w=((m==0)&(g>np.percentile(g[m==0],50)-20)).astype(np.float32)
                    num=cv2.GaussianBlur(roi.astype(np.float32)*w[...,None],(0,0),9); den=cv2.GaussianBlur(w,(0,0),9)[...,None]
                    fill=num/np.maximum(den,1e-3)
                else:
                    fill=cv2.inpaint(roi,m,7,cv2.INPAINT_TELEA)
                    fill=cv2.GaussianBlur(fill,(0,0),3).astype(np.float32)
                h=roi.astype(np.float32)-cv2.GaussianBlur(roi,(0,0),1.5).astype(np.float32)
                sd=float(h[m==0].std())
                fill+=rng.normal(0,sd*(0.45 if k=='tube' else 0.8),fill.shape[:2])[...,None]
                al=cv2.GaussianBlur(m.astype(np.float32),(0,0),2.5)[...,None]; al=np.clip(al*1.3,0,1)
                f[y0:y1,x0:x1]=np.clip(roi*(1-al)+fill*al,0,255).astype(np.uint8); n+=1
        p.stdin.write(f.tobytes()); i+=1
    p.stdin.close(); p.wait()
    tmp.replace(wd/'source_fixed.mp4'); print(vid,'patched frames',n,'of',i)
