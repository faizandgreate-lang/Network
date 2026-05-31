#!/bin/bash
# Slim copy for GitHub (under ~100 files — web upload limit). Use git push, not drag-and-drop.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${1:-$HOME/Desktop/Network-Monitor-GitHub}"

mkdir -p "$DEST"
rsync -a --delete \
  --exclude '.venv/' \
  --exclude '__pycache__/' \
  --exclude 'logs/' \
  --exclude '.DS_Store' \
  --exclude '**/.DS_Store' \
  --exclude '*.db' \
  --exclude '*.sqlite' \
  --exclude '*.sqlite3' \
  --exclude '.git/' \
  --exclude 'dist/' \
  --exclude 'web/locales/_langs/' \
  --exclude 'web/locales/_*.py' \
  --exclude 'web/locales/_*.part' \
  --exclude 'web/locales/*.command' \
  --exclude 'web/locales/build_phrases.py' \
  --exclude 'web/locales/write_phrases.py' \
  --exclude 'web/locales/emit_stdout.py' \
  --exclude 'assets/logo_2.png' \
  --exclude 'assets/creator_logo.png' \
  --exclude 'assets/creator-portrait.png' \
  --exclude 'web/assets/logo-mono.png' \
  --exclude 'web/assets/logo-display.png' \
  --exclude 'web/assets/creator-mono.png' \
  --exclude 'web/assets/creator-display.png' \
  "$ROOT/" "$DEST/"

# Post-clean (rsync excludes miss some paths on macOS)
rm -rf "$DEST/web/locales/_langs"
find "$DEST/web/locales" -maxdepth 1 -name '_*.py' -delete 2>/dev/null || true
find "$DEST/web/locales" -maxdepth 1 -name '_*.part' -delete 2>/dev/null || true
find "$DEST/web/locales" -maxdepth 1 -name '*.command' -delete 2>/dev/null || true
rm -f "$DEST/web/locales/build_phrases.py" "$DEST/web/locales/write_phrases.py" "$DEST/web/locales/emit_stdout.py" 2>/dev/null || true
rm -f "$DEST/assets/logo_2.png" "$DEST/assets/creator_logo.png" "$DEST/assets/creator-portrait.png" 2>/dev/null || true
rm -f "$DEST/web/assets/logo-mono.png" "$DEST/web/assets/logo-display.png" 2>/dev/null || true
rm -f "$DEST/web/assets/creator-mono.png" "$DEST/web/assets/creator-display.png" 2>/dev/null || true
find "$DEST" -name '.DS_Store' -delete 2>/dev/null || true

cp "$ROOT/.gitignore" "$DEST/.gitignore" 2>/dev/null || true

cat > "$DEST/GITHUB-UPLOAD.txt" << 'EOF'
Network Monitor — upload to GitHub (Terminal only)
=================================================

GitHub website "Upload files" allows only ~100 files — use git push instead.

PREVIEW (same layout): https://faizandgreate-lang.github.io/Network/
  → Repo Settings → Pages → branch main, folder /docs

FULL APP (scan): download ZIP → START.command / START.bat → http://127.0.0.1:5080/

STEP 1 — Create empty repo on github.com (no README, no .gitignore).

STEP 2 — Run these commands (copy/paste):

  cd ~/Desktop/Network-Monitor-GitHub
  git init
  git add .
  git commit -m "Network Monitor by Mohammad Faizan Khan"
  git branch -M main
  git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
  git push -u origin main

Replace YOUR_USERNAME and YOUR_REPO with your repo.

Or double-click: PUSH-TO-GITHUB.command (edit repo URL inside first).

Creator: Mohammad Faizan Khan — https://khan.linux-aios.com
Read DISCLAIMER.md before publishing.
EOF

cat > "$DEST/PUSH-TO-GITHUB.command" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
REPO_URL="https://github.com/YOUR_USERNAME/YOUR_REPO.git"
echo "Edit PUSH-TO-GITHUB.command and set REPO_URL first."
echo "Current: $REPO_URL"
read -r -p "Press Enter to cancel, or type YES to push: " ok
[[ "$ok" == "YES" ]] || exit 0
git init 2>/dev/null || true
git add .
git commit -m "Network Monitor by Mohammad Faizan Khan" || true
git branch -M main
git remote remove origin 2>/dev/null || true
git remote add origin "$REPO_URL"
git push -u origin main
echo "Done."
read -r -p "Press Enter to close."
EOF
chmod +x "$DEST/PUSH-TO-GITHUB.command"

chmod +x "$DEST/START.command" 2>/dev/null || true
chmod +x "$DEST/launcher.sh" 2>/dev/null || true
chmod +x "$DEST/scripts/prepare-github-desktop.sh" 2>/dev/null || true

COUNT=$(find "$DEST" -type f | wc -l | tr -d ' ')
bash "$ROOT/scripts/sync-docs-for-github-pages.sh" 2>/dev/null || true
if [[ -d "$ROOT/docs" ]]; then
  rsync -a --delete --exclude '.DS_Store' "$ROOT/docs/" "$DEST/docs/"
fi

COUNT=$(find "$DEST" -type f | wc -l | tr -d ' ')
echo "Ready: $DEST ($COUNT files)"
open "$DEST" 2>/dev/null || true
