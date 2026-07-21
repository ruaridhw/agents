#!/bin/zsh
# Todoist REST call with the token taken from the environment.
# The single Bash entrypoint unattended jobs are allowed to use for Todoist —
# the token never appears in a command line, log, or tool output.
#   scripts/todoist-api.sh METHOD PATH [JSON_BODY]
#   e.g. scripts/todoist-api.sh GET "/tasks?project_id=$TODOIST_PROJECT_ID"
#        scripts/todoist-api.sh POST /tasks '{"content":"…"}'
set -euo pipefail

: "${TODOIST_TOKEN:?set TODOIST_TOKEN in .env (run scripts/sync-secrets-from-1password.sh)}"
# NB: not `path=` — zsh ties lowercase `path` to PATH.
method="$1" api_path="$2" body="${3:-}"

args=(-sf -X "$method" -H "Authorization: Bearer $TODOIST_TOKEN")
if [[ -n "$body" ]]; then
  args+=(-H "Content-Type: application/json" -d "$body")
fi
curl "${args[@]}" "https://api.todoist.com/api/v1${api_path}"
