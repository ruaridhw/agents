#!/bin/zsh
# Render and load the two LaunchAgents. Idempotent: reloads if already loaded.
#   ./scripts/install-launchd.sh            install/reload both
#   ./scripts/install-launchd.sh render     write plists to launchd/ only (no load)
#   ./scripts/install-launchd.sh remove     unload and delete both
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

if [[ "${1:-}" == "remove" ]]; then
  for job in morning-brief granola-notion-sync; do
    unload_agent "${PREFIX}.${job}"
    rm -f "${AGENTS_DIR}/${PREFIX}.${job}.plist"
    echo "removed ${PREFIX}.${job}"
  done
  exit 0
fi

if [[ "${1:-}" == "render" ]]; then
  AGENTS_DIR="$REPO/launchd"   # preview only — nothing gets loaded
fi

mkdir -p "$AGENTS_DIR" "$REPO/logs"

# morning-brief: 08:00 Mon–Fri
brief_intervals=""
for wd in 1 2 3 4 5; do
  brief_intervals+="$(interval_entry "$wd" 8)"$'\n'
done
render_plist "${PREFIX}.morning-brief" "morning_brief" "${brief_intervals%$'\n'}" \
  > "${AGENTS_DIR}/${PREFIX}.morning-brief.plist"

# granola-notion-sync: hourly 08:00–18:00 Mon–Fri (launchd has no range syntax)
sync_intervals=""
for wd in 1 2 3 4 5; do
  for hour in $(seq 8 18); do
    sync_intervals+="$(interval_entry "$wd" "$hour")"$'\n'
  done
done
render_plist "${PREFIX}.granola-notion-sync" "granola_notion_sync" "${sync_intervals%$'\n'}" \
  > "${AGENTS_DIR}/${PREFIX}.granola-notion-sync.plist"

for job in morning-brief granola-notion-sync; do
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
