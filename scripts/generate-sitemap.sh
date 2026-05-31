#!/bin/bash
# Regenerate web/sitemap.xml (canonical host: network.linux-aios.com).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ORIGIN="${SITE_ORIGIN:-https://network.linux-aios.com}"
LASTMOD="${SITEMAP_LASTMOD:-$(date +%Y-%m-%d)}"
OUT="$ROOT/web/sitemap.xml"

pages=(
  "/:1.0:weekly"
  "/index.html:1.0:weekly"
  "/devices.html:0.9:weekly"
  "/map.html:0.9:weekly"
  "/calendar.html:0.8:daily"
  "/clock.html:0.8:daily"
)

{
  echo '<?xml version="1.0" encoding="UTF-8"?>'
  echo '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
  for row in "${pages[@]}"; do
    IFS=':' read -r path priority freq <<< "$row"
    echo "  <url>"
    echo "    <loc>${ORIGIN}${path}</loc>"
    echo "    <lastmod>${LASTMOD}</lastmod>"
    echo "    <changefreq>${freq}</changefreq>"
    echo "    <priority>${priority}</priority>"
    echo "  </url>"
  done
  echo '</urlset>'
} > "$OUT"

echo "Wrote $OUT ($ORIGIN, lastmod=$LASTMOD)"
