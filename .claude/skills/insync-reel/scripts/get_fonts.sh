#!/usr/bin/env bash
# Fetch the INSYNC fonts (Anton, Manrope variable) from the Google Fonts repo.
# usage: get_fonts.sh <dest_dir>
set -euo pipefail
d=$1; mkdir -p "$d"
curl -sSL --retry 3 -o "$d/Anton-Regular.ttf" "https://raw.githubusercontent.com/google/fonts/main/ofl/anton/Anton-Regular.ttf"
curl -sSL --retry 3 -o "$d/Manrope[wght].ttf" "https://raw.githubusercontent.com/google/fonts/main/ofl/manrope/Manrope%5Bwght%5D.ttf"
ls -la "$d"
