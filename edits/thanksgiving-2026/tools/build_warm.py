"""Thanksgiving overlay (v3 look): natural color, polaroid-to-life transitions, clean kinetic type,
a polaroid collage and a soft end card. Deliberately unlike the red-bar Certified Red text system.

usage: python3 tools/build_warm.py   (run from edits/thanksgiving-2026; reads ../../src/thanksgiving-2026/timeline.json)
writes hf/index.html and hf/compositions/warm.html. Every quote is the speaker's own words.
"""
import json, html
T = json.load(open("../../src/thanksgiving-2026/timeline.json")); FPS = T["fps"]
DUR = round(T["durationInFrames"] / FPS, 3)
S = {s["id"]: (s["from"] / FPS, (s["from"] + s["dur"]) / FPS) for s in T["segments"]}
st = lambda k: round(S[k][0], 3); en = lambda k: round(S[k][1], 3)
esc = html.escape
CREAM, GOLD, RED, INK = "#FFFFFF", "#FF5A4E", "#E01B22", "#0B0B0C"

css = f"""
    @font-face {{ font-family: "Barlow"; font-weight: 800; src: url("assets/fonts/Barlow-ExtraBold.ttf"); }}
    @font-face {{ font-family: "Barlow"; font-weight: 700; src: url("assets/fonts/Barlow-Bold.ttf"); }}
    @font-face {{ font-family: "Barlow"; font-weight: 600; src: url("assets/fonts/Barlow-SemiBold.ttf"); }}
    @font-face {{ font-family: "BarlowC"; font-weight: 900; src: url("assets/fonts/BarlowCondensed-Black.ttf"); }}
    #w {{ position: absolute; inset: 0; overflow: hidden; color: {CREAM}; }}
    /* film look */
    #flash {{ position: absolute; inset: 0; background: #FFFFFF; opacity: 0; }}
    .tveil {{ position: absolute; inset: 0; background: rgba(10,10,12,.55); opacity: 0; }}
    .tcard {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; border: 46px solid #FBF7EF; border-bottom-width: 190px;
      background: #FBF7EF; opacity: 0; transform-origin: 50% 50%; box-shadow: 0 40px 90px rgba(0,0,0,.55); }}
    .tcard img {{ display: block; width: 100%; height: 100%; object-fit: cover; }}
    /* type */
    .soft {{ text-shadow: 0 4px 22px rgba(0,0,0,.6), 0 2px 4px rgba(0,0,0,.55); }}
    #hello {{ position: absolute; left: 0; right: 0; top: 520px; text-align: center; }}
    #h1 {{ font-family: "Barlow"; font-weight: 800; font-size: 64px; letter-spacing: .32em; margin-right: -.32em; opacity: 0; }}
    #h2 {{ font-family: "BarlowC"; font-weight: 900; font-size: 150px; line-height: .9; text-transform: uppercase; opacity: 0;
      color: #FFF3DF; text-shadow: 0 0 34px rgba(0,0,0,.35), 0 6px 18px rgba(0,0,0,.7); }}
    #h3 {{ font-family: "Barlow"; font-weight: 700; font-size: 40px; letter-spacing: .14em; margin-top: 22px; opacity: 0; }}
    .word {{ position: absolute; left: 0; right: 0; text-align: center; opacity: 0; }}
    .word .a {{ font-family: "Barlow"; font-weight: 600; font-size: 50px; letter-spacing: .26em; margin-right: -.26em; display: block; }}
    .word .b {{ font-family: "BarlowC"; font-weight: 900; font-size: 150px; line-height: .95; text-transform: uppercase; display: block; }}
    .q {{ position: absolute; left: 80px; right: 80px; top: 1010px; text-align: center; font-family: "Barlow"; font-weight: 800; font-size: 60px;
      line-height: 1.18; opacity: 0; }}
    .q .who {{ display: block; font-size: 30px; font-weight: 800; letter-spacing: .3em; color: {GOLD}; margin-bottom: 12px; }}
    .q .ln {{ display: inline-block; }}
    /* collage */
    .pol {{ position: absolute; width: 440px; padding: 18px 18px 64px; background: #FBF7EF; border-radius: 6px; opacity: 0;
      box-shadow: 0 22px 50px rgba(30,10,0,.45), 0 2px 4px rgba(0,0,0,.2); }}
    .pol img {{ display: block; width: 404px; height: 404px; object-fit: cover; }}
    #feat {{ position: absolute; left: 0; right: 0; top: 330px; margin: 0 auto; width: 700px; padding: 26px 26px 0; background: #FBF7EF;
      border-radius: 8px; opacity: 0; box-shadow: 0 34px 80px rgba(0,0,0,.55), 0 2px 4px rgba(0,0,0,.25); }}
    #feat img {{ display: block; width: 648px; height: 810px; object-fit: cover; }}
    #feat .cap {{ font-family: "Barlow"; font-weight: 700; font-size: 38px; color: #2A2A2E; text-align: center; padding: 26px 0 32px; }}
    #outt {{ position: absolute; left: 0; right: 0; top: 300px; text-align: center; opacity: 0; }}
    #outt span {{ display: inline-block; padding: 14px 34px 12px; border-radius: 999px; background: rgba(10,10,12,.55); backdrop-filter: blur(14px);
      font-family: "Barlow"; font-weight: 800; font-size: 40px; letter-spacing: .3em; margin-right: -.3em; color: #FFFFFF; }}
    #coll-veil {{ position: absolute; inset: 0; background: rgba(10,10,12,.35); backdrop-filter: blur(16px); opacity: 0; }}
    #coll-t {{ position: absolute; left: 0; right: 0; top: 1240px; text-align: center; opacity: 0; }}
    #coll-t .a {{ font-family: "Barlow"; font-weight: 600; font-size: 46px; letter-spacing: .26em; margin-right: -.26em; }}
    #coll-t .b {{ font-family: "BarlowC"; font-weight: 900; font-size: 140px; line-height: .95; color: {CREAM}; }}
    /* ending */
    #love {{ position: absolute; left: 0; right: 0; top: 300px; text-align: center; }}
    #love div {{ opacity: 0; }}
    #l1, #l2 {{ font-family: "BarlowC"; font-weight: 900; font-size: 86px; line-height: 1; text-transform: uppercase; }}
    #l1 span, #l2 span {{ color: {GOLD}; }}
    #end-veil {{ position: absolute; inset: 0; background: radial-gradient(ellipse at 50% 45%, rgba(10,10,12,.55), rgba(5,5,6,.88)); opacity: 0; }}
    #end {{ position: absolute; left: 0; right: 0; top: 560px; text-align: center; }}
    #end > * {{ opacity: 0; }}
    #e-logo {{ width: 620px; display: block; margin: 0 auto; }}
    #e-h {{ font-family: "BarlowC"; font-weight: 900; font-size: 100px; line-height: .95; margin-top: 34px; text-transform: uppercase;
      color: #FFF3DF; text-shadow: 0 0 34px rgba(0,0,0,.35), 0 6px 18px rgba(0,0,0,.7); }}
    #e-s {{ font-family: "Barlow"; font-weight: 700; font-size: 40px; margin-top: 20px; letter-spacing: .04em; }}
    #e-s b {{ color: #FF5A4E; }}
"""
js = []; A = lambda s: js.append("      " + s)
# warm flashes on the fast cuts
for k in ("m2", "m3", "m4", "m5", "m6", "m7", "b2", "b3", "b4", "b5", "b6"):          # camera-flash on the fast montage cuts
    A(f'tl.fromTo("#flash", {{opacity: 0.5}}, {{opacity: 0, duration: 0.25, ease: "power2.out", immediateRender: false}}, {st(k):.2f});')
# polaroid-to-life: a photo of the next scene drops in, then grows until it becomes the live shot
TR = ["m1", "j1", "c1", "f1"]
tr_html = ""
for k in TR:
    T = st(k); r = -7 if k in ("m1", "c1") else 6
    tr_html += f'      <div class="tveil" id="tv_{k}"></div><div class="tcard" id="tc_{k}"><img src="assets/tr/{k}.jpg" alt="" /></div>\n'
    A(f'tl.fromTo("#tv_{k}", {{opacity: 0}}, {{opacity: 1, duration: 0.3}}, {T - 0.8:.2f}); tl.set("#tv_{k}", {{opacity: 0}}, {T:.2f});')
    A(f'tl.fromTo("#tc_{k}", {{opacity: 1, scale: 0.34, rotation: {r * 2}, y: -1500}}, {{opacity: 1, scale: 0.38, rotation: {r}, y: 0, duration: 0.42, ease: "back.out(1.3)", immediateRender: false}}, {T - 0.8:.2f});')
    A(f'tl.to("#tc_{k}", {{scale: 1.14, rotation: 0, duration: 0.38, ease: "power3.inOut"}}, {T - 0.38:.2f});')
    A(f'tl.set("#tc_{k}", {{opacity: 0}}, {T:.2f});')
    A(f'tl.fromTo("#flash", {{opacity: 0.35}}, {{opacity: 0, duration: 0.2, ease: "power2.out", immediateRender: false}}, {T:.2f});')
# opener
A('tl.fromTo("#h1", {opacity: 0, y: 30, scaleX: 1.3}, {opacity: 1, y: 0, scaleX: 1, duration: 0.7, ease: "expo.out"}, 0.15);')
A('tl.fromTo("#h2", {opacity: 0, scale: 1.25, filter: "blur(16px)"}, {opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.7, ease: "expo.out"}, 0.45);')
A('tl.fromTo("#h3", {opacity: 0, y: 20}, {opacity: 1, y: 0, duration: 0.5, ease: "cubic.out"}, 0.95);')
A(f'tl.to("#hello", {{opacity: 0, y: -60, filter: "blur(10px)", duration: 0.35, ease: "power2.in"}}, {en("o1") - 0.3:.2f});')
# montage words
def word(i, t0, t1, a, b, top):
    A(f'tl.fromTo("#wd{i}", {{opacity: 0, y: 40, filter: "blur(12px)"}}, {{opacity: 1, y: 0, filter: "blur(0px)", duration: 0.45, ease: "expo.out"}}, {t0:.2f});')
    A(f'tl.to("#wd{i}", {{opacity: 0, y: -30, filter: "blur(8px)", duration: 0.25, ease: "power2.in"}}, {t1 - 0.25:.2f});')
    return f'      <div class="word soft" id="wd{i}" style="top:{top}px"><span class="a">{esc(a)}</span><span class="b">{esc(b)}</span></div>\n'
words = word(0, st("m1") + 0.1, en("m4") - 0.05, "GRATEFUL FOR", "our community", 1060)
words += word(1, st("m5") + 0.05, en("m7"), "GRATEFUL FOR", "our team", 1060)
# quotes (their own words), line by line
def quote(i, t0, dur, who, lines):
    A(f'tl.fromTo("#q{i}", {{opacity: 0}}, {{opacity: 1, duration: 0.2}}, {t0:.2f});')
    A(f'tl.fromTo("#q{i} .ln", {{opacity: 0, y: 18}}, {{opacity: 1, y: 0, duration: 0.35, ease: "cubic.out", stagger: 0.25}}, {t0:.2f});')
    A(f'tl.to("#q{i}", {{opacity: 0, duration: 0.2}}, {t0 + dur - 0.2:.2f});')
    return (f'      <div class="q soft" id="q{i}"><span class="who">{esc(who)}</span>'
            + "<br />".join(f'<span class="ln">{esc(l)}</span>' for l in lines) + "</div>\n")
j = st("j1")
qs = quote(0, j + 0.12, 2.3, "JOSH", ["“I’m Josh from", "Certified Collision Kirby.”"])
qs += quote(1, j + 2.5, 2.05, "JOSH", ["“This year I’m", "thankful for family.”"])
qs += quote(2, j + 4.6, en("j3") - j - 4.6, "JOSH", ["“Thankful for my son,", "Bruce.”"])
qs += quote(3, st("c1") + 0.02, en("c1") - st("c1"), "CRYSTAL", ["“It’s definitely become a family", "and I couldn’t ask for more.”"])
qs += quote(4, st("k1") + 0.08, en("k1") - st("k1") - 0.08, "MARCOS", ["“And we’re just blessed", "to be a part of it.”"])
# featured photo: volunteering at the Turkey Giveaway
v0, v1e = st("v1"), en("v1")
A(f'tl.fromTo("#feat", {{opacity: 0, scale: 1.5, y: -500, rotation: -14}}, {{opacity: 1, scale: 1, y: 0, rotation: -3, duration: 0.55, ease: "back.out(1.25)"}}, {v0 + 0.05:.2f});')
A(f'tl.to("#feat", {{rotation: -1, y: -14, duration: {v1e - v0 - 0.8:.2f}, ease: "sine.inOut"}}, {v0 + 0.6:.2f});')
A(f'tl.to("#feat", {{opacity: 0, y: 120, rotation: 6, duration: 0.3, ease: "power2.in"}}, {v1e - 0.3:.2f});')
# polaroid collage
pols = [("c1", 560, 300, 7), ("o1", 90, 260, -8), ("m2", 120, 720, 5), ("m7", 530, 760, -6), ("j2", 300, 520, -2)]
c0 = st("cl")
A(f'tl.fromTo("#coll-veil", {{opacity: 0}}, {{opacity: 1, duration: 0.4}}, {c0:.2f});')
pol_html = ""
for i, (img, x, y, r) in enumerate(pols):
    t = c0 + 0.15 + i * 0.42
    pol_html += f'      <div class="pol" id="p{i}" style="left:{x}px; top:{y}px; transform: rotate({r}deg)"><img src="assets/pol/{img}.jpg" alt="" /></div>\n'
    A(f'tl.fromTo("#p{i}", {{opacity: 0, scale: 1.6, y: -120, rotation: {r * 3}}}, {{opacity: 1, scale: 1, y: 0, rotation: {r}, duration: 0.45, ease: "back.out(1.4)"}}, {t:.2f});')
A(f'tl.fromTo("#coll-t", {{opacity: 0, y: 30}}, {{opacity: 1, y: 0, duration: 0.5, ease: "expo.out"}}, {c0 + 1.9:.2f});')
A(f'tl.to(["#coll-veil", ".pol", "#coll-t"], {{opacity: 0, duration: 0.35, ease: "power2.in"}}, {en("cl") - 0.3:.2f});')
# ending on the team photo: Joe's words, then the card
f0 = st("f1")
A(f'tl.fromTo("#l1", {{opacity: 0, y: 30}}, {{opacity: 1, y: 0, duration: 0.5, ease: "expo.out"}}, {f0 + 0.35:.2f});')
A(f'tl.fromTo("#l2", {{opacity: 0, y: 30}}, {{opacity: 1, y: 0, duration: 0.5, ease: "expo.out"}}, {f0 + 1.0:.2f});')
A(f'tl.to("#love", {{opacity: 0, duration: 0.3}}, {f0 + 2.9:.2f});')
A(f'tl.fromTo("#end-veil", {{opacity: 0}}, {{opacity: 1, duration: 0.6, ease: "power2.inOut"}}, {f0 + 2.95:.2f});')
for k, sel in enumerate(("#e-logo", "#e-h", "#e-s")):
    A(f'tl.fromTo("{sel}", {{opacity: 0, y: 30, filter: "blur(10px)"}}, {{opacity: 1, y: 0, filter: "blur(0px)", duration: 0.6, ease: "expo.out"}}, {f0 + 3.2 + 0.25 * k:.2f});')

body = f"""    <div id="w">
      <div id="hello" class="soft"><div id="h1">HAPPY</div><div id="h2">Thanksgiving</div><div id="h3">FROM OUR FAMILY TO YOURS</div></div>
{words}{qs}      <div id="feat"><img src="assets/pol/v1.jpg" alt="" /><div class="cap">Volunteering at the Turkey Giveaway</div></div>
      <div id="coll-veil"></div>
{pol_html}      <div id="coll-t" class="soft"><div class="a">THIS IS OUR</div><div class="b">FAMILY</div></div>
      <div id="love" class="soft"><div id="l1">Grateful for <span>our customers</span></div><div id="l2">Grateful for <span>our team</span></div></div>
      <div id="end-veil"></div>
      <div id="end" class="soft"><img id="e-logo" src="assets/logo.png" alt="Certified Collision Center" />
        <div id="e-h">Happy Thanksgiving</div><div id="e-s">Driven to repair. <b>Committed to care.</b></div></div>
{tr_html}      <div id="flash"></div>
    </div>"""
open("hf/compositions/warm.html", "w").write(f"""<template>
  <style>{css}  </style>
  <div id="root" data-composition-id="warm" data-width="1080" data-height="1920">
{body}
  </div>
  <script>
    (() => {{
      const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
      window.__timelines["warm"] = tl;
    }})();
  </script>
</template>
""")
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
      #base {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; z-index: 1; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
      <video id="base" class="clip" src="assets/base.mp4" data-start="0" data-duration="{DUR}" data-track-index="0"
        playsinline data-has-audio="true" data-volume="1"></video>
      <div id="warm" data-composition-id="warm" data-composition-src="compositions/warm.html" data-start="0" data-duration="{DUR}"
        data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920" style="z-index:2"></div>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
""")
json.dump({"flash": [st(k) for k in ("m2", "m3", "m4", "m5", "m6", "m7", "b2", "b3", "b4", "b5", "b6")], "trans": [st(k) for k in TR], "pols": [c0 + 0.15 + i * 0.42 for i in range(len(pols))] + [st("v1") + 0.1],
           "title": [0.15, 0.45], "end": f0 + 3.2}, open("cues.json", "w"), indent=1)
print(f"warm overlay: {DUR}s")
