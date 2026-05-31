#!/bin/bash
# Push current folder to GitHub (run from repo root or Desktop copy).
set -euo pipefail
cd "$(dirname "$0")/.."
REPO_URL="${1:-}"
if [[ -z "$REPO_URL" ]]; then
  echo "Usage: ./scripts/github-push.sh https://github.com/USER/REPO.git"
  exit 1
fi
git init
git add .
git commit -m "Network Monitor by Mohammad Faizan Khan" || true
git branch -M main
git remote remove origin 2>/dev/null || true
git remote add origin "$REPO_URL"
git push -u origin main
echo "Pushed to $REPO_URL"
