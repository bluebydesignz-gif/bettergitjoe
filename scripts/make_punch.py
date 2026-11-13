#!/usr/bin/env python3
"""Synthesize a short punch "thud" sound effect (no samples, no licensing).

Usage: python3 -I scripts/make_punch.py public/sfx/punch.wav
"""
import sys
import wave

import numpy as np

SR = 48000
out = sys.argv[1] if len(sys.argv) > 1 else "public/sfx/punch.wav"
t = np.arange(int(SR * 0.45)) / SR
rng = np.random.default_rng(7)

# Body: a low sine that drops in pitch, like a glove landing.
freq = 110 * np.exp(-t * 9) + 45
body = np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-t * 11)
# Smack: a short burst of filtered noise at the front.
noise = rng.standard_normal(t.size)
noise = np.convolve(noise, np.ones(6) / 6, mode="same")
smack = noise * np.exp(-t * 60) * 0.9
# Whoosh tail: quiet, slightly brighter noise.
whoosh = rng.standard_normal(t.size) * np.exp(-t * 18) * 0.08

sig = body * 0.9 + smack + whoosh
sig = np.tanh(sig * 2.2)  # a bit of saturation for punch
sig /= np.max(np.abs(sig)) / 0.9
data = (np.stack([sig, sig], axis=1) * 32767).astype(np.int16)

import os

os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(data.tobytes())
print(f"wrote {out}")
