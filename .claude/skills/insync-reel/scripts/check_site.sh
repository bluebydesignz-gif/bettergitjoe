#!/usr/bin/env bash
# Before anything with the CTA is published: confirm the website and intake page load.
# usage: check_site.sh [intake_url]
site="https://insynccredit.com"; intake=${1:-}
for u in "$site" $intake; do
  code=$(curl -sS -o /dev/null -L -w '%{http_code}' -m 20 "$u" || echo ERR)
  echo "$code $u"
  [ "$code" = "200" ] || { echo "STOP: $u does not load. Tell Joe before publishing."; exit 1; }
done
