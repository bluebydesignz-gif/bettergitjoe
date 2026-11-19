"""Builds the reality -> GTA transformation schedule shared by the video and the audio.

Writes src/flickerSchedule.json: {"toggles": [frame, ...], "duration": N}.
Mode starts in reality (0); each toggle flips it. The video opens on real
footage, flickers three times into the GTA art style, then stays there.
"""
import json

FPS = 30
DURATION = 825
# on, off, on, off, on (and stay): three GTA flashes, the last one sticks
TOGGLES = [20, 24, 29, 33, 38]

with open('src/flickerSchedule.json', 'w') as f:
    json.dump({'fps': FPS, 'duration': DURATION, 'toggles': TOGGLES}, f)
print(len(TOGGLES), 'toggles, duration', DURATION)
