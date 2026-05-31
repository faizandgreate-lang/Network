#!/bin/bash
# Build docs/ with same paths as localhost (/static/* and /assets/*).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DOCS="$ROOT/docs"
WEB="$ROOT/web"

rm -rf "$DOCS"
mkdir -p "$DOCS/static" "$DOCS/assets"

# HTML at site root (same as local routes)
for f in "$WEB"/*.html; do
  [ -f "$f" ] && cp "$f" "$DOCS/"
done

# SEO — must live at site root (not only under /static/)
for f in sitemap.xml robots.txt; do
  [ -f "$WEB/$f" ] && cp "$WEB/$f" "$DOCS/$f"
done

# Images (local: /assets/logo.png)
if [ -d "$WEB/assets" ]; then
  rsync -a "$WEB/assets/" "$DOCS/assets/"
fi

# Static bundle (local: /static/site.css → web/site.css via FastAPI)
rsync -a \
  --exclude '.DS_Store' \
  --exclude '*.html' \
  --exclude 'assets/' \
  --exclude 'locales/_langs/' \
  --exclude 'locales/_*.py' \
  --exclude 'locales/_*.part' \
  --exclude 'locales/*.command' \
  --exclude 'locales/build_phrases.py' \
  --exclude 'locales/write_phrases.py' \
  --exclude 'locales/emit_stdout.py' \
  "$WEB/" "$DOCS/static/"

bash "$ROOT/scripts/build-public-downloads.sh"
mkdir -p "$DOCS/downloads"
rsync -a "$ROOT/downloads/" "$DOCS/downloads/"

# Custom domain (GitHub Pages → network.linux-aios.com)
if [ -f "$ROOT/docs/CNAME" ]; then
  cp "$ROOT/docs/CNAME" "$DOCS/CNAME"
elif [ ! -f "$DOCS/CNAME" ]; then
  echo "network.linux-aios.com" > "$DOCS/CNAME"
fi

touch "$DOCS/.nojekyll"
echo "docs/ ready: HTML + static/ + assets/ + downloads/ ($(find "$DOCS" -type f | wc -l | tr -d ' ') files)"
echo "GitHub Pages: branch main, folder /docs"
echo "URL: https://faizandgreate-lang.github.io/Network/"
