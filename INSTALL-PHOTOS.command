#!/bin/bash
cd "$(dirname "$0")" || exit 1
python3 -c "
import sys
sys.path.insert(0, 'server')
from install_assets import install_web_assets
r = install_web_assets()
print('Logo:', r['logo'])
print('Photo:', r['creator'])
"
echo ""
echo "Done. Now double-click START.command and open http://127.0.0.1:5080/"
read -n 1 -s -r -p "Press any key to close…"
