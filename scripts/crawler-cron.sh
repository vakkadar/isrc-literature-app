#!/usr/bin/env bash
# Wrapper invoked by user-cron on HP to run the weekly crawler.
# Cron entry (Saturday 09:00 America/New_York):
#   CRON_TZ=America/New_York
#   0 9 * * 6 /opt/isrc-literature-app/scripts/crawler-cron.sh >> /var/log/isrc-crawler.log 2>&1
set -euo pipefail

APP_DIR="/opt/isrc-literature-app"
COMPOSE_FILE="docker-compose.hp.yml"

cd "$APP_DIR"

echo "==== $(date -Is) crawler run start ===="
docker compose -f "$COMPOSE_FILE" exec -T api python manage.py run_crawler --group all --triggered-by cron
echo "==== $(date -Is) crawler run end ===="
