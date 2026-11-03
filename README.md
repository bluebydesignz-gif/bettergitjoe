# bettergitjoe video studio

AI-driven video workspace. Ask Claude for a video in plain English; it writes the scenes and renders the MP4.

## Setup (fresh container)

```bash
scripts/setup.sh
npm test   # renders out/hello.mp4
```

## What is installed

| Tool | Role | Status |
|---|---|---|
| Remotion | Compose and render video in React | Installed |
| Remotion Skills | Video guidance for Claude | Installed as plugin |
| GSAP | Motion and kinetic type | Installed |
| Three.js | 3D scenes | Installed (`@remotion/three`) |
| HyperFrames skills | HTML to video | `.claude/skills/` |
| Impeccable | Design critique | `.claude/skills/impeccable` |
| FFmpeg | Encode and inspect MP4 | Preinstalled |
| yt-dlp | Pull reference clips | pip |
| faster-whisper | Captions | pip, needs huggingface.co for models |

## Not installed here

| Tool | Why |
|---|---|
| Blender, Blender MCP | Desktop app; MCP drives Blender on your own computer |
| ComfyUI | Needs a GPU; this container has none |
| Chatterbox | Needs Hugging Face model downloads (blocked) and a GPU for usable speed |
| Chrome DevTools MCP | Covered by preinstalled Playwright Chromium |
