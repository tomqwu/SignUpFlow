#!/bin/sh
# Production container entrypoint: apply DB migrations, then run the app.
#
# Runs `alembic upgrade head` so a fresh Postgres (docker-compose `db`
# service) is schema-ready on first boot, then exec's the CMD (uvicorn).
# `exec` keeps uvicorn as PID 1 so signals/healthchecks work.
set -e

echo "[entrypoint] Applying database migrations (alembic upgrade head)…"
alembic upgrade head
echo "[entrypoint] Migrations applied. Starting: $*"

exec "$@"
