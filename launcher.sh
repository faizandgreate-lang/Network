#!/bin/bash
# One-click start — used by START.command and the .app (no typing needed)
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT" || exit 1
chmod +x launcher.sh run.sh START.command 2>/dev/null
chmod +x "Office Network Monitor.app/Contents/MacOS/launcher" 2>/dev/null

export BIND=0.0.0.0
export PORT=5080
export AUTO_SCAN_MINUTES=0
export RESOLVE_NAMES=1
export ENRICH_PORTS=1

if ! command -v python3 >/dev/null 2>&1; then
  osascript -e 'display alert "Install Python 3" message "Download from python.org" as critical'
  exit 1
fi

[ -d .venv ] || python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -r requirements.txt 2>/dev/null
python3 -c "import sys; sys.path.insert(0,'server'); from install_assets import install_web_assets; install_web_assets()" 2>/dev/null || true

# Stop old copy so port is free
for p in 5080 5081 5082; do
  lsof -ti:"$p" 2>/dev/null | xargs kill -9 2>/dev/null
done

mkdir -p logs
LOG="$ROOT/logs/server.log"

if [ "${1:-}" = "--background" ]; then
  nohup python3 server/main.py >>"$LOG" 2>&1 &
  sleep 3
  open "http://127.0.0.1:${PORT}/devices.html"
  osascript -e 'display notification "Open Safari if the page did not appear." with title "Network Monitor"'
  exit 0
fi

echo "Starting… browser opens automatically. Keep this window open."
open "http://127.0.0.1:${PORT}/devices.html" 2>/dev/null &
exec python3 server/main.py
