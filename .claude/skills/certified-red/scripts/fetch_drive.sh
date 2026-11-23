#!/usr/bin/env bash
# Download Drive files that were set to "Anyone with the link can view".
# usage: fetch_drive.sh manifest.tsv <dest_dir>
#   manifest.tsv: one line per file: <name>\t<drive_file_id>\t<size_in_bytes>
# Resumes partial downloads and checks every size. Runs 5 at a time.
set -euo pipefail
man=$1; dest=$2; mkdir -p "$dest"
one() {
  name=$1; id=$2; size=$3; dest=$4
  for try in 1 2 3 4; do
    have=$(stat -c %s "$dest/$name" 2>/dev/null || echo 0)
    [ "$have" = "$size" ] && { echo "OK $name"; return 0; }
    curl -sSL -C - --retry 3 -o "$dest/$name" "https://drive.usercontent.google.com/download?id=$id&export=download&confirm=t" || true
    sleep $((try * 3))
  done
  have=$(stat -c %s "$dest/$name" 2>/dev/null || echo 0)
  [ "$have" = "$size" ] && echo "OK $name" || echo "FAIL $name have=$have want=$size"
}
export -f one
sort -t$'\t' -k3 -n "$man" | xargs -P 5 -L 1 bash -c 'one "$0" "$1" "$2" "'"$dest"'"'
