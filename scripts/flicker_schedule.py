"""Builds the reality <-> GTA flicker schedule shared by the video and the audio.

Writes src/flickerSchedule.json: {"toggles": [frame, ...], "duration": N}.
Mode starts in reality (0); each toggle flips it. Flicker gets denser through
the video and ends in a full strobe.
"""
import json
import random

FPS = 30
SEGMENTS = [(0, 120), (120, 210), (210, 300), (300, 390), (390, 480), (480, 570), (570, 675), (675, 825)]
DURATION = SEGMENTS[-1][1]
rng = random.Random(11)
toggles = []
state = 0


def flip(f):
    global state
    toggles.append(f)
    state ^= 1


def window(a, b, target, hold=(1, 3)):
    """Flicker between frames a and b, landing on target at b."""
    t = a
    while True:
        h = rng.randint(*hold)
        if t + h >= b:
            break
        flip(t)
        t += h
    if state != target:
        flip(b)


for i, (s, e) in enumerate(SEGMENTS):
    last = i == len(SEGMENTS) - 1
    lead = 22 if i == 0 else max(3, 12 - 2 * i)
    fin = 8 + 2 * i
    hold = (1, 3) if i < 4 else (1, 2)
    window(s + lead, s + lead + fin, 1, hold)
    if last:
        # full flicker to the end, landing on the GTA end card for the last frames
        window(e - 66, e - 3, 1, (1, 2))
    else:
        fout = 6 + i
        window(e - fout, e, 0, hold)

toggles = sorted(set(toggles))
with open('src/flickerSchedule.json', 'w') as f:
    json.dump({'fps': FPS, 'duration': DURATION, 'toggles': toggles}, f)
print(len(toggles), 'toggles, duration', DURATION)
