"""Turn edl.json into (1) the Remotion timeline and (2) the natural-sound mix.

usage: python3 assemble.py edl.json <footage_dir> <seg_dir> public/<slug> src/<slug>/timeline.json

Audio rules (no music is mixed in; the track is added later in Instagram):
  voice  -> cleaned, levelled speech, full level
  nat    -> the shot's own ambience at a low, fixed level (featured moments use a higher db)
  bed    -> no clip audio; a continuous low ambience bed runs under the whole reel
"""
import json, os, shutil, subprocess, sys, wave
import numpy as np

SR = 48000
CHAINS = {
    "pa":    "highpass=f=110,lowpass=f=9500,afftdn=nr=12:nf=-45:tn=1,equalizer=f=280:t=q:w=1.2:g=-3,"
             "equalizer=f=3200:t=q:w=1.3:g=3.5,acompressor=threshold=-24dB:ratio=3:attack=6:release=140:makeup=3",
    "close": "highpass=f=90,afftdn=nr=6:nf=-50,equalizer=f=3000:t=q:w=1.5:g=2,"
             "acompressor=threshold=-22dB:ratio=2.5:attack=8:release=120:makeup=2",
    # speech followed by a much louder laugh: level to the words, then hold the laugh down
    "close_lvl": "highpass=f=90,afftdn=nr=6:nf=-50,equalizer=f=3000:t=q:w=1.5:g=2,"
             "acompressor=threshold=-17dB:ratio=8:attack=2:release=260:makeup=1",
    "nat":   "highpass=f=120,lowpass=f=10000",
}

def pcm(src, t0, dur, af=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{max(t0,0):.3f}", "-t", f"{dur:.3f}", "-i", src, "-vn", "-ac", "1", "-ar", str(SR)]
    if af: cmd += ["-af", af]
    cmd += ["-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).copy()

def rms_db(x, active=False):
    if len(x) == 0: return -99.0
    n = int(0.05 * SR); fr = x[: len(x) // n * n].reshape(-1, n)
    p = (fr ** 2).mean(axis=1) + 1e-12
    if active: p = np.sort(p)[int(len(p) * 0.4):]          # loudest 60% = the words, not the gaps
    return 10 * np.log10(p.mean())

def process(src, t0, dur, chain, target_db, active, window=None, speed=1.0):
    """Level a clip to target_db. `window` = [start, end] seconds to measure (e.g. just the words).
    `speed` > 1 speeds the audio up with pitch kept (atempo), to match a sped-up shot."""
    tempo = f"atempo={speed:.4f}," if speed != 1.0 else ""
    def meas(x):
        if window: x = x[int(window[0] * SR): int(window[1] * SR)]
        return rms_db(x, active)
    raw = pcm(src, t0, dur, tempo.rstrip(",") or None)
    g = min(target_db - meas(raw), 34.0)                      # cap make-up gain
    out = pcm(src, t0, dur, tempo + f"volume={g:.2f}dB," + CHAINS[chain])
    g2 = target_db - meas(out)                                # trim after the chain
    return out * (10 ** (g2 / 20)), g + g2

def fade(x, fin, fout):
    a, b = int(fin * SR), int(fout * SR)
    if a: x[:a] *= np.linspace(0, 1, a) ** 1.0
    if b: x[-b:] *= np.linspace(1, 0, b) ** 1.0
    return x

if __name__ == "__main__":
    edl_path, footage, segdir, pub, tl_out = sys.argv[1:6]
    edl = json.load(open(edl_path)); fps = edl["fps"]
    slug = edl.get("slug", "reel")                       # public/<slug>/ holds this reel's media
    os.makedirs(os.path.join(pub, "seg"), exist_ok=True)

    # ---- timeline -------------------------------------------------------
    t = 0.0; segs = []; starts = {}
    for b in edl["beats"]:
        xf = b.get("xfade", 0.0)
        start = t - xf
        starts[b["id"]] = start
        play = b.get("use", b["dur"])                       # "use" = seconds of the built shot to show (audio may run longer)
        segs.append({"id": b["id"], "file": f"{slug}/seg/{b['id']}.mp4", "from": round(start * fps), "dur": round(play * fps),
                     "xfade": round(xf * fps), "push": b.get("push", [1.0, 1.025])})
        a_, b_ = os.path.join(segdir, b["id"] + ".mp4"), os.path.join(pub, "seg", b["id"] + ".mp4")
        if not (os.path.exists(b_) and os.path.getsize(a_) == os.path.getsize(b_) and os.path.getmtime(b_) >= os.path.getmtime(a_)):
            shutil.copy2(a_, b_)                                # only copy shots that changed
        t = start + play
    total = t + edl.get("tail", 0.0)

    def at(ref):                                   # "beatId+1.25" -> seconds
        import re; m = re.match(r"(\w+?)([+-][\d.]+)?$", ref); bid, off = m.group(1), m.group(2)
        return starts[bid] + (float(off) if off else 0.0)
    overlays = []
    for o in edl.get("overlays", []):
        o = dict(o); o["from"] = round(at(o.pop("at")) * fps); o["dur"] = round(o["dur"] * fps); overlays.append(o)
    json.dump({"slug": slug, "fps": fps, "durationInFrames": round(total * fps), "segments": segs, "overlays": overlays},
              open(tl_out, "w"), indent=1)

    # ---- audio ----------------------------------------------------------
    n = int(total * SR) + SR
    mix = np.zeros(n, np.float32); report = []
    for b in edl["beats"]:
        a = b.get("audio", {"kind": "bed"}); kind = a["kind"]
        if kind == "bed": continue
        src = os.path.join(footage, a.get("src", b["src"]))
        a_in = a.get("in", b["in"]); lead = a.get("lead", 0.0); length = a.get("len", b["dur"])
        sp = a.get("speed", b.get("speed", 1.0)) if kind == "voice" else 1.0   # len/pre/tail are source seconds
        if kind == "voice":
            pre, post = a.get("pre", 0.06), a.get("tail", 0.10)
            x, g = process(src, a_in - pre, length + pre + post, a.get("chain", "close"), a.get("db", -20.0), True,
                           a.get("window"), sp)
            x = fade(x, a.get("fin", 0.05), 0.09); t0 = starts[b["id"]] - lead - pre / sp
        else:
            pre = post = 0.12                                   # overlap neighbours for a soft crossfade
            x, g = process(src, a_in - pre, length + pre + post, "nat", a.get("db", -32.0), False)
            x = fade(x, 0.22, 0.22); t0 = starts[b["id"]] - lead - pre
        i0 = max(int(t0 * SR), 0); x = x[: n - i0]
        mix[i0:i0 + len(x)] += x
        report.append((b["id"], kind, round(g, 1)))
    # free-placed sounds: speech that starts over another shot (J-cut), applause, etc.
    for sd in edl.get("sounds", []):
        pre, post = 0.06, 0.10
        x, g = process(os.path.join(footage, sd["src"]), sd["in"] - pre, sd["len"] + pre + post,
                       sd.get("chain", "close"), sd.get("db", -20.0), sd.get("active", True), sd.get("window"))
        x = fade(x, sd.get("fin", 0.05), sd.get("fout", 0.09))
        i0 = max(int((at(sd["at"]) - pre) * SR), 0); x = x[: n - i0]
        mix[i0:i0 + len(x)] += x
        report.append((sd["at"], "sound", round(float(g), 1)))
    # continuous low ambience bed so drone / slow-motion shots are never dead silent
    bed = edl.get("bed")
    if bed:
        loop, _ = process(os.path.join(footage, bed["src"]), bed["in"], bed["len"], "nat", bed.get("db", -40.0), False)
        xf = int(0.5 * SR); out = np.zeros(n, np.float32); pos = 0
        while pos < n:
            seg = loop.copy(); seg[:xf] *= np.linspace(0, 1, xf); seg[-xf:] *= np.linspace(1, 0, xf)
            m = min(len(seg), n - pos); out[pos:pos + m] += seg[:m]; pos += len(loop) - xf
        mix += out
    end = int(total * SR)
    mix = mix[:end]; mix = fade(mix, 0.25, 1.2)
    mix = np.tanh(mix * 1.0)                                   # gentle safety limiter
    tmp = os.path.join(pub, "mix_raw.wav")
    w = wave.open(tmp, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
    # static loudness trim to -16 LUFS + true-peak limit (static gain, so quiet shots stay quiet)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", tmp, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    I = float([l for l in r.splitlines() if l.strip().startswith("I:")][-1].split()[1])
    gain = -16.0 - I
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", f"volume={gain:.2f}dB,alimiter=limit=0.84:attack=3:release=60:level=disabled",
                    "-ac", "2", "-ar", str(SR), os.path.join(pub, "mix.wav")], check=True)
    os.remove(tmp)
    print(f"timeline {total:.2f}s, {len(segs)} shots, {len(overlays)} overlays; loudness {I:.1f} LUFS -> trim {gain:+.1f} dB")
    print("clip gains (dB):", [(i, k, float(g)) for i, k, g in report])
    # per-shot level check of the finished mix
    w = wave.open(os.path.join(pub, "mix.wav")); y = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2)[:, 0] / 32768
    for b in edl["beats"]:
        a0 = int(starts[b["id"]] * SR); chunk = y[a0:a0 + int(b.get("use", b["dur"]) * SR)]
        q = [chunk[i:i + SR // 2] for i in range(0, len(chunk), SR // 2)]
        print(f"  {b['id']:>3} @{starts[b['id']]:5.1f}s " + " ".join(f"{10*np.log10((c**2).mean()+1e-12):4.0f}" for c in q if len(c)))
