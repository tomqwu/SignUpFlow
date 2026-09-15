# SignUpFlow — Operations Runbook

Production-like operator reference grounded in the current `Dockerfile`,
`docker-compose.yml`, and app endpoints. It does not authorize deployment or
claim production readiness. Read the [effective configuration contract](PRODUCTION_CONFIGURATION.md)
and [release roadmap](ROADMAP.md) first.

## Stack

`docker-compose.yml` runs six services on `signupflow-network`:

- **db** — `postgres:16-alpine`, private-only, volume `postgres_data`, and a
  `pg_isready` healthcheck.
- **redis** — `redis:7-alpine` for shared rate limits, tenant-scoped solution-refresh
  pub/sub, and the notification broker/result backend. It is authenticated and private-only.
- **migrate** — one-shot `alembic upgrade head`; starts after PostgreSQL is
  healthy and must exit successfully before API replicas start.
- **api** — built from `Dockerfile`; depends on the completed migration and
  healthy Redis; serves the API and same-origin web UI on `:8000` with one worker.
  It runs non-root with read-only source, no bind mounts, no capabilities, and
  `no-new-privileges`.
- **celery-worker** — consumes committed notification references with late acknowledgement,
  one-at-a-time prefetch, database leases, bounded retry, and dead-letter states.
- **celery-beat** — the single scheduler instance; re-enqueues due intents and starts
  reminder/digest jobs without activating a paid provider.

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
The command terminates HTTPS with an ephemeral self-signed loopback certificate and
verifies secure browser-session behavior through an owned reverse proxy. It deletes
the private key after the run. This command does not exercise external ingress or
managed TLS, use Compose volumes, contact staging, or authorize release.

## Authorized Staging Acceptance

Only after the owner records the disposable target and deployment authorization, run the
provider-neutral staging receipt from a clean committed checkout:

```bash
STAGING_BASE_URL=https://staging.example.invalid \
STAGING_EXPECTED_RELEASE_SHA=<exact-deployed-40-character-sha> \
STAGING_APPROVAL_REFERENCE=<https-approval-receipt> \
make test-staging
```

The command refuses remote HTTP, URL credentials, paths, missing approval receipts and
release-header mismatches before creating test data. It verifies managed TLS, `/health`,
`/ready`, every selected pluggable six-week API playbook, secure browser cookies and
browser security headers. Credentials are generated in memory and omitted from the
report. The report retains synthetic organization IDs so the staging owner can apply the
target's approved cleanup procedure.

This command does not create or update a deployment, run migrations, configure DNS,
enable email/billing/SMS, trigger operator alerts, restore backups, prove rollback or
approve a release. A passing receipt satisfies only the staging business/browser smoke
portion of #265/#271 for the exact observed SHA.

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
| `EMAIL_ENABLED` + `SENDGRID_API_KEY` + `SENDGRID_WEBHOOK_PUBLIC_KEY` | Transactional email and signed delivery callback | default `false`; provider acceptance is not complete |
| `SMS_ENABLED` + `TWILIO_ACCOUNT_SID`/`_AUTH_TOKEN`/`_PHONE_NUMBER` + callback URLs | Deferred paid SMS | default `false`; production callback URLs must be exact external HTTPS URLs; enable only for an authorized sandbox validation |
| `BILLING_ENABLED` + `STRIPE_SECRET_KEY` + `STRIPE_WEBHOOK_SECRET` | Deferred billing | default `false`; enable only for an authorized Stripe sandbox validation |
| `READINESS_FAILURE_ALERT_THRESHOLD` | Consecutive DB readiness failures before a local trigger | default `3`; must be a positive integer |
| `SENTRY_DSN` | Optional Sentry error reporting | absent means explicitly disabled; a configured sink initializes with PII and tracing off; invalid initialization stops startup |

Email, billing, and SMS are feature-gated off by default. Credentials alone do
not enable them. Their direct routes return 404 and their navigation is hidden.
Do not enable a provider without its separate authorized acceptance.

When an authorized SMS sandbox is used, configure Twilio's incoming-message URL
as `TWILIO_INCOMING_SMS_URL` and delivery callback as
`TWILIO_STATUS_CALLBACK_URL`. The application validates signatures against
those configured URLs instead of trusting request or forwarded-host headers.
Missing or invalid signatures return 403 before callback state changes.

When an authorized Stripe sandbox is used, configure the signed callback as
`/api/v1/webhooks/stripe`. Subscription and invoice events must carry `org_id` in
provider metadata. The handler records `provider_events` receipts and applies only
newer state for the matched tenant. Checkout creation records `provider_operations`;
`reconciliation_required` means the provider outcome was uncertain and the same
operation must not be retried until an operator compares it with Stripe. There is no
approved automated refund, credit, pricing, quota, or live-mode policy. Do not infer
one from historical specifications, and do not edit entitlement to make a sandbox
journey appear successful.

## Backups

Postgres data lives in the `postgres_data` volume. No scheduled PostgreSQL backup,
host backup mount, off-site destination, key-custody arrangement, retention guarantee,
or production restore is supplied. Follow #268 before relying on this topology for
recovery.

### SQLite recovery foundation

The supported local SQLite tool never defaults to `roster.db`, copies a live database,
overwrites a target, or performs cutover. Use absolute paths and create a new workspace
in an empty location. Keep the key outside the workspace and backup storage.

```bash
poetry run python scripts/sqlite_recovery.py init-workspace /absolute/new/recovery-workspace
poetry run python scripts/sqlite_recovery.py generate-key /absolute/new/recovery.key

scripts/backup_database.sh \
  --workspace /absolute/new/recovery-workspace \
  --source /absolute/source.sqlite \
  --key-file /absolute/new/recovery.key \
  --name incident-20260915 \
  --dry-run

scripts/backup_database.sh \
  --workspace /absolute/new/recovery-workspace \
  --source /absolute/source.sqlite \
  --key-file /absolute/new/recovery.key \
  --name incident-20260915

poetry run python scripts/sqlite_recovery.py verify \
  --workspace /absolute/new/recovery-workspace \
  --bundle /absolute/new/recovery-workspace/backups/incident-20260915.sufbackup \
  --key-file /absolute/new/recovery.key

scripts/restore_database.sh \
  --workspace /absolute/new/recovery-workspace \
  --bundle /absolute/new/recovery-workspace/backups/incident-20260915.sufbackup \
  --key-file /absolute/new/recovery.key \
  --name isolated-restore \
  --dry-run

scripts/restore_database.sh \
  --workspace /absolute/new/recovery-workspace \
  --bundle /absolute/new/recovery-workspace/backups/incident-20260915.sufbackup \
  --key-file /absolute/new/recovery.key \
  --name isolated-restore
```

The backup uses SQLite's backup API, verifies the current Alembic head, encrypts with
AES-256-GCM, authenticates metadata, and stores plaintext/ciphertext SHA-256 checksums.
Restore verifies authentication, checksum, SQLite integrity, foreign keys, and migration
head before atomically publishing `restores/isolated-restore.sqlite`. If interrupted
before publication, only the operation's temporary file is removed. If interrupted after
atomic publication, preserve the complete target for inspection; rerunning refuses to
touch it.

Do not point the application at the restored file until an operator has reviewed its
`.restore.json` receipt and explicitly prepared an isolated provider-disabled environment.
The recovery tool never starts workers or replays queued work. Terminal notification
rows remain terminal; pending rows remain pending and must be reconciled before any
delivery provider is enabled. There is no overwrite or production-cutover option.

Run `make test-recovery` to execute the fictional WAL and restored Church/Basketball
acceptance drill. The report records source SHA, checksums, measured local backup/restore
time, recovery-point age, migration head, test counts, and key destruction. These local
measurements are not owner-approved production RPO/RTO evidence.

## Database readiness

For a readiness trigger, inspect database reachability and pool health without
restarting the live process merely because PostgreSQL is unavailable. Restore
the dependency, verify `/ready` returns 200, and confirm one
`database.readiness` recovery record. External notification receipt is not yet
configured or proven.

## Notification queue

Committed scheduling-notification intents survive broker loss. A worker atomically claims
each tenant-scoped row, recovers expired leases, backs off transient failures, and stops
automatic retries in `dead_letter` or `uncertain`; administrators can see those states in
notification statistics. Celery beat scans due rows once per minute. Investigate worker,
broker, and database health before manually reconciling either terminal state.

With delivery disabled, the scheduler leaves committed intents pending and does not contact
the broker. Daily and weekly preferences also remain pending for their digest job instead of
being sent immediately; the digest tasks are still placeholders. A provider can accept a
message immediately before a worker dies or its completion commit fails. The observable
commit-failure path becomes `uncertain`, but external exactly-once delivery still requires
provider idempotency or reconciliation and is not claimed by this local implementation.

The bounded `notification.queue` operational rule is not yet wired to these worker states,
and no external recipient is configured. #267 retains external alert delivery and operator
receipt acceptance; do not call local database visibility an alert.

## Backup freshness

The bounded `backup.freshness` rule triggers on the first failed freshness check
and emits one recovery. The local SQLite tool and drill do not schedule backups or
record this signal. #268 must still define an approved production policy, wire the
real producer, and prove operator receipt before this is an operational alert.

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
an immutable image identity and migration behavior, and the SQLite drill proves only
isolated fictional restoration. #268 still needs an approved PostgreSQL/hosting backup,
restore, cutover, retention, and data-compatible rollback procedure.
