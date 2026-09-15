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
| `SECRET_KEY` | `api.security` | known sample value | Supply a unique value of at least 32 characters; known repository samples fail. |
| `DATABASE_URL` | `api.database` | local SQLite | Use a PostgreSQL URL with a host and database; known sample credentials fail. |
| `ACCESS_TOKEN_EXPIRE_HOURS` | `api.core.runtime_config` | `24` | Use a positive finite value of at least one minute. Browser session `Max-Age` uses the same value. |
| `APP_URL` | message-link generation and browser-origin fallback | localhost | Supply one HTTPS origin with no path, query, or credentials. |
| `FRONTEND_URL` | browser-origin enforcement and message links | APP_URL/localhost fallback | Supply the exact public HTTPS browser origin. |
| `API_BASE_URL` | deployment/operator contract | localhost | Supply the public HTTPS API origin. |
| `CORS_ALLOWED_ORIGINS` | CORS middleware | local origins | Supply explicit comma-separated HTTPS origins including `FRONTEND_URL`; wildcard is rejected. |
| `TRUSTED_PROXY_IPS` | rate limits and audit logging | empty | Leave empty for direct peers or list only the actual proxy IPs/CIDRs. Invalid or all-address networks fail. |
| `SECURITY_HSTS_MAX_AGE` | security-header middleware | `31536000` | Use a positive integer number of seconds. |

## Fail-Closed Controls

Production requires `TESTING`, `DEBUG`, `DEBUG_RETURN_RESET_TOKEN`,
`DISABLE_RATE_LIMITS`, `DISABLE_USAGE_LIMITS`, and
`SIGNUPFLOW_ALLOW_TEST_CLOCK` to be false. `LOCAL_EMAIL_CAPTURE_DIR` must be
unset. HSTS and CSP must remain enabled. Boolean settings accept only
`true/false`, `yes/no`, `on/off`, or `1/0`.

Provider keys do not enable a feature. `EMAIL_ENABLED`, `SMS_ENABLED`, and
`BILLING_ENABLED` default to false and disabled services perform no external
delivery or payment action. If explicitly enabled later, startup requires the
corresponding SendGrid, Twilio, or Stripe credential names. This validation is
configuration coherence, not provider acceptance or permission to enable them.

Rotating `SECRET_KEY` invalidates every existing JWT and browser session. Apply
the new key to every application process in one coordinated restart, then require
users to sign in again. Do not run old and new signing keys concurrently; staged
multi-key rotation is not implemented.

## Container Boundary

`docker-compose.yml` requires database, Redis, signing-key, and HTTPS-origin
inputs instead of supplying sample production credentials. It passes the
canonical access-token setting and defaults every provider off. The image runs
one Uvicorn worker because rate limits and SSE fan-out are process-local.
Compose binds PostgreSQL and Redis host ports to loopback by default and uses an
authenticated Redis health check; change those bind addresses only within an
explicitly secured operator environment.
Do not increase the worker count until #261 and #266 have shared-state and
cross-worker acceptance evidence.

The entrypoint still runs `alembic upgrade head` before application startup.
Local SQLite remains a development/test option and newly prepared files use
owner-only `0600` permissions; production rejects SQLite entirely.
Artifact, managed-database, TLS/proxy, backup, restore, alert, and rollback
acceptance remain separate work under #253, #261, and #265 through #271.

## Local Validation

Run the clean-process configuration tests without provider credentials:

```bash
poetry run pytest tests/unit/test_production_config.py -q
poetry run pytest tests/unit/test_secret_key_guard.py tests/unit/test_cors_config.py -q
make test-all
```

The tests cover each unsafe setting in a fresh process, prove failure occurs
before `init_db`, verify errors redact values, and exercise a valid synthetic
production startup with Secure/HttpOnly cookies. They do not contact a provider
or deploy an environment.
