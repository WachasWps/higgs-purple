import cv2,numpy as np,sys
def hp(g): g=g.astype(np.float32); return g-cv2.GaussianBlur(g,(0,0),3)
def frame(id,t):
    c=cv2.VideoCapture(f'work/{id}/source_fixed.mp4'); c.set(cv2.CAP_PROP_POS_MSEC,t*1000); return c.read()[1]
f=frame('d6c1e78e',13.5); g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
# locate tight box: high-pass energy in region
r=np.abs(hp(g[1840:1920,940:1080]))
ys,xs=np.where(r>12); print('cap box',xs.min()+940,ys.min()+1840,xs.max()+940,ys.max()+1840)
f2=frame('d6c1e78e',19.2); g2=cv2.cvtColor(f2,cv2.COLOR_BGR2GRAY)
r=np.abs(hp(g2[1860:1920,900:1080])); ys,xs=np.where(r>12); print('tube box',xs.min()+900,ys.min()+1860,xs.max()+900,ys.max()+1860)
