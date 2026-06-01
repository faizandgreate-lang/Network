#!/bin/bash
# Build tab icons from web/assets/logo.png
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOGO="$ROOT/web/assets/logo.png"
ASSETS="$ROOT/web/assets"

if [ ! -f "$LOGO" ]; then
  echo "Missing $LOGO"
  exit 1
fi

sips -z 16 16 "$LOGO" --out "$ASSETS/favicon-16.png" >/dev/null
sips -z 32 32 "$LOGO" --out "$ASSETS/favicon-32.png" >/dev/null
sips -z 180 180 "$LOGO" --out "$ASSETS/apple-touch-icon.png" >/dev/null
cp -f "$ASSETS/favicon-32.png" "$ROOT/web/favicon.ico"
cp -f "$ASSETS/favicon-32.png" "$ROOT/web/favicon.png"
echo "Favicons ready in web/assets/ and web/favicon.ico"
