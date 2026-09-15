# Production Configuration Contract

This is the maintained effective-settings reference for the application. It is
not deployment authorization or production acceptance. `config/env.prod.yaml`
is a human-readable checklist only; the application reads environment variables.

At startup, `api.main.lifespan` calls
`api.core.runtime_config.validate_production_environment()` before database
initialization. Development and test behavior is unchanged. When
`ENVIRONMENT=production`, any invalid item below stops startup with variable
names and reasons only; secret values are not included in the error.

## Required Settings

| Setting | Runtime reader | Development default | Production rule |
| --- | --- | --- | --- |
| `ENVIRONMENT` | runtime validator and middleware | `development` | Set exactly to `production` for this contract. |
| `RELEASE_SHA` | structured logging and operational signals | `unknown` | Supply the exact 40-character lowercase Git commit SHA; missing or malformed values fail. |
| `SECRET_KEY` | `api.security` | known sample value | Supply a unique value of at least 32 characters; known repository samples fail. |
| `DATABASE_URL` | `api.database` | local SQLite | Use a PostgreSQL URL with a host and database; known sample credentials fail. |
| `RATE_LIMIT_STORAGE` | `api.utils.rate_limiter` | process-local memory | Set to `redis`; any other production value fails. |
| `REDIS_URL` or `RATE_LIMIT_REDIS_URL` | shared request limiter | localhost Redis | Supply an authenticated `redis://` or `rediss://` URL; missing, malformed, or sample credentials fail. |
| `EVENT_BUS_STORAGE` | `api.services.event_bus` | process-local memory | Set to `redis`; any other production value fails. |
| `EVENT_BUS_REDIS_URL` or `REDIS_URL` | solution-review refresh bus | localhost Redis | Supply the private authenticated Redis endpoint used for tenant-scoped cross-worker refresh hints. |
| `CELERY_BROKER_URL` / `CELERY_RESULT_BACKEND` | notification worker and beat | localhost Redis | Supply private authenticated Redis endpoints; Compose derives both from `REDIS_URL`. |
| `ACCESS_TOKEN_EXPIRE_HOURS` | `api.core.runtime_config` | `24` | Use a positive finite value of at least one minute. Browser session `Max-Age` uses the same value. |
| `APP_URL` | message-link generation and browser-origin fallback | localhost | Supply one HTTPS origin with no path, query, or credentials. |
| `FRONTEND_URL` | browser-origin enforcement and message links | APP_URL/localhost fallback | Supply the exact public HTTPS browser origin. |
| `API_BASE_URL` | deployment/operator contract | localhost | Supply the public HTTPS API origin. |
| `CORS_ALLOWED_ORIGINS` | CORS middleware | local origins | Supply explicit comma-separated HTTPS origins including `FRONTEND_URL`; wildcard is rejected. |
| `TRUSTED_PROXY_IPS` | rate limits and audit logging | empty | Leave empty for direct peers or list only the actual proxy IPs/CIDRs. Invalid or all-address networks fail. |
| `SECURITY_HSTS_MAX_AGE` | security-header middleware | `31536000` | Use a positive integer number of seconds. |
| `READINESS_FAILURE_ALERT_THRESHOLD` | database readiness signal | `3` | Use a positive integer; one trigger is emitted after this many consecutive failures and one recovery after success. |
| `SENTRY_DSN` | optional error reporter | absent/disabled | When supplied, Sentry initializes before database startup with PII and tracing disabled. Invalid initialization stops startup without logging the DSN. |

## Fail-Closed Controls

Production requires `TESTING`, `DEBUG`, `DEBUG_RETURN_RESET_TOKEN`,
`DISABLE_RATE_LIMITS`, `DISABLE_USAGE_LIMITS`, and
`SIGNUPFLOW_ALLOW_TEST_CLOCK` to be false. `LOCAL_EMAIL_CAPTURE_DIR` must be
unset. HSTS and CSP must remain enabled. Boolean settings accept only
`true/false`, `yes/no`, `on/off`, or `1/0`.

Provider keys do not enable a feature. `EMAIL_ENABLED`, `SMS_ENABLED`, and
`BILLING_ENABLED` default to false and disabled services perform no external
delivery or payment action. If explicitly enabled later, startup requires the
corresponding SendGrid, Twilio, or Stripe credential names. Email also requires the
SendGrid Event Webhook ECDSA public verification key; SMS requires
`TWILIO_INCOMING_SMS_URL` and `TWILIO_STATUS_CALLBACK_URL` as the exact external
HTTPS callback URLs used for Twilio signature validation. This validation is
configuration coherence, not provider acceptance or permission to enable them.
Billing additionally requires `STRIPE_WEBHOOK_SECRET`; the mounted callback returns
404 while billing is disabled and rejects unverifiable payloads when enabled. Verified
events must include tenant metadata and are recorded for replay, ordering, and
reconciliation. This local control does not approve prices, refunds, quotas, provider
sandbox results, or live activation.

The mounted SendGrid callback is `/api/v1/webhooks/sendgrid`. It returns 404 while
email is disabled and rejects missing or invalid signatures when enabled. Scheduling
messages carry `signupflow_org_id` and `signupflow_notification_id` custom arguments;
an event must match those values and the stored provider message ID. Durable provider
event receipts prevent duplicate delivery logs and retain identity mismatches for
reconciliation.

Rotating `SECRET_KEY` invalidates every existing JWT and browser session. Apply
the new key to every application process in one coordinated restart, then require
users to sign in again. Do not run old and new signing keys concurrently; staged
multi-key rotation is not implemented.

## Container Boundary

`docker-compose.yml` requires database, Redis, signing-key, and HTTPS-origin
inputs instead of supplying sample production credentials. It passes the
canonical access-token setting and defaults every provider off. Production rate limits
use shared Redis and fail protected operations closed during an outage. Tenant-scoped
solution refresh hints use Redis pub/sub, while committed notification intents use one
Celery worker plus one beat scheduler with leases, retry backoff, and dead-letter states.
Keep delivery disabled until the provider is separately authorized and accepted. In that
state the beat scheduler leaves committed intents pending without contacting the broker.
External exactly-once delivery is not guaranteed across provider acceptance and worker death;
reconcile `uncertain` rows before retrying them. Daily and weekly digest tasks remain placeholders.
The reference API service retains one Uvicorn worker as a conservative default; local
acceptance proves the event bus across independent clients and the artifact across two API replicas.
Compose does not publish PostgreSQL or Redis host ports and uses an authenticated
Redis health check. The API image has no source bind mounts and runs non-root,
read-only, capability-free, and with `no-new-privileges`.
Production logs are JSON records on stdout with request ID, environment, release
SHA, and bounded event fields. Credential-shaped assignments and PostgreSQL/Redis
URL userinfo are redacted. `/health` is dependency-free process liveness;
container health uses sanitized database readiness from `/ready`.
Size API and Celery workers only after authorized staging load and restart drills; local
cross-worker correctness does not establish production capacity.

The entrypoint never runs migrations. Compose uses one `migrate` service and API
replicas start only after it exits successfully; deployment operators must preserve
that one-shot ordering.
Local SQLite remains a development/test option and newly prepared files use
owner-only `0600` permissions; production rejects SQLite entirely.
Managed-database, TLS/proxy, scheduled/off-site backup, production restore, external
alert receipt, and rollback acceptance remain separate work under #253, #261, and #265
through #271. `make test-recovery` proves only an encrypted, isolated fictional SQLite
restore and must not be presented as production PostgreSQL/PITR or cutover evidence.

## Local Validation

Run the clean-process configuration tests without provider credentials:

```bash
poetry run pytest tests/unit/test_production_config.py -q
poetry run pytest tests/unit/test_secret_key_guard.py tests/unit/test_cors_config.py -q
make test-redis
make test-all
make test-artifact
make test-recovery
```

The tests cover each unsafe setting in a fresh process, prove failure occurs
before `init_db`, verify errors redact values, and exercise a valid synthetic
production startup with Secure/HttpOnly cookies. The opt-in artifact target uses
only an owned local Docker network and provider-free synthetic data; it does not
contact staging or deploy an environment.
