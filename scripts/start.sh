#!/bin/sh
set -eu

APP_MODULE="${APP_MODULE:-app.main:app}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
WEB_CONCURRENCY="${WEB_CONCURRENCY:-2}"
LOG_LEVEL="${LOG_LEVEL:-info}"

mkdir -p /var/www/static /var/www/media

# Keep shared static volume populated for the Nginx container.
cp -R /app/app/static/. /var/www/static/

if [ "${RUN_MIGRATIONS:-false}" = "true" ]; then
  alembic upgrade head
fi

exec uvicorn "${APP_MODULE}" \
  --host "${HOST}" \
  --port "${PORT}" \
  --workers "${WEB_CONCURRENCY}" \
  --proxy-headers \
  --forwarded-allow-ips="*"
