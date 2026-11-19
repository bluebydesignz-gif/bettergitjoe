"""Original synthwave bed + game-menu SFX for the Certified Collision GTA-style promo.

Writes public/ccc/music.wav (stereo, 48 kHz). All sounds are synthesized here,
so the track is royalty-free. Timeline matches src/CertifiedGTA.tsx.
"""
import numpy as np
from scipy.signal import butter, sosfilt
import wave, sys, json

SR = 48000
BPM = 120
BEAT = 60 / BPM
BAR = 4 * BEAT
SCHED = json.load(open('src/flickerSchedule.json'))
DUR = SCHED['duration'] / SCHED['fps']
N = int(SR * DUR)
rng = np.random.default_rng(7)

L = np.zeros(N)
R = np.zeros(N)


def t_arr(sec):
    return np.arange(int(sec * SR)) / SR


def add(sig, start, gain=1.0, pan=0.0):
    i = int(start * SR)
    if i >= N:
        return
    sig = sig[: N - i]
    l = gain * np.cos((pan + 1) * np.pi / 4)
    r = gain * np.sin((pan + 1) * np.pi / 4)
    L[i : i + len(sig)] += sig * l * np.sqrt(2)
    R[i : i + len(sig)] += sig * r * np.sqrt(2)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, 'low', fs=SR, output='sos'), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, 'high', fs=SR, output='sos'), x)


def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], 'band', fs=SR, output='sos'), x)


def saw(f, t):
    return 2 * ((f * t) % 1) - 1


def sq(f, t, duty=0.5):
    return np.where((f * t) % 1 < duty, 1.0, -1.0)


def env(t, a=0.005, d=0.2, s=0.0, r=0.05, length=None):
    length = t[-1] if length is None else length
    e = np.where(t < a, t / a, s + (1 - s) * np.exp(-(t - a) / d))
    rel = np.clip((t - length) / r, 0, 1)
    return e * (1 - rel)


def note(n):  # MIDI -> Hz
    return 440 * 2 ** ((n - 69) / 12)


# ---------- drums ----------
def kick():
    t = t_arr(0.45)
    f = 45 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 7) + 0.3 * np.exp(-t * 300) * rng.standard_normal(len(t))


def snare():
    t = t_arr(0.9)
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25)
    noise = bp(rng.standard_normal(len(t)), 900, 7000) * (np.exp(-t * 9) * 0.9)
    # gated-reverb style tail
    tail = lp(rng.standard_normal(len(t)), 5000) * 0.35 * np.where(t < 0.32, 1, np.exp(-(t - 0.32) * 40))
    return body * 0.7 + noise + tail


def hat(open_=False):
    t = t_arr(0.25 if open_ else 0.06)
    return hp(rng.standard_normal(len(t)), 8000) * np.exp(-t * (14 if open_ else 70))


K, S, H, HO = kick(), snare(), hat(), hat(True)

DROP = 4.0       # drums enter on the first card
END_HIT = 22.5   # final hit / end card
for b in range(int(DUR / BEAT) + 1):
    tb = b * BEAT
    if tb < DROP - 0.01 or tb >= DUR - 0.6:
        continue
    add(K, tb, 0.9)
    if b % 2 == 1:
        add(S, tb, 0.42, 0.05)
    add(H, tb + BEAT / 2, 0.14, 0.3)
    add(H, tb + BEAT / 4, 0.06, -0.3)
    add(H, tb + 3 * BEAT / 4, 0.06, -0.3)
    if b % 4 == 3:
        add(HO, tb + BEAT / 2, 0.1, 0.35)

# ---------- harmony: Am  F  C  G ----------
prog = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [55, 60, 64]), (55, [55, 59, 62])]


def chord_at(time):
    return prog[int(time // BAR) % 4]


# pad (all song), filtered open over time
for bar in range(int(DUR / BAR) + 1):
    t0 = bar * BAR
    root, ch = chord_at(t0)
    t = t_arr(BAR + 0.3)
    sig = np.zeros(len(t))
    for n in ch + [ch[0] + 12]:
        for det in (-0.12, 0.0, 0.12):
            sig += saw(note(n) * 2 ** (det / 12), t)
    cutoff = 900 if t0 < DROP else 2400
    sig = lp(sig, cutoff) * env(t, a=0.25, d=99, s=1, r=0.3, length=BAR) * 0.05
    add(sig, t0, 1.0, -0.25)
    add(lp(sig, cutoff * 0.8), t0 + 0.012, 0.8, 0.35)

# bass: pulsing 8ths with octave jump
for i in range(int(DUR / (BEAT / 2))):
    tb = i * BEAT / 2
    if tb < DROP - 0.01 or tb >= DUR - 0.6:
        continue
    root, _ = chord_at(tb)
    f = note(root - 24 + (12 if i % 2 else 0))
    t = t_arr(BEAT / 2)
    sig = lp(saw(f, t) + 0.5 * sq(f * 1.003, t), 700) * env(t, a=0.004, d=0.12, s=0.35, r=0.02, length=BEAT / 2 - 0.02)
    add(sig, tb, 0.34)

# lead arp: 16ths over chord tones, with ping-pong delay
arp_pat = [0, 1, 2, 3, 2, 1, 2, 3]
for i in range(int(DUR / (BEAT / 4))):
    tb = i * BEAT / 4
    if tb < DROP - 0.01 or tb >= DUR - 0.6:
        continue
    _, ch = chord_at(tb)
    tones = ch + [ch[0] + 12]
    n = tones[arp_pat[i % 8]] + 12
    t = t_arr(BEAT / 4)
    sig = lp(sq(note(n), t, 0.3), 3200) * env(t, a=0.002, d=0.07, s=0.0, r=0.01, length=BEAT / 4 - 0.01)
    add(sig, tb, 0.07, 0.15)
    add(sig, tb + 3 * BEAT / 4, 0.035, -0.6)
    add(sig, tb + 6 * BEAT / 4, 0.02, 0.6)

# ---------- SFX ----------
def whoosh(length=0.55, up=True):
    t = t_arr(length)
    x = rng.standard_normal(len(t))
    out = np.zeros(len(t))
    seg = 1200
    for s in range(0, len(t), seg):
        frac = s / len(t)
        fc = 400 + 5000 * (frac if up else 1 - frac)
        out[s : s + seg] = bp(x[s : s + seg + 0], max(100, fc * 0.6), min(20000, fc * 1.4))[: len(out[s : s + seg])]
    e = np.sin(np.pi * np.clip(t / length, 0, 1)) ** 2
    return lp(out, 9000) * e


def blip(f1=880, f2=1760):
    t = t_arr(0.16)
    return sq(np.where(t < 0.06, f1, f2), t, 0.25) * env(t, a=0.002, d=0.05, s=0.2, r=0.02, length=0.13) * 0.6


def chime():
    t = t_arr(1.4)
    sig = np.zeros(len(t))
    for k, n in enumerate([76, 79, 83, 88]):
        tt = np.clip(t - k * 0.07, 0, None)
        sig += np.sin(2 * np.pi * note(n) * tt) * np.exp(-tt * 3) * (t > k * 0.07)
    return sig * 0.35


def glitch(length=0.35):
    t = t_arr(length)
    sig = sq(60 + 900 * rng.random(), t) * 0.0
    out = np.zeros(len(t))
    pos = 0
    while pos < len(t):
        seg = int(SR * rng.uniform(0.008, 0.04))
        f = rng.choice([220, 440, 1320, 2640, 90])
        tt = t[pos : pos + seg]
        out[pos : pos + seg] = (sq(f, tt) if rng.random() < 0.6 else rng.standard_normal(len(tt))) * rng.uniform(0.2, 0.8)
        pos += seg
    return lp(out, 7000) * 0.5 + sig


def impact():
    t = t_arr(2.2)
    f = 35 + 80 * np.exp(-t * 10)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    crash = lp(rng.standard_normal(len(t)), 6000) * np.exp(-t * 3.5) * 0.4
    return boom + crash


def riser(length):
    t = t_arr(length)
    f = 200 * 2 ** (3 * t / length)
    tone = saw(1, np.cumsum(f) / SR) * 0.15
    noise = hp(rng.standard_normal(len(t)), 2000) * 0.2
    return lp(tone + noise, 6000) * (t / length) ** 2


# intro: loading
add(glitch(0.4), 0.25, 0.5)
for k in range(6):
    add(blip(660, 660), 1.2 + k * 0.45, 0.10, 0.4 if k % 2 else -0.4)
add(riser(1.9), 2.1, 0.7)
add(impact(), DROP, 0.55)

for tcard in (4.0, 7.0, 10.0, 13.0):
    add(whoosh(0.5), tcard - 0.25, 0.32, 0.2)
    add(blip(), tcard + 0.12, 0.22)
    add(blip(1320, 2640), tcard + 0.5, 0.10, 0.3)
add(whoosh(0.5), 16.0 - 0.25, 0.35)
add(chime(), 16.35, 0.6)
add(whoosh(0.6, up=False), 19.0 - 0.3, 0.35)
add(glitch(0.3), 19.0, 0.35)
add(riser(1.4), END_HIT - 1.4, 0.6)
add(impact(), END_HIT, 0.75)
add(chime(), END_HIT + 0.4, 0.4)

# reality <-> GTA: reality is the same mix heard muffled, GTA is full range
fps = SCHED['fps']
mode = np.zeros(N)
state, last = 0, 0
for f in SCHED['toggles'] + [SCHED['duration']]:
    a, b = int(last / fps * SR), int(f / fps * SR)
    mode[a:b] = state
    state ^= 1
    last = f
ramp = int(0.004 * SR)
mode = np.convolve(mode, np.ones(ramp) / ramp, mode='same')
for ch in (L, R):
    muffled = lp(ch, 450, 4) * 0.8 + hp(rng.standard_normal(N), 3000) * 0.004
    ch[:] = muffled * (1 - mode) + ch * mode
tick_t = t_arr(0.035)
for f in SCHED['toggles']:
    tick = hp(rng.standard_normal(len(tick_t)), 1500) * np.exp(-tick_t * 90)
    add(tick, f / fps, 0.16, rng.uniform(-0.6, 0.6))

# master: gentle sidechain-ish pump, soft clip, fade
pump = np.ones(N)
for b in range(int(DUR / BEAT) + 1):
    tb = b * BEAT
    if DROP - 0.01 <= tb < DUR - 0.6:
        i = int(tb * SR)
        ln = int(0.22 * SR)
        seg = 1 - 0.35 * np.exp(-np.arange(ln) / SR * 18)
        pump[i : i + ln] = np.minimum(pump[i : i + ln], seg[: len(pump[i : i + ln])])
L *= pump
R *= pump
mix = np.stack([L, R], 1)
mix = np.tanh(mix * 1.4) / np.tanh(1.4)
fade = np.ones(N)
fl = int(1.2 * SR)
fade[-fl:] = np.linspace(1, 0, fl)
fade[: int(0.05 * SR)] = np.linspace(0, 1, int(0.05 * SR))
mix *= fade[:, None]
mix *= 0.89 / np.max(np.abs(mix))
out = sys.argv[1] if len(sys.argv) > 1 else 'public/ccc/music.wav'
with wave.open(out, 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('wrote', out, DUR, 's')
