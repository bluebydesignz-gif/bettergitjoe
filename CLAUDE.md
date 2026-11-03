# Video studio

This repo is a video production workspace.

- Remotion project in `src/`. Register new videos in `src/Root.tsx`.
- Render: `npx remotion render src/index.ts <CompositionId> out/<name>.mp4`
- Libraries: GSAP (eases, timelines), Three.js via `@remotion/three`.
- Skills in `.claude/skills/`: hyperframes (HTML to video), impeccable (design critique).
- CLI tools: ffmpeg, yt-dlp, faster-whisper.
- In a fresh container, run `scripts/setup.sh` first.
- Hugging Face is blocked by the network policy here, so faster-whisper models
  will not download unless the environment allows `huggingface.co`.
- Put finished videos in `out/` (gitignored). Send them to the user as files.

## INSYNC Halloween reel (`src/insync/`)

Event recap reel, 124 BPM, every cut on the beat. Style: bold Anton title,
Space Mono subtitle, glitch/flash/whip/zoom transitions, stutters, B&W
inserts, orange/purple grade, grain. Do not say it was a "first" event.

1. `scripts/prep_clips.sh <raw folder>` makes 1080x1920 proxies in
   `public/clips/` and `out/clips.json`.
2. Look at contact sheets of each clip and replace the evenly spaced
   `moments` in `out/clips.json` with the best start times.
3. `npx remotion render src/index.ts InsyncHalloween out/insync.mp4 --props=out/clips.json`

Music: `public/music/beat.wav` is a synthesized placeholder
(`scripts/make_beat.py`). Swap in a licensed 124 BPM track for posting,
or retime `BPM` in `src/insync/timeline.ts`.
