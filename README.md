<div align="center">

# SignUpFlow

### Volunteer Scheduling Made Simple

*AI-powered sign-up management for churches, sports leagues, and non-profits*

[![Tests](https://img.shields.io/badge/tests-413%20passing-brightgreen?style=for-the-badge)](#testing)
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

---

## Quick Start

```bash
git clone https://github.com/tomqwu/signupflow.git
cd signupflow && make setup
```

---

## CLI Example: Schedule a Church in 3 Commands

### 1. Create a workspace

```bash
$ poetry run python -m api.cli.main init my-church

Created workspace at my-church/
  org.yaml      — organization config
  people.yaml   — volunteers and their roles
  events.yaml   — events to schedule
```

This generates three YAML files. Here's what `people.yaml` looks like:

```yaml
people:
- id: sarah
  name: Sarah Chen
  roles: [musician, teacher]     # Serves in worship AND Sunday school
- id: david
  name: David Kim
  roles: [musician, sound_tech]
- id: maria
  name: Maria Lopez
  roles: [teacher, volunteer]
- id: james
  name: James Brown
  roles: [usher, volunteer]
- id: emily
  name: Emily Davis
  roles: [musician, youth_leader]
```

And `events.yaml`:

```yaml
events:
- id: sunday-worship-1
  type: Sunday Worship
  start: '2026-04-23T09:00:00'
  end: '2026-04-23T11:00:00'
  required_roles:
  - {role: musician, count: 2}
  - {role: sound_tech, count: 1}
  - {role: usher, count: 1}
- id: sunday-worship-2
  type: Sunday Worship
  start: '2026-04-30T09:00:00'
  end: '2026-04-30T11:00:00'
  required_roles:
  - {role: musician, count: 2}
  - {role: sound_tech, count: 1}
  - {role: usher, count: 1}
```

### 2. Run the solver

```bash
$ poetry run python -m api.cli.main solve my-church

Workspace: my-church
People:    5
Events:    2
Range:     2026-04-23 → 2026-04-30
Mode:      relaxed

Solved in 0ms
Health score: 100.0/100
Assignments:  2
Violations:   0 hard, 0 soft
Fairness:     stdev=0.43

  sunday-worship-1: Sarah Chen, David Kim, James Brown
  sunday-worship-2: Emily Davis, Sarah Chen, David Kim, James Brown

Solution saved to my-church/output/solution.json
```

### 3. Get JSON output (for scripting)

```bash
$ poetry run python -m api.cli.main solve my-church --json-output
```

```json
{
  "solve_ms": 0.12,
  "health_score": 100.0,
  "hard_violations": 0,
  "assignment_count": 2,
  "fairness_stdev": 0.43,
  "assignments": [
    {"event_id": "sunday-worship-1", "assignees": ["sarah", "david", "james"]},
    {"event_id": "sunday-worship-2", "assignees": ["emily", "sarah", "david", "james"]}
  ],
  "violations": []
}
```

### CLI Reference

```bash
poetry run python -m api.cli.main init <workspace>           # Create sample workspace
poetry run python -m api.cli.main solve <workspace>           # Solve and print results
poetry run python -m api.cli.main solve <workspace> --json-output     # JSON to stdout
poetry run python -m api.cli.main solve <workspace> -o results/       # Custom output dir
poetry run python -m api.cli.main solve <workspace> --from-date 2026-05-01 --to-date 2026-05-31
poetry run python -m api.cli.main solve <workspace> --mode strict
```

---

## API Example: Full Volunteer Onboarding Workflow

Start the server: `make run` (runs on http://localhost:8000)

### 1. Create an organization

```bash
$ curl -X POST http://localhost:8000/api/organizations/ \
  -H "Content-Type: application/json" \
  -d '{"id": "grace-church", "name": "Grace Community Church", "region": "US"}'
```

```json
{
  "id": "grace-church",
  "name": "Grace Community Church",
  "region": "US",
  "config": {}
}
```

### 2. Sign up (first user becomes admin automatically)

```bash
$ curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "org_id": "grace-church",
    "name": "Pastor Mike",
    "email": "mike@grace.org",
    "password": "Pass123!"
  }'
```

```json
{
  "person_id": "person_mike_d2d61d7f",
  "org_id": "grace-church",
  "name": "Pastor Mike",
  "roles": ["admin"],
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

### 3. Create an event with role requirements

```bash
$ curl -X POST http://localhost:8000/api/events/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{
    "id": "sunday-worship",
    "org_id": "grace-church",
    "type": "Sunday Worship",
    "start_time": "2026-04-30T09:00:00",
    "end_time": "2026-04-30T11:00:00",
    "extra_data": {
      "role_counts": {"musician": 2, "sound_tech": 1, "usher": 1}
    }
  }'
```

```json
{
  "id": "sunday-worship",
  "org_id": "grace-church",
  "type": "Sunday Worship",
  "start_time": "2026-04-30T09:00:00",
  "end_time": "2026-04-30T11:00:00",
  "extra_data": {"role_counts": {"musician": 2, "sound_tech": 1, "usher": 1}}
}
```

### 4. Invite a volunteer

```bash
$ curl -X POST "http://localhost:8000/api/invitations?org_id=grace-church" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{
    "email": "sarah@grace.org",
    "name": "Sarah Chen",
    "roles": ["musician", "teacher"]
  }'
```

```json
{
  "id": "inv_1776368711_0a9cc225",
  "email": "sarah@grace.org",
  "status": "pending",
  "token": "vvNr67Ft_yVLJTGLxAVb..."
}
```

### 5. Volunteer accepts invitation

```bash
$ curl -X POST http://localhost:8000/api/invitations/{token}/accept \
  -H "Content-Type: application/json" \
  -d '{"password": "Sarah123!", "timezone": "US/Eastern"}'
```

```json
{
  "person_id": "person_sarah_540dc7d0",
  "name": "Sarah Chen",
  "roles": ["musician", "teacher"],
  "org_id": "grace-church"
}
```

### 6. Run the solver

```bash
$ curl -X POST http://localhost:8000/api/solver/solve \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{
    "org_id": "grace-church",
    "from_date": "2026-04-25",
    "to_date": "2026-05-10",
    "mode": "relaxed",
    "change_min": false
  }'
```

```json
{
  "solution_id": 1,
  "assignment_count": 1,
  "metrics": {
    "health_score": 100.0,
    "hard_violations": 0,
    "solve_ms": 0.1,
    "fairness": {"stdev": 0.0, "per_person_counts": {"person_sarah_540dc7d0": 1}}
  },
  "violations": []
}
```

Interactive API docs: http://localhost:8000/docs

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
**CLI:** YAML workspace in, JSON solution out (`api.cli.main`)
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
/api/password-reset — request/confirm password reset
```

### Disabled Features

Billing (Stripe), email (SendGrid), SMS (Twilio), and notification routers are not active. Their code remains but is not registered in `api/main.py`.

---

## Testing

### Test Pyramid: 413 tests

```bash
make test-unit                        # Unit tests (338 tests, ~4min)
poetry run pytest tests/api/ -v       # API integration (59 tests, ~90s)
poetry run pytest tests/cli/ -v       # CLI E2E (16 tests, ~11s)
```

| Layer | Suite | Tests | What it tests | Speed |
|-------|-------|-------|---------------|-------|
| **Unit** | `tests/unit/` | 338 | Individual functions, mocked auth, endpoint coverage | ~4min |
| **API** | `tests/api/` | 59 | Full HTTP workflows with real JWT + in-memory DB | ~90s |
| **CLI E2E** | `tests/cli/` | 16 | Subprocess CLI: YAML in, JSON out, real solver | ~11s |

### API Test Coverage

| Area | Tests | What's covered |
|------|-------|----------------|
| Event CRUD | 12 | Create, read, update, delete, list, RBAC enforcement |
| Conflict detection | 6 | Already assigned, time-off overlap, double-booking, 404s |
| Availability | 4 | Add/list/delete time-off periods |
| Profile + Teams | 2 | Update own profile, add/remove team members |
| Scheduling workflow | 4 | Full solver lifecycle, manual assign/unassign |
| Church scenario | 8 | Ministry teams, multi-role members, invitation flow |
| Sports scenario | 8 | Dual-sport players, tournament, injury time-off |
| Org lifecycle | 9 | First-user admin, RBAC, duplicate email |
| Multi-tenant | 7 | Cross-org isolation for people/teams/events/solver |

### Scenario Tests

Both API and CLI suites include real-world scenario tests:

**Church ministry** — Pastor manages worship team, Sunday school teachers, youth group. Multi-role members (Sarah plays keyboard AND teaches). 4 weeks of scheduling, fairness distribution, manual adjustments, invitation workflow.

**Sports club** — Coach manages cricket + basketball rosters. Dual-sport players (Priya bowls AND plays point guard). Regular week, tournament week with 5 events, injury time-off, date range filtering.

### Commands

```bash
make setup                # First-time setup
make run                  # Dev server on :8000
make test                 # Backend comprehensive tests
make test-unit            # Python unit tests only
make test-unit-fast       # Skip slow bcrypt tests (~7s)
make test-all             # Full suite: unit + api + cli + integration
make migrate              # Run Alembic migrations
```

Single test: `poetry run pytest tests/unit/test_events.py::test_create_event -v`

---

## Workspace Format (CLI)

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
