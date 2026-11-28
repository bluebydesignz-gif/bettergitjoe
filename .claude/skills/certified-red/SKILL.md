---
name: certified-red
description: Edit raw event footage into a cinematic, feel-good 9:16 thank-you reel for Certified Collision Center (community events, giveaways, festivals, sponsorships, drone plus phone footage). Real footage only, steady aerials, captioned speech, Barlow text built in HyperFrames, a team-photo ending and the brand end card, delivered as a primary reel and a clean version. Use this skill whenever Joe asks for an event recap, community reel, thank-you video, "make a reel from this footage", or anything cut from Certified Collision event clips, even if he does not name the skill.
---

# Certified Red

Turns a batch of raw event clips (iPhone 4K vertical, DJI 720p landscape aerials) into a 45 to 60 s
Instagram Reel that thanks a community and shows Certified Collision Center taking part.
First approved run: the 24th Annual Thanksgiving Turkey Giveaway, Nov 2026 (v5, 56 s). Joe: "This is amazing."

Pipeline: ffmpeg cuts and grades each shot, Remotion assembles the picture and the natural-sound mix,
HyperFrames lays the text on top. Scripts are in `scripts/`; the approved cut list is
`templates/edl.example.json`; its fields are in `references/cut-list.md`.

## Hard rules (Joe's, learned over five versions)

**Truth**
- Only the original footage. No generated video, no stock, no outside footage.
- Never invent dialogue, hosts, sponsors, slogans or taglines. Every on-screen line is either a quote
  from the footage, a fact from the event flyer, or brand copy from the brand kit.
- Name a host only if the flyer or footage confirms it. Ask Joe who the reel thanks before building the end.
- Exact brand lines: "Driven to repair. Committed to care." (this case). Kirby's line: "Small City, Big Heart."
  Only use the Kirby line when the event was actually in Kirby.
- No music in the file unless Joe supplies a track; he adds music in Instagram. Deliver a clean natural-sound mix.

**Aerials** (his top complaint)
- Steady stretches only. Run `scripts/motion.py` on every drone clip; use seconds with jitter under ~0.3
  and no sideways drift. Never cut on a yaw, a jerk or a turn.
- Real speed, `stab: true`, `push: [1,1]`. No speed-ups, no pans across the frame, no slow zooms.
- Consecutive aerials fly the same direction at a similar pace, so the car line reads as one drive.
- Three aerials at most in the opening: the line on the main road, the line through the side streets, the lot.
- 720p drone sources are upscaled before cropping (the builder does this); they stay softer than phone footage.

**People and sound**
- Cut the filmer's voice everywhere: prompts like "We're driven to what?", "okay", "one, two, three".
  Check every kept line with `scripts/pitch_track.py`; the filmer is louder and pitched differently.
- Speakers get at least one full sentence. End a speaker's shot on a clean pose, never mid-handoff or mid-gesture.
- Keep a genuine flub-and-laugh beat when it exists (the team practicing the slogan was a favorite).
- Don't show other booths' branded items as if they are ours; find the team at the Certified tent instead.
- Blur readable license plates with `scripts/track_blur.py`; check each at a 2x crop.

**Structure**
1. Opening aerials with the title (0:00 to ~0:10).
2. Speech: Marcos (or the owner) on the mic, then the event host or pastor, captioned.
3. Community: volunteers, families, laughter, the dog or other mascot moment, slow motion only on a real moment.
4. Team: Certified crew working, the slogan practice.
5. End on the posed team photo under the Certified tent: hold it clean ~3 s, dim, "THANK YOU" card,
   then the logo, "Certified Collision Center was proud to be part of it.", and the slogan. Never end on people walking off.

**Cuts**: dissolves (0.3 to 0.5 s) only at scene changes, hard cuts inside a scene. Start a speaker's voice
over the previous shot (J-cut) when it helps.

**Text** (built in HyperFrames, not Remotion)
- One family, Barlow (house font). No italic serif. Three roles:
  display = Barlow Condensed Black caps (title, THANK YOU); label = red rule + Barlow Condensed ExtraBold
  caps with a Barlow SemiBold line (name, mascot line); caption = Barlow Bold sentence case on a dark scrim
  sized to the text.
- Everything readable inside the Reels band (y 168 to 1330 of 1920); captions about 690 px from the bottom.
- Short quotes only, one at a time, timed to the words.

## Workflow

### 1. Intake
- Read the brand kit from Drive (`Certified_Collision_Brand_Kit.md`, use `read_file_content`); it wins over this skill.
- Find the clips in Drive (`search_files`, newest videos). The Drive connector only downloads files under 10 MB.
  For larger clips: ask Joe first, then `share_file` with `permissionId: anyoneWithLink`, role `reader`,
  write a manifest (name, id, size) and run `scripts/fetch_drive.sh manifest.tsv <scratchpad>/dl`.
  You cannot unshare: list the shared files for Joe and ask him to turn sharing off afterwards (the footage shows kids).
- Logo: `certified-collision-logo.png` in Drive (small, the connector downloads it). Fonts: `scripts/get_fonts.sh`.
- Keep footage in the scratchpad, never in git.

### 2. Review
- `ffprobe` every clip; build timestamped contact sheets (1 to 3 s apart).
- Extract audio (`ffmpeg -i clip -vn -ac 1 -ar 16000 wav/clip.wav`) and run `scripts/transcribe.py small`.
  Re-check every captioned line with `large-v3-turbo`; when models disagree, flag the line for Joe.
- `scripts/motion.py` on all aerials. Pick shots, write the cut list (start from `templates/edl.example.json`).

### 3. Build
```bash
python3 scripts/build_segments.py edl.json <dl> <seg>              # cut, reframe, grade, stabilize
python3 scripts/track_blur.py <seg>/<id>.mp4 frame:cx:cy:w:h ...   # then rename <id>_b.mp4 over <id>.mp4
python3 scripts/assemble.py edl.json <dl> <seg> public/<slug> src/<slug>/timeline.json
```
Copy `templates/ReelBase.tsx` to `src/<slug>/`, register `<Slug>Base` in `src/Root.tsx`, then:
```bash
npx remotion render src/index.ts <Slug>Base out/_base_raw.mp4 --crf 14
npx hyperframes init <hf_dir> --example blank --resolution portrait --non-interactive --skip-skills
# copy fonts to <hf_dir>/assets/fonts, logo to assets/logo.png, base video to assets/base.mp4 (-g 15)
python3 scripts/build_text.py src/<slug>/timeline.json <hf_dir>            # primary
python3 scripts/build_text.py src/<slug>/timeline.json <hf_clean> --clean  # logo-and-slogan only
(cd <hf_dir> && npx hyperframes check --json && npx hyperframes render -o out/_hf_primary.mp4 -f 30 --crf 15)
```
Renders take ~5 min each; run them in the background.

### 4. Check before sending
- `hyperframes check` has no errors and no Instagram safe-zone warnings.
- A frame sheet every ~1.5 s: no text on faces, captions never collide, plates blurred, no other booth's merch.
- Transcribe the final mix: every kept line reads cleanly, no filmer's voice.
- Loudness ~ -16 LUFS integrated; dialogue about 17 dB above b-roll ambience.

### 5. Deliver
- Encode: `libx264 -preset slow -crf 19 -maxrate 12M -bufsize 24M -c:a aac -b:a 256k -movflags +faststart`.
- Names: `Certified_<Event>_ThankYou_vN.mp4` and `Certified_<Event>_Clean_vN.mp4`, in `out/`.
- Send both with `SendUserFile`. Say plainly you cannot hear the audio and list the exact timestamps to check by ear.
- Commit the cut list, scripts and HyperFrames project (not media) and push.
- Keep the reply short: what changed, what to check, what's still open (sharing, names, unsure captions).
