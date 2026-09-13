# Testing and Merge Policy

Current policy, reconciled 2026-09-13 against `Makefile`, the registered pytest
plugin, and `.github/workflows/`. This guide supersedes testing commands,
counts, timing estimates, and hosted-test proposals in older reports.

## Local Setup

```bash
poetry install
poetry run pip install "playwright==1.60.0"
poetry run playwright install chromium
```

On Linux, install browser system dependencies with
`poetry run playwright install --with-deps chromium`. Playwright is currently
outside the Poetry lockfile; reinstall it after a dependency sync that removes
it. Install Flutter separately for mobile work; never silently skip a missing SDK.

## Test Commands

```bash
make test-unit-fast     # Iteration only; excludes slow-marked tests
make test-unit          # Complete Python unit tier
make test-all           # All seven Python tiers below, in separate processes
make test-mobile        # Flutter unit/widget tests; requires Flutter SDK
```

Set `FLUTTER=/absolute/path/to/flutter` when the SDK is not on PATH.
Disable external delivery for local acceptance runs with
`EMAIL_ENABLED=false SMS_ENABLED=false make test-all`.

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
follow [mobile smoke checks](../mobile/SMOKE.md) for the latter. Legacy
`make test` runs `tests/comprehensive_test_suite.py`, not the seven-tier suite.

The [playbook guide](playbooks/README.md) describes automatic discovery, selectors,
and external definitions. Church and basketball run in API and browser tiers;
browser cases use phone and desktop widths. Manual drills, live delivery, and
production database/concurrency acceptance are not implied by a green local run.

## Hosted Checks

GitHub Actions does not execute test suites. It runs:

- `Lint and type-check`: Black, Ruff, blocking scoped mypy, advisory whole-API
  mypy, and PostgreSQL migration smoke validation in `ci.yml`.
- `Flutter analyze`: static analysis for mobile-path changes in `mobile-ci.yml`.
- `codex-pr-review-gate`: independent Ollama review for PRs in `codex-review.yml`.

The README CI badge reports hosted workflow status, not passing test counts.
Local results are procedural evidence, not independently attested by GitHub.
The reviewer accepts local-only execution but still flags incorrect code,
security defects, missing/weakened coverage, broken commands, and deceptive claims.

## Before Merge

1. Run `make test-all` on the final source; run `make test-mobile` for mobile changes.
2. Record commands, pass/skip/failure counts, date, and the pushed head SHA in the PR.
   If tests ran immediately before committing, confirm the committed tree is identical.
3. Record initial failures and reruns. Do not hide flakes or treat skipped tests as passed.
4. Require passing hosted checks, current-head/base AI review, no unresolved blocking
   review items, and GitHub mergeability. Do not bypass failed checks.
5. Merge using the repository's normal method, verify the merge, and update local main.

Counts and durations are run-specific. Obtain current evidence by executing the
commands; use `poetry run pytest tests/api/test_domain_playbooks.py --collect-only -q`
to inspect collection without claiming execution. Historical results in
[playbook validation](playbooks/validation.md) remain dated snapshots, not live status.
