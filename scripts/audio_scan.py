#!/usr/bin/env python3
"""Find talking and laughing moments in clips without speech-to-text.

Usage: python3 -I scripts/audio_scan.py public/clips/clip01.mp4 [more clips...]

For each clip: extracts mono 16 kHz audio with ffmpeg, measures loudness in
0.1 s windows, then prints the sound "events" (stretches above the noise floor)
with a guess at what they are:
  speech  - steady syllable rhythm (~3-7 bursts/s), mid loudness
  laugh?  - fast repeated bursts that are louder than the clip's speech
  loud    - anything else loud (clippers, crowd, music)
Use the times to listen/look closer; it is a shortlist, not a transcript.
"""
import subprocess
import sys

import numpy as np

SR = 16000
WIN = 0.05
CHUNK = 2.0  # long events are reported in chunks this long


def load(path):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
        capture_output=True, check=True,
    ).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0


def db(x):
    return 20 * np.log10(np.maximum(x, 1e-6))


def scan(path):
    a = load(path)
    if a.size == 0:
        print(f"{path}: no audio track (re-run prep_clips.sh with KEEP_AUDIO=1)")
        return
    n = int(SR * WIN)
    frames = a[: len(a) // n * n].reshape(-1, n)
    level = db(np.sqrt((frames**2).mean(axis=1)))
    floor = np.percentile(level, 20)
    loud_ref = np.percentile(level, 90)
    active = level > floor + 8

    events, start = [], None
    for i, on in enumerate(np.append(active, False)):
        if on and start is None:
            start = i
        elif not on and start is not None:
            if events and start - events[-1][1] <= 8:  # merge gaps < 0.4 s
                events[-1] = (events[-1][0], i)
            else:
                events.append((start, i))
            start = None

    print(f"\n{path}  ({len(a) / SR:.1f}s, noise floor {floor:.0f} dB)")
    step = int(CHUNK / WIN)
    chunks = [(c, min(c + step, e)) for s, e in events for c in range(s, e, step)]
    for s, e in chunks:
        dur = (e - s) * WIN
        if dur < 0.3:
            continue
        seg = level[s:e]
        # Count loudness peaks (syllables / laugh pulses) per second.
        peaks = np.sum((seg[1:-1] > seg[:-2]) & (seg[1:-1] > seg[2:]) & (seg[1:-1] > floor + 12))
        rate = peaks / dur
        mean = np.percentile(seg, 80)  # level of the bursts, not the gaps between them
        if rate >= 3.5 and mean >= loud_ref - 3:
            kind = "laugh?"
        elif 2.0 <= rate <= 7.5:
            kind = "speech"
        else:
            kind = "loud"
        print(f"  {s * WIN:7.1f}s - {e * WIN:7.1f}s  {dur:4.1f}s  {kind:6}  level {mean:5.1f} dB  {rate:3.1f} bursts/s")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for p in sys.argv[1:]:
        scan(p)
