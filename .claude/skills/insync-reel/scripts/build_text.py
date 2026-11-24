"""Generate the INSYNC HyperFrames text layer from src/<slug>/timeline.json.

usage: python3 build_text.py <timeline.json> <hf_dir> [--clean] [--night]

House rules baked in (BRAND.md, INSYNC Brand Rules):
  - Anton all caps headlines in solid cobalt #146BDE; Manrope Bold support text in ink #111317
  - every text block sits on clear refractive liquid glass; only the background bends
  - no periods on screen (except inside a web address), no em or en dashes, no white outlines
  - safe area on 1080x1920: top 250, right 150, left 64; key text above y 1330 (Instagram overlay)
  - entrances 9 frames from the top or a side on a long ease-out; setup text clears before a punchline
  - CTA = approved logo (unaltered) + "Start your intake" + insynccredit.com
--clean keeps only the CTA. --night uses the stronger glass tint for dark footage.
"""
import json, os, re, sys, html

tl_path, hf = sys.argv[1], sys.argv[2]
clean, night = "--clean" in sys.argv, "--night" in sys.argv
T = json.load(open(tl_path)); FPS = T["fps"]; DUR = round(T["durationInFrames"] / FPS, 3)
sec = lambda f: round(f / FPS, 3)
ov = [dict(o, start=sec(o["from"]), len=sec(o["dur"])) for o in T["overlays"]]
by = lambda t: [o for o in ov if o["type"] == t]
COBALT, MIDNIGHT, WARM, INK = "#146BDE", "#05070A", "#F7F4EE", "#111317"
SAFE = dict(top=250, right=150, bottom=400, left=64)   # brand doc
IG_LOW = 1330   # Instagram draws its caption and buttons below this line: key text stays above it
BOX_W = 1080 - SAFE["left"] - SAFE["right"]          # 866 px usable width
TINT = 0.74 if night else 0.62                        # glass tint: cobalt on glass needs >= 3:1
TINT_STRONG = 0.86 if night else 0.80                 # small CTA and disclaimer text

# ---------------------------------------------------------------- copy checks
URL = re.compile(r"\b[\w-]+\.(com|net|org|co)\b", re.I)
def clean_copy(s, where):
    if re.search("[–—]", s):
        sys.exit(f"STOP: {where} has an em or en dash: {s!r}. Rewrite the line without it.")
    masked = URL.sub(lambda m: m.group(0).replace(".", "\0"), s)
    masked = re.sub(r"\.(?=\s|$|\|)", "", masked)      # sentence periods go
    if "." in masked:
        sys.exit(f"STOP: {where} still has a period mid-line: {s!r}. Rewrite it.")
    return masked.replace("\0", ".")
RISKY = re.compile(r"\b(guarantee\w*|\d+\s*(pts?|points)|score (jump|increase)|delete\w* (all|every)|remove\w* (all|every)|"
                   r"fix\w* your credit (fast|in))\b", re.I)
def results_check(s, o):
    if RISKY.search(s) and not o.get("verified"):
        sys.exit(f"STOP: {s!r} reads as a result or promise. Use it only with verified facts and client "
                 f"authorization, then mark the overlay \"verified\": true (adds the disclaimer).")

esc = html.escape
FACES = """
    @font-face { font-family: "Anton"; font-weight: 400; src: url("assets/fonts/Anton-Regular.ttf"); }
    @font-face { font-family: "Manrope"; font-weight: 200 800; src: url("assets/fonts/Manrope[wght].ttf"); }
"""
def glass_svg(fid):
    # Refraction map: only the footage behind the panel bends (displacement 42, frequency 0.008/0.012).
    return f"""    <svg width="0" height="0" style="position:absolute">
      <filter id="{fid}" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">
        <feTurbulence type="fractalNoise" baseFrequency="0.008 0.012" numOctaves="2" seed="7" result="n" />
        <feGaussianBlur in="n" stdDeviation="2" result="nb" />
        <feDisplacementMap in="SourceGraphic" in2="nb" scale="42" xChannelSelector="R" yChannelSelector="G" />
      </filter>
    </svg>"""
def glass_css(fid, tint):
    return f"""    .glass {{ position: absolute; border-radius: 38px; overflow: hidden;
      background: rgba(247,244,238,{tint});
      backdrop-filter: url(#{fid}) blur(0.65px) saturate(1.2) brightness(1.05);
      box-shadow: inset 0 2px 0 rgba(255,255,255,.95), inset 0 -1.5px 0 rgba(255,255,255,.45),
        inset 0 0 0 1.5px rgba(255,255,255,.6), 0 14px 34px rgba(5,7,10,.24); }}
    .glass .sheen {{ position: absolute; top: -20%; bottom: -20%; width: 46%; left: -50%;
      background: linear-gradient(105deg, rgba(255,255,255,0) 0%, rgba(255,255,255,.28) 50%, rgba(255,255,255,0) 100%); }}
    .glass .in {{ position: relative; }}"""

def scene(cid, css, body, js, tint=TINT):
    fid = f"{cid}-lg"
    return f"""<template>
  <style>{FACES}
    #root {{ position: absolute; inset: 0; }}
{glass_css(fid, tint)}
{css}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="1080" data-height="1920">
{glass_svg(fid)}
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
    os.makedirs(os.path.join(hf, "compositions"), exist_ok=True)
    open(os.path.join(hf, "compositions", name + ".html"), "w").write(text)

IN = 0.3   # 9 frames
def enter(sel, at, frm="top"):
    v = {"top": "y: -46", "left": "x: -60", "right": "x: 60"}[frm]
    return f'      tl.fromTo("{sel}", {{ opacity: 0, {v} }}, {{ opacity: 1, x: 0, y: 0, duration: {IN}, ease: "expo.out" }}, {at});\n'
def leave(sel, at):
    return f'      tl.to("{sel}", {{ opacity: 0, duration: 0.17, ease: "power2.in" }}, {at});\n'
def sheen(sel, at, d):
    return f'      tl.fromTo("{sel} .sheen", {{ xPercent: 0 }}, {{ xPercent: 330, duration: {max(d, 1.5)}, ease: "none" }}, {at});\n'

disclaimers = []

# ---------------------------------------------------------------- headlines (hooks, punchlines, name supers)
if not clean:
    items = sorted(by("hook") + by("name"), key=lambda o: o["start"])
    if items:
        first = items[0]["start"]; last = max(o["start"] + o["len"] for o in items)
        css = f"""    .hl {{ left: {SAFE['left']}px; max-width: {BOX_W}px; padding: 26px 40px 30px; }}
    .hl-line {{ font-family: "Anton"; font-size: 112px; line-height: 1.0; color: {COBALT}; text-transform: uppercase;
      letter-spacing: .005em; white-space: nowrap; }}
    .hl-sub {{ font-family: "Manrope"; font-weight: 700; font-size: 38px; line-height: 1.25; color: {INK}; margin-top: 10px; }}"""
        body, js = "", ""
        for i, o in enumerate(items):
            ls = round(o["start"] - first, 3); cid = f"hl-{i}"
            if o["type"] == "name":
                lines = [clean_copy(o["name"], "name")]; sub = clean_copy(o.get("role", ""), "role")
                top = o.get("top", 800); size = 84
            else:
                lines = [clean_copy(l, "hook") for l in o["lines"]]; sub = clean_copy(o.get("sub", ""), "hook sub")
                for l in lines + [sub]: results_check(l, o)
                top = o.get("top", SAFE["top"] + 30); size = o.get("size", 112)
            if o.get("verified"): disclaimers.append((o["start"], o["len"]))
            # name supers sit over people (dark clothes): use the strong tint so cobalt keeps 3:1
            tint_css = f"; background: rgba(247,244,238,{TINT_STRONG})" if (o["type"] == "name" or o.get("strong")) else ""
            longest = max(len(l) for l in lines)
            size = min(size, int((BOX_W - 80) / (0.42 * max(longest, 1))))   # Anton is ~0.42 em per glyph
            body += f"""    <div id="{cid}" class="clip" data-start="{ls}" data-duration="{o['len']}">
      <div id="{cid}-g" class="glass hl" style="top:{top}px{tint_css}"><div class="sheen"></div><div class="in">
{chr(10).join(f'        <div class="hl-line" style="font-size:{size}px">{esc(l)}</div>' for l in lines)}
{f'        <div class="hl-sub">{esc(sub)}</div>' if sub else ''}
      </div></div>
    </div>
"""
            js += enter(f"#{cid}-g", ls, o.get("enter", "top" if o["type"] == "hook" else "left"))
            js += sheen(f"#{cid}-g", ls, o["len"])
            js += leave(f"#{cid}-g", round(ls + o["len"] - 0.17, 3))
        write("headlines", scene("headlines", css, body.rstrip("\n"), js.rstrip("\n")))
        host("headlines", first, round(last - first, 3), track=2)

# ---------------------------------------------------------------- captions (speech)
if not clean:
    caps = sorted(by("caption"), key=lambda o: o["start"])
    if caps:
        css = f"""    #cap-stage {{ position: absolute; left: {SAFE['left']}px; width: {BOX_W}px; bottom: {1920 - IG_LOW + 176}px; height: 0; }}
    .cap {{ position: absolute; left: 0; right: 0; bottom: 0; display: flex; justify-content: center; opacity: 0; }}
    .cap .glass {{ position: relative; padding: 18px 34px 20px; border-radius: 30px; }}
    .cap-t {{ font-family: "Manrope"; font-weight: 700; font-size: 44px; line-height: 1.24; color: {INK}; text-align: center;
      text-wrap: balance; }}"""
        body = '    <div id="cap-stage">\n'; js = ""
        for i, o in enumerate(caps):
            text = clean_copy(o["text"], "caption"); results_check(text, o)
            if o.get("verified"): disclaimers.append((o["start"], o["len"]))
            lines = "<br />".join(esc(x) for x in text.split("|"))
            s, e_ = o["start"], round(o["start"] + o["len"], 3)
            body += f'      <div id="cap-{i}" class="cap"><div class="glass"><div class="sheen"></div><div class="in cap-t">{lines}</div></div></div>\n'
            js += f"""      tl.fromTo("#cap-{i}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.12, ease: "power2.out" }}, {s});
      tl.to("#cap-{i}", {{ opacity: 0, duration: 0.12, ease: "power2.in" }}, {round(e_ - 0.12, 3)});
      tl.set("#cap-{i}", {{ visibility: "hidden" }}, {e_});
"""
        body += "    </div>"
        write("captions", scene("captions", css, body, js.rstrip("\n"))); host("captions", 0, DUR, kind="captions", track=3)

# ---------------------------------------------------------------- disclaimer (any verified result or testimonial)
if disclaimers and not clean:
    s0 = min(a for a, _ in disclaimers); s1 = max(a + b for a, b in disclaimers)
    css = f"""    #disc {{ left: {SAFE['left']}px; width: {BOX_W}px; top: {IG_LOW - 160}px; padding: 10px 22px; border-radius: 18px; }}
    #disc .in {{ font-family: "Manrope"; font-weight: 700; font-size: 28px; color: {INK}; text-align: center; }}"""
    body = f"""    <div id="disc-clip" class="clip" data-start="0" data-duration="{round(s1 - s0, 3)}">
      <div id="disc" class="glass"><div class="sheen"></div><div class="in">Individual results vary and aren't guaranteed</div></div>
    </div>"""
    js = enter("#disc", 0, "left")
    write("disclaimer", scene("disclaimer", css, body, js.rstrip("\n"), tint=TINT_STRONG)); host("disclaimer", s0, round(s1 - s0, 3), track=4)

# ---------------------------------------------------------------- CTA end card
cta = by("cta")
if cta:
    o = cta[0]; d = round(DUR - o["start"], 3)
    line1 = clean_copy(o.get("line1", "Start your intake"), "cta"); site = o.get("site", "insynccredit.com")
    css = f"""    #cta-dim {{ position: absolute; inset: 0; background: {MIDNIGHT}; opacity: 0; }}
    #cta {{ left: 107px; width: 866px; top: {o.get('top', 760)}px; padding: 54px 60px 50px; text-align: center; }}
    #cta-logo {{ width: 640px; height: auto; display: block; margin: 0 auto; }}
    #cta-l1 {{ font-family: "Anton"; font-size: 92px; line-height: 1; color: {COBALT}; text-transform: uppercase; margin-top: 40px; }}
    #cta-l2 {{ font-family: "Manrope"; font-weight: 800; font-size: 44px; color: {INK}; margin-top: 18px; letter-spacing: .01em; }}"""
    body = f"""    <div id="cta-clip" class="clip" data-start="0" data-duration="{d}">
      <div id="cta-dim"></div>
      <div id="cta" class="glass"><div class="sheen"></div><div class="in">
        <img id="cta-logo" src="assets/logo.png" alt="INSYNC Credit Repair" />
        <div id="cta-l1">{esc(line1)}</div>
        <div id="cta-l2">{esc(site)}</div>
      </div></div>
    </div>"""
    js = f"""      tl.fromTo("#cta-dim", {{ opacity: 0 }}, {{ opacity: {o.get('dim', 0.25)}, duration: 0.4, ease: "power2.inOut" }}, 0);
{enter('#cta', 0.1, 'top')}{sheen('#cta', 0.1, d)}      tl.fromTo("#cta-l1", {{ opacity: 0, y: -24 }}, {{ opacity: 1, y: 0, duration: {IN}, ease: "expo.out" }}, 0.4);
      tl.fromTo("#cta-l2", {{ opacity: 0, y: -24 }}, {{ opacity: 1, y: 0, duration: {IN}, ease: "expo.out" }}, 0.52);"""
    write("cta", scene("cta", css, body, js, tint=TINT_STRONG)); host("cta", o["start"], d, track=5)

# ---------------------------------------------------------------- root
index = f"""<!doctype html>
<html lang="en" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: {MIDNIGHT}; }}
      #root {{ position: relative; width: 100%; height: 100%; }}
      #base {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: contain; z-index: 1; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
      <!-- picture cut and sound, rendered without text by Remotion -->
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
print(f"wrote {'clean' if clean else 'primary'} INSYNC text layer: {len(hosts)} scenes, {DUR}s"
      + (f", disclaimer on {len(disclaimers)} item(s)" if disclaimers else ""))
