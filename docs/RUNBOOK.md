# SignUpFlow — Operations Runbook

Operator guide for deploying and running SignUpFlow in production. Grounded
in the actual `Dockerfile`, `docker-compose.yml`, and app endpoints.

## Stack

`docker-compose.yml` runs three services on `signupflow-network`:

- **db** — `postgres:16-alpine`, volume `postgres_data`, `./backups` mounted
  for dumps, `pg_isready` healthcheck.
- **redis** — `redis:7-alpine` (caching / rate-limit / sessions).
- **api** — built from `Dockerfile`; depends on `db` + `redis` being
  *healthy*; serves the API **and** the same-origin web UI on `:8000`.

## Deploy

```bash
cp .env.example .env          # then edit secrets (see below)
docker compose up -d --build
docker compose ps             # all services should be healthy
```

The image **entrypoint** (`docker-entrypoint.sh`) runs
`alembic upgrade head` before starting uvicorn, so a fresh Postgres is
migrated automatically on first boot. No manual migration step is needed;
to run migrations by hand: `docker compose exec api alembic upgrade head`.

## Health & readiness

- **Liveness:** `GET /health` → `200` `{"status":"healthy","database":"connected"}`
  (or `503` if the DB is down). Used by the container `HEALTHCHECK`.
- **Readiness:** `GET /ready` → `200 {"status":"ready"}` or
  `503 {"status":"not_ready",...}`. Point the orchestrator/load balancer
  at `/ready` so a node is pulled from rotation when the DB is unreachable.

## Required configuration

| Env var | Purpose | Notes |
|---|---|---|
| `SECRET_KEY` | JWT signing | **Must** be unique & ≥ 32 chars. Production logs a `CRITICAL` if it's the default/short. |
| `DATABASE_URL` | Postgres DSN | compose sets `postgresql://…@db:5432/…` |
| `ENVIRONMENT` | `production` enables HSTS + the SECRET_KEY guard | |
| `EMAIL_ENABLED` + `MAILTRAP_SMTP_USER`/`_PASSWORD` | Transactional email (sandbox: Mailtrap) | or `SENDGRID_API_KEY` for prod |
| `SMS_ENABLED` + `TWILIO_ACCOUNT_SID`/`_AUTH_TOKEN`/`_PHONE_NUMBER` | SMS | sandbox: Twilio magic number `+15005550006` |
| `STRIPE_SECRET_KEY` (`sk_test_…` for sandbox) | Billing | absent → billing UI shows setup notice, no crash |
| `SENTRY_DSN` | Error reporting | absent → disabled (logged at startup) |

Email/SMS/billing are **feature-gated**: absent credentials disable the
feature with an in-app notice — they never block startup.

## Backups

Postgres data lives in the `postgres_data` volume; `./backups` is mounted
into the `db` container.

```bash
# nightly dump
docker compose exec db pg_dump -U signupflow signupflow > backups/$(date +%F).sql
# restore
docker compose exec -T db psql -U signupflow signupflow < backups/<file>.sql
```

## Common incidents

| Symptom | Check | Action |
|---|---|---|
| `api` unhealthy | `docker compose logs api` | DB down? `/health` shows DB status |
| 503 on `/ready` | DB reachability | restart `db`; verify volume mounted |
| Login tokens rejected after deploy | `SECRET_KEY` changed | keep `SECRET_KEY` stable across deploys |
| Emails/SMS not sending | startup log + Settings page | set the sandbox/prod creds; features are gated |
| Migration error on boot | entrypoint log | `docker compose run --rm api alembic history` |

## Rollback

`docker compose` keeps the previous image until rebuilt. To roll back:
`docker compose up -d --no-build` with the prior image tag, then
`alembic downgrade -1` only if a migration must be reversed (rare —
prefer forward fixes).
