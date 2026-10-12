import cv2,numpy as np,sys
def hp(g): g=g.astype(np.float32); return g-cv2.GaussianBlur(g,(0,0),3)
c=cv2.VideoCapture('work/d6c1e78e/source_fixed.pregrok.mp4')
fr=[]; i=0
while i<=int(19.2*30): ok,f=c.read(); fr.append(f) if i in (int(13.5*30),int(19.2*30)) else None; i+=1
T=[hp(cv2.cvtColor(fr[0],cv2.COLOR_BGR2GRAY))[1866:1898,972:1062], hp(cv2.cvtColor(fr[1],cv2.COLOR_BGR2GRAY))[1883:1913,972:1062]]
for id in sys.argv[1:]:
    c=cv2.VideoCapture(f'work/{id}/source_fixed.mp4'); i=0; hits=[]
    while True:
        ok,f=c.read()
        if not ok: break
        t=i/30
        if t>9:
            R=hp(cv2.cvtColor(f[1830:1920,920:1080],cv2.COLOR_BGR2GRAY))
            best=(0,None)
            for k,tm in enumerate(T):
                m=cv2.matchTemplate(R,tm,cv2.TM_CCOEFF_NORMED); _,v,_,loc=cv2.minMaxLoc(m)
                if v>best[0]: best=(v,(k,loc[0]+920,loc[1]+1830))
            if best[0]>0.45: hits.append((round(t,2),round(best[0],2),best[1]))
        i+=1
    # summarize runs
    runs=[];
    for h in hits:
        if runs and h[0]-runs[-1][1]<0.1: runs[-1][1]=h[0]; runs[-1][2].append(h)
        else: runs.append([h[0],h[0],[h]])
    for a,b,hs in runs: print(id,a,b,len(hs),'min',min(x[1] for x in hs),'locs',sorted(set(x[2] for x in hs))[:4])
