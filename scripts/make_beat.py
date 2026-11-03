"""Synthesize a placeholder 124 BPM dark house beat for the INSYNC Halloween reel.

Arrangement (in beats) matches src/insync/timeline.ts:
  0-4   intro: drone + riser
  4-16  drop: four-on-the-floor, claps, hats, bass
  12-16 burst: 16th hats + snare roll
  16    impact
  18-28 groove + spooky lead
  28-30 snare roll
  30    impact, then outro

Usage: python3 scripts/make_beat.py public/music/beat.wav
"""
import sys
import wave

import numpy as np

SR = 48000
BPM = 124
BEAT = 60 / BPM
TOTAL_BEATS = 36
LEN = int(SR * (TOTAL_BEATS * BEAT + 1.5))
rng = np.random.default_rng(7)
out = np.zeros((LEN, 2))


def at(beat):
    return int(beat * BEAT * SR)


def add(sig, beat, gain=1.0, pan=0.0):
    i = at(beat)
    sig = sig[: max(0, LEN - i)]
    left, right = gain * (1 - max(pan, 0)), gain * (1 + min(pan, 0))
    out[i : i + len(sig), 0] += sig * left
    out[i : i + len(sig), 1] += sig * right


def env(n, attack=0.002, decay=0.2):
    t = np.arange(n) / SR
    a = np.clip(t / attack, 0, 1)
    return a * np.exp(-t / decay)


def kick():
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    freq = 45 + 110 * np.exp(-t * 28)
    phase = 2 * np.pi * np.cumsum(freq) / SR
    body = np.sin(phase) * np.exp(-t * 7)
    click = rng.standard_normal(n) * np.exp(-t * 400) * 0.3
    return np.tanh((body + click) * 2.2) * 0.9


def noise_hit(length, decay, hp=True):
    n = int(length * SR)
    x = rng.standard_normal(n)
    if hp:
        x = np.diff(np.concatenate([[0], x]))
    return x * env(n, 0.001, decay)


def clap():
    x = np.zeros(int(0.3 * SR))
    for off in (0, 0.011, 0.022):
        h = noise_hit(0.25, 0.06 if off == 0.022 else 0.012)
        i = int(off * SR)
        x[i : i + len(h)] += h[: len(x) - i]
    return x * 0.5


def hat(open_=False):
    return noise_hit(0.25 if open_ else 0.06, 0.07 if open_ else 0.015) * 0.18


def note(freq, length, decay=0.5, detune=0.006, kind="saw"):
    n = int(length * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for d in (-detune, 0, detune):
        ph = (t * freq * (1 + d)) % 1
        sig += (2 * ph - 1) if kind == "saw" else np.sin(2 * np.pi * ph)
    sig /= 3
    # crude low-pass by smoothing
    k = 18
    sig = np.convolve(sig, np.ones(k) / k, mode="same")
    return sig * env(n, 0.005, decay)


def riser(beats):
    n = at(beats)
    t = np.arange(n) / n
    x = rng.standard_normal(n)
    # brighten over time by mixing raw and smoothed noise
    smooth = np.convolve(x, np.ones(40) / 40, mode="same")
    sig = smooth * (1 - t) + np.diff(np.concatenate([[0], x])) * t
    return sig * t**2 * 0.35


def impact():
    n = int(2.0 * SR)
    t = np.arange(n) / SR
    boom = np.sin(2 * np.pi * (38 + 60 * np.exp(-t * 10)) * t) * np.exp(-t * 2.2)
    crash = noise_hit(2.0, 0.5) * 0.4
    return np.tanh(boom * 1.6) * 0.8 + crash


def drone(beats, freq=55):
    n = at(beats)
    t = np.arange(n) / SR
    sig = note(freq, beats * BEAT, decay=999, detune=0.01) * 0.5
    sig += np.sin(2 * np.pi * freq * 1.5 * t) * 0.08 * (1 + np.sin(2 * np.pi * 0.5 * t))
    fade = np.minimum(1, np.minimum(t / 0.8, (n / SR - t) / 0.4))
    return sig * fade


# Intro
add(drone(4.2), 0, 0.6)
add(riser(4), 0, 0.8)

# A minor dark bassline per bar: A, A, F, G
bass_roots = [55.0, 55.0, 43.65, 49.0]

for b in range(4, 30):
    add(kick(), b, 1.0)
    if b % 2 == 1:
        add(clap(), b, 0.9)
    add(hat(open_=True), b + 0.5, 0.9, pan=0.2)
    root = bass_roots[((b - 4) // 4) % 4]
    for off in (0.5, 0.75):
        add(note(root, BEAT * 0.25, 0.08, kind="saw"), b + off, 0.55)

# Burst: 16th hats and snare roll into the impact
for b in np.arange(12, 16, 0.25):
    add(hat(), b, 1.0, pan=-0.3)
for b in np.arange(14, 16, 0.25 if True else 0.5):
    add(clap(), b, 0.25 + 0.2 * (b - 14))
add(riser(4), 12, 0.6)
add(impact(), 16, 0.9)

# Spooky lead, beats 18-28
lead = [220.0, 261.63, 329.63, 311.13, 220.0, 261.63, 349.23, 329.63]
for i, b in enumerate(np.arange(18, 28, 0.5)):
    add(note(lead[i % len(lead)] * 2, BEAT * 0.45, 0.18, detune=0.012), b, 0.18, pan=0.4 * (-1) ** i)

# Roll into the outro
for b in np.arange(28, 30, 0.125):
    add(clap(), b, 0.15 + 0.25 * (b - 28) / 2)
add(riser(2), 28, 0.7)
add(impact(), 30, 1.0)
add(drone(6, 55), 30, 0.5)
for b in (30, 32, 34):
    add(kick(), b, 0.6)

# Master: soft clip and normalize
out = np.tanh(out * 1.1)
out /= np.max(np.abs(out)) + 1e-9
out *= 0.89
pcm = (out * 32767).astype(np.int16)

path = sys.argv[1] if len(sys.argv) > 1 else "beat.wav"
with wave.open(path, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f"wrote {path} ({LEN / SR:.1f}s @ {BPM} BPM)")
