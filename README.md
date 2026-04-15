<div align="center">

# SignUpFlow

### Volunteer Scheduling Made Simple

*AI-powered sign-up management for churches, sports leagues, and non-profits*

[![Tests](https://img.shields.io/badge/tests-390%20passing-brightgreen?style=for-the-badge)](#-testing)
[![Python](https://img.shields.io/badge/python-3.11+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](LICENSE)

</div>

---

## Features

- **Greedy Heuristic Solver** — auto-generate fair schedules with role-based constraints
- **CLI + API** — schedule from YAML files or through REST endpoints
- **Multi-tenant** — full org isolation with JWT auth and RBAC (admin/volunteer)
- **Invitation system** — token-based volunteer onboarding
- **Availability tracking** — volunteers block dates, time-off with reasons
- **Calendar export** — ICS files and webcal subscriptions
- **i18n** — 6 languages (EN, ES, PT, ZH-CN, ZH-TW, FR)
- **Frontend** — Vanilla JS SPA with admin + volunteer views

---

## Quick Start

### CLI (no server needed)

```bash
# Install
git clone https://github.com/tomqwu/signupflow.git
cd signupflow && make setup

# Create a workspace with sample data
poetry run python -m api.cli.main init my-church

# Edit YAML files: org.yaml, people.yaml, events.yaml
# Then solve:
poetry run python -m api.cli.main solve my-church
```

Output:
```
Workspace: my-church
People:    5
Events:    2
Range:     2026-04-22 → 2026-04-29
Mode:      relaxed

Solved in 0ms
Health score: 100.0/100
Assignments:  2
Fairness:     stdev=0.43

  sunday-worship-1: Sarah Chen, David Kim, James Brown
  sunday-worship-2: Emily Davis, Sarah Chen, David Kim, James Brown

Solution saved to my-church/output/solution.json
```

CLI options: `--json-output`, `-o <dir>`, `--from-date`, `--to-date`, `--mode strict|relaxed`

### API Server

```bash
make setup    # First-time: install deps, run migrations, seed data
make run      # Dev server on http://localhost:8000 (uvicorn --reload)
```

Default login: `jane@test.com` / `password`

Interactive API docs at `http://localhost:8000/docs`

---

## Architecture

```
signupflow init / solve        →  api/cli/main.py      (YAML workspace)
POST /api/solver/solve         →  api/routers/solver.py (HTTP + DB)
                                      │
                                      ▼
                               api/core/solver/heuristics.py
                               (GreedyHeuristicSolver)
                                      │
                                      ▼
                               SolveContext → SolutionBundle
                               (people, events, constraints, holidays)
```

**Backend:** FastAPI + SQLAlchemy 2.0 + Pydantic 2.x (Python 3.11+)
**Frontend:** Vanilla JS SPA + i18next
**Database:** SQLite (dev) / PostgreSQL (prod)
**Auth:** JWT (HS256) + bcrypt

### Active API Endpoints

```
/api/auth           — signup, login, email check
/api/organizations  — CRUD for organizations
/api/people         — CRUD for people, /me profile
/api/teams          — CRUD for teams + membership
/api/events         — CRUD for events + manual assignments
/api/constraints    — CRUD for scheduling constraints
/api/solver         — POST /solve to generate schedules
/api/solutions      — list/view generated solutions
/api/availability   — time-off / blocked dates
/api/conflicts      — conflict checking
/api/invitations    — create/verify/accept invitation tokens
/api/calendar       — ICS export
/api/analytics      — volunteer + event stats
/api/onboarding     — wizard progress
/api/password-reset — request/confirm password reset
```

### Disabled Features

Billing (Stripe), email (SendGrid), SMS (Twilio), and notification routers are not active. Their code remains but is not registered in `api/main.py`. The `/api/config/safe-flags` endpoint returns `false` for all.

---

## Testing

### Test Pyramid: 390 tests

```bash
make test-unit            # Unit tests (338 tests, ~4min)
poetry run pytest tests/api/ -v   # API integration (36 tests, ~70s)
poetry run pytest tests/cli/ -v   # CLI E2E (16 tests, ~11s)
```

| Layer | Suite | Tests | What it tests | Speed |
|-------|-------|-------|---------------|-------|
| **Unit** | `tests/unit/` | 338 | Individual functions, mocked auth, endpoint coverage | ~4min |
| **API** | `tests/api/` | 36 | Full HTTP workflows with real JWT + in-memory DB | ~70s |
| **CLI E2E** | `tests/cli/` | 16 | Subprocess CLI: YAML in, JSON out, real solver | ~11s |

### Scenario Tests

Both API and CLI suites include real-world scenario tests:

**Church ministry** — Pastor manages worship team, Sunday school teachers, youth group. Multi-role members (Sarah plays keyboard AND teaches). 4 weeks of scheduling, fairness distribution, manual adjustments.

**Sports club** — Coach manages cricket + basketball rosters. Dual-sport players (Priya bowls AND plays point guard). Tournament week with 5 events, injury time-off, roster adjustments.

### Commands

```bash
make setup                # First-time setup
make run                  # Dev server on :8000
make test                 # Frontend + backend tests
make test-unit            # Python unit tests only
make test-unit-fast       # Skip slow bcrypt tests (~7s)
make test-e2e             # Playwright browser tests
make test-e2e-file FILE=tests/e2e/test_auth_flows.py
make migrate              # Run Alembic migrations
```

Single test: `poetry run pytest tests/unit/test_events.py::test_create_event -v`

---

## CLI Reference

```bash
# Create sample workspace
poetry run python -m api.cli.main init <workspace>

# Solve a workspace
poetry run python -m api.cli.main solve <workspace> [options]

Options:
  --json-output          Output JSON to stdout (for piping)
  -o, --output <dir>     Save solution to custom directory
  --from-date YYYY-MM-DD Filter events by start date
  --to-date YYYY-MM-DD   Filter events by end date
  --mode strict|relaxed  Solver mode (default: relaxed)
```

### Workspace Format

```
my-workspace/
  org.yaml        # Organization config (org_id, region, defaults)
  people.yaml     # Volunteers: id, name, roles[]
  events.yaml     # Events: id, type, start, end, required_roles[]
  output/         # Generated by solve command
    solution.json # Assignments, metrics, violations
```

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Write tests first (TDD), implement, verify with `make test-unit`
4. Commit and push
5. Open a Pull Request

---

## License

MIT License — see [LICENSE](LICENSE) for details.
