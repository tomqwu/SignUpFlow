# Testing and Merge Policy

Current policy, reconciled 2026-09-14 against `Makefile`, the registered pytest
plugin, and `.github/workflows/`. This guide supersedes testing commands,
counts, timing estimates, and hosted-test proposals in older reports.

## Local Setup

```bash
poetry install
poetry run playwright install chromium
```

On Linux, install browser system dependencies with
`poetry run playwright install --with-deps chromium`. Playwright is a locked
development dependency. Install Flutter separately for mobile work; never
silently skip a missing SDK.

## Test Commands

```bash
make test-unit-fast     # Iteration only; excludes slow-marked tests
make test-unit          # Complete Python unit tier
make test               # Alias for the complete seven-tier local suite
make test-all           # All seven Python tiers below, in separate processes
make test-postgres      # Opt-in PostgreSQL migration/business/race acceptance
make test-artifact      # Opt-in production image and private-stack acceptance
make test-security      # Opt-in exact-source/image scan and CycloneDX evidence
make test-performance   # Opt-in, owned loopback target only
make test-mobile        # Flutter unit/widget tests; requires Flutter SDK
```

Set `FLUTTER=/absolute/path/to/flutter` when the SDK is not on PATH.
The test harness strips provider credentials, disables external email/SMS/billing,
ignores the developer `.env`, and gives each invocation a disposable database. BO-09
uses a dedicated live server and owned temporary `.eml` sink; no provider is enabled.
Keep the
flags explicit for focused manual runs:
`EMAIL_ENABLED=false SMS_ENABLED=false BILLING_ENABLED=false make test-all`.
Default Python tests also reject non-loopback socket connections before transport.

| Tier | Location | Purpose |
| --- | --- | --- |
| Unit | `tests/unit/` | Fast regressions, mocked auth, policy/runner checks |
| API | `tests/api/`, `tests/security/` | HTTP and authentication workflows with real JWT and isolated SQLite |
| CLI | `tests/cli/` | YAML-to-solution subprocess workflows |
| Integration | `tests/integration/` | Application/database integration |
| Web | `tests/web/` | In-process cookie and HTMX workflows |
| Contract | `tests/contract/` | OpenAPI snapshot compatibility |
| Browser | `tests/e2e/` | Playwright with a disposable live application |

[`tests/local_validation_manifest.json`](../tests/local_validation_manifest.json) is the
executable inventory for these default tiers and the opt-in performance, PostgreSQL,
mobile, provider, and artifact scopes. The validator rejects a new runnable Python test
that is not classified, overlapping ownership, missing security coverage, missing Church
or Basketball playbook coverage, and empty default-tier collection. Each `make test-all`
invocation writes `report.json`, per-tier JUnit XML, and complete tier logs to a unique
directory under `test-artifacts/local-validation/`. The report records tool versions,
the source SHA, whether tracked files were clean, counts, failures, skips, and every
explicitly unrun scope.

Use `make test-web`, `make test-contract`, or `make test-e2e` for focused runs.
Do not combine API and browser tiers in one pytest process: their event-loop
fixtures differ. `make test-all` keeps them separate and stops on failure.
It does not include Flutter tests or device-dependent mobile integration tests;
follow [mobile smoke checks](../mobile/SMOKE.md) for the latter. `make test` and
`make test-all` are the same supported complete Python entry point.

The obsolete `tests/test_test_data_setup.py` file was retired because it imported the
removed comprehensive suite and included assertions that could not fail. The maintained
`tests/performance/test_load.py` suite is opt-in: set
`SIGNUPFLOW_PERFORMANCE_BASE_URL` to the `/api/v1` URL of an explicitly owned loopback
test server before running `make test-performance`. Missing, malformed, or non-loopback
targets fail before the first HTTP request. PostgreSQL remains a separate isolated target.

`make test-artifact` requires a clean tracked Git revision and Docker. It builds a
fresh SHA-labeled image from the lockfile and source, scans its runtime contents,
and retains that image as the local artifact. The runner creates one labeled private
Docker network with disposable PostgreSQL and authenticated Redis containers. It runs
Alembic once as a separate job, proves an API replica cannot start or mutate an
unmigrated database, starts two non-root read-only API replicas without bind mounts,
and drives health, login/static, Basketball schedule/publish/export, and SIGTERM checks.
Only the application ports are published, on random loopback ports. The runner removes
only containers and the network carrying its exact ownership label and writes build,
migration, failure, shutdown, image identity, and result evidence under
`test-artifacts/artifact-validation/`. It disables external providers. A pass is local
artifact evidence, not staging, TLS/proxy, managed-service, backup/restore, or release
authorization.

Run `make test-security` only after `make test-artifact` passes for the same clean
revision. It requires the immutable Trivy image documented in
[SECURITY_VALIDATION.md](SECURITY_VALIDATION.md), fetches a fresh advisory database into
an owned temporary cache, scans a committed source archive and the exact retained image,
and writes sanitized findings plus source/image CycloneDX documents under
`test-artifacts/security-validation/`. It persists no raw secret match, mounts no Docker
socket, and fails on missing tools/databases, an expired exception, stale artifact
identity, or an unaccepted blocking finding. This is local artifact evidence, not hosted
attestation or a deployed-environment scan.

Monitoring regressions run without an external reporting sink:

```bash
poetry run pytest tests/api/test_readiness.py tests/api/test_middleware.py \
  tests/unit/test_logging_config.py tests/unit/test_observability.py \
  tests/unit/test_operational_alerts.py -q
```

They prove sanitized liveness/readiness and request errors, structured production
logging, optional reporter initialization through an injected SDK, and fake-sink
trigger/recovery state. They do not prove Sentry transport or operator receipt.

`make test-postgres` creates one uniquely named PostgreSQL 16 Docker container with
loopback-only networking, an ownership label, ephemeral tmpfs storage, and no host
mounts or Docker volumes. It builds both databases through Alembic, runs migration,
upgrade-from-existing-data, authentication, membership, claim, and publication races,
then removes only the verified owned container. Two invocations can run concurrently.
Missing Docker or any ownership/cleanup mismatch fails explicitly. Each invocation
writes JUnit XML and a SHA-bound report with PostgreSQL version and counts under
`test-artifacts/postgres-validation/`. It never reads provider credentials or targets a
caller-supplied database.

The [playbook guide](playbooks/README.md) describes automatic discovery, selectors,
and external definitions. Church and basketball run in API and browser tiers;
browser cases use phone and desktop widths. Owned local delivery runs in both domains;
their calendar cases also refresh one stable assignment across publish, move, and cancel
in `America/Toronto`, with a unit-level DST boundary. The same local-mail journey exercises
administrator and volunteer password change/recovery, logout/login, stale-session
revocation, old credentials, replay, and captured recovery screenshots. Manual drills,
external delivery, and production infrastructure acceptance are not implied by a green
local run. Run the separate PostgreSQL target for database-specific acceptance.

BO-12 keeps both bundled organizations alive in one disposable browser server. Each
administrator sees only its own directory, and every declared Church and Basketball
scheduling qualification signs in as a volunteer, stays on the member surface, and is
denied administrative, peer-mutation, foreign-person, and publication operations. API
and web regressions also require every access/session token to carry the account tenant
and reject missing, mismatched, or inactive membership claims.

The [web journey matrix](web-journey-matrix.json) is the maintained inventory for all
server-rendered routes and templates. `tests/unit/test_web_journey_matrix.py` compares it
with the live router and template tree and resolves every named test function. Each case
must retain happy-path, error, and permission evidence or an explicit accepted limitation.
`tests/e2e/test_web_recovery.py` verifies the shared browser contract: `4xx` HTMX error
fragments render, safe form values survive failure, network retry succeeds, rapid repeated
submission sends one request, expired sessions navigate to login, long labels remain
separate and keyboard reachable at phone width and zoom, and an SSE reconnect refetches
authoritative solution state. These are local Chromium results; they do not establish
cross-browser, assistive-technology, or production-network acceptance.

`tests/web/test_request_integrity.py` inventories every unsafe `/auth/`, `/a/`, and `/v/`
route and verifies signed double-submit CSRF, exact-origin rejection, no-write failures,
browser authentication rate-limit wiring, and trusted-proxy boundaries.
`tests/e2e/test_request_integrity.py` proves that normal forms receive a token, a foreign
origin cannot change a member profile, and a same-origin HTMX save succeeds in Chromium.
The limiter remains process-local; shared quotas, Redis outage behavior, and multi-worker
acceptance remain deferred under #261.

## Local Validation Only

No CI checks. Run code review, formatting, lint, type checks, migration
validation, unit tests, E2E tests, dependency scans, artifact checks and mobile
validation locally. Do not recreate hosted validation workflows or publish
synthetic success statuses. The Pages workflow only publishes the static site;
it is not a validation or merge gate.

```bash
poetry run black --check api web tests scripts/run_local_validation.py scripts/validate_production_artifact.py scripts/run_security_validation.py
poetry run ruff check api web tests scripts/run_local_validation.py scripts/validate_production_artifact.py scripts/run_security_validation.py
poetry run mypy --no-incremental api/utils api/core api/schemas
poetry run mypy api
make test-all
make test-recovery
make test-security
```

Use a clean environment installed from the lockfile, not another worktree's
virtualenv, when diagnosing type-check discrepancies. Record legacy full-API
typing failures separately; do not suppress errors to claim success. Require
changed modules to pass their applicable checks.

For database or migration work, run `make test-postgres`; do not supply a database URL
or reuse a developer database. The owned runner proves a fresh migration, upgrade from
representative existing data, Alembic drift check, business requests, and synchronized
write races. This is local application acceptance, not deployment, managed-service,
or production-data evidence.

For SQLite backup/restore work, run `make test-recovery`. The owned runner creates a
migrated fictional WAL database, encrypts and restores it under a marker-bound workspace,
measures the local operation, and runs recovery unit plus Church/Basketball restored-app
acceptance. Its report, JUnit, and log live under `test-artifacts/recovery-drill/`. It does
not test scheduled PostgreSQL backups, off-site storage, production keys, retention,
cutover, provider replay, or approved RPO/RTO. Run Flutter analysis and tests locally for
mobile work.

Follow [local code review](ai-pr-review.md) and [the roadmap](ROADMAP.md).
Local results are procedural evidence, not independently attested by GitHub.
No hosted check, including a static check, is a merge prerequisite.

## Before Merge

1. Run `make test-all` on the final source; run `make test-postgres` for database or
   migration changes, `make test-artifact` and then `make test-security` for release-image changes,
   `make test-recovery` for backup/restore changes, and `make test-mobile` for mobile
   changes.
2. Record the report path, commands, pass/skip/failure counts, date, and pushed head SHA in the PR.
   If tests ran immediately before committing, confirm the committed tree is identical.
3. Record initial failures and reruns. Do not hide flakes or treat skipped tests as passed.
4. Require recorded successful local validation and current-head/base local code
   review, no unresolved blocking review items, and GitHub mergeability.
   Do not bypass protection or invent CI checks to satisfy stale settings.
5. Merge using the repository's normal method, verify the merge, and update local main.

Counts and durations are run-specific. Obtain current evidence by executing the
commands; use `poetry run pytest tests/api/test_domain_playbooks.py --collect-only -q`
to inspect collection without claiming execution. Historical results in
[playbook validation](playbooks/validation.md) remain dated snapshots, not live status.
