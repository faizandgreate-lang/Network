#!/bin/bash
cd "$(dirname "$0")" || exit 1
chmod +x launcher.sh run.sh 2>/dev/null
exec ./launcher.sh
