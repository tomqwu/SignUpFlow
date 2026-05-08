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

### Disabled Features

Billing (Stripe), email (SendGrid), SMS (Twilio), and notification routers are **not registered** in `api/main.py`. Their service files and models remain in the codebase but are inactive. Tests for these features are skipped via `pytestmark`.

## Commands

```bash
make setup                # First-time: install deps, run migrations, seed data
make run                  # Dev server on :8000 (uvicorn --reload)
make test                 # Backend comprehensive tests
make test-all             # Full suite: unit + api + cli + integration
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
tests/api/                     # Real HTTP + JWT against in-memory DB
tests/cli/                     # Subprocess CLI: YAML in, JSON out
tests/integration/             # Real DB tests
tests/comprehensive_test_suite.py  # Full API workflow tests
tests/setup_test_data.py       # Seed data for test DB
```

## Key Patterns

**Authentication:** Backend uses `Depends(get_current_user)` or `Depends(get_current_admin_user)` for route protection.

**Multi-tenancy:** Every query MUST filter by `org_id`. Use `verify_org_member(person, org_id)` from `api/dependencies.py` to enforce org isolation.

**RBAC:** Two roles: `volunteer` (view own data, manage availability) and `admin` (full CRUD, solver, invitations). Roles stored as JSON array on Person model.

**Test auth mocking:** Unit tests auto-mock authentication via `conftest.py` (returns a test admin user). Integration tests use real auth. Mark tests with `@pytest.mark.no_mock_auth` to opt out of mocking.

## Testing Rules

Write tests first (TDD), implement to make them pass, then run `make test-unit` to verify no regressions. All tests must pass before committing.

Pytest markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`, `@pytest.mark.no_mock_auth`.

## PR rules

1. **Run tests after every code change.** After any edit to code or tests, run `make test-unit` (or `make test-unit-fast` during iteration). The change is not "done" until local tests pass. Run `make test-all` before pushing a PR.
2. **Commit and let CI run.** After local tests pass, commit and push. Do not declare a change shippable based on local results alone — wait for CI on the branch.
3. **Merge only when CI is green and the GitHub-enforced review gate has passed** (see next section).

## GitHub-Enforced PR Review Gate

I am the builder/coding agent for this repository.

I may write code, push branches, open PRs, respond to PR feedback, resolve merge
conflicts, and merge my PR only after GitHub branch protection passes.

Do not merge before the review gate passes.

A PR may merge only when all of these are true:
1. The PR is not draft.
2. GitHub says the PR is mergeable.
3. Required CI checks are green.
4. The required `codex-pr-review-gate` check is green for the current head SHA.
5. There are no merge conflicts.
6. There is no newer blocking review feedback.

The `codex-pr-review-gate` check is the source of truth for independent AI
review approval. Do not bypass it by reading old LGTM comments directly.

Do not post `LGTM` yourself.
Do not post or edit `<!-- codex-pr-review: ... -->` markers yourself.
Do not treat an old approval as valid after pushing a new commit.

If review feedback says `Not LGTM yet`:
1. Treat it as blocking.
2. Fix the issue.
3. Run relevant local checks.
4. Push a follow-up commit.
5. Reply on the PR with what changed.
6. Wait for CI and `codex-pr-review-gate` again.

If the PR has merge conflicts:
1. Update the branch against the latest base branch.
2. Resolve conflicts carefully.
3. Preserve requested changes and current base behavior when possible.
4. Run relevant local checks.
5. Commit and push the resolution.
6. Wait for CI and `codex-pr-review-gate` again.

Before merging, re-fetch PR state:

```bash
gh pr view <PR> --json number,url,isDraft,headRefName,headRefOid,mergeStateStatus,statusCheckRollup,comments,reviews
gh pr checks <PR>
```

Merge only if GitHub reports the PR is mergeable and all required checks,
including `codex-pr-review-gate`, are passing for the current head SHA.

Use the repository's normal merge method. If unclear, prefer:

```bash
gh pr merge <PR> --squash --delete-branch
```

If GitHub blocks the merge, report the exact blocker and leave the PR unmerged.
Do not work around branch protection.

## Common Gotchas

- Missing `org_id` filter in DB queries → cross-tenant data leaks
- Password-related tests slow → use `make test-unit-fast` to skip bcrypt tests during iteration
