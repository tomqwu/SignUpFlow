# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Read the constitution:** `.specify/memory/constitution.md` — single source of truth for project principles.

## Project

SignUpFlow is an AI-powered volunteer scheduling and sign-up management SaaS (churches, sports leagues, non-profits). It uses OR-Tools constraint-based optimization to auto-generate fair schedules.

- **Backend:** FastAPI + SQLAlchemy 2.0 + Pydantic 2.x (Python 3.11+)
- **Frontend:** Vanilla JS SPA (no framework) + i18next (6 languages)
- **Database:** SQLite (dev: `roster.db`), PostgreSQL (prod via Docker)
- **Auth:** JWT (HS256, 24h expiry) + bcrypt password hashing
- **Billing:** Stripe integration
- **Messaging:** SendGrid (email), Twilio (SMS) — both disabled by default

## Commands

```bash
make setup                # First-time: install deps, run migrations, seed data
make run                  # Dev server on :8000 (uvicorn --reload)
make test                 # Frontend (Jest) + backend comprehensive tests
make test-all             # Full suite: frontend + backend + integration + E2E (~50s)
make test-unit            # Python unit tests only
make test-unit-fast       # Unit tests excluding slow bcrypt tests (~7s)
make test-e2e             # Playwright browser tests (auto-starts server)
make test-e2e-file FILE=tests/e2e/test_auth_flows.py  # Single E2E file

# Individual test commands
poetry run pytest tests/unit/test_events.py -v                    # One test file
poetry run pytest tests/unit/test_events.py::test_create_event -v # One test function
npm test                  # Frontend Jest tests
npm run test:watch        # Jest watch mode

# Database
make migrate              # Run Alembic migrations
# Reset: rm roster.db && make migrate

# Docker (optional, for PostgreSQL + Redis)
make up                   # Start containers
make down                 # Stop containers
```

## Architecture

```
Browser (SPA)
  │  fetch() + JWT Bearer token
  ▼
FastAPI (:8000)
  ├── api/main.py              # App entry, router registration, SPA fallback
  ├── api/routers/             # 21 route modules (auth, people, events, solver, billing, ...)
  ├── api/dependencies.py      # Auth middleware: get_current_user(), get_current_admin_user(), get_db()
  ├── api/security.py          # JWT creation/verification, bcrypt hashing
  ├── api/services/            # Business logic (billing, email, SMS, notifications, solver)
  ├── api/schemas/             # Pydantic request/response models
  ├── api/models.py            # SQLAlchemy ORM (Organization, Person, Event, Team, Role, Invitation, ...)
  └── api/database.py          # Engine, session factory, get_db() dependency

frontend/
  ├── index.html               # SPA shell (102KB, contains embedded templates)
  ├── js/router.js             # Client-side routing (22 routes)
  ├── js/app.js                # Admin console initialization
  ├── js/app-user.js           # Volunteer UI (10k+ LOC)
  ├── js/app-admin.js          # Admin UI
  ├── js/auth.js               # authFetch() — auto-attaches JWT header
  ├── js/i18n.js               # i18next setup, language switching
  └── tests/                   # Jest unit tests

locales/{en,es,pt,zh-CN,zh-TW,fr}/  # i18n JSON files (common, auth, schedule, admin, messages)

tests/
  ├── conftest.py              # Fixtures: auto-mocks auth for unit tests, real auth for integration/e2e
  ├── unit/                    # ~193 tests, fast, mocked auth
  ├── integration/             # Real DB tests
  ├── e2e/                     # Playwright browser automation
  ├── comprehensive_test_suite.py  # Full API + GUI workflow tests
  └── setup_test_data.py       # Seed data for test DB
```

## Key Patterns

**Authentication:** All protected frontend API calls MUST use `authFetch()` from `auth.js`, never raw `fetch()`. Backend uses `Depends(get_current_user)` or `Depends(get_current_admin_user)` for route protection.

**Multi-tenancy:** Every query MUST filter by `org_id`. Use `verify_org_member(person, org_id)` from `api/dependencies.py` to enforce org isolation.

**RBAC:** Two roles: `volunteer` (view own data, manage availability) and `admin` (full CRUD, solver, invitations). Roles stored as JSON array on Person model.

**Frontend i18n:** Use `data-i18n="namespace.key"` attributes in HTML. In JS, use `i18n.t('namespace.key')`. Always add translations to ALL 6 language files.

**Test auth mocking:** Unit tests auto-mock authentication via `conftest.py` (returns a test admin user). Integration/E2E tests use real auth. Mark tests with `@pytest.mark.no_mock_auth` to opt out of mocking.

**Feature flags:** `EMAIL_ENABLED`, `SMS_ENABLED`, `BILLING_ENABLED` control external service integration. All default to false/disabled in test environments. Check flags via `GET /api/config/safe-flags`.

**E2E test server:** `make test-e2e` automatically starts a test server with `DISABLE_RATE_LIMITS=true TESTING=true EMAIL_ENABLED=false SMS_ENABLED=false` via `scripts/run_with_server.sh`.

## Testing Rules

Every user-visible feature needs an E2E test that simulates the actual user journey (clicks, form fills, visual verification). Write tests first (TDD), implement to make them pass, then run `make test-all` to verify no regressions. All tests must pass before committing.

Pytest markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.e2e`, `@pytest.mark.gui`, `@pytest.mark.slow`, `@pytest.mark.no_mock_auth`.

## Common Gotchas

- Using `fetch()` instead of `authFetch()` → 401/403 errors
- Missing `org_id` filter in DB queries → cross-tenant data leaks
- Roles showing as `[object Object]` → roles is an array, needs `.map()/.join()` formatting
- Hardcoded English text → must use `data-i18n` or `i18n.t()` for all UI text
- E2E tests failing with rate limit errors → ensure `DISABLE_RATE_LIMITS=true` in test env
- Password-related tests slow → use `make test-unit-fast` to skip bcrypt tests during iteration
