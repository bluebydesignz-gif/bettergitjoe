"""Synthesize the reel's sound design and mix it under the voice.
usage: python3 sfx.py <in.mp4 (voice)> <out.wav>   run from the episode folder; cue times come from cues.json (build_overlay.py)"""
import sys, subprocess, numpy as np, wave
SR = 48000; rng = np.random.default_rng(3)
def env(n, a, d): e = np.ones(n); a = int(a * SR); e[:a] = np.linspace(0, 1, a); e *= np.exp(-np.arange(n) / (d * SR)); return e
def whoosh(L=0.38):
    n = int(L * SR); x = rng.normal(0, 1, n); f = np.fft.rfft(x); fr = np.fft.rfftfreq(n, 1 / SR)
    out = np.zeros(n); seg = n // 8
    for k in range(8):                                   # sweep a band upward
        c = 400 * (2 ** (k * 0.55)); band = np.exp(-((fr - c) / (c * 0.5)) ** 2)
        y = np.fft.irfft(f * band, n); out[k * seg:(k + 1) * seg] = y[k * seg:(k + 1) * seg]
    w = np.sin(np.linspace(0, np.pi, n)) ** 1.5; return out / np.abs(out).max() * w
def pop(f0=900):
    n = int(0.09 * SR); t = np.arange(n) / SR; f = f0 * np.exp(-t * 18)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.025)
def thud():
    n = int(0.35 * SR); t = np.arange(n) / SR; f = 110 * np.exp(-t * 9) + 40
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.25 * rng.normal(0, 1, n) * np.exp(-t * 60)) * env(n, 0.002, 0.09)
def ding():
    n = int(1.1 * SR); t = np.arange(n) / SR
    x = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, a, d in ((1568, 1, 3.2), (3136, .45, 5), (4704, .25, 7), (2093, .3, 4)))
    return x * env(n, 0.001, 10)
def wrench():
    n = int(0.38 * SR); t = np.arange(n) / SR
    buzz = rng.normal(0, 1, n) * (0.55 + 0.45 * np.sign(np.sin(2 * np.pi * 38 * t))) + 0.6 * np.sign(np.sin(2 * np.pi * 76 * t))
    x = buzz * np.minimum(1, t / 0.01) * np.minimum(1, (0.38 - t) / 0.05)
    clicks = np.zeros(int(0.5 * SR))
    for k in range(4):
        i = int((0.06 + k * 0.1) * SR); m = int(0.012 * SR)
        clicks[i:i + m] += rng.normal(0, 1, m) * np.exp(-np.arange(m) / (0.002 * SR))
    return np.concatenate([x * 0.6, clicks])
import json
C = json.load(open("cues.json"))
CUES = [(C["title"][0], whoosh(), .30), (C["title"][1], whoosh(), .32), (C["title"][2] + 0.1, thud(), .55),
        (C["myth"], whoosh(), .26), (C["stamp"] + 0.3, thud(), .6), (C["list"], whoosh(), .26)]
CUES += [(t - 0.02, pop(800 + 120 * k), .3) for k, t in enumerate(C["rows"])]
CUES += [(C["end"], whoosh(0.5), .32), (C["end"] + 0.35, wrench(), .32)]
v = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", sys.argv[1], "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                 capture_output=True, check=True).stdout, np.float32).astype(np.float64)
fx = np.zeros(len(v) + SR)
for t, x, g in CUES:
    i = int(t * SR); fx[i:i + len(x)] += x / (np.abs(x).max() + 1e-9) * g
mix = v + fx[:len(v)] * 0.35
w = wave.open(sys.argv[2], "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
print("sfx mixed:", len(CUES), "cues")
