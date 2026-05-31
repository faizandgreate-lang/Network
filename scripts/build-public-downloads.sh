#!/bin/bash
# Build zips + copy launchers into downloads/ (served locally and copied to docs/ for GitHub Pages).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/downloads"
mkdir -p "$OUT"

cd "$ROOT"
python3 <<'PY'
import shutil
import sys
from pathlib import Path

sys.path.insert(0, "server")
from downloads import (
    APP_BUNDLE,
    FULL_MAC_ZIP,
    FULL_WIN_ZIP,
    MAC_ZIP,
    ROOT,
    _build_full_zip,
    _ensure_full_zip,
)

_ensure_full_zip(FULL_MAC_ZIP, include_app=APP_BUNDLE.is_dir())
_ensure_full_zip(FULL_WIN_ZIP, include_app=False)
if APP_BUNDLE.is_dir():
    app_mtime = max(
        (p.stat().st_mtime for p in APP_BUNDLE.rglob("*") if p.is_file()),
        default=0,
    )
    if not MAC_ZIP.is_file() or MAC_ZIP.stat().st_mtime < app_mtime:
        base = MAC_ZIP.with_suffix("")
        if base.with_suffix(".zip").is_file():
            base.with_suffix(".zip").unlink()
        shutil.make_archive(str(base), "zip", ROOT, APP_BUNDLE.name)
print("Built:", FULL_MAC_ZIP.name, FULL_WIN_ZIP.name, end="")
if MAC_ZIP.is_file():
    print(",", MAC_ZIP.name, end="")
print()
PY

cp -f "$ROOT/data/Network-Monitor-Full-Mac.zip" "$OUT/"
cp -f "$ROOT/data/Network-Monitor-Full-Windows.zip" "$OUT/"
[ -f "$ROOT/data/Office-Network-Monitor-Mac.zip" ] && \
  cp -f "$ROOT/data/Office-Network-Monitor-Mac.zip" "$OUT/" || true

cp -f "$ROOT/START.command" "$OUT/"
cp -f "$ROOT/START.bat" "$OUT/"
chmod +x "$OUT/START.command" 2>/dev/null || true

if [ -f "$ROOT/web/guide.txt" ]; then
  cp -f "$ROOT/web/guide.txt" "$OUT/office-network-monitor-guide.txt"
fi

echo "downloads/ ready ($(find "$OUT" -type f | wc -l | tr -d ' ') files)"
