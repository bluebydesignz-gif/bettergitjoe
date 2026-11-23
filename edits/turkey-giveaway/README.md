# Thanksgiving Turkey Giveaway thank-you reel

A 58-second 9:16 reel cut only from the original event footage. No generated video and no music bed:
the music track is added in Instagram.

| File | Role |
|---|---|
| `edl.json` | The cut list: every shot, crop, speed, audio rule and text overlay |
| `build_segments.py` | Cuts, reframes to 1080x1920 and grades each shot with ffmpeg |
| `track_blur.py` | Tracks and blurs license plates in a rendered shot |
| `assemble.py` | Writes `src/turkey/timeline.json` and the natural-sound mix |
| `src/turkey/TurkeyReel.tsx` | Remotion composition: picture, text animation, end card |

## Rebuild

Footage, fonts, logo and the mix are not committed. Put the original clips in a folder, then:

```bash
python3 edits/turkey-giveaway/build_segments.py edits/turkey-giveaway/edl.json <footage> <segs>
python3 edits/turkey-giveaway/track_blur.py <segs>/t2.mp4 85:688:777:104:68 5:1026:873:58:48
python3 edits/turkey-giveaway/track_blur.py <segs>/t1.mp4 5:733:700:76:44
python3 edits/turkey-giveaway/track_blur.py <segs>/g2.mp4 10:713:826:58:42
python3 edits/turkey-giveaway/assemble.py edits/turkey-giveaway/edl.json <footage> <segs> public/turkey src/turkey/timeline.json
npx remotion render src/index.ts TurkeyThankYou out/turkey_primary.mp4
npx remotion render src/index.ts TurkeyThankYouClean out/turkey_clean.mp4
```

`track_blur.py` writes `<shot>_b.mp4`; rename it over the original shot before `assemble.py`.
`public/turkey/` also needs `logo.png` and `fonts/` (Barlow, Barlow Condensed, Instrument Serif).
