#!/usr/bin/env bash
# Fetch the brand fonts (Barlow, Barlow Condensed) from the Google Fonts repo.
# usage: get_fonts.sh <dest_dir>
set -euo pipefail
d=$1; mkdir -p "$d"
for f in barlow/Barlow-Medium barlow/Barlow-SemiBold barlow/Barlow-Bold barlow/Barlow-ExtraBold barlow/Barlow-Black \
         barlowcondensed/BarlowCondensed-ExtraBold barlowcondensed/BarlowCondensed-Black; do
  curl -sSL --retry 3 -o "$d/$(basename $f).ttf" "https://raw.githubusercontent.com/google/fonts/main/ofl/$f.ttf"
done
ls "$d"
