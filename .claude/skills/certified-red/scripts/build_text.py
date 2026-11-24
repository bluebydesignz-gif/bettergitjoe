"""Generate the HyperFrames text layer (hf/) from src/<slug>/timeline.json.

usage: python3 build_text.py <timeline.json> <hf_dir> [--clean]

Type system (one family, three roles):
  display  Barlow Condensed Black, uppercase   title, THANK YOU
  label    Barlow Condensed ExtraBold + Barlow SemiBold   name, dog line, credits
  caption  Barlow Bold, sentence case, dark scrim sized to the text   speech
Everything readable sits inside the Reels safe band (y 168 to 1330).
"""
import json, os, sys, html
from PIL import ImageFont

tl_path, hf = sys.argv[1], sys.argv[2]
clean = "--clean" in sys.argv
T = json.load(open(tl_path)); FPS = T["fps"]; DUR = round(T["durationInFrames"] / FPS, 3)
sec = lambda f: round(f / FPS, 3)
ov = [dict(o, start=sec(o["from"]), len=sec(o["dur"])) for o in T["overlays"]]
by = lambda t: [o for o in ov if o["type"] == t]
esc = html.escape
RED, INK = "#E01B22", "#0B0B0C"

def fit(text, font, width, tracking=0.0):
    """Font size (px) at which `text` is exactly `width` px wide."""
    f = ImageFont.truetype(os.path.join(hf, "assets/fonts", font), 400)
    w = f.getlength(text) + tracking * 400 * len(text)
    return int(400 * width / w)

FACES = """
    @font-face { font-family: "Barlow Condensed"; font-weight: 900; src: url("assets/fonts/BarlowCondensed-Black.ttf"); }
    @font-face { font-family: "Barlow Condensed"; font-weight: 800; src: url("assets/fonts/BarlowCondensed-ExtraBold.ttf"); }
    @font-face { font-family: "Barlow"; font-weight: 800; src: url("assets/fonts/Barlow-ExtraBold.ttf"); }
    @font-face { font-family: "Barlow"; font-weight: 700; src: url("assets/fonts/Barlow-Bold.ttf"); }
    @font-face { font-family: "Barlow"; font-weight: 600; src: url("assets/fonts/Barlow-SemiBold.ttf"); }
    @font-face { font-family: "Barlow"; font-weight: 500; src: url("assets/fonts/Barlow-Medium.ttf"); }
"""
SHADOW = "0 2px 14px rgba(0,0,0,.55), 0 1px 2px rgba(0,0,0,.5)"

def scene(cid, css, body, js):
    return f"""<template>
  <style>{FACES}
    #root {{ position: absolute; inset: 0; color: #fff; }}
{css}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="1080" data-height="1920">
{body}
  </div>
  <script>
    (() => {{
      const tl = gsap.timeline({{ paused: true }});
{js}
      window.__timelines["{cid}"] = tl;
    }})();
  </script>
</template>
"""

hosts = []
def host(cid, start, dur, kind="graphics", track=1):
    hosts.append(f'      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" '
                 f'data-start="{start}" data-duration="{dur}" data-track-index="{track}" data-track-kind="{kind}" '
                 f'data-width="1080" data-height="1920" style="z-index:{track + 1}"></div>')

def write(name, text):
    open(os.path.join(hf, "compositions", name + ".html"), "w").write(text)

# ---------------------------------------------------------------- title
if not clean and by("title"):
    t = by("title")[0]; d = t["len"]; W = 840
    l1, l2, sub = t["line1"].upper(), t["line2"].upper(), t["eyebrow"].upper()
    s1, s2 = fit(l1, "BarlowCondensed-Black.ttf", W, 0.005), fit(l2, "BarlowCondensed-Black.ttf", W, 0.005)
    css = f"""    #title-scrim {{ position: absolute; inset: 0; opacity: 0;
      background: linear-gradient(180deg, rgba(11,11,12,.72) 0%, rgba(11,11,12,.5) 26%, rgba(11,11,12,0) 50%); }}
    #title-block {{ position: absolute; left: 120px; width: {W}px; top: 300px; text-align: center; }}
    .title-mask {{ overflow: hidden; }}
    .title-line {{ font-family: "Barlow Condensed"; font-weight: 900; line-height: .92; letter-spacing: .005em;
      white-space: nowrap; text-shadow: {SHADOW}; }}
    #title-l1 {{ font-size: {s1}px; }}
    #title-l2 {{ font-size: {s2}px; }}
    #title-rule {{ width: 96px; height: 6px; margin: 30px auto 24px; background: {RED}; }}
    #title-sub {{ font-family: "Barlow"; font-weight: 700; font-size: 44px; letter-spacing: .22em; margin-right: -.22em;
      text-shadow: {SHADOW}; }}"""
    body = f"""    <div id="title-clip" class="clip" data-start="0" data-duration="{d}">
      <div id="title-scrim"></div>
      <div id="title-block">
        <div class="title-mask" data-layout-allow-overflow><div id="title-l1" class="title-line">{esc(l1)}</div></div>
        <div class="title-mask" data-layout-allow-overflow><div id="title-l2" class="title-line">{esc(l2)}</div></div>
        <div id="title-rule"></div>
        <div id="title-sub">{esc(sub)}</div>
      </div>
    </div>"""
    out = round(d - 0.28, 3)
    js = f"""      tl.fromTo("#title-scrim", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.6, ease: "power2.out" }}, 0);
      tl.fromTo("#title-l1", {{ yPercent: 104 }}, {{ yPercent: 0, duration: 0.8, ease: "expo.out" }}, 0.05);
      tl.fromTo("#title-l2", {{ yPercent: 104 }}, {{ yPercent: 0, duration: 0.8, ease: "expo.out" }}, 0.15);
      tl.fromTo("#title-rule", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.5, ease: "power4.out" }}, 0.5);
      tl.fromTo("#title-sub", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, ease: "power2.out" }}, 0.62);
      tl.to("#title-block", {{ opacity: 0, filter: "blur(8px)", duration: 0.24, ease: "power2.in" }}, {out});
      tl.to("#title-scrim", {{ opacity: 0, duration: 0.26, ease: "power2.in" }}, {out});"""
    write("title", scene("title", css, body, js)); host("title", t["start"], d, track=2)

# ---------------------------------------------------------------- labels (name + dog line)
if not clean and (by("name") or by("label")):
    items = []
    for n in by("name")[:1]:
        items.append(("lab-name", n["start"], n["len"], n["name"].upper(), n["role"], n.get("top", 930)))
    for i, o in enumerate(by("label")):
        items.append((f"lab-{i}", o["start"], o["len"], o["text"].upper(), "", 1100))
    first = min(i[1] for i in items); last = max(i[1] + i[2] for i in items)
    css = f"""    .lab {{ position: absolute; left: 84px; }}
    .lab-scrim {{ position: absolute; left: 0; right: 0; top: 780px; height: 620px; opacity: 0;
      background: linear-gradient(180deg, rgba(11,11,12,0) 0%, rgba(11,11,12,.5) 42%, rgba(11,11,12,.5) 70%, rgba(11,11,12,0) 100%); }}
    .lab-rule {{ width: 64px; height: 6px; background: {RED}; margin-bottom: 14px; }}
    .lab-head {{ font-family: "Barlow Condensed"; font-weight: 800; font-size: 70px; line-height: 1; letter-spacing: .015em;
      white-space: nowrap; text-shadow: {SHADOW}; }}
    .lab-sub {{ font-family: "Barlow"; font-weight: 600; font-size: 33px; line-height: 1.2; margin-top: 8px; text-shadow: {SHADOW}; }}"""
    body, js = "", ""
    for cid, st, ln, head, sub, top in items:
        ls = round(st - first, 3)
        body += f"""    <div id="{cid}" class="clip" data-start="{ls}" data-duration="{ln}">
      <div id="{cid}-scrim" class="lab-scrim" style="top:{max(top - 150, 0)}px"></div>
      <div id="{cid}-in" class="lab" style="top:{top}px">
        <div id="{cid}-rule" class="lab-rule"></div>
        <div id="{cid}-head" class="lab-head">{esc(head)}</div>
        {f'<div id="{cid}-sub" class="lab-sub">{esc(sub)}</div>' if sub else ''}
      </div>
    </div>
"""
        js += f"""      tl.fromTo("#{cid}-scrim", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, ease: "power2.out" }}, {ls});
      tl.fromTo("#{cid}-rule", {{ scaleX: 0, transformOrigin: "0 50%" }}, {{ scaleX: 1, duration: 0.45, ease: "power4.out" }}, {ls});
      tl.fromTo("#{cid}-head", {{ opacity: 0, x: -28 }}, {{ opacity: 1, x: 0, duration: 0.55, ease: "power4.out" }}, {round(ls + 0.08, 3)});
"""
        if sub:
            js += f"""      tl.fromTo("#{cid}-sub", {{ opacity: 0, x: -28 }}, {{ opacity: 1, x: 0, duration: 0.55, ease: "power4.out" }}, {round(ls + 0.17, 3)});
"""
        js += f"""      tl.to(["#{cid}-in", "#{cid}-scrim"], {{ opacity: 0, duration: 0.22, ease: "power2.in" }}, {round(ls + ln - 0.26, 3)});
"""
    write("labels", scene("labels", css, body.rstrip("\n"), js.rstrip("\n"))); host("labels", first, round(last - first, 3), track=3)

# ---------------------------------------------------------------- captions (speech)
if not clean:
    caps = sorted(by("caption"), key=lambda o: o["start"])
    css = """    #cap-stage { position: absolute; left: 0; right: 0; bottom: 690px; height: 0; }
    .cap { position: absolute; left: 90px; right: 90px; bottom: 0; text-align: center; opacity: 0; }
    .cap span { display: inline-block; padding: 14px 30px 16px; border-radius: 14px; background: rgba(11,11,12,.68);
      font-family: "Barlow"; font-weight: 700; font-size: 47px; line-height: 1.22; text-wrap: balance; }"""
    body = '    <div id="cap-stage">\n'; js = ""
    for i, o in enumerate(caps):
        text = "<br />".join(esc(x) for x in o["text"].split("|"))
        s, e_ = o["start"], round(o["start"] + o["len"], 3)
        body += f'      <div id="cap-{i}" class="cap"><span>{text}</span></div>\n'
        js += f"""      tl.fromTo("#cap-{i}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.12, ease: "power2.out" }}, {s});
      tl.to("#cap-{i}", {{ opacity: 0, duration: 0.12, ease: "power2.in" }}, {round(e_ - 0.12, 3)});
      tl.set("#cap-{i}", {{ visibility: "hidden" }}, {e_});
"""
    body += "    </div>"
    write("captions", scene("captions", css, body, js.rstrip("\n"))); host("captions", 0, DUR, kind="captions", track=4)

# ---------------------------------------------------------------- finale (thank you + end card)
th, en = (by("thanks") or [None])[0], by("endcard")[0]
has_th = th is not None and not clean            # single-speaker episodes have no thank-you card
f0 = th["start"] if has_th else en["start"]; fd = round(DUR - f0, 3)
e0 = round(en["start"] - f0, 3); el = round(DUR - en["start"], 3)
proud = en["proud"].split("|"); s_a, s_b = [x.strip() + "." for x in en["slogan"].rstrip(".").split(". ")]
css = f"""    #fin-dim {{ position: absolute; inset: 0; background: {INK}; opacity: 0; }}
    #fin-thanks {{ position: absolute; left: 0; right: 0; top: 600px; text-align: center; }}
    #fin-ty {{ font-family: "Barlow Condensed"; font-weight: 900; font-size: 212px; line-height: .95; letter-spacing: .005em; }}
    #fin-ty-rule {{ width: 96px; height: 6px; margin: 30px auto 30px; background: {RED}; }}
    .fin-credit {{ font-family: "Barlow"; font-weight: 600; font-size: 36px; line-height: 1.6; letter-spacing: .14em; margin-right: -.14em; }}
    #fin-card {{ position: absolute; left: 0; right: 0; top: {640 if clean else 460}px; text-align: center; }}
    #fin-logo {{ width: 700px; height: auto; }}
    .fin-proud {{ font-family: "Barlow"; font-weight: 500; font-size: 46px; line-height: 1.3; }}
    #fin-proud {{ margin-top: 44px; }}
    #fin-rule {{ width: 96px; height: 6px; margin: 38px auto 34px; background: {RED}; }}
    .fin-mask {{ overflow: hidden; }}
    .fin-slogan {{ font-family: "Barlow"; font-weight: 800; font-size: 66px; line-height: 1.16; letter-spacing: -.005em; }}
    #fin-s2 {{ color: #FF2A31; }}"""
body = '    <div id="fin-dim-clip" class="clip" data-start="0" data-duration="{0}"><div id="fin-dim"></div></div>\n'.format(fd)
js = ""
if has_th:
    body += f"""    <div id="fin-thanks-clip" class="clip" data-start="0" data-duration="{th['len']}">
      <div id="fin-thanks">
        <div id="fin-ty">{esc(th['head'].upper())}</div>
        <div id="fin-ty-rule"></div>
        <div id="fin-credits">
{chr(10).join(f'          <div class="fin-credit" id="fin-c{i}">{esc(l.upper())}</div>' for i, l in enumerate(th['lines']))}
        </div>
      </div>
    </div>
"""
    js += f"""      tl.fromTo("#fin-dim", {{ opacity: 0 }}, {{ opacity: 0.74, duration: 0.6, ease: "power2.inOut" }}, 0);
      tl.fromTo("#fin-ty", {{ opacity: 0, filter: "blur(14px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.45, ease: "power3.out" }}, 0.35);
      tl.fromTo("#fin-ty-rule", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.45, ease: "power4.out" }}, 0.6);
      tl.fromTo(".fin-credit", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.35, ease: "power2.out", stagger: 0.09 }}, 0.72);
      tl.to("#fin-thanks", {{ opacity: 0, filter: "blur(8px)", duration: 0.24, ease: "power2.in" }}, {round(th['len'] - 0.28, 3)});
      tl.to("#fin-dim", {{ opacity: 1, duration: 0.5, ease: "power2.inOut" }}, {round(e0 - 0.3, 3)});
"""
else:
    js += f"""      tl.fromTo("#fin-dim", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.7, ease: "power2.inOut" }}, 0);
"""
body += f"""    <div id="fin-card-clip" class="clip" data-start="{e0}" data-duration="{el}">
      <div id="fin-card">
        <img id="fin-logo" src="assets/logo.png" alt="Certified Collision Center" />
{'' if clean else f'''        <div id="fin-proud">
{chr(10).join(f'          <div class="fin-proud">{esc(l)}</div>' for l in proud)}
        </div>
'''}        <div id="fin-rule"></div>
        <div class="fin-mask" data-layout-allow-overflow><div id="fin-s1" class="fin-slogan">{esc(s_a)}</div></div>
        <div class="fin-mask" data-layout-allow-overflow><div id="fin-s2" class="fin-slogan">{esc(s_b)}</div></div>
      </div>
    </div>"""
k = e0 + (0.15 if has_th else 0.45)
js += f"""      tl.fromTo("#fin-logo", {{ opacity: 0, filter: "blur(10px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.55, ease: "power3.out" }}, {round(k + 0.1, 3)});
"""
if not clean:
    js += f"""      tl.fromTo("#fin-proud", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5, ease: "power2.out" }}, {round(k + 0.55, 3)});
"""
js += f"""      tl.fromTo("#fin-rule", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.45, ease: "power4.out" }}, {round(k + 1.0, 3)});
      tl.fromTo("#fin-s1", {{ yPercent: 104 }}, {{ yPercent: 0, duration: 0.8, ease: "expo.out" }}, {round(k + 1.15, 3)});
      tl.fromTo("#fin-s2", {{ yPercent: 104 }}, {{ yPercent: 0, duration: 0.8, ease: "expo.out" }}, {round(k + 1.27, 3)});"""
write("finale", scene("finale", css, body, js)); host("finale", f0, fd, track=5)

# ---------------------------------------------------------------- root
index = f"""<!doctype html>
<html lang="en" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: {INK}; }}
      #root {{ position: relative; width: 100%; height: 100%; }}
      #base {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: contain; z-index: 1; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
      <!-- picture cut and natural-sound mix, rendered without text by Remotion (TurkeyBase) -->
      <video id="base" class="clip" src="assets/base.mp4" data-start="0" data-duration="{DUR}" data-track-index="0"
        playsinline data-has-audio="true" data-volume="1"></video>
{chr(10).join(hosts)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""
open(os.path.join(hf, "index.html"), "w").write(index)
print(f"wrote {'clean' if clean else 'primary'} text layer: {len(hosts)} scenes, {DUR}s")
