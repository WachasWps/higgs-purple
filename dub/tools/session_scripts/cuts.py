import cv2,numpy as np,sys
for id in sys.argv[1:]:
    c=cv2.VideoCapture(f'work/{id}/source_fixed.mp4'); fps=c.get(5); c.set(cv2.CAP_PROP_POS_MSEC,10000)
    prev=None; cuts=[]; i=int(round(10*fps))
    while True:
        ok,f=c.read()
        if not ok or i/fps>31: break
        s=cv2.resize(f,(90,160)).astype(np.float32)
        if prev is not None and np.abs(s-prev).mean()>25: cuts.append(round(i/fps,3))
        prev=s; i+=1
    print(id,fps,cuts)
