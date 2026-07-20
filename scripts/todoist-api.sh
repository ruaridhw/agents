#!/bin/zsh
# Todoist REST call with the token resolved internally (Keychain → 1Password).
# The single Bash entrypoint unattended jobs are allowed to use for Todoist —
# the token never appears in a command line, log, or tool output.
#   scripts/todoist-api.sh METHOD PATH [JSON_BODY]
#   e.g. scripts/todoist-api.sh GET "/tasks?project_id=$TODOIST_PROJECT_ID"
#        scripts/todoist-api.sh POST /tasks '{"content":"…"}'
set -euo pipefail

: "${TODOIST_TOKEN_OP_REF:?set TODOIST_TOKEN_OP_REF (see .env.example)}"
# NB: not `path=` — zsh ties lowercase `path` to PATH.
method="$1" api_path="$2" body="${3:-}"

# Split declaration from assignment so `set -e` catches a failed fetch
# (`export VAR="$(cmd)"` masks the command's exit status).
OP_SERVICE_ACCOUNT_TOKEN="$(security find-generic-password -s op-service-account -w)"
export OP_SERVICE_ACCOUNT_TOKEN
token="$(op read "$TODOIST_TOKEN_OP_REF")"

args=(-sf -X "$method" -H "Authorization: Bearer $token")
if [[ -n "$body" ]]; then
  args+=(-H "Content-Type: application/json" -d "$body")
fi
curl "${args[@]}" "https://api.todoist.com/api/v1${api_path}"
