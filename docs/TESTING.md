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
| API | `tests/api/` | HTTP workflows with real JWT and isolated SQLite |
| CLI | `tests/cli/` | YAML-to-solution subprocess workflows |
| Integration | `tests/integration/` | Application/database integration |
| Web | `tests/web/` | In-process cookie and HTMX workflows |
| Contract | `tests/contract/` | OpenAPI snapshot compatibility |
| Browser | `tests/e2e/` | Playwright with a disposable live application |

Use `make test-web`, `make test-contract`, or `make test-e2e` for focused runs.
Do not combine API and browser tiers in one pytest process: their event-loop
fixtures differ. `make test-all` keeps them separate and stops on failure.
It does not include Flutter tests or device-dependent mobile integration tests;
follow [mobile smoke checks](../mobile/SMOKE.md) for the latter. `make test` and
`make test-all` are the same supported complete Python entry point.

Three historical files are intentionally outside that entry point:
`tests/security/test_authentication.py` duplicates current unit/API auth coverage
and still uses shared-database/obsolete HTTPX patterns;
`tests/test_test_data_setup.py` imports the removed comprehensive suite; and
`tests/performance/test_load.py` mutates a hard-coded running service. Do not run
them against a developer or customer environment. Rehabilitate a valuable case
into an owned tier before adding it; load and PostgreSQL tests remain explicit
isolated targets.

The [playbook guide](playbooks/README.md) describes automatic discovery, selectors,
and external definitions. Church and basketball run in API and browser tiers;
browser cases use phone and desktop widths. Owned local delivery runs in both domains;
their calendar cases also refresh one stable assignment across publish, move, and cancel
in `America/Toronto`, with a unit-level DST boundary. Manual drills, external delivery, and
production database/concurrency acceptance are not implied by a green local run.

## Local Validation Only

No CI checks. Run code review, formatting, lint, type checks, migration
validation, unit tests, E2E tests, dependency scans, artifact checks and mobile
validation locally. Do not recreate hosted validation workflows or publish
synthetic success statuses. The Pages workflow only publishes the static site;
it is not a validation or merge gate.

```bash
poetry run black --check api tests
poetry run ruff check api tests
poetry run mypy --no-incremental api/utils api/core api/schemas
poetry run mypy api
make test-all
```

Use a clean environment installed from the lockfile, not another worktree's
virtualenv, when diagnosing type-check discrepancies. Record legacy full-API
typing failures separately; do not suppress errors to claim success. Require
changed modules to pass their applicable checks.

For migration/release work, set DATABASE_URL to a disposable local PostgreSQL
database, then run `poetry run alembic upgrade head` and
`poetry run alembic check`. Never target customer data. PostgreSQL business,
concurrency and upgrade-from-existing-data coverage remains tracked in
[#260](https://github.com/tomqwu/SignUpFlow/issues/260); migration success alone
does not establish it. Run Flutter analysis and tests locally for mobile work.

Follow [local code review](ai-pr-review.md) and [the roadmap](ROADMAP.md).
Local results are procedural evidence, not independently attested by GitHub.
No hosted check, including a static check, is a merge prerequisite.

## Before Merge

1. Run `make test-all` on the final source; run `make test-mobile` for mobile changes.
2. Record commands, pass/skip/failure counts, date, and the pushed head SHA in the PR.
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
