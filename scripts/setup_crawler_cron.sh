#!/usr/bin/env bash
set -euo pipefail

CRON_CMD='0 3 * * 0 cd /opt/isrc-literature-app && docker compose -f docker-compose.prod.yml exec -T api python manage.py run_crawler >> /var/log/isrc-crawler.log 2>&1'
LOG_FILE="/var/log/isrc-crawler.log"

if ! command -v crontab &>/dev/null; then
    echo "ERROR: crontab not found. Install cron first."
    exit 1
fi

sudo touch "$LOG_FILE"
sudo chmod 666 "$LOG_FILE"

existing=$(crontab -l 2>/dev/null || true)
if echo "$existing" | grep -qF "run_crawler"; then
    echo "Crawler cron job already exists:"
    echo "$existing" | grep "run_crawler"
    echo ""
    echo "To replace it, remove the existing entry first: crontab -e"
    exit 0
fi

(echo "$existing"; echo ""; echo "$CRON_CMD") | crontab -
echo "Cron job installed. Crawler will run every Sunday at 3:00 AM."
echo "Logs: $LOG_FILE"
echo ""
echo "Verify with: crontab -l"
