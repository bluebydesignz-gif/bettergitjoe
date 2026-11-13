#!/usr/bin/env bash
# Timestamped contact sheet of a clip: one thumbnail every N seconds, time burned in.
# Usage: scripts/contact_sheet.sh public/clips/clip01.mp4 [every_seconds=2] [out.jpg]
set -euo pipefail
SRC=${1:?pass a clip}
EVERY=${2:-2}
OUT=${3:-out/sheets/$(basename "${SRC%.*}").jpg}
mkdir -p "$(dirname "$OUT")"
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$SRC")
n=$(python3 -I -c "import math; print(max(1, math.ceil($dur / $EVERY)))")
rows=$(( (n + 5) / 6 ))
ffmpeg -loglevel error -y -i "$SRC" -vf "fps=1/$EVERY,scale=270:-2,\
drawtext=text='%{pts\:hms}':x=8:y=8:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.6,\
tile=6x$rows" -frames:v 1 -q:v 3 "$OUT"
echo "$OUT ($n frames, every ${EVERY}s)"
