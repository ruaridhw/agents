#!/bin/zsh
# Render and load the LaunchAgents. Idempotent: reloads if already loaded.
#   ./scripts/install-launchd.sh [jobs…]           install/reload (default: both)
#   ./scripts/install-launchd.sh render            write plists to launchd/ only (no load)
#   ./scripts/install-launchd.sh remove [jobs…]    unload and delete (default: both)
# Job names: morning-brief granola-notion-sync — per-job installs support the
# one-at-a-time migration cutover.
#
# launchd (not cron) because StartCalendarInterval fires a missed run once on
# the next wake — cron silently skips runs while the Mac is asleep.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
AGENTS_DIR="$HOME/Library/LaunchAgents"
PREFIX="com.ruaridh.agent-jobs"

# label:job-name:calendar-entry generator
render_plist() {
  local label="$1" job="$2" intervals="$3"
  cat <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>${label}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/zsh</string>
    <string>-lc</string>
    <string>cd ${REPO} &amp;&amp; ./run.sh ${job}</string>
  </array>
  <key>StartCalendarInterval</key>
  <array>
${intervals}
  </array>
  <key>StandardOutPath</key><string>${REPO}/logs/launchd.${job}.out.log</string>
  <key>StandardErrorPath</key><string>${REPO}/logs/launchd.${job}.err.log</string>
</dict>
</plist>
PLIST
}

interval_entry() {
  printf '    <dict><key>Weekday</key><integer>%s</integer><key>Hour</key><integer>%s</integer><key>Minute</key><integer>0</integer></dict>\n' "$1" "$2"
}

unload_agent() {
  local label="$1"
  launchctl bootout "gui/$(id -u)/${label}" 2>/dev/null || true
}

ALL_JOBS=(morning-brief granola-notion-sync)

if [[ "${1:-}" == "remove" ]]; then
  shift
  if [[ $# -gt 0 ]]; then jobs=("$@"); else jobs=("${ALL_JOBS[@]}"); fi
  for job in "${jobs[@]}"; do
    unload_agent "${PREFIX}.${job}"
    rm -f "${AGENTS_DIR}/${PREFIX}.${job}.plist"
    echo "removed ${PREFIX}.${job}"
  done
  exit 0
fi

if [[ "${1:-}" == "render" || $# -eq 0 ]]; then
  jobs=("${ALL_JOBS[@]}")
else
  jobs=("$@")
fi

if [[ "${1:-}" == "render" ]]; then
  AGENTS_DIR="$REPO/launchd"   # preview only — nothing gets loaded
fi

mkdir -p "$AGENTS_DIR" "$REPO/logs"

for job in "${jobs[@]}"; do
  case "$job" in
    morning-brief)  # 08:00 Mon–Fri
      intervals=""
      for wd in 1 2 3 4 5; do
        intervals+="$(interval_entry "$wd" 8)"$'\n'
      done
      render_plist "${PREFIX}.${job}" "morning_brief" "${intervals%$'\n'}" \
        > "${AGENTS_DIR}/${PREFIX}.${job}.plist"
      ;;
    granola-notion-sync)  # hourly 08:00–18:00 Mon–Fri (launchd has no range syntax)
      intervals=""
      for wd in 1 2 3 4 5; do
        for hour in $(seq 8 18); do
          intervals+="$(interval_entry "$wd" "$hour")"$'\n'
        done
      done
      render_plist "${PREFIX}.${job}" "granola_notion_sync" "${intervals%$'\n'}" \
        > "${AGENTS_DIR}/${PREFIX}.${job}.plist"
      ;;
    *)
      echo "unknown job: $job (expected: ${ALL_JOBS[*]})" >&2
      exit 2
      ;;
  esac
done

for job in "${jobs[@]}"; do
  label="${PREFIX}.${job}"
  plutil -lint "${AGENTS_DIR}/${label}.plist" >/dev/null
  if [[ "${1:-}" == "render" ]]; then
    echo "rendered ${AGENTS_DIR}/${label}.plist (not loaded)"
    continue
  fi
  unload_agent "$label"
  launchctl bootstrap "gui/$(id -u)" "${AGENTS_DIR}/${label}.plist"
  echo "loaded ${label}"
done

echo
echo "Kick a job manually with:  launchctl kickstart gui/$(id -u)/${PREFIX}.morning-brief"
