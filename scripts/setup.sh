#!/usr/bin/env bash
# Reinstalls the video toolkit in a fresh cloud container.
set -euo pipefail
cd "$(dirname "$0")/.."
npm ci
pip install -q yt-dlp faster-whisper numpy
mkdir -p public/music && python3 -I scripts/make_beat.py public/music/beat.wav
command -v ffmpeg >/dev/null || echo "WARNING: ffmpeg missing"
echo "Video studio ready. Try: npm test"
