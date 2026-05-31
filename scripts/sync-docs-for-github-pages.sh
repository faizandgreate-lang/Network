#!/bin/bash
# Copy web/ → docs/ for GitHub Pages (Settings only offers /root or /docs).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DOCS="$ROOT/docs"
WEB="$ROOT/web"

rm -rf "$DOCS"
mkdir -p "$DOCS"
rsync -a \
  --exclude '.DS_Store' \
  "$WEB/" "$DOCS/"

echo "Synced web/ → docs/ ($(find "$DOCS" -type f | wc -l | tr -d ' ') files)"
echo "GitHub Pages: branch main, folder /docs"
