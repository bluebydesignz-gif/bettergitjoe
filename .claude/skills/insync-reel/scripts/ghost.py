"""Make the person in a shot see-through, like a ghost, over a rebuilt background.

usage: python3 ghost.py <in.mp4> <out.mp4> [--alpha 0.42] [--fade START END] [--tint 0.18]
  in.mp4   a built shot (1080x1920, no audio) from build_segments.py
  --alpha  how solid the person stays (0 = invisible, 1 = normal)
  --fade   seconds in this shot where the person goes from solid to --alpha (e.g. on the word "transparent");
           without it the person is see-through from the first frame
  --tint   cool cobalt cast on the person (0 to 1)

How: rembg (u2net_human_seg) finds the person each frame. The background behind them is rebuilt
row by row from the pixels either side (works on plain walls and pavement), smoothed vertically,
then the person is laid back over it at --alpha with a soft cobalt edge glow. Works best on a plain
background; busy backgrounds will show smearing where the person stood.
"""
import argparse, subprocess, sys
import numpy as np, cv2
from rembg import new_session, remove

ap = argparse.ArgumentParser()
ap.add_argument("inp"); ap.add_argument("out")
ap.add_argument("--alpha", type=float, default=0.42)
ap.add_argument("--fade", type=float, nargs=2)
ap.add_argument("--tint", type=float, default=0.18)
ap.add_argument("--frames", type=int, default=0, help="debug: stop after N frames")
a = ap.parse_args()

W, H, FPS = 1080, 1920, 30
sess = new_session("u2net_human_seg")
COBALT = np.array([222, 107, 20], np.float32)          # BGR of #146BDE
GLOW = np.array([255, 205, 150], np.float32)           # pale blue edge light (BGR)

def person_mask(img):
    small = cv2.resize(img, (W // 2, H // 2), interpolation=cv2.INTER_AREA)
    m = remove(cv2.cvtColor(small, cv2.COLOR_BGR2RGB), session=sess, only_mask=True)
    m = np.asarray(m, np.float32) / 255.0
    return cv2.resize(m, (W, H), interpolation=cv2.INTER_LINEAR)

def fill_rows(img, hole):
    """Linear fill of each masked run in each row from its left and right neighbours."""
    h, w = hole.shape
    idx = np.arange(w)[None, :].repeat(h, 0)
    valid = ~hole
    left = np.where(valid, idx, -1); left = np.maximum.accumulate(left, axis=1)
    right = np.where(valid, idx, w); right = np.minimum.accumulate(right[:, ::-1], axis=1)[:, ::-1]
    left_c = np.clip(left, 0, w - 1); right_c = np.clip(right, 0, w - 1)
    rows = np.arange(h)[:, None]
    L = img[rows, left_c].astype(np.float32); R = img[rows, right_c].astype(np.float32)
    L = np.where((left < 0)[..., None], R, L); R = np.where((right >= w)[..., None], L, R)
    span = np.maximum(right - left, 1).astype(np.float32)
    t = ((idx - left) / span).clip(0, 1)[..., None]
    fill = L * (1 - t) + R * t
    out = img.astype(np.float32).copy(); out[hole] = fill[hole]
    return out

dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", a.inp, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                       stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                        "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "fast", "-crf", "13", "-g", "15",
                        "-pix_fmt", "yuv420p", "-movflags", "+faststart", a.out], stdin=subprocess.PIPE)
prev = None; n = 0; rng = np.random.default_rng(7)
while True:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    img = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    m = person_mask(img)
    m = m if prev is None else 0.55 * m + 0.45 * prev                 # calm frame-to-frame flicker
    prev = m
    hole = cv2.dilate((m > 0.08).astype(np.uint8), np.ones((31, 31), np.uint8)) > 0
    bg = fill_rows(img, hole)
    sm = cv2.blur(bg, (9, 61))                                        # tall blur hides row streaks, keeps wall seams
    bg = np.where(hole[..., None], sm, bg)
    bg[hole] += rng.normal(0, 2.2, (int(hole.sum()), 1)).astype(np.float32)   # match the footage grain
    t = n / FPS
    if a.fade:
        k = np.clip((t - a.fade[0]) / max(a.fade[1] - a.fade[0], 1e-3), 0, 1)
        k = k * k * (3 - 2 * k)
        alpha = 1 - (1 - a.alpha) * k
    else:
        alpha, k = a.alpha, 1.0
    alpha += 0.035 * k * np.sin(2 * np.pi * 0.45 * t)                # slow breathe once see-through
    soft = cv2.GaussianBlur(m, (0, 0), 3)
    fg = img.astype(np.float32)
    fg = fg * (1 - a.tint * k) + (fg.mean(axis=2, keepdims=True) * 0.55 + COBALT * 0.45) * (a.tint * k)
    edge = np.clip(cv2.GaussianBlur(soft, (0, 0), 10) - soft * 0.9, 0, 1) * k
    out = bg * (1 - alpha * soft[..., None]) + fg * (alpha * soft[..., None]) + GLOW * (edge[..., None] * 0.38)
    enc.stdin.write(np.clip(out, 0, 255).astype(np.uint8).tobytes())
    n += 1
    if a.frames and n >= a.frames: break
enc.stdin.close(); enc.wait(); dec.terminate()
print(f"ghost: {n} frames -> {a.out}")
