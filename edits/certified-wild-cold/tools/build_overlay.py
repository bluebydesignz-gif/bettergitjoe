"""Overlay for Certified Wild: cold weather tips (coolant, black ice, tire pressure).
usage: python3 tools/build_overlay.py  (run from edits/certified-wild-cold; reads edl.json + words.json)
Every card mirrors Marcos's own words. Brand: Barlow only, red #E01B22, ink #0B0B0C, chrome #C9CDD2, bolted logo.
"""
import json, html, re

E = json.load(open("edl.json")); B = {b["id"]: b for b in E["beats"]}
W = json.load(open("words.json")); DUR = E["duration"]; esc = html.escape
FIX = {"and": "in the", "arrange.": "rain."}            # transcriber misheard the last words ("in the rain")
W = [[FIX.get(w, w) if s > 25.2 else w, s, e] for w, s, e in W]
RED, CHROME, HOT, ICE = "#E01B22", "#C9CDD2", "#ff4a50", "#BFE6FF"
st = lambda k: B[k]["start"]; en = lambda k: B[k]["end"]
def t_of(word, after=0.0):
    for w, s, e in W:
        if re.sub(r"\W", "", w).lower() == word.lower() and s >= after: return s
    raise SystemExit(f"word {word} not found after {after}")
END0 = st("tail")

# captions (everything after the hook)
cap_words = [w for w in W if st("cool1") - 0.05 <= w[1] < END0]
chunks, cur = [], []
for w, s, e in cap_words:
    full = len(cur) == 4 or (len(cur) == 3 and sum(len(x[0]) for x in cur) + len(w) > 17)
    cut = any(cur and cur[-1][1] < b["start"] <= s + 0.05 for b in E["beats"])
    if cur and (full or cut or s - cur[-1][2] > 0.3 or re.search(r"[,.?!]$", cur[-1][0])):
        chunks.append(cur); cur = []
    cur.append((w, s, e))
if cur: chunks.append(cur)

css = f"""
    @font-face {{ font-family: "Barlow"; font-weight: 900; src: url("assets/fonts/Barlow-Black.ttf"); }}
    @font-face {{ font-family: "Barlow"; font-weight: 800; src: url("assets/fonts/Barlow-ExtraBold.ttf"); }}
    @font-face {{ font-family: "Barlow"; font-weight: 700; src: url("assets/fonts/Barlow-Bold.ttf"); }}
    @font-face {{ font-family: "BarlowC"; font-weight: 900; src: url("assets/fonts/BarlowCondensed-Black.ttf"); }}
    #ov {{ position: absolute; inset: 0; color: #fff; overflow: hidden; }}
    .glass {{ background: rgba(11,11,12,.6); backdrop-filter: blur(24px) saturate(1.45); -webkit-backdrop-filter: blur(24px) saturate(1.45);
      border: 2px solid rgba(255,255,255,.43); box-shadow: inset 0 2px 0 rgba(255,255,255,.28), 0 18px 50px rgba(0,0,0,.35); }}
    #frost {{ position: absolute; inset: 0; opacity: 0; background:
      radial-gradient(ellipse 120% 60% at 50% 0%, rgba(190,230,255,.55), rgba(190,230,255,0) 55%),
      radial-gradient(ellipse 140% 50% at 50% 100%, rgba(190,230,255,.35), rgba(190,230,255,0) 60%); }}
    .flake {{ position: absolute; top: -40px; border-radius: 50%; background: #fff; opacity: 0; box-shadow: 0 0 10px rgba(255,255,255,.8); }}
    #title {{ position: absolute; left: 0; right: 0; top: 300px; text-align: center; transform-origin: 50% 0%; }}
    #t1 {{ display: inline-flex; align-items: center; gap: 22px; font-family: "Barlow"; font-weight: 900; font-size: 58px; letter-spacing: .22em; opacity: 0; }}
    #t1 i {{ display: block; width: 80px; height: 7px; background: {RED}; border-radius: 4px; }}
    .big {{ font-family: "BarlowC"; font-weight: 900; line-height: .88; text-transform: uppercase; opacity: 0; }}
    #t2 {{ font-size: 230px; margin-top: 8px; color: #fff; text-shadow: 0 0 40px rgba(170,220,255,.9), 0 10px 30px rgba(0,0,0,.55); }}
    #t3 {{ font-size: 150px; background: linear-gradient(180deg, #ffffff 0%, {ICE} 50%, #6FB8F0 100%); -webkit-background-clip: text; background-clip: text;
      color: transparent; filter: drop-shadow(0 10px 24px rgba(0,0,0,.6)); }}
    #badge {{ position: absolute; top: 255px; left: 0; right: 0; margin: 0 auto; width: fit-content; display: flex; align-items: center;
      gap: 16px; padding: 14px 30px 14px 22px; border-radius: 999px; white-space: nowrap; opacity: 0; }}
    #badge.glass {{ background: rgba(11,11,12,.72); }}
    #badge img {{ height: 46px; }}
    #badge span {{ font-family: "Barlow"; font-weight: 900; font-size: 32px; letter-spacing: .05em; }}
    #badge b {{ color: #ff6a70; }}
    .tip {{ position: absolute; left: 60px; right: 60px; top: 300px; border-radius: 34px; padding: 22px 30px 24px; display: flex; align-items: center;
      gap: 24px; opacity: 0; }}
    .tip .n {{ flex: none; width: 104px; height: 104px; border-radius: 26px; background: {RED}; display: flex; align-items: center; justify-content: center;
      font-family: "BarlowC"; font-weight: 900; font-size: 74px; box-shadow: 0 8px 22px rgba(224,27,34,.5); }}
    .tip .tx .k {{ font-family: "Barlow"; font-weight: 800; font-size: 28px; letter-spacing: .22em; color: {CHROME}; }}
    .tip .tx .h {{ font-family: "BarlowC"; font-weight: 900; font-size: 64px; line-height: .95; text-transform: uppercase; }}
    .tip .ck {{ flex: none; margin-left: auto; width: 76px; height: 76px; border-radius: 50%; background: #2BB673; display: flex; align-items: center;
      justify-content: center; transform: scale(0); box-shadow: 0 6px 18px rgba(43,182,115,.5); }}
    .tip .ck::after {{ content: ""; width: 30px; height: 15px; border-left: 8px solid #fff; border-bottom: 8px solid #fff; transform: translateY(-4px) rotate(-45deg); }}
    #cap-stage {{ position: absolute; left: 70px; right: 70px; top: 1200px; height: 0; }}
    .cap {{ position: absolute; left: 0; right: 0; top: 0; display: flex; justify-content: center; opacity: 0; }}
    .cap .glass {{ padding: 16px 34px 18px; border-radius: 30px; font-family: "Barlow"; font-weight: 900; font-size: 66px;
      line-height: 1.05; text-transform: uppercase; white-space: nowrap; }}
    .cap .w {{ display: inline-block; margin: 0 .12em; }}
    #endcard {{ position: absolute; left: 70px; right: 70px; top: 760px; border-radius: 44px; padding: 34px 40px 36px; text-align: center; opacity: 0; }}
    #endcard img {{ width: 400px; height: auto; display: block; margin: 0 auto 10px; }}
    #endcard .e {{ opacity: 0; }}
    #e1 {{ font-family: "Barlow"; font-weight: 700; font-size: 38px; }}
    #e2 {{ font-family: "BarlowC"; font-weight: 900; font-size: 98px; line-height: .95; color: {HOT}; }}
    #e3 {{ font-family: "Barlow"; font-weight: 800; font-size: 36px; letter-spacing: .08em; margin-top: 8px; }}
    #e4 {{ font-family: "Barlow"; font-weight: 800; font-size: 28px; letter-spacing: .14em; color: {CHROME}; margin-top: 12px; }}
"""
TIPS = [("1", "Tip one", "Proper coolant,|not water", st("cool1"), en("cool2"), t_of("engine")),
        ("2", "Tip two", "Careful for|black ice", st("ice"), en("ice"), t_of("road")),
        ("3", "Tip three", "Tires filled to|necessary air pressure", st("tire1"), en("diff"), t_of("pressure"))]
flakes = [(int(60 + (i * 97) % 960), 8 + (i * 7) % 14, 0.9 + ((i * 13) % 10) / 10, ((i * 29) % 100) / 100) for i in range(36)]
body = '    <div id="ov">\n      <div id="frost"></div>\n'
body += "".join(f'      <div class="flake" id="f{i}" style="left:{x}px; width:{s}px; height:{s}px"></div>\n' for i, (x, s, _, _) in enumerate(flakes))
body += """      <div id="title"><div id="t1"><i></i>I KNOW THE<i></i></div><div id="t2" class="big">Cold Weather</div><div id="t3" class="big">Is Coming</div></div>
      <div id="badge" class="glass"><img src="assets/mark.png" alt="" /><span>WHAT'S <b>CERTIFIED WILD</b> THIS WEEK?</span></div>
"""
for n, k, h, *_ in TIPS:
    body += (f'      <div class="tip glass" id="tip{n}"><div class="n">{n}</div><div class="tx"><div class="k">{esc(k.upper())}</div>'
             f'<div class="h">{"<br />".join(esc(x) for x in h.split("|"))}</div></div><div class="ck"></div></div>\n')
body += '      <div id="cap-stage">\n'
js = []; A = lambda s: js.append("      " + s)
# hook: frost + snow + title on his words
tc, tco = t_of("cold"), t_of("coming")
A('tl.fromTo("#frost", {opacity: 0}, {opacity: 1, duration: 0.5}, 0);')
A(f'tl.to("#frost", {{opacity: 0, duration: 0.5}}, {st("cool1") - 0.1:.2f});')
for i, (x, s, sp, ph) in enumerate(flakes):
    t0 = ph * 0.8; d = 2.6 / sp
    A(f'tl.fromTo("#f{i}", {{opacity: 0.9, y: 0, x: 0}}, {{y: 2000, x: {((i * 41) % 120) - 60}, duration: {d:.2f}, ease: "none"}}, {t0:.2f}); tl.set("#f{i}", {{opacity: 0}}, {min(t0 + d, st("cool1") + 0.4):.2f});')
A('tl.fromTo("#t1", {opacity: 0, y: 38, filter: "blur(14px)"}, {opacity: 1, y: 0, filter: "blur(0px)", duration: 0.4, ease: "cubic.out"}, 0.0);')
for sel, t in (("#t2", tc), ("#t3", tco)):
    A(f'tl.fromTo("{sel}", {{opacity: 0, y: 44, scale: 1.22, filter: "blur(18px)"}}, {{opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.45, ease: "cubic.out"}}, {max(t - 0.12, 0.05):.2f});')
A(f'tl.fromTo("#title", {{x: 0}}, {{keyframes: [{{x: -8}}, {{x: 7}}, {{x: -4}}, {{x: 0}}], duration: 0.22, ease: "none"}}, {tco + 0.2:.2f});')
A(f'tl.to("#title", {{y: -130, scale: 0.36, opacity: 0, duration: 0.4, ease: "power3.in"}}, {st("cool1") + 0.05:.2f});')
# tips: banner up top, check pops on the word that ends each tip
prev_out = 0
for n, k, h, a, b, tdone in TIPS:
    tin = max(a + 0.15, prev_out + 0.32); tout = max(b - 0.3, tdone + 0.55)
    A(f'tl.fromTo("#tip{n}", {{opacity: 0, y: -50, scale: 0.94}}, {{opacity: 1, y: 0, scale: 1, duration: 0.45, ease: "back.out(1.7)"}}, {tin:.2f});')
    A(f'tl.fromTo("#tip{n} .ck", {{scale: 0}}, {{scale: 1, duration: 0.5, ease: "back.out(3)"}}, {tdone - 0.2:.2f});')
    A(f'tl.to("#tip{n}", {{opacity: 0, y: -40, duration: 0.3, ease: "power2.in"}}, {tout:.2f});')
    prev_out = tout
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
push = [f'      tl.set("#base", {{scale: 1}}, {b["start"]}); tl.to("#base", {{scale: 1.035, duration: {round(b["end"] - b["start"], 3)}, ease: "sine.inOut"}}, {b["start"]});'
        for b in E["beats"]]
open("hf/index.html", "w").write(f"""<!doctype html>
<html lang="en" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #0B0B0C; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; }}
      #base {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; transform-origin: 50% 35%; z-index: 1; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
      <video id="base" class="clip" src="assets/base.mp4" data-start="0" data-duration="{DUR}" data-track-index="0"
        playsinline data-has-audio="true" data-volume="1"></video>
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
json.dump({"stamp": tco + 0.2, "title": [0.0, tc - 0.12, tco - 0.12], "rows": [t[5] - 0.2 for t in TIPS], "end": END0,
           "myth": st("cool1") + 0.15, "list": st("ice") + 0.15}, open("cues.json", "w"), indent=1)
print(f"overlay: {len(chunks)} caption chunks, {DUR}s")
