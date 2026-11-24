---
name: insync-reel
description: Edit raw footage into a short 9:16 Instagram Reel for INSYNC Credit Repair (Leonard's business), covering event pop-ups, community tables, behind the scenes, client moments and authorized testimonials. Real footage only, cobalt Anton headlines and Manrope text on liquid glass, the approved logo with the "Start your intake / insynccredit.com" end card, built-in checks against result claims, guarantees, periods and dashes on screen. Delivers a primary reel and a clean version. Use this skill whenever Joe asks for an INSYNC reel, video, recap, event edit or testimonial cut, or says "INSYNC this up" about video, even if he does not name the skill.
---

# INSYNC Reel

The INSYNC version of the Certified Red pipeline: same editing engine (ffmpeg shots, Remotion picture and
sound, HyperFrames text), with INSYNC's own look, copy rules and compliance checks.
Brand sources in Drive win over this file: `INSYNC Brand Rules.md` (id `1WrpkYak92_EV6_E-Bnq7lShrGC1Vu8K6`)
and the reel `BRAND.md` (id `1f99xhCQVZ62OYGyX0V_-4pH6ymw-CiwL`). Read both with `read_file_content` first.
Source order when they conflict: Joe's current message, the approved logo file, Brand Source of Truth,
Master Prompt Kit, approved finals, then older drafts.

## Brand rules (locked)

**Identity**: INSYNC, all caps, always. CREDIT REPAIR only as the descriptor. Never NSYNC, *NSYNC, InSync or a suffix.

**Logo**: the approved original transparent PNG only (Drive `INSYNC-approved-original-logo.png`,
id `1sEACbFW8EaB0p4074zCPPrKwqYtXuPCZ`, 1180x298). Run `scripts/check_logo.sh` on it. It is black and cobalt
on transparent, so it always sits on light glass, never straight on footage. No recolor, crop, outline, glow,
shadow, stretch or redraw. Never type the logo in a font.

**Color**: cobalt `#146BDE` for headline lettering, midnight `#05070A`, warm white `#F7F4EE`, ink `#111317`,
cool gray `#6D7178`. Cobalt is the accent, about 10 to 15 percent of the frame.

**Type**: Anton, all caps, cobalt, for headlines. Manrope Bold, ink, for support text and captions.
No periods on screen (a web address keeps its dot). No em or en dashes. No white outlines.

**Glass**: clear refractive liquid glass behind every text block. Only the footage behind bends
(displacement 42, frequency 0.008/0.012, 38 px corners, bright beveled rim, slow reflection drift).
Lettering and logo stay sharp. Stronger tint for small text and night footage (`--night`). Not an opaque box,
not heavy frosted blur.

**Motion**: entrances in 9 frames from the top or a side on a long ease-out. Setup text clears at least
4 frames before a punchline. Push-ins 1.00 to 1.06 at most; reaction punch only on a real reaction.
No constant motion.

**Safe area** (1080x1920): top 250, right 150, left 64 (brand). Key text stays above y 1330 because
Instagram's caption and buttons cover the bottom; `hyperframes check` must show no Instagram warnings.

**CTA end card**: approved logo + "Start your intake" + insynccredit.com, on light glass. Run
`scripts/check_site.sh` before Joe publishes; it must return 200.

**Voice**: clear, direct, human, nonjudgmental, lightly playful. One joke and one visual idea per reel.
Less copy wins. No shame, fear, fake urgency, "level up", "boss moves" or emoji piles.
Approved tone (examples, not copy to reuse): "YOUR CREDIT DOES NOT DEFINE YOU",
"THE NUMBER YOU SEE MAY NOT BE THE WHOLE STORY", "MONDAY NEEDS COFFEE. YOUR CREDIT NEEDS A PLAN."

## Compliance (credit repair is regulated)

The federal Credit Repair Organizations Act bars misleading claims about what credit repair can do.
- Never invent or imply results, score increases, timelines, prices, plans, guarantees, credentials,
  testimonials or contact details. Missing fact: ask Joe or mark it `[NEEDS OWNER CONFIRMATION]`.
- A client result or testimonial appears only with verified facts and the client's authorization. Mark that
  overlay `"verified": true`; the builder then adds "Individual results vary and aren't guaranteed" on screen.
- `build_text.py` stops on result or promise language without `verified`, on any dash, and on periods.
- Confirmed facts: website insynccredit.com, Instagram @insync.credit, founder Leonard. Nothing else unless Joe confirms it.

## Sound

INSYNC's rule: sound must be requested or supplied by Joe. Ask once at intake: natural sound from the footage,
a track he supplies, or silent for him to add music in Instagram. Never add generated or stock music.

## Editing rules (carried over from Certified Red, all still apply)

- Real footage only. No generated video, no stock, no outside footage.
- Aerials: steady stretches only (`scripts/motion.py`, jitter under ~0.3, no sideways drift), real speed,
  `stab: true`, no pans or slow zooms, consecutive aerials fly the same direction.
- Cut the filmer's voice (prompts, counting, "okay"); verify with `scripts/pitch_track.py`.
- Speakers get a full sentence and end on a clean pose. Leonard's likeness is never altered.
- Don't show another vendor's merch or booth as INSYNC's. Blur readable plates (`scripts/track_blur.py`).
- Ask before using footage of kids or anyone who looks uncomfortable.

## Structure (20 to 45 s)

1. Hook in the first 2 seconds: one line on glass (Anton, cobalt) over the strongest moment.
2. The table or event: people stopping by, Leonard talking with them, real reactions.
3. Optional: one authorized client line, captioned, with the disclaimer.
4. CTA end card over the last clean shot, held 3 to 4 s.

## Workflow

1. **Intake**: read both brand files; find clips in Drive (`INSYNC Credit` folder: `Events`, `Photos`,
   `Logos and Brand Assets`). Files over 10 MB: ask Joe, then `share_file` (anyoneWithLink, reader),
   `scripts/fetch_drive.sh`, and remind him to turn sharing off. Fonts: `scripts/get_fonts.sh`.
   Ask about sound, the hook line, and whether any testimonial is authorized.
2. **Review**: contact sheets, `scripts/transcribe.py`, `scripts/motion.py` on aerials. Offer five hook lines
   ranked strongest first when Joe hasn't settled the joke, then wait for his pick.
3. **Build**: write the cut list (`templates/edl.example.json`, fields in `references/cut-list.md`), then
   ```bash
   python3 scripts/build_segments.py edl.json <dl> <seg>
   python3 scripts/assemble.py edl.json <dl> <seg> public/<slug> src/<slug>/timeline.json
   npx remotion render src/index.ts <Slug>Base out/_base_raw.mp4 --crf 14     # ReelBase.tsx template
   npx hyperframes init <hf> --example blank --resolution portrait --non-interactive --skip-skills
   # assets/: fonts (Anton, Manrope), logo.png (checked), base.mp4 (-g 15)
   python3 scripts/build_text.py src/<slug>/timeline.json <hf> [--night]
   python3 scripts/build_text.py src/<slug>/timeline.json <hf_clean> --clean
   (cd <hf> && npx hyperframes check --json && npx hyperframes render -o out/_hf.mp4 -f 30 --crf 15)
   ```
4. **Check**: `hyperframes check` with no errors and no Instagram warnings; a frame sheet every ~1.5 s at full
   and thumbnail size (text off faces, logo unclipped, spelling INSYNC); transcribe the final audio.
5. **Deliver**: `INSYNC-<Event>-vN.mp4` and `INSYNC-<Event>-Clean-vN.mp4` (clean = CTA card only), encoded
   `libx264 -crf 19 -maxrate 12M -c:a aac -b:a 256k -movflags +faststart`, sent with `SendUserFile`.
   Say you can't hear the audio. Offer a caption: one joke, plain, ends with "Start your intake at insynccredit.com",
   no result claims. Commit the cut list and HyperFrames project (no media) and push.
