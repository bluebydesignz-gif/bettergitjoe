"""Track and blur small regions (license plates) in a rendered segment.

usage: python3 track_blur.py seg.mp4 frame:cx:cy:w:h [frame:cx:cy:w:h ...]
Each box is given on one reference frame (output pixels) and tracked forward and
backward with template matching. Tracking stops when the match gets weak
(the plate left the frame or was covered).
"""
import sys, subprocess, cv2, numpy as np

def track(frames, f0, cx, cy, w, h, thr=0.5):
    H, W = frames[0].shape[:2]
    pos = {}
    def clampbox(cx, cy):
        x0 = int(round(cx - w / 2)); y0 = int(round(cy - h / 2))
        return max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    x0, y0, x1, y1 = clampbox(cx, cy)
    tmpl0 = frames[f0][y0:y1, x0:x1].copy()
    pos[f0] = (cx, cy)
    for step in (1, -1):
        tmpl = tmpl0.copy(); c = (cx, cy); i = f0 + step
        while 0 <= i < len(frames):
            R = 70
            sx0 = int(max(0, c[0] - w / 2 - R)); sy0 = int(max(0, c[1] - h / 2 - R))
            sx1 = int(min(W, c[0] + w / 2 + R)); sy1 = int(min(H, c[1] + h / 2 + R))
            win = frames[i][sy0:sy1, sx0:sx1]
            if win.shape[0] < tmpl.shape[0] or win.shape[1] < tmpl.shape[1]: break
            res = cv2.matchTemplate(win, tmpl, cv2.TM_CCOEFF_NORMED)
            _, score, _, loc = cv2.minMaxLoc(res)
            if score < thr: break
            c = (sx0 + loc[0] + tmpl.shape[1] / 2, sy0 + loc[1] + tmpl.shape[0] / 2)
            pos[i] = c
            bx0, by0, bx1, by1 = clampbox(*c)
            new = frames[i][by0:by1, bx0:bx1]
            if new.shape == tmpl.shape:
                tmpl = cv2.addWeighted(tmpl, 0.7, new, 0.3, 0)
            if bx0 <= 0 or bx1 >= W: break   # sliding out of frame
            i += step
    return pos

if __name__ == "__main__":
    path = sys.argv[1]
    cap = cv2.VideoCapture(path); fps = cap.get(cv2.CAP_PROP_FPS)
    frames = []
    while True:
        ok, f = cap.read()
        if not ok: break
        frames.append(f)
    gray = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in frames]
    H, W = frames[0].shape[:2]
    for spec in sys.argv[2:]:
        f0, cx, cy, w, h = [int(float(v)) for v in spec.split(":")]
        pos = track(gray, f0, cx, cy, w, h)
        ks = sorted(pos)
        # hold the blur a few frames past where tracking stopped
        for extra in range(1, 7):
            for k, d in ((ks[0], -extra), (ks[-1], extra)):
                if 0 <= k + d < len(frames) and (k + d) not in pos: pos[k + d] = pos[k]
        print(f"{spec}: tracked frames {ks[0]}..{ks[-1]} of {len(frames)}", flush=True)
        for i, (px, py) in pos.items():
            bw, bh = int(w * 1.25), int(h * 1.35)
            x0 = max(0, int(px - bw / 2)); y0 = max(0, int(py - bh / 2)); x1 = min(W, x0 + bw); y1 = min(H, y0 + bh)
            if x1 - x0 < 4 or y1 - y0 < 4: continue
            roi = frames[i][y0:y1, x0:x1]
            k = max(15, (min(bw, bh) // 2) * 2 + 1)
            blur = cv2.GaussianBlur(roi, (k, k), 0)
            blur = cv2.GaussianBlur(cv2.resize(cv2.resize(blur, (8, 5)), (x1 - x0, y1 - y0)), (k, k), 0)
            mask = np.zeros((y1 - y0, x1 - x0), np.float32)
            cv2.ellipse(mask, ((x1 - x0) // 2, (y1 - y0) // 2), ((x1 - x0) // 2 - 2, (y1 - y0) // 2 - 2), 0, 0, 360, 1, -1)
            mask = cv2.GaussianBlur(mask, (15, 15), 0)[..., None]
            frames[i][y0:y1, x0:x1] = (roi * (1 - mask) + blur * mask).astype(np.uint8)
    out = path.replace(".mp4", "_b.mp4")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(fps),
        "-i", "-", "-c:v", "libx264", "-preset", "fast", "-crf", "13", "-g", "15", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out],
        stdin=subprocess.PIPE)
    for f in frames: p.stdin.write(f.tobytes())
    p.stdin.close(); p.wait()
    print("wrote", out)
