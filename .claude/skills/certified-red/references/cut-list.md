# Cut list (edl.json) fields

The cut list drives every script. `templates/edl.example.json` is the approved Turkey Giveaway reel.

## Top level

| Field | Meaning |
|---|---|
| `slug` | Folder name under `public/` and `src/` for this reel's media and timeline |
| `fps` | 30 |
| `tail` | Seconds of black held after the last shot (0 when the end card sits on the last shot) |
| `bed` | Low ambience loop under the whole reel: `{src, in, len, db}`; about -46 dB |
| `sounds` | Free-placed sound, e.g. a J-cut: `{at: "beatId+0.4", src, in, len, chain, db}` |
| `beats` | Shots in order |
| `overlays` | Text, timed relative to beats |

## Beat (one shot)

| Field | Meaning |
|---|---|
| `id` | Short unique id (`d1`, `m3`, `f1`) |
| `src`, `in` | Source file and start second |
| `dur` | Output seconds |
| `use` | Show fewer seconds of picture than built while the audio runs on (L-cut) |
| `src_len` | Stop reading the source after this many seconds and hold the last frame |
| `speed` | `0.5` slow motion (needs 60 fps source); avoid speed-ups on aerials |
| `zoom`, `cx`, `cy` | Crop: zoom 1 = widest 9:16 window; centre as fractions; `cx: [a, b]` pans (avoid on aerials) |
| `rot` | `cw` or `ccw` for clips shot sideways |
| `stab` | `true` = two-pass vidstab (use on every aerial) |
| `grade` | `phone`, `drone` or `bright` |
| `sharpen`, `grain` | Drone upscale help: `0.8` and `4` |
| `xfade` | Seconds of dissolve from the previous shot (scene changes only) |
| `push` | Scale over the shot, `[1, 1]` = locked off; `[1, 1.04]` max on people shots |
| `audio` | `{kind: "voice" | "nat" | "bed", chain, db, in, len, lead, pre, tail, window}` |

Audio kinds: `voice` = cleaned speech, levelled to `db` (default -20; `chain` `pa` for a mic through speakers,
`close` for phone-close speech, `close_lvl` when a loud laugh follows the words, with `window` = the words);
`nat` = the shot's own ambience at a fixed low level (-38 to -40); `bed` = silent, the bed covers it.

## Overlay types (read by build_text.py)

Times: `at` = `"beatId+seconds"` (or `-seconds`), `dur` = seconds.

| Type | Fields | Renders as |
|---|---|---|
| `title` | `eyebrow`, `line1`, `line2` | Two condensed caps lines, red rule, small spaced line |
| `name` | `name`, `role` | Red rule, name in caps, role below (lower left) |
| `label` | `text` | Red rule and one caps line (mascot or moment line) |
| `caption` | `text` (`|` = line break) | Speech caption on a dark scrim |
| `thanks` | `head`, `lines` | Dims the picture, THANK YOU and credits |
| `endcard` | `proud` (`|` break), `slogan`, `keepInMinimal` | Logo, proud line, slogan; the clean version keeps logo and slogan |
