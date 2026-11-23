"""Cut, reframe and grade every beat in edl.json into 1080x1920/30fps clips.

usage: python3 build_segments.py edl.json <footage_dir> <out_dir> [only_id ...]

Each beat: {id, src, in, dur, speed?, zoom?, cx?, cy?, rot?, grade?, sharpen?}
  in/dur are SOURCE seconds / OUTPUT seconds. speed 0.5 = slow motion (60fps sources).
  zoom 1.0 = fit width for vertical sources; cx/cy = crop centre as fractions.
"""
import json, subprocess, sys, os

FPS = 30
W, H = 1080, 1920
GRADES = {
    # natural, slightly warm correction for the overcast day
    "phone": "eq=contrast=1.05:saturation=1.10:gamma=1.03,colorbalance=rm=0.025:gm=0.005:bm=-0.03:rh=0.015:bh=-0.02",
    "drone": "eq=contrast=1.10:saturation=1.22:gamma=1.04,colorbalance=rm=0.03:gm=0.0:bm=-0.035:rh=0.02:bh=-0.02",
    "bright": "eq=contrast=1.04:saturation=1.10:gamma=0.94,colorbalance=rm=0.02:bm=-0.025",
}

def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
        "stream=width,height:stream_side_data=rotation", "-of", "json", path], capture_output=True, text=True).stdout
    s = json.loads(out)["streams"][0]
    w, h = s["width"], s["height"]
    rot = 0
    for sd in s.get("side_data_list", []):
        if "rotation" in sd: rot = int(sd["rotation"])
    if abs(rot) in (90, 270): w, h = h, w
    return w, h

def build(b, footage, outdir):
    src = os.path.join(footage, b["src"])
    w, h = probe(src)
    pre = []
    if b.get("rot") == "cw": pre.append("transpose=1"); w, h = h, w
    if b.get("rot") == "ccw": pre.append("transpose=2"); w, h = h, w
    speed = b.get("speed", 1.0)
    dur = b["dur"]
    src_dur = dur * speed
    zoom = b.get("zoom", 1.0)
    cx, cy = b.get("cx", 0.5), b.get("cy", 0.5)
    vf = list(pre)
    if h < H:
        # Low-res landscape source (720p drone): upscale first, then crop, so a moving
        # crop window pans in sub-source-pixel steps instead of juddering.
        sw = int(round(w * H * zoom / h)) // 2 * 2; sh = int(round(H * zoom)) // 2 * 2
        vf.append(f"scale={sw}:{sh}:flags=lanczos")
        y = int(min(max(cy * sh - H / 2, 0), sh - H)) // 2 * 2
        if isinstance(cx, list):
            x = f"'min(max(({cx[0]}+({cx[1]}-{cx[0]})*min(t/{src_dur:.3f},1))*{sw}-{W / 2},0),{sw - W})'"
        else:
            x = str(int(min(max(cx * sw - W / 2, 0), sw - W)) // 2 * 2)
        vf.append(f"crop={W}:{H}:{x}:{y}")
        info = {"upscale": round(H * zoom / h, 2)}
    else:
        # crop window with 9:16 aspect; zoom 1.0 = largest 9:16 window that fits
        base_w = min(w, h * W / H)
        cw = int(base_w / zoom) // 2 * 2
        ch = int(cw * H / W) // 2 * 2
        x = int(min(max(cx * w - cw / 2, 0), w - cw)) // 2 * 2
        y = int(min(max(cy * h - ch / 2, 0), h - ch)) // 2 * 2
        vf.append(f"crop={cw}:{ch}:{x}:{y}")
        info = {"crop": [x, y, cw, ch], "upscale": round(W / cw, 2)}
    if speed > 1.0 and float(speed).is_integer():
        n = int(speed)                      # speed-up with frame blending = natural motion blur
        vf += [f"fps={FPS}", f"tmix=frames={n}", f"select='not(mod(n,{n}))'", f"setpts=N/({FPS}*TB)"]
    elif speed != 1.0:
        vf.append(f"setpts={1/speed}*PTS")
    vf += [f"fps={FPS}", f"scale={W}:{H}:flags=lanczos", GRADES[b.get("grade", "phone")]]
    if b.get("sharpen"): vf.append(f"unsharp=5:5:{b['sharpen']}:5:5:0.0")
    if b.get("grain"): vf.append(f"noise=alls={b['grain']}:allf=t")
    nfr = int(round(dur * FPS))
    vf.append(f"tpad=stop_mode=clone:stop_duration={dur:.2f}")     # hold the last frame if the source runs out
    vf.append("setsar=1,format=yuv420p")
    out = os.path.join(outdir, b["id"] + ".mp4")
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{b['in']:.3f}", "-t", f"{b.get('src_len', src_dur + 0.3):.3f}", "-i", src,
           "-an", "-vf", ",".join(vf), "-frames:v", str(nfr),
           "-c:v", "libx264", "-preset", "fast", "-crf", "13", "-g", "15", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    info.update({"id": b["id"], "frames": nfr})
    return info

if __name__ == "__main__":
    edl = json.load(open(sys.argv[1])); footage, outdir = sys.argv[2], sys.argv[3]
    only = set(sys.argv[4:]); os.makedirs(outdir, exist_ok=True)
    for b in edl["beats"]:
        if only and b["id"] not in only: continue
        print(build(b, footage, outdir), flush=True)
