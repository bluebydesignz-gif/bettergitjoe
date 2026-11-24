# Cut list (edl.json) fields

Beats and audio work exactly as in the Certified Red skill. Only the overlay types differ.

## Top level

| Field | Meaning |
|---|---|
| `slug` | Folder under `public/` and `src/` for this reel's media and timeline |
| `fps` | 30 |
| `tail` | Seconds held after the last shot (0 when the CTA sits on the last shot) |
| `bed` | Optional low ambience loop `{src, in, len, db}`; omit when Joe wants a silent file |
| `sounds` | Free-placed sound, e.g. a J-cut `{at: "beatId+0.4", src, in, len, chain, db}` |
| `beats` | Shots in order |
| `overlays` | Text, timed relative to beats (`at: "beatId+seconds"`, `dur`) |

## Beat (one shot)

| Field | Meaning |
|---|---|
| `id`, `src`, `in`, `dur` | Id, source file, source start second, output seconds |
| `use`, `src_len` | L-cut (show less picture than built) / hold the last frame after this many source seconds |
| `speed` | `0.5` slow motion on a real moment (60 fps source); no speed-ups on aerials |
| `zoom`, `cx`, `cy`, `rot` | Crop and rotation; `cx: [a, b]` pans (avoid on aerials) |
| `stab` | `true` on every aerial |
| `grade`, `sharpen`, `grain` | `phone`, `drone` or `bright`; drone upscale help `0.8` and `4` |
| `xfade` | Dissolve seconds from the previous shot (scene changes only) |
| `push` | `[1, 1]` locked; `[1, 1.06]` is the brand maximum |
| `audio` | `{kind: "voice" | "nat" | "bed", chain, db, ...}` |

## Overlay types (read by build_text.py)

| Type | Fields | Renders as |
|---|---|---|
| `hook` | `lines` (list), `sub`, `enter` (`top`, `left`, `right`), `top`, `size`, `strong`, `verified` | Anton cobalt caps on glass, top of frame |
| `name` | `name`, `role`, `top` | Name super on strong glass, mid frame |
| `caption` | `text` (`|` = line break), `verified` | Manrope Bold ink on glass, above Instagram's caption |
| `cta` | `line1` (default "Start your intake"), `site`, `top`, `dim` | Logo, Anton cobalt line, site, on strong glass |

`verified: true` means the line states a client result or testimonial that is confirmed and authorized.
It adds "Individual results vary and aren't guaranteed" while it shows. Without it, result or promise
language stops the build.
