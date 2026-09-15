# SignUpFlow — Operations Runbook

Production-like operator reference grounded in the current `Dockerfile`,
`docker-compose.yml`, and app endpoints. It does not authorize deployment or
claim production readiness. Read the [effective configuration contract](PRODUCTION_CONFIGURATION.md)
and [release roadmap](ROADMAP.md) first.

## Stack

`docker-compose.yml` runs four services on `signupflow-network`:

- **db** — `postgres:16-alpine`, private-only, volume `postgres_data`, and a
  `pg_isready` healthcheck.
- **redis** — `redis:7-alpine` for configured task/broker consumers. Rate limits
  and SSE remain process-local. Redis is authenticated and private-only.
- **migrate** — one-shot `alembic upgrade head`; starts after PostgreSQL is
  healthy and must exit successfully before API replicas start.
- **api** — built from `Dockerfile`; depends on the completed migration and
  healthy Redis; serves the API and same-origin web UI on `:8000` with one worker.
  It runs non-root with read-only source, no bind mounts, no capabilities, and
  `no-new-privileges`.

## Local Artifact Exercise

```bash
cp .env.example .env          # supply every required production-like value
VCS_REF=$(git rev-parse HEAD) BUILD_DATE=$(date -u +%FT%TZ) docker compose up -d --build
docker compose ps --all       # migrate exited 0; db/redis/api are healthy
```

The image entrypoint only executes its declared command. It never migrates.
Compose runs the migration service exactly once before replicas. For a later
schema change, run an explicitly approved one-shot migration using the same image
and configuration, verify its zero exit code, then replace API replicas. Never
run Alembic concurrently from each replica.

For the maintained provider-free local artifact proof, commit the tracked source
and run `make test-artifact`. Inspect the emitted report and retained image tag.
This command does not use Compose volumes, contact staging, or authorize release.

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

Postgres data lives in the `postgres_data` volume. No scheduled backup, host
backup mount, retention guarantee, or tested restore procedure is supplied.
Follow #268 before relying on this topology for recovery.

## Common incidents

| Symptom | Check | Action |
|---|---|---|
| `api` unhealthy | `docker compose logs api` | DB down? `/health` shows DB status |
| 503 on `/ready` | DB reachability | restart `db`; verify volume mounted |
| Login tokens rejected after deploy | `SECRET_KEY` changed | keep `SECRET_KEY` stable across deploys |
| Emails/SMS not sending | startup log + Settings page | set the sandbox/prod creds; features are gated |
| `migrate` exits nonzero | `docker compose logs migrate` | keep API replicas stopped; diagnose against an approved copy before retrying |

## Rollback

Rollback is not yet an accepted operator procedure. Do not run an Alembic
downgrade or substitute an unrecorded image. The local artifact harness records
an immutable image identity and migration behavior, but #268 must still produce
a restore drill and an operator-approved data-compatible rollback procedure.
