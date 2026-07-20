#!/bin/zsh
# Entry point for launchd (and manual runs): ./run.sh <job-name>
# Sources .env, activates the venv, then runs the job (which preflights itself).
set -euo pipefail

REPO="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO"

if [[ $# -lt 1 ]]; then
  echo "usage: ./run.sh <job-name> [--dry-run]" >&2
  exit 2
fi

# Export .env so stdio MCP servers spawned by the SDK inherit their secrets.
if [[ -f .env ]]; then
  set -a
  source .env
  set +a
fi

if [[ ! -d .venv ]]; then
  echo "no .venv — run: uv sync" >&2
  exit 1
fi
source .venv/bin/activate

# stdio MCP servers are launched with npx; make sure node is on PATH under launchd.
if ! command -v node >/dev/null 2>&1 && [[ -d "$HOME/.nvm" ]]; then
  export NVM_DIR="$HOME/.nvm"
  [[ -s "$NVM_DIR/nvm.sh" ]] && source "$NVM_DIR/nvm.sh"
fi

exec python -m runner.run_job "$@"
