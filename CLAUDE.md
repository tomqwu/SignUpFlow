# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

The cross-agent baseline lives in [`AGENTS.md`](./AGENTS.md). Read it first when rules in the two files appear to overlap; Claude-specific addenda below take precedence inside Claude Code sessions.

**Read the constitution:** `.specify/memory/constitution.md` — single source of truth for project principles.

## Agent instruction hierarchy

When rules overlap, follow the more specific and safer one. Precedence:

1. The user's request in the current task.
2. This file (`CLAUDE.md`) and `AGENTS.md`.
3. Path-scoped rules under `.github/instructions/` (Copilot) when applicable.
4. General guidance in `docs/ai-agent-coding-strategy.md`.
5. Inferred best practice.

## Project

SignUpFlow is a headless volunteer scheduling and sign-up management API + CLI (churches, sports leagues, non-profits). It uses a greedy heuristic solver with constraint-based optimization to auto-generate fair schedules.

- **Backend:** FastAPI + SQLAlchemy 2.0 + Pydantic 2.x (Python 3.11+)
- **CLI:** YAML workspace in, JSON solution out (`api.cli.main`)
- **Database:** SQLite (dev: `roster.db`), PostgreSQL (prod via Docker)
- **Auth:** JWT (HS256, 24h expiry) + bcrypt password hashing

### Provider-backed Features

Notification routes are registered under `/api/v1`. Billing and SMS code is registered but feature-gated off by default with `BILLING_ENABLED=false` and `SMS_ENABLED=false`; core scheduling must not require either paid integration. See `docs/TESTING.md` for current validation scope.

## Commands

```bash
make setup                # First-time: install deps, run migrations, seed data
make run                  # Dev server on :8000 (uvicorn --reload)
make test                 # Backend comprehensive tests
make test-all             # All Python tiers, including web + contract + Playwright
make test-mobile          # Flutter tests (requires Flutter SDK)
make test-unit            # Python unit tests only
make test-unit-fast       # Unit tests excluding slow bcrypt tests (~7s)

# Individual test commands
poetry run pytest tests/unit/test_events.py -v                    # One test file
poetry run pytest tests/unit/test_events.py::test_create_event -v # One test function

# Database
make migrate              # Run Alembic migrations
# Reset: rm roster.db && make migrate
```

## Architecture

### Active API Routers (registered in `api/main.py`)

```
/api/v1/auth           — signup, login, refresh, email check
/api/v1/organizations  — CRUD for organizations
/api/v1/people         — CRUD for people, /me profile
/api/v1/teams          — CRUD for teams + membership
/api/v1/events         — CRUD for events + assignments
/api/v1/constraints    — CRUD for scheduling constraints (DSL-based)
/api/v1/solver         — POST /solve to generate schedules
/api/v1/solutions      — list/view/stats, compare, publish/unpublish/rollback
/api/v1/availability   — time-off / blocked dates
/api/v1/conflicts      — conflict checking between person+event
/api/v1/invitations    — create/verify/accept invitation tokens
/api/v1/calendar       — ICS export of personal schedules
/api/v1/analytics      — volunteer stats, event stats
/api/v1/password-reset — request/confirm password reset
/api/v1/notifications  — list / read / unread-count, email preferences (mobile Inbox)

Bare `/api` is a 308 redirect to `/api/v1` for one release.
```

### Key Files

```
api/main.py              # App entry, router registration
api/cli/                 # YAML workspace CLI (init, solve)
api/dependencies.py      # Auth: get_current_user(), get_current_admin_user(), verify_org_member()
api/security.py          # JWT creation/verification, bcrypt hashing
api/models.py            # SQLAlchemy ORM (Organization, Person, Event, Team, Assignment, Constraint, ...)
api/database.py          # Engine, session factory, get_db() dependency
api/core/solver/         # GreedyHeuristicSolver + constraint evaluation engine
api/core/models.py       # In-memory domain models for solver (separate from ORM models)
api/core/constraints/    # Constraint DSL: eval.py (evaluator), predicates.py (built-in predicates)
api/schemas/             # Pydantic request/response models per domain
```

### Tests

```
tests/conftest.py              # Fixtures: auto-mocks auth for unit, real auth for integration
tests/unit/                    # Fast, mocked auth
tests/api/, tests/security/    # Real HTTP + JWT against isolated test DB
tests/cli/                     # Subprocess CLI: YAML in, JSON out
tests/integration/             # Real DB tests
tests/local_validation_manifest.json  # Default and explicit opt-in test inventory
tests/setup_test_data.py       # Seed data for test DB
```

## Key Patterns

**Authentication:** Backend uses `Depends(get_current_user)` or `Depends(get_current_admin_user)` for route protection.

**Multi-tenancy:** Every query MUST filter by `org_id`. Use `verify_org_member(person, org_id)` from `api/dependencies.py` to enforce org isolation.

**Organizations:** `POST /api/v1/auth/signup` atomically creates one organization and its first admin. It rejects an existing organization ID; all later accounts join through administrator-created invitations. There is no public empty-organization endpoint. Require membership for organization reads/listing and same-tenant admin access for update/delete/cancel/restore. Commit each lifecycle mutation and its audit record together.

**RBAC:** Grant exactly one permission role: `volunteer` (view own data, manage availability) or `admin` (full CRUD, solver, invitations). Store scheduling qualifications such as `usher` or `coach` in the same Person JSON array, but never interpret them as permissions. Normalize request input with `api.roles.normalize_roles`.

**Test auth mocking:** Unit tests auto-mock authentication via `conftest.py` (returns a test admin user). Integration tests use real auth. Mark tests with `@pytest.mark.no_mock_auth` to opt out of mocking.

## Testing Rules

Write tests first (TDD), implement to make them pass, then run `make test-unit` to verify no regressions. All tests must pass before committing.

Pytest markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`, `@pytest.mark.no_mock_auth`.

## PR rules

1. **Run tests after every code change.** After any edit to code or tests, run `make test-unit` (or `make test-unit-fast` during iteration). The change is not "done" until local tests pass. Run `make test-all` before pushing a PR.
2. **No CI checks.** Run formatting, lint, type checks, migration validation, all tests and local code review locally. Run `make test-all` for every PR and `make test-mobile` for mobile changes. Record the local report path, commands, results, limitations and the pushed head SHA.
3. **Merge only when local validation passes, local code review is completed, successful local test results are recorded with the pushed head SHA, and GitHub reports mergeable** (see next section).

## Local Code Review

Complete local code review for the current PR head/base before merging. Record
reviewed SHAs, findings, fixes, and any remaining limitations in the PR. Follow
[the local review checklist](docs/ai-pr-review.md). Missing review is not approval.

All validation runs locally. Do not run CI checks in GitHub Actions,
send PR patches to Ollama, or substitute another hosted review provider.

Builder agents may merge only after successful local validation and review are
recorded, GitHub reports mergeable, and required reviews and blocking
comments are resolved. Reviewer agents must not merge. Do not bypass checks.

## Common Gotchas

- Missing `org_id` filter in DB queries → cross-tenant data leaks
- Password-related tests slow → use `make test-unit-fast` to skip bcrypt tests during iteration
