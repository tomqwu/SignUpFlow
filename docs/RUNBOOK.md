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
RELEASE_SHA=$(git rev-parse HEAD) VCS_REF=$(git rev-parse HEAD) \
  BUILD_DATE=$(date -u +%FT%TZ) docker compose up -d --build
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

## Health and readiness

- **Liveness:** `GET /health` always reports process health as `200`
  `{"status":"healthy","service":"signupflow-api","version":"1.0.0"}`.
  It does not open a database session and must be a separate orchestrator
  liveness probe when the platform supports distinct probes.
- **Readiness:** `GET /ready` → `200 {"status":"ready"}` or
  `503 {"status":"not_ready","reason":"dependency_unavailable"}`. Docker
  and Compose health checks use `/ready` so a node leaves rotation when the
  database is unreachable without exposing the dependency exception.

Every readiness session closes on success or failure. Three consecutive local
readiness failures emit one `database.readiness` trigger; the first success
emits one recovery. These are structured log signals, not proof an operator was
notified.

## Required configuration

| Env var | Purpose | Notes |
|---|---|---|
| `SECRET_KEY` | JWT signing | Must be unique and at least 32 characters. Invalid production values stop startup. |
| `DATABASE_URL` | Postgres DSN | compose sets `postgresql://…@db:5432/…` |
| `ENVIRONMENT` | Selects the production validator and secure middleware behavior | Compose sets `production`. |
| `RELEASE_SHA` | Correlates logs, reports, and deployed source | Required 40-character lowercase Git commit SHA. |
| `APP_URL`, `API_BASE_URL`, `FRONTEND_URL` | Public origins | Production requires explicit HTTPS origins. |
| `CORS_ALLOWED_ORIGINS` | API browser origins | Must explicitly include `FRONTEND_URL`; wildcard fails. |
| `ACCESS_TOKEN_EXPIRE_HOURS` | JWT and browser-session lifetime | One canonical positive value; default 24. |
| `EMAIL_ENABLED` + `SENDGRID_API_KEY` | Transactional email | default `false`; provider acceptance is not complete |
| `SMS_ENABLED` + `TWILIO_ACCOUNT_SID`/`_AUTH_TOKEN`/`_PHONE_NUMBER` | Deferred paid SMS | default `false`; enable only for an authorized sandbox validation |
| `BILLING_ENABLED` + `STRIPE_SECRET_KEY` | Deferred billing | default `false`; enable only for an authorized Stripe sandbox validation |
| `READINESS_FAILURE_ALERT_THRESHOLD` | Consecutive DB readiness failures before a local trigger | default `3`; must be a positive integer |
| `SENTRY_DSN` | Optional Sentry error reporting | absent means explicitly disabled; a configured sink initializes with PII and tracing off; invalid initialization stops startup |

Email, billing, and SMS are feature-gated off by default. Credentials alone do
not enable them. Their direct routes return 404 and their navigation is hidden.
Do not enable a provider without its separate authorized acceptance.

## Backups

Postgres data lives in the `postgres_data` volume. No scheduled backup, host
backup mount, retention guarantee, or tested restore procedure is supplied.
Follow #268 before relying on this topology for recovery.

## Database readiness

For a readiness trigger, inspect database reachability and pool health without
restarting the live process merely because PostgreSQL is unavailable. Restore
the dependency, verify `/ready` returns 200, and confirm one
`database.readiness` recovery record. External notification receipt is not yet
configured or proven.

## Notification queue

The bounded `notification.queue` rule triggers after three consecutive failures
and emits one recovery after success. No production worker currently records
this signal and no external recipient is configured; #266 owns queue wiring and
delivery acceptance.

## Backup freshness

The bounded `backup.freshness` rule triggers on the first failed freshness check
and emits one recovery. No backup scheduler currently records this signal. #268
must define the policy, wire the check, and prove backup/restore behavior before
this is an operational alert.

## Common incidents

| Symptom | Check | Action |
|---|---|---|
| `api` unhealthy | `docker compose logs api` and `curl /ready` | diagnose database reachability; do not restart the app into a liveness loop |
| 503 on `/ready` | sanitized `readiness.dependency_unavailable` log and database service logs | restore database reachability, then verify one readiness recovery signal |
| Login tokens rejected after deploy | `SECRET_KEY` changed | keep `SECRET_KEY` stable across deploys |
| Emails/SMS not sending | startup log + Settings page | set the sandbox/prod creds; features are gated |
| `migrate` exits nonzero | `docker compose logs migrate` | keep API replicas stopped; diagnose against an approved copy before retrying |

## Rollback

Rollback is not yet an accepted operator procedure. Do not run an Alembic
downgrade or substitute an unrecorded image. The local artifact harness records
an immutable image identity and migration behavior, but #268 must still produce
a restore drill and an operator-approved data-compatible rollback procedure.
