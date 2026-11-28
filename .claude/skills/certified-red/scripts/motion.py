"""Camera motion per second of a clip: mean flow (x,y px/frame at 640 wide) and jitter.

usage: python3 motion.py <clip> [...]
Use only stretches with jitter under ~0.3 and no sideways (x) drift for aerials.
"""
import cv2, sys, numpy as np
# per-second global motion (px/frame at 640w) and jerk (frame-to-frame change in motion) for a clip
for path in sys.argv[1:]:
    cap=cv2.VideoCapture(path); prev=None; mv=[]
    while True:
        ok,f=cap.read()
        if not ok: break
        g=cv2.cvtColor(cv2.resize(f,(640,360)),cv2.COLOR_BGR2GRAY)
        if prev is not None:
            p0=cv2.goodFeaturesToTrack(prev,200,0.01,12)
            if p0 is not None:
                p1,st,_=cv2.calcOpticalFlowPyrLK(prev,g,p0,None)
                d=(p1-p0)[st.ravel()==1].reshape(-1,2)
                mv.append(np.median(d,axis=0) if len(d) else [0,0])
            else: mv.append([0,0])
        prev=g
    mv=np.array(mv); jerk=np.abs(np.diff(mv,axis=0)).sum(axis=1)
    print("==",path.split('/')[-1], len(mv)+1,"frames")
    out=[]
    for s in range(0,len(mv)//30):
        m=mv[s*30:(s+1)*30]; j=jerk[s*30:(s+1)*30-1]
        out.append(f"{s:02d}:{m[:,0].mean():+.1f},{m[:,1].mean():+.1f}|{j.mean():.2f}")
    for i in range(0,len(out),8): print("  "+"  ".join(out[i:i+8]))
