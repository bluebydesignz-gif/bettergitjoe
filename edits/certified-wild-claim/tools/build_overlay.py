"""Overlay for Certified Wild: "You don't have to file your claim alone".
usage: python3 tools/build_overlay.py  (run from edits/certified-wild-claim; reads edl.json + words.json)
Every card mirrors Marcos's own words. Brand: Barlow only, red #E01B22, ink #0B0B0C, chrome #C9CDD2, bolted logo.
"""
import json, html, re

E = json.load(open("edl.json")); B = {b["id"]: b for b in E["beats"]}
W = json.load(open("words.json")); DUR = E["duration"]; esc = html.escape
RED, INK, CHROME, HOT = "#E01B22", "#0B0B0C", "#C9CDD2", "#ff4a50"
st = lambda k: B[k]["start"]; en = lambda k: B[k]["end"]
def t_of(word, after=0.0):
    for w, s, e in W:
        if re.sub(r"\W", "", w).lower() == word.lower() and s >= after: return s
    raise SystemExit(f"word {word} not found after {after}")
END0 = st("tail")

# captions only where no card already shows the words
SHOW = [(st("here") - 0.05, en("here")), (st("close") - 0.05, END0)]
cap_words = [w for w in W if any(a <= w[1] < b for a, b in SHOW)]
chunks, cur = [], []
for w, s, e in cap_words:
    full = len(cur) == 4 or (len(cur) == 3 and sum(len(x[0]) for x in cur) + len(w) > 17)
    if cur and (full or s - cur[-1][2] > 0.3 or re.search(r"[,.?!]$", cur[-1][0])
                or any(a <= s and cur[-1][1] < a for a, _ in SHOW)):
        chunks.append(cur); cur = []
    cur.append((w, s, e))
if cur: chunks.append(cur)

css = f"""
    @font-face {{ font-family: "Barlow"; font-weight: 900; src: url("assets/fonts/Barlow-Black.ttf"); }}
    @font-face {{ font-family: "Barlow"; font-weight: 800; src: url("assets/fonts/Barlow-ExtraBold.ttf"); }}
    @font-face {{ font-family: "Barlow"; font-weight: 700; src: url("assets/fonts/Barlow-Bold.ttf"); }}
    @font-face {{ font-family: "BarlowC"; font-weight: 900; src: url("assets/fonts/BarlowCondensed-Black.ttf"); }}
    #ov {{ position: absolute; inset: 0; color: #fff; overflow: hidden; }}
    .glass {{ background: rgba(11,11,12,.56); backdrop-filter: blur(24px) saturate(1.45); -webkit-backdrop-filter: blur(24px) saturate(1.45);
      border: 2px solid rgba(255,255,255,.43); box-shadow: inset 0 2px 0 rgba(255,255,255,.28), 0 18px 50px rgba(0,0,0,.35); }}
    #veil {{ position: absolute; left: 0; right: 0; top: 0; height: 900px; opacity: 0;
      background: linear-gradient(180deg, rgba(0,0,0,.62) 0%, rgba(0,0,0,.35) 55%, rgba(0,0,0,0) 100%); }}
    #title {{ position: absolute; left: 0; right: 0; top: 300px; text-align: center; transform-origin: 50% 0%; }}
    #t1 {{ display: inline-flex; align-items: center; gap: 22px; font-family: "Barlow"; font-weight: 900; font-size: 58px;
      letter-spacing: .22em; opacity: 0; }}
    #t1 i {{ display: block; width: 80px; height: 7px; background: {RED}; border-radius: 4px; }}
    .big {{ font-family: "BarlowC"; font-weight: 900; line-height: .88; text-transform: uppercase; opacity: 0; text-shadow: 0 10px 36px rgba(0,0,0,.55); }}
    #t2 {{ font-size: 240px; margin-top: 10px; }}
    #t3 {{ font-size: 128px; background: linear-gradient(180deg, #ff3a40 0%, {RED} 55%, #b3121a 100%); -webkit-background-clip: text;
      background-clip: text; color: transparent; filter: drop-shadow(0 10px 24px rgba(0,0,0,.6)); }}
    #badge {{ position: absolute; top: 255px; left: 0; right: 0; margin: 0 auto; width: fit-content; display: flex; align-items: center;
      gap: 16px; padding: 14px 30px 14px 22px; border-radius: 999px; white-space: nowrap; opacity: 0; }}
    #badge img {{ height: 46px; }}
    #badge.glass {{ background: rgba(11,11,12,.72); }}
    #badge span {{ font-family: "Barlow"; font-weight: 900; font-size: 32px; letter-spacing: .05em; }}
    #badge b {{ color: #ff6a70; }}
    #myth {{ position: absolute; left: 80px; right: 80px; top: 300px; border-radius: 40px; padding: 40px 44px 44px; text-align: center; opacity: 0; }}
    #myth .q {{ font-family: "Barlow"; font-weight: 900; font-size: 64px; line-height: 1.08; text-transform: uppercase; position: relative; display: inline-block; }}
    #strike {{ position: absolute; left: -10px; right: -10px; top: 50%; height: 12px; background: {RED}; border-radius: 6px;
      transform-origin: 0 50%; box-shadow: 0 0 22px rgba(224,27,34,.7); }}
    #stamp {{ position: absolute; left: 0; right: 0; margin: 0 auto; width: fit-content; top: 520px; padding: 10px 30px 6px; border: 8px solid {HOT};
      border-radius: 18px; font-family: "BarlowC"; font-weight: 900; font-size: 104px; line-height: 1; color: {HOT}; transform: rotate(-7deg);
      opacity: 0; background: rgba(11,11,12,.55); }}
    #list {{ position: absolute; left: 60px; right: 60px; top: 270px; border-radius: 40px; padding: 30px 40px 34px; opacity: 0; }}
    #list .h {{ font-family: "Barlow"; font-weight: 900; font-size: 40px; letter-spacing: .14em; color: {CHROME}; text-align: center; margin-bottom: 18px; }}
    .row {{ display: flex; align-items: center; gap: 22px; margin-top: 14px; opacity: 0; }}
    .row .ck {{ flex: none; width: 62px; height: 62px; border-radius: 50%; background: {RED}; display: flex; align-items: center; justify-content: center;
      box-shadow: 0 6px 18px rgba(224,27,34,.5); }}
    .row .ck::after {{ content: ""; width: 26px; height: 13px; border-left: 7px solid #fff; border-bottom: 7px solid #fff; transform: translateY(-3px) rotate(-45deg); }}
    .row span {{ font-family: "Barlow"; font-weight: 900; font-size: 46px; line-height: 1.02; text-transform: uppercase; }}
    #cap-stage {{ position: absolute; left: 70px; right: 70px; top: 1200px; height: 0; }}
    .cap {{ position: absolute; left: 0; right: 0; top: 0; display: flex; justify-content: center; opacity: 0; }}
    .cap .glass {{ padding: 16px 34px 18px; border-radius: 30px; font-family: "Barlow"; font-weight: 900; font-size: 66px;
      line-height: 1.05; text-transform: uppercase; white-space: nowrap; }}
    .cap .w {{ display: inline-block; margin: 0 .12em; }}
    #endcard {{ position: absolute; left: 70px; right: 70px; top: 800px; border-radius: 44px; padding: 34px 40px 36px; text-align: center; opacity: 0; }}
    #endcard img {{ width: 400px; height: auto; display: block; margin: 0 auto 10px; }}
    #endcard .e {{ opacity: 0; }}
    #e1 {{ font-family: "Barlow"; font-weight: 700; font-size: 38px; }}
    #e2 {{ font-family: "BarlowC"; font-weight: 900; font-size: 98px; line-height: .95; color: {HOT}; }}
    #e3 {{ font-family: "Barlow"; font-weight: 800; font-size: 36px; letter-spacing: .08em; margin-top: 8px; }}
    #e4 {{ font-family: "Barlow"; font-weight: 800; font-size: 28px; letter-spacing: .14em; color: {CHROME}; margin-top: 12px; }}
"""
ROWS = [("walk", 0, "Walk you through the process"), ("coordinate", 0, "Coordinate with your insurance"),
        ("rental", 0, "Coordinate rental cars"), ("schedule", 0, "Coordinate with your schedule")]
body = f"""    <div id="ov">
      <div id="veil"></div>
      <div id="title"><div id="t1"><i></i>ONE OF THE<i></i></div><div id="t2" class="big">Biggest</div><div id="t3" class="big">Misconceptions</div></div>
      <div id="badge" class="glass"><img src="assets/mark.png" alt="" /><span>WHAT'S <b>CERTIFIED WILD</b> THIS WEEK?</span></div>
      <div id="myth" class="glass"><div class="q" id="mq">You have to file your<br />insurance claim alone<div id="strike"></div></div></div>
      <div id="stamp">MISCONCEPTION</div>
      <div id="list" class="glass"><div class="h" id="lh">WE'D BE GLAD TO HELP YOU</div>
{chr(10).join(f'        <div class="row" id="r{i}"><div class="ck"></div><span>{esc(t)}</span></div>' for i, (_, _, t) in enumerate(ROWS))}
      </div>
      <div id="cap-stage">
"""
js = []; A = lambda s: js.append("      " + s)
# hook
tb, tm = t_of("biggest"), t_of("misconceptions")
A('tl.set("#strike", {scaleX: 0}, 0);')
A(f'tl.fromTo("#veil", {{opacity: 0}}, {{opacity: 1, duration: 0.35}}, 0);')
A(f'tl.fromTo("#t1", {{opacity: 0, y: 38, filter: "blur(14px)"}}, {{opacity: 1, y: 0, filter: "blur(0px)", duration: 0.45, ease: "cubic.out"}}, 0.02);')
for sel, t in (("#t2", tb), ("#t3", tm)):
    A(f'tl.fromTo("{sel}", {{opacity: 0, y: 44, scale: 1.22, filter: "blur(18px)"}}, {{opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.5, ease: "cubic.out"}}, {t - 0.1:.2f});')
A(f'tl.fromTo("#title", {{x: 0}}, {{keyframes: [{{x: -8}}, {{x: 7}}, {{x: -4}}, {{x: 0}}], duration: 0.22, ease: "none"}}, {tm + 0.25:.2f});')
A(f'tl.to("#title", {{y: -130, scale: 0.36, opacity: 0, duration: 0.45, ease: "power3.in"}}, {st("myth") - 0.1:.2f});')
A(f'tl.to("#veil", {{opacity: 0, duration: 0.5}}, {st("myth") + 0.1:.2f});')
# misconception card: the claim appears, then gets struck and stamped
ty, ta = t_of("you", st("myth")), t_of("alone")
A(f'tl.fromTo("#myth", {{opacity: 0, y: 60, scale: 0.94}}, {{opacity: 1, y: 0, scale: 1, duration: 0.45, ease: "back.out(1.7)"}}, {ty - 0.2:.2f});')
A(f'tl.to("#strike", {{scaleX: 1, duration: 0.3, ease: "expo.out"}}, {ta + 0.05:.2f});')
A(f'tl.to("#mq", {{opacity: 0.55, duration: 0.3}}, {ta + 0.1:.2f});')
A(f'tl.fromTo("#stamp", {{opacity: 0, scale: 2.4, rotation: -18}}, {{opacity: 1, scale: 1, rotation: -7, duration: 0.32, ease: "power4.in"}}, {ta + 0.15:.2f});')
A(f'tl.to("#stamp", {{keyframes: [{{x: -9}}, {{x: 8}}, {{x: -4}}, {{x: 0}}], duration: 0.22, ease: "none"}}, {ta + 0.47:.2f});')
A(f'tl.to(["#myth", "#stamp"], {{opacity: 0, y: -40, duration: 0.3, ease: "power2.in"}}, {st("here") + 0.2:.2f});')
# series badge while he talks, out of the way of the cards
for a, b in ((st("here") + 0.3, st("list1") - 0.2), (st("close") + 0.3, END0 - 0.1)):
    A(f'tl.fromTo("#badge", {{opacity: 0, y: -30}}, {{opacity: 1, y: 0, duration: 0.45, ease: "back.out(1.6)", immediateRender: false}}, {a:.2f});')
    A(f'tl.to("#badge", {{opacity: 0, y: -24, duration: 0.25, ease: "power2.in"}}, {b:.2f});')
# checklist: each row ticks on the word he says it
rt = [t_of("walk"), t_of("coordinate"), t_of("rental"), t_of("schedule")]
rt[3] = t_of("coordinate", t_of("rental"))   # "and coordinate with your schedule"
A(f'tl.fromTo("#list", {{opacity: 0, y: 60, scale: 0.94}}, {{opacity: 1, y: 0, scale: 1, duration: 0.45, ease: "back.out(1.6)"}}, {st("list1") - 0.05:.2f});')
A(f'tl.fromTo("#lh", {{opacity: 0}}, {{opacity: 1, duration: 0.3}}, {st("list1") + 0.1:.2f});')
for i, t in enumerate(rt):
    A(f'tl.fromTo("#r{i}", {{opacity: 0, x: -50}}, {{opacity: 1, x: 0, duration: 0.35, ease: "cubic.out"}}, {t - 0.08:.2f});')
    A(f'tl.fromTo("#r{i} .ck", {{scale: 0}}, {{scale: 1, duration: 0.45, ease: "back.out(3)"}}, {t - 0.02:.2f});')
A(f'tl.to("#list", {{opacity: 0, y: -40, duration: 0.3, ease: "power2.in"}}, {st("close") + 0.35:.2f});')
# captions
for i, ch in enumerate(chunks):
    s = ch[0][1]; e = ch[-1][2] + 0.5
    e = max(e, s + 0.7)
    if i + 1 < len(chunks): e = min(e, chunks[i + 1][0][1] - 0.06)
    e = min(e, END0 - 0.05)
    words = "".join(f'<span class="w" id="c{i}w{j}">{esc(re.sub(r"[,.]$", "", w))}</span>' for j, (w, _, _) in enumerate(ch))
    body += f'        <div id="cap-{i}" class="cap"><div class="glass">{words}</div></div>\n'
    A(f'tl.fromTo("#cap-{i}", {{opacity: 0, scale: 0.86, y: 22}}, {{opacity: 1, scale: 1, y: 0, duration: 0.25, ease: "back.out(2.4)"}}, {s - 0.04:.2f});')
    for j, (w, ws, we) in enumerate(ch):
        A(f'tl.set("#c{i}w{j}", {{color: "#FF2129"}}, {ws:.2f}); tl.set("#c{i}w{j}", {{color: "#ffffff"}}, {max(we, ws + 0.12):.2f});')
    A(f'tl.to("#cap-{i}", {{opacity: 0, duration: 0.1}}, {e - 0.1:.2f}); tl.set("#cap-{i}", {{visibility: "hidden"}}, {e:.2f});')
body += """      </div>
      <div id="endcard" class="glass">
        <img id="e0" class="e" src="assets/logo.png" alt="Certified Collision Center" />
        <div id="e1" class="e">Visit our website for a</div>
        <div id="e2" class="e">FREE ESTIMATE</div>
        <div id="e3" class="e">CERTIFIEDCOLLISIONSA.COM</div>
        <div id="e4" class="e">BANDERA · HUEBNER · KIRBY</div>
      </div>
    </div>"""
A(f'tl.fromTo("#endcard", {{opacity: 0, y: 260}}, {{opacity: 1, y: 0, duration: 0.6, ease: "back.out(1.4)"}}, {END0 + 0.05:.2f});')
for k, sel in enumerate(("#e0", "#e1", "#e2", "#e3", "#e4")):
    A(f'tl.fromTo("{sel}", {{opacity: 0, y: 30}}, {{opacity: 1, y: 0, duration: 0.4, ease: "cubic.out"}}, {END0 + 0.3 + 0.11 * k:.2f});')

open("hf/compositions/overlay.html", "w").write(f"""<template>
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
""")
push = []
for b in E["beats"]:
    push.append(f'      tl.set("#base", {{scale: 1}}, {b["start"]}); tl.to("#base", {{scale: 1.035, duration: {round(b["end"] - b["start"], 3)}, ease: "sine.inOut"}}, {b["start"]});')
push.append(f'      tl.to("#basewrap", {{keyframes: [{{scale: 1.04, duration: 0.07}}, {{scale: 1.0, duration: 0.45}}], ease: "power2.out"}}, {ta + 0.45:.2f});')
open("hf/index.html", "w").write(f"""<!doctype html>
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
""")
json.dump({"stamp": ta + 0.15, "title": [0.02, tb - 0.1, tm - 0.1], "rows": rt, "end": END0, "myth": ty - 0.2, "list": st("list1") - 0.05},
          open("cues.json", "w"), indent=1)
print(f"overlay: {len(chunks)} caption chunks, {DUR}s")
