#!/usr/bin/env bash
# Installs the weekly crawler user-cron on HP. Run on HP as the deploy user (rvakkada).
# Idempotent: replaces any existing 'crawler-cron.sh' entry.
set -euo pipefail

APP_DIR="/opt/isrc-literature-app"
SCRIPT="$APP_DIR/scripts/crawler-cron.sh"
LOG_FILE="/var/log/isrc-crawler.log"
MARKER="crawler-cron.sh"
TZ_LINE="CRON_TZ=America/New_York"
CRON_LINE="0 9 * * 6 $SCRIPT >> $LOG_FILE 2>&1"

if [[ ! -x "$SCRIPT" ]]; then
    echo "ERROR: $SCRIPT not found or not executable. Run 'git pull' in $APP_DIR first." >&2
    exit 1
fi

if [[ ! -w "$LOG_FILE" ]]; then
    sudo touch "$LOG_FILE"
    sudo chown "$USER":"$USER" "$LOG_FILE"
fi

current=$(crontab -l 2>/dev/null || true)
filtered=$(echo "$current" | grep -v "$MARKER" | grep -v '^CRON_TZ=America/New_York$' || true)

{
    [[ -n "$filtered" ]] && echo "$filtered"
    echo "$TZ_LINE"
    echo "$CRON_LINE"
} | crontab -

echo "Installed crawler cron (Saturday 09:00 America/New_York)."
echo "Logs: $LOG_FILE"
echo "Verify: crontab -l"
