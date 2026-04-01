#!/usr/bin/env bash
set -euo pipefail

REMOTE_URL="${1:-git@github.com:Security-Si/CYBER-PROJECT.git}"
BRANCH="${2:-main}"

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
  echo "Erreur: exécuter ce script dans un dépôt git." >&2
  exit 1
}

git remote get-url origin >/dev/null 2>&1 || git remote add origin "$REMOTE_URL"
git remote set-url origin "$REMOTE_URL"

git fetch origin

CURRENT_BRANCH="$(git branch --show-current || true)"
if [[ -z "${CURRENT_BRANCH}" ]]; then
  git checkout -B "$BRANCH"
fi

git pull --rebase origin "$BRANCH"
git push -u origin "$BRANCH"

echo "OK: push sur $REMOTE_URL ($BRANCH)"

