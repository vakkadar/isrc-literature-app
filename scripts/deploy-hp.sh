#!/usr/bin/env bash
# Deploy/update on HP. Run from /opt/isrc-literature-app on HP.
set -euo pipefail

APP_DIR="/opt/isrc-literature-app"
COMPOSE_FILE="docker-compose.hp.yml"

cd "$APP_DIR"

echo "[1/5] git pull"
git pull --ff-only origin main

echo "[2/5] build images"
docker compose -f "$COMPOSE_FILE" build

echo "[3/5] up -d"
docker compose -f "$COMPOSE_FILE" up -d

echo "[4/5] migrate"
docker compose -f "$COMPOSE_FILE" exec -T api python manage.py migrate --noinput

echo "[5/5] collectstatic"
docker compose -f "$COMPOSE_FILE" exec -T api python manage.py collectstatic --noinput

echo "Done. Status:"
docker compose -f "$COMPOSE_FILE" ps
