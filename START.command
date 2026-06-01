#!/bin/bash
# Double-click this file in Finder (do not paste into Terminal).
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT" || exit 1
chmod +x launcher.sh run.sh START.command 2>/dev/null
exec "$ROOT/launcher.sh"
