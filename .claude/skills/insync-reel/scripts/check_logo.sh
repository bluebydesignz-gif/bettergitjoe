#!/usr/bin/env bash
# The CTA must use the approved original logo, byte for byte.
# usage: check_logo.sh <logo.png>
want=e090d242b8c12fd9ea6c73d4a725b6030dfc509ecb3031fa7bb1a6c28e78b9db
have=$(sha256sum "$1" | cut -d' ' -f1)
[ "$have" = "$want" ] && echo "OK approved INSYNC logo (1180x298)" || { echo "STOP: $1 is not the approved logo ($have)"; exit 1; }
