"""Transcribe clips with word timings (faster-whisper).

usage: python3 transcribe.py <model> <out_dir> <clip.wav> [...]
  Extract audio first: ffmpeg -i clip.MOV -vn -ac 1 -ar 16000 wav/clip.wav
  Use "small" for a fast pass; re-check any line you will caption with "large-v3-turbo".
  Writes <out_dir>/<clip>.json and prints each segment.
"""
import sys, json, os, wave
import numpy as np
from faster_whisper import WhisperModel

model, out, files = sys.argv[1], sys.argv[2], sys.argv[3:]
os.makedirs(out, exist_ok=True)
m = WhisperModel(model, device="cpu", compute_type="int8", cpu_threads=4)
PROMPT = ("Certified Collision Center. Keep your Toyota a Toyota. Driven to repair. Committed to care. "
          "Marcos. Kirby. Small city, big heart.")
for f in files:
    n = os.path.splitext(os.path.basename(f))[0]
    w = wave.open(f); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    if len(a) < 1600: continue
    segs, info = m.transcribe(a, language="en", word_timestamps=True, vad_filter=True, initial_prompt=PROMPT)
    res = [{"s": round(s.start, 2), "e": round(s.end, 2), "t": s.text.strip(),
            "w": [[x.word, round(x.start, 2), round(x.end, 2)] for x in (s.words or [])]} for s in segs]
    json.dump({"segs": res}, open(f"{out}/{n}.json", "w"))
    print(f"== {n}", flush=True)
    for r in res: print(f"  {r['s']:7.2f}-{r['e']:7.2f} {r['t']}", flush=True)
