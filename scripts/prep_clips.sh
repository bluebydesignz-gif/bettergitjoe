#!/usr/bin/env bash
# Turn a folder of raw footage (iPhone MOV, DJI MP4, any orientation) into
# 1080x1920 30fps proxies in public/clips/, and write out/clips.json with
# evenly spaced starting "moments" for the InsyncHalloween composition.
#
# Usage: scripts/prep_clips.sh /path/to/raw/folder [moments_per_clip]
#   KEEP_AUDIO=1 keeps each clip's own sound (AAC) for shots that play real audio.
#   Photos (jpg/png/heic) in the folder become 1080x1920 JPGs in public/photos/.
# Then:  npx remotion render src/index.ts InsyncHalloween out/insync.mp4 --props=out/clips.json
set -euo pipefail
cd "$(dirname "$0")/.."

SRC_DIR=${1:?pass the folder with raw clips}
MOMENTS=${2:-4}
mkdir -p public/clips out

# HDR iPhone footage needs tone mapping to look right in SDR.
HAS_ZSCALE=$(ffmpeg -hide_banner -filters 2>/dev/null | grep -c ' zscale ' || true)

json='{"music":"music/beat.wav","clips":['
i=0
shopt -s nullglob nocaseglob
for f in "$SRC_DIR"/*.{mov,mp4,m4v}; do
  i=$((i + 1))
  name=$(printf 'clip%02d.mp4' "$i")
  dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
  trc=$(ffprobe -v error -select_streams v:0 -show_entries stream=color_transfer -of csv=p=0 "$f" || true)

  vf="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30"
  if [[ "$trc" == "arib-std-b67" || "$trc" == "smpte2084" ]] && [[ "$HAS_ZSCALE" -gt 0 ]]; then
    vf="zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,$vf"
  fi

  echo "[$i] $(basename "$f") (${dur%.*}s, $trc) -> public/clips/$name"
  if [[ "${KEEP_AUDIO:-0}" == 1 ]]; then audio=(-c:a aac -b:a 192k -ar 48000 -ac 2); else audio=(-an); fi
  ffmpeg -loglevel error -y -i "$f" -vf "$vf,format=yuv420p" "${audio[@]}" \
    -c:v libx264 -preset veryfast -crf 20 -g 15 "public/clips/$name"

  moments=$(python3 -I -c "
d=float('$dur'); n=$MOMENTS; lo=0.5; hi=max(lo, d-2.0)
print(','.join(f'{lo + (hi-lo)*k/max(n-1,1):.2f}' for k in range(n)))")
  [[ $i -gt 1 ]] && json+=','
  json+="{\"src\":\"clips/$name\",\"moments\":[$moments]}"
done
json+=']}'

p=0
mkdir -p public/photos
for f in "$SRC_DIR"/*.{jpg,jpeg,png,heic}; do
  p=$((p + 1))
  out=$(printf 'public/photos/photo%02d.jpg' "$p")
  echo "[photo $p] $(basename "$f") -> $out"
  ffmpeg -loglevel error -y -i "$f" -frames:v 1 \
    -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" -q:v 2 "$out" \
    || echo "  could not convert $(basename "$f") (HEIC may need exporting as JPG)"
done

[[ $i -eq 0 ]] && { echo "No video files found in $SRC_DIR"; exit 1; }
[[ $p -gt 0 ]] && echo "Prepared $p photos in public/photos/"
echo "$json" > out/clips.json
echo "Prepared $i clips. Props written to out/clips.json"
