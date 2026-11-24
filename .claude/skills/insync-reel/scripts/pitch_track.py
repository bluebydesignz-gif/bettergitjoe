"""Voice pitch and level every 0.1 s, to tell speakers apart (e.g. the person filming).

usage: python3 pitch_track.py <clip.wav 16 kHz mono> <start_s> <end_s>
Prints t:pitchHz/levelDb. The filmer is usually louder (mic is on the phone) and has a
different pitch from the people on camera; check every line you plan to keep.
"""
import sys, wave
import numpy as np

path, a, b = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]); sr = 16000
w = wave.open(path); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
out = []; t = a
while t < b:
    seg = x[int(t * sr):int((t + 0.1) * sr)]; ps = []
    for i in range(0, len(seg) - 640 + 1, 160):
        fr = seg[i:i + 640] * np.hanning(640)
        ac = np.correlate(fr, fr, 'full')[639:]; ac /= ac[0] + 1e-9
        lo, hi = sr // 400, sr // 70; k = lo + np.argmax(ac[lo:hi])
        if ac[k] > 0.45: ps.append(sr / k)
    db = 20 * np.log10(np.sqrt((seg ** 2).mean()) + 1e-9)
    out.append(f"{t:.1f}:{int(np.median(ps)) if ps else 0}/{db:.0f}")
    t += 0.1
print(" ".join(out))
