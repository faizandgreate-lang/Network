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
