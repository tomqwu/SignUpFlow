# SignUpFlow — Operations Runbook

Production-like operator reference grounded in the current `Dockerfile`,
`docker-compose.yml`, and app endpoints. It does not authorize deployment or
claim production readiness. Read the [effective configuration contract](PRODUCTION_CONFIGURATION.md)
and [release roadmap](ROADMAP.md) first.

## Stack

`docker-compose.yml` runs three services on `signupflow-network`:

- **db** — `postgres:16-alpine`, volume `postgres_data`, `./backups` mounted
  for dumps, `pg_isready` healthcheck.
- **redis** — `redis:7-alpine` for configured task/broker consumers. Rate limits
  and SSE remain process-local.
- **api** — built from `Dockerfile`; depends on `db` + `redis` being
  *healthy*; serves the API and same-origin web UI on `:8000` with one worker.

## Local Artifact Exercise

```bash
cp .env.example .env          # supply every required production-like value
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
| `SECRET_KEY` | JWT signing | Must be unique and at least 32 characters. Invalid production values stop startup. |
| `DATABASE_URL` | Postgres DSN | compose sets `postgresql://…@db:5432/…` |
| `ENVIRONMENT` | Selects the production validator and secure middleware behavior | Compose sets `production`. |
| `APP_URL`, `API_BASE_URL`, `FRONTEND_URL` | Public origins | Production requires explicit HTTPS origins. |
| `CORS_ALLOWED_ORIGINS` | API browser origins | Must explicitly include `FRONTEND_URL`; wildcard fails. |
| `ACCESS_TOKEN_EXPIRE_HOURS` | JWT and browser-session lifetime | One canonical positive value; default 24. |
| `EMAIL_ENABLED` + `SENDGRID_API_KEY` | Transactional email | default `false`; provider acceptance is not complete |
| `SMS_ENABLED` + `TWILIO_ACCOUNT_SID`/`_AUTH_TOKEN`/`_PHONE_NUMBER` | Deferred paid SMS | default `false`; enable only for an authorized sandbox validation |
| `BILLING_ENABLED` + `STRIPE_SECRET_KEY` | Deferred billing | default `false`; enable only for an authorized Stripe sandbox validation |
| `SENTRY_DSN` | Error reporting | absent → disabled (logged at startup) |

Email, billing, and SMS are feature-gated off by default. Credentials alone do
not enable them. Their direct routes return 404 and their navigation is hidden.
Do not enable a provider without its separate authorized acceptance.

## Backups

Postgres data lives in the `postgres_data` volume and `./backups` is mounted
into the database container. No scheduled backup, retention guarantee, or
tested restore procedure is currently supplied. Follow #268 before relying on
this mount for recovery.

## Common incidents

| Symptom | Check | Action |
|---|---|---|
| `api` unhealthy | `docker compose logs api` | DB down? `/health` shows DB status |
| 503 on `/ready` | DB reachability | restart `db`; verify volume mounted |
| Login tokens rejected after deploy | `SECRET_KEY` changed | keep `SECRET_KEY` stable across deploys |
| Emails/SMS not sending | startup log + Settings page | set the sandbox/prod creds; features are gated |
| Migration error on boot | entrypoint log | `docker compose run --rm api alembic history` |

## Rollback

Rollback is not yet an accepted operator procedure. Do not run an Alembic
downgrade or substitute an unrecorded image. #265 and #268 must produce an
immutable artifact, migration compatibility decision, restore drill, and
recorded rollback command before this section can become operational.
