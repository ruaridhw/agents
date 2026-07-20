#!/bin/zsh
# Symlink the repo's git hooks into .git/hooks.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
ln -sf "$REPO/scripts/hooks/pre-commit" "$REPO/.git/hooks/pre-commit"
echo "installed pre-commit hook (gitleaks)"
