#!/bin/zsh
# One-time/manual bootstrap: pull secrets from 1Password and write them into
# .env as plain values. Run this yourself after cloning, and again whenever a
# token rotates — jobs read .env directly at run time and never call `op`
# themselves (op reads hung under launchd, 30-90s timeouts, cause unconfirmed;
# see git log 2026-07-21). 1Password stays the place you actually manage these
# credentials; .env is just the last-synced cache launchd reads from.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$REPO/.env"
[[ -f "$ENV_FILE" ]] || { echo "no .env — copy .env.example first" >&2; exit 1; }

OP_SERVICE_ACCOUNT_TOKEN="$(security find-generic-password -s op-service-account -w)"
export OP_SERVICE_ACCOUNT_TOKEN

# ENV_VAR=op://vault/item/field
MANIFEST=(
  "SLACK_MCP_TOKEN=op://Duvo/SlackApp/user_oauth_token"
  "GOOGLE_OAUTH_CLIENT_ID=op://Duvo/GoogleOAuth/client_id"
  "GOOGLE_OAUTH_CLIENT_SECRET=op://Duvo/GoogleOAuth/client_secret"
  "TODOIST_TOKEN=op://Duvo/Todoist/credential"
)

set_env_var() {
  local key="$1" value="$2"
  # Backslash-escape & and | so they survive sed's replacement text; value
  # may still contain other sed metacharacters, hence -e with a rare delim.
  local escaped="${value//\\/\\\\}"
  escaped="${escaped//|/\\|}"
  if grep -q "^${key}=" "$ENV_FILE"; then
    sed -i '' -e "s|^${key}=.*|${key}=${escaped}|" "$ENV_FILE"
  else
    printf '%s=%s\n' "$key" "$value" >> "$ENV_FILE"
  fi
}

for entry in "${MANIFEST[@]}"; do
  key="${entry%%=*}" ref="${entry#*=}"
  echo "syncing ${key} <- ${ref}"
  value="$(op read "$ref")"
  set_env_var "$key" "$value"
done

echo "done — .env updated (still gitignored)."
