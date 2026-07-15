#!/usr/bin/env bash
# Render one HTML/SVG file to PNG at 2x via Chrome headless, then cap width.
# Usage: render.sh <input.html> <output.png> <width> <height> [maxwidth]
#   maxwidth (optional): downscale the 2x capture to this max width (retina-crisp, leaner).
set -euo pipefail
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
IN="$1"; OUT="$2"; W="$3"; H="$4"; MAXW="${5:-0}"
PROFILE="$(mktemp -d)"
rm -f "$OUT"
"$CHROME" --headless=new --disable-gpu --no-first-run --no-default-browser-check \
  --disable-extensions --disable-background-networking --disable-sync --hide-scrollbars \
  --force-device-scale-factor=2 --user-data-dir="$PROFILE" \
  --screenshot="$OUT" --window-size="$W,$H" "file://$IN" >/dev/null 2>&1 &
PID=$!
for i in $(seq 1 30); do [ -s "$OUT" ] && break; sleep 1; done
kill "$PID" >/dev/null 2>&1 || true
wait "$PID" 2>/dev/null || true
rm -rf "$PROFILE"
[ -s "$OUT" ] || { echo "FAIL $OUT"; exit 1; }
if [ "$MAXW" -gt 0 ]; then sips --resampleWidth "$MAXW" "$OUT" >/dev/null 2>&1; fi
echo "OK  $OUT ($(du -h "$OUT" | cut -f1))"
