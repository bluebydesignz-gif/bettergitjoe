"""Write the HyperFrames overlay for the Certified Wild Black Friday reel.

usage: python3 tools/build_overlay.py   (run from edits/certified-wild-blackfriday)
reads edl.json (rough-cut beats) and words.json ([word, start, end] on the cut timeline),
writes hf/index.html and hf/compositions/overlay.html. Base video: hf/assets/base.mp4 (rough cut).
Brand: Barlow / Barlow Condensed only, red #E01B22, ink #0B0B0C, chrome #C9CDD2, bolted logo.
"""
import json, html, re

E = json.load(open("edl.json")); B = {b["id"]: b for b in E["beats"]}
W = json.load(open("words.json")); DUR = E["duration"]
esc = html.escape
RED, INK, CHROME = "#E01B22", "#0B0B0C", "#C9CDD2"
HOOK_END = B["loc"]["start"]; END0 = B["tail"]["start"]

# words that are never captioned (picked up by the transcriber, not said)
W = [w for w in W if not (w[0].lower() == "and" and 18.0 < w[1] < 18.5)]
def t_of(word, after=0.0):
    for w, s, e in W:
        if re.sub(r"\W", "", w).lower() == word.lower() and s >= after: return s
    raise SystemExit(f"word {word} not found after {after}")

# ---------------------------------------------------------------- caption chunks
cap_words = [w for w in W if HOOK_END - 0.05 <= w[1] < END0]
chunks, cur = [], []
for i, (w, s, e) in enumerate(cap_words):
    full = len(cur) == 4 or (len(cur) == 3 and sum(len(x[0]) for x in cur) + len(w) > 17)
    if cur and (full or s - cur[-1][2] > 0.3 or re.search(r"[,.?!]$", cur[-1][0])):
        chunks.append(cur); cur = []
    cur.append((w, s, e))
if cur: chunks.append(cur)

# ---------------------------------------------------------------- overlay html
css = f"""
    @font-face {{ font-family: "Barlow"; font-weight: 900; src: url("assets/fonts/Barlow-Black.ttf"); }}
    @font-face {{ font-family: "Barlow"; font-weight: 800; src: url("assets/fonts/Barlow-ExtraBold.ttf"); }}
    @font-face {{ font-family: "Barlow"; font-weight: 700; src: url("assets/fonts/Barlow-Bold.ttf"); }}
    @font-face {{ font-family: "Barlow"; font-weight: 600; src: url("assets/fonts/Barlow-SemiBold.ttf"); }}
    @font-face {{ font-family: "BarlowC"; font-weight: 900; src: url("assets/fonts/BarlowCondensed-Black.ttf"); }}
    #ov {{ position: absolute; inset: 0; color: #fff; overflow: hidden; }}
    .glass {{ background: rgba(11,11,12,.56); backdrop-filter: blur(24px) saturate(1.45); -webkit-backdrop-filter: blur(24px) saturate(1.45);
      border: 2px solid rgba(255,255,255,.43); box-shadow: inset 0 2px 0 rgba(255,255,255,.28), 0 18px 50px rgba(0,0,0,.35); }}
    #veil {{ position: absolute; left: 0; right: 0; top: 0; height: 900px; opacity: 0;
      background: linear-gradient(180deg, rgba(0,0,0,.62) 0%, rgba(0,0,0,.35) 55%, rgba(0,0,0,0) 100%); }}
    #title {{ position: absolute; left: 0; right: 0; top: 300px; text-align: center; transform-origin: 50% 0%; }}
    #t-open {{ display: inline-flex; align-items: center; gap: 22px; font-family: "Barlow"; font-weight: 900; font-size: 60px;
      letter-spacing: .22em; text-transform: uppercase; opacity: 0; }}
    #t-open i {{ display: block; width: 86px; height: 7px; background: {RED}; border-radius: 4px; }}
    .t-big {{ font-family: "BarlowC"; font-weight: 900; font-size: 250px; line-height: .86; text-transform: uppercase; opacity: 0;
      text-shadow: 0 10px 36px rgba(0,0,0,.55); }}
    #t-black {{ color: #fff; margin-top: 14px; }}
    #t-friday {{ background: linear-gradient(180deg, #ff3a40 0%, {RED} 55%, #b3121a 100%); -webkit-background-clip: text; background-clip: text;
      color: transparent; filter: drop-shadow(0 10px 24px rgba(0,0,0,.6)); }}
    #slash {{ position: absolute; left: 140px; right: 140px; top: 835px; height: 10px; background: {RED}; transform-origin: 0 50%;
      border-radius: 5px; box-shadow: 0 0 24px rgba(224,27,34,.7); }}
    #badge {{ position: absolute; top: 255px; left: 0; right: 0; margin: 0 auto; width: fit-content; display: flex; align-items: center; gap: 16px;
      padding: 14px 30px 14px 22px; border-radius: 999px; white-space: nowrap; opacity: 0; }}
    #badge img {{ height: 46px; }}
    #badge span {{ font-family: "Barlow"; font-weight: 900; font-size: 34px; letter-spacing: .06em; }}
    #badge b {{ color: #ff5a60; }}
    .chip {{ position: absolute; top: 370px; left: 0; right: 0; margin: 0 auto; width: fit-content; display: flex; align-items: center; gap: 14px; padding: 12px 28px 12px 18px;
      border-radius: 999px; white-space: nowrap; opacity: 0; }}
    .chip .pin {{ width: 34px; height: 34px; border-radius: 50% 50% 50% 0; background: {RED}; transform: rotate(-45deg); position: relative; }}
    .chip .pin::after {{ content: ""; position: absolute; left: 11px; top: 11px; width: 12px; height: 12px; border-radius: 50%; background: #fff; }}
    .chip span {{ font-family: "Barlow"; font-weight: 900; font-size: 38px; letter-spacing: .08em; }}
    #ding {{ position: absolute; left: 70px; top: 560px; font-family: "BarlowC"; font-weight: 900; font-size: 210px; line-height: 1;
      color: #ff2a31; transform: rotate(-9deg); opacity: 0; text-shadow: 0 0 0 #fff, 6px 6px 0 #0B0B0C, 0 14px 40px rgba(0,0,0,.6); }}
    #flash {{ position: absolute; inset: 0; background: radial-gradient(ellipse at center, rgba(224,27,34,0) 45%, rgba(224,27,34,.55) 100%); opacity: 0; }}
    #est {{ position: absolute; left: 90px; right: 90px; top: 300px; border-radius: 40px; padding: 34px 40px 40px; text-align: center; opacity: 0; }}
    #est .l1 {{ font-family: "Barlow"; font-weight: 800; font-size: 46px; letter-spacing: .12em; }}
    #est .l2 {{ font-family: "BarlowC"; font-weight: 900; font-size: 168px; line-height: .9; color: #ff4a50; margin-top: 10px;
      text-shadow: 0 8px 26px rgba(0,0,0,.45); }}
    #cap-stage {{ position: absolute; left: 70px; right: 70px; top: 1200px; height: 0; }}
    .cap {{ position: absolute; left: 0; right: 0; top: 0; display: flex; justify-content: center; opacity: 0; }}
    .cap .glass {{ padding: 16px 34px 18px; border-radius: 30px; font-family: "Barlow"; font-weight: 900; font-size: 66px;
      line-height: 1.05; text-transform: uppercase; white-space: nowrap; }}
    .cap .w {{ display: inline-block; margin: 0 .12em; }}
    .cap .w.bf {{ font-family: "BarlowC"; font-size: 88px; vertical-align: -6px; }}
    #endcard {{ position: absolute; left: 70px; right: 70px; top: 800px; border-radius: 44px; padding: 34px 40px 36px; text-align: center; opacity: 0; }}
    #endcard img {{ width: 400px; height: auto; display: block; margin: 0 auto 10px; }}
    #endcard .e {{ opacity: 0; }}
    #e1 {{ font-family: "Barlow"; font-weight: 700; font-size: 38px; }}
    #e2 {{ font-family: "BarlowC"; font-weight: 900; font-size: 98px; line-height: .95; color: #ff4a50; }}
    #e3 {{ font-family: "Barlow"; font-weight: 800; font-size: 36px; letter-spacing: .08em; margin-top: 8px; }}
    #e4 {{ font-family: "Barlow"; font-weight: 800; font-size: 28px; letter-spacing: .12em; color: {CHROME}; margin-top: 12px; }}
"""
body = f"""    <div id="ov">
      <div id="flash"></div>
      <div id="veil"></div>
      <div id="title">
        <div id="t-open"><i></i>WE'RE OPEN<i></i></div>
        <div id="t-black" class="t-big">Black</div>
        <div id="t-friday" class="t-big">Friday</div>
      </div>
      <div id="slash"></div>
      <div id="badge" class="glass"><img src="assets/mark.png" alt="" /><span>BLACK FRIDAY <b>WE'RE OPEN</b></span></div>
      <div id="chip1" class="chip glass"><div class="pin"></div><span>BANDERA RD LOCATION</span></div>
      <div id="chip2" class="chip glass"><div class="pin"></div><span>BANDERA RD</span></div>
      <div id="ding">DING!</div>
      <div id="est" class="glass"><div class="l1" id="est1">STOP BY FOR YOUR</div><div class="l2" id="est2">FREE ESTIMATE</div></div>
      <div id="cap-stage">
"""
js = []
A = lambda s: js.append("      " + s)
# hook title: reveal on Marcos's words
t_open, t_black, t_fri = t_of("open"), t_of("black"), t_of("friday")
A(f'tl.fromTo("#veil", {{opacity: 0}}, {{opacity: 1, duration: 0.35, ease: "power2.out"}}, 0);')
A(f'tl.fromTo("#t-open", {{opacity: 0, y: 38, filter: "blur(14px)"}}, {{opacity: 1, y: 0, filter: "blur(0px)", duration: 0.5, ease: "cubic.out"}}, 0.12);')
for sel, t in (("#t-black", t_black), ("#t-friday", t_fri)):
    A(f'tl.fromTo("{sel}", {{opacity: 0, y: 44, scale: 1.22, filter: "blur(18px)"}}, '
      f'{{opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.55, ease: "cubic.out"}}, {t - 0.1:.2f});')
A('tl.set("#slash", {scaleX: 0}, 0);'); A(f'tl.to("#slash", {{scaleX: 1, duration: 0.32, ease: "expo.out"}}, {t_fri + 0.15:.2f});')
A(f'tl.fromTo("#title", {{x: 0}}, {{keyframes: [{{x: -8}}, {{x: 7}}, {{x: -4}}, {{x: 0}}], duration: 0.22, ease: "none"}}, {t_fri + 0.12:.2f});')
g = HOOK_END - 0.05
A(f'tl.to("#title", {{y: -130, scale: 0.36, opacity: 0, duration: 0.5, ease: "power3.in"}}, {g:.2f});')
A(f'tl.to("#slash", {{opacity: 0, duration: 0.3}}, {g:.2f});')
A(f'tl.to("#veil", {{opacity: 0, duration: 0.5}}, {g + 0.1:.2f});')
A(f'tl.fromTo("#badge", {{opacity: 0, y: -30}}, {{opacity: 1, y: 0, duration: 0.45, ease: "back.out(1.6)"}}, {g + 0.35:.2f});')
A(f'tl.to("#badge", {{opacity: 0, y: -24, duration: 0.3, ease: "power2.in"}}, {END0 - 0.1:.2f});')
# location chips
def chip(sel, t, out):
    A(f'tl.fromTo("{sel}", {{opacity: 0, scale: 0.6, y: 20}}, {{opacity: 1, scale: 1, y: 0, duration: 0.5, ease: "back.out(2.2)"}}, {t:.2f});')
    A(f'tl.to("{sel}", {{opacity: 0, y: -14, duration: 0.25, ease: "power2.in"}}, {out:.2f});')
chip("#chip1", t_of("bandera") - 0.05, B["shop"]["start"] + 1.6)
chip("#chip2", t_of("bandera", 17) - 0.05, END0 - 0.15)
# DING!
td = t_of("ding")
A(f'tl.fromTo("#ding", {{opacity: 0, scale: 0.2, rotation: -24}}, {{opacity: 1, scale: 1, rotation: -9, duration: 0.42, ease: "back.out(3)"}}, {td - 0.04:.2f});')
A(f'tl.to("#ding", {{keyframes: [{{x: -10}}, {{x: 9}}, {{x: -6}}, {{x: 4}}, {{x: 0}}], duration: 0.3, ease: "none"}}, {td + 0.3:.2f});')
A(f'tl.to("#ding", {{opacity: 0, scale: 1.25, duration: 0.25, ease: "power2.in"}}, {B["est"]["start"] - 0.1:.2f});')
# free estimate card
ts, tf = t_of("stop"), t_of("free", 11.0)
A(f'tl.fromTo("#est", {{opacity: 0, y: 70, scale: 0.92}}, {{opacity: 1, y: 0, scale: 1, duration: 0.5, ease: "back.out(1.7)"}}, {ts - 0.15:.2f});')
A(f'tl.fromTo("#est1", {{opacity: 0, y: 16}}, {{opacity: 1, y: 0, duration: 0.3, ease: "power2.out"}}, {ts - 0.05:.2f});')
A(f'tl.fromTo("#est2", {{opacity: 0, scale: 0.5}}, {{opacity: 1, scale: 1, duration: 0.55, ease: "elastic.out(1, 0.55)"}}, {tf - 0.05:.2f});')
A(f'tl.to("#est", {{opacity: 0, y: -40, duration: 0.3, ease: "power2.in"}}, {B["crazy"]["start"] + 0.35:.2f});')
A(f'tl.to("#badge", {{opacity: 0, y: -20, duration: 0.2, ease: "power2.in"}}, {ts - 0.25:.2f});')
A(f'tl.to("#badge", {{opacity: 1, y: 0, duration: 0.35, ease: "back.out(1.6)"}}, {B["crazy"]["start"] + 0.6:.2f});')
# accident flash
ta = t_of("accident")
A(f'tl.fromTo("#flash", {{opacity: 0}}, {{keyframes: [{{opacity: 1, duration: 0.08}}, {{opacity: 0, duration: 0.5}}], ease: "power2.out"}}, {ta:.2f});')
# captions
hidden = [(B["est"]["start"], B["crazy"]["start"] + 0.35)]   # the estimate card already shows those words
for i, ch in enumerate(chunks):
    s, e = ch[0][1], (chunks[i + 1][0][1] if i + 1 < len(chunks) and chunks[i + 1][0][1] - ch[-1][2] < 0.5 else ch[-1][2] + 0.5)
    e = max(e, s + 0.7)
    if i + 1 < len(chunks): e = min(e, chunks[i + 1][0][1] - 0.06)
    e = min(e, END0 - 0.05)
    if any(a <= s < b for a, b in hidden): continue
    words = "".join(f'<span class="w{" bf" if re.sub(chr(92)+"W","",w).lower() in ("black","friday") else ""}" id="c{i}w{j}">{esc(re.sub(r"[,.]$", "", w))}</span>'
                    for j, (w, _, _) in enumerate(ch))
    body += f'        <div id="cap-{i}" class="cap"><div class="glass">{words}</div></div>\n'
    A(f'tl.fromTo("#cap-{i}", {{opacity: 0, scale: 0.86, y: 22}}, {{opacity: 1, scale: 1, y: 0, duration: 0.28, ease: "back.out(2.4)"}}, {s - 0.04:.2f});')
    for j, (w, ws, we) in enumerate(ch):
        A(f'tl.set("#c{i}w{j}", {{color: "#FF2129"}}, {ws:.2f}); tl.set("#c{i}w{j}", {{color: "#ffffff"}}, {max(we, ws + 0.12):.2f});')
    A(f'tl.to("#cap-{i}", {{opacity: 0, duration: 0.1}}, {e - 0.1:.2f}); tl.set("#cap-{i}", {{visibility: "hidden"}}, {e:.2f});')
body += "      </div>\n"
# end card
body += f"""      <div id="endcard" class="glass">
        <img id="e0" class="e" src="assets/logo.png" alt="Certified Collision Center" />
        <div id="e1" class="e">Visit our website for a</div>
        <div id="e2" class="e">FREE ESTIMATE</div>
        <div id="e3" class="e">CERTIFIEDCOLLISIONSA.COM</div>
        <div id="e4" class="e">OPEN BLACK FRIDAY · BANDERA RD</div>
      </div>
    </div>"""
A(f'tl.fromTo("#endcard", {{opacity: 0, y: 260}}, {{opacity: 1, y: 0, duration: 0.6, ease: "back.out(1.4)"}}, {END0 + 0.05:.2f});')
for k, sel in enumerate(("#e0", "#e1", "#e2", "#e3", "#e4")):
    A(f'tl.fromTo("{sel}", {{opacity: 0, y: 30}}, {{opacity: 1, y: 0, duration: 0.4, ease: "cubic.out"}}, {END0 + 0.3 + 0.11 * k:.2f});')

overlay = f"""<template>
  <style>{css}  </style>
  <div id="root" data-composition-id="overlay" data-width="1080" data-height="1920">
{body}
  </div>
  <script>
    (() => {{
      const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
      window.__timelines["overlay"] = tl;
    }})();
  </script>
</template>
"""
open("hf/compositions/overlay.html", "w").write(overlay)

# root: base video with a gentle push-in per beat and punch-ins on "ding" and "accident"
push = []
for b in E["beats"]:
    d = round(b["end"] - b["start"], 3)
    push.append(f'      tl.set("#base", {{scale: 1}}, {b["start"]}); tl.to("#base", {{scale: 1.035, duration: {d}, ease: "sine.inOut"}}, {b["start"]});')
for t in (td, ta):
    push.append(f'      tl.to("#basewrap", {{keyframes: [{{scale: 1.04, duration: 0.07}}, {{scale: 1.0, duration: 0.45}}], ease: "power2.out"}}, {t:.2f});')
index = f"""<!doctype html>
<html lang="en" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: {INK}; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; }}
      #basewrap {{ position: absolute; inset: 0; transform-origin: 50% 40%; z-index: 1; }}
      #base {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; transform-origin: 50% 35%; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
      <div id="basewrap">
        <video id="base" class="clip" src="assets/base.mp4" data-start="0" data-duration="{DUR}" data-track-index="0"
          playsinline data-has-audio="true" data-volume="1"></video>
      </div>
      <div id="overlay" data-composition-id="overlay" data-composition-src="compositions/overlay.html" data-start="0" data-duration="{DUR}"
        data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920" style="z-index:2"></div>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
{chr(10).join(push)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open("hf/index.html", "w").write(index)
print(f"overlay: {len(chunks)} caption chunks, {DUR}s")
