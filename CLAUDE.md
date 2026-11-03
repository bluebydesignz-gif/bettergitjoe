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
