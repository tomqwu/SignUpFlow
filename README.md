<div align="center">

# SignUpFlow

### Volunteer Scheduling Made Simple

*AI-powered sign-up management for churches, sports leagues, and non-profits*

[![Python](https://img.shields.io/badge/python-3.11+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](LICENSE)

</div>

---

## Features

- **Greedy Heuristic Solver** — auto-generate fair schedules with role-based constraints
- **Responsive web app** — full admin + volunteer workflow in the browser, served by the same FastAPI process ([walkthrough below](#web-app--end-to-end-walkthrough)) — the primary surface
- **Flutter mobile app** (`mobile/`) — volunteer + admin app, local analysis and tests; see `mobile/README.md` for status
- **CLI + API** — schedule from YAML files or through REST endpoints
- **Multi-tenant** — full org isolation with JWT auth and RBAC (admin/volunteer)
- **Invitation system** — token-based volunteer onboarding
- **Truthful responses** — unanswered, accepted, declined, and replacement-needed work stay distinct from roster allocation
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

### 1. Create an organization and its first admin atomically

```bash
$ curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "org_id": "grace-church",
    "org_name": "Grace Community Church",
    "region": "US",
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

Existing organizations reject public signup. Add every later member through an
administrator-created invitation.

### 2. Create an event with role requirements

```bash
$ curl -X POST http://localhost:8000/api/v1/events/ \
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

### 3. Invite a volunteer

```bash
$ curl -X POST "http://localhost:8000/api/v1/invitations?org_id=grace-church" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{
    "email": "sarah@grace.org",
    "name": "Sarah Chen",
    "roles": ["volunteer", "musician", "teacher"]
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

### 4. Volunteer accepts invitation

```bash
$ curl -X POST http://localhost:8000/api/v1/invitations/{token}/accept \
  -H "Content-Type: application/json" \
  -d '{"password": "Sarah123!", "timezone": "US/Eastern"}'
```

```json
{
  "person_id": "person_sarah_540dc7d0",
  "name": "Sarah Chen",
  "roles": ["volunteer", "musician", "teacher"],
  "org_id": "grace-church"
}
```

### 5. Run the solver

```bash
$ curl -X POST http://localhost:8000/api/v1/solver/solve \
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

## Web App - Church and Basketball Workflows

SignUpFlow ships a responsive web app (HTMX + Alpine.js + Jinja2) served by the
**same FastAPI process** - same origin, no separate build or deploy. These are
real Playwright captures from the fixture-driven Church and Basketball workflows,
not mockups. The complete 44-image phone/desktop set and provenance are in the
[screenshot guide](docs/screenshots/README.md) and
[manifest](docs/screenshots/current/manifest.json).

### Church Week-to-Week Operations

The Church administrator onboards qualified members, reviews a complete six-week
service/rehearsal roster, follows up on unanswered work, exposes a real qualified-cover
gap, publishes a holiday service with minimized changes, and rolls the horizon forward.

| Administrator operations | Member and reserve operations |
| --- | --- |
| ![Church administrator dashboard](docs/screenshots/current/church/1440/dashboard.png) | ![Church setup checklist](docs/screenshots/current/church/360/onboarding.png) |
| ![Church qualified member directory](docs/screenshots/current/church/1440/qualified.png) | ![Church member unanswered schedule](docs/screenshots/current/church/360/unanswered.png) |
| ![Church six-week solution](docs/screenshots/current/church/1440/six-week-solution.png) | ![Church member accepted commitment](docs/screenshots/current/church/360/accepted.png) |
| ![Church qualified replacement needed](docs/screenshots/current/church/1440/replacement-needed.png) | ![Church reserve covered assignment](docs/screenshots/current/church/360/replacement-covered.png) |
| ![Church holiday service published](docs/screenshots/current/church/1440/schedule-change-admin.png) | ![Church member holiday commitment](docs/screenshots/current/church/360/schedule-change-member.png) |
| ![Church week-seven rollover](docs/screenshots/current/church/1440/week-seven-rollover.png) | |

### Basketball Week-to-Week Operations

The Basketball manager runs the same operating cycle for games and practices, while
players and staff retain role-specific responses and cover. A postponed game resets the
affected response, preserves staffing, and moves the same logical calendar entry.

| Manager operations | Player, staff, and reserve operations |
| --- | --- |
| ![Basketball manager dashboard](docs/screenshots/current/basketball/1440/dashboard.png) | ![Basketball setup checklist](docs/screenshots/current/basketball/360/onboarding.png) |
| ![Basketball qualified member directory](docs/screenshots/current/basketball/1440/qualified.png) | ![Basketball player unanswered schedule](docs/screenshots/current/basketball/360/unanswered.png) |
| ![Basketball six-week solution](docs/screenshots/current/basketball/1440/six-week-solution.png) | ![Basketball player accepted commitment](docs/screenshots/current/basketball/360/accepted.png) |
| ![Basketball qualified replacement needed](docs/screenshots/current/basketball/1440/replacement-needed.png) | ![Basketball reserve covered assignment](docs/screenshots/current/basketball/360/replacement-covered.png) |
| ![Basketball postponed game published](docs/screenshots/current/basketball/1440/schedule-change-admin.png) | ![Basketball player postponed commitment](docs/screenshots/current/basketball/360/schedule-change-member.png) |
| ![Basketball week-seven rollover](docs/screenshots/current/basketball/1440/week-seven-rollover.png) | |

Reproduce the evidence locally with `make capture-screenshots`, inspect every resulting
image, then run `make validate-screenshots`. The capture uses synthetic `.example` data,
a fixed January 9, 2030 clock, Chromium, an owned temporary database, and no providers.

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
/api/v1/auth           — atomic organization bootstrap, login, refresh, email check
/api/v1/organizations  — authenticated read/update/lifecycle operations
/api/v1/people         — CRUD for people, /me profile
/api/v1/teams          — CRUD for teams + membership
/api/v1/events         — CRUD for events + manual assignments
/api/v1/constraints    — CRUD for scheduling constraints
/api/v1/solver         — POST /solve to generate schedules
/api/v1/solutions      — list/view generated solutions
/api/v1/availability   — time-off / blocked dates
/api/v1/conflicts      — conflict checking
/api/v1/invitations    — create/verify/accept invitation tokens
/api/v1/calendar       — ICS export
/api/v1/analytics      — volunteer + event stats
/api/v1/password-reset — request/confirm password reset
```

### Provider-backed Features

Notification routes are registered under `/api/v1`. Billing routes remain in the
codebase under `/api/v1`, and SMS routes under `/api/sms`, but both return 404 by
default behind `BILLING_ENABLED=false` and `SMS_ENABLED=false`. Paid billing and
SMS are deferred; the complete scheduling workflow does not require them.

---

## Testing

Run all review and validation locally. `make test-all` executes the maintained
unit, API/security, CLI, integration, web, contract, and Playwright tiers; GitHub
Actions is not test or code-review evidence. See [Testing](docs/TESTING.md).

Delegated agent runs use a finite, versioned work-item contract with guarded
Git/GitHub access. See [Agent runner](docs/AGENT_RUNNER.md) for Claude/Gemini
commands, local evidence, ownership rules, and failure behavior.

Use the [church and basketball operational playbooks](docs/playbooks/README.md)
for six-week acceptance scenarios, reproducible API/browser tests, and explicit
manual release checks.

### Test Coverage

```bash
make test-all                        # All seven Python tiers, including Playwright
make test-performance               # Opt-in; requires an owned loopback test server
make test-mobile                     # Flutter unit/widget tests
make capture-screenshots             # Regenerate asserted Church/Basketball UI evidence
make validate-screenshots            # Reject missing, altered, or stale captures
```

See the [current testing and merge guide](docs/TESTING.md) for all tiers,
dependencies and local review/validation evidence requirements.
See the [tool safety ledger](docs/TOOLS.md) before running maintenance,
migration, provider, database-inspection, Docker cleanup, or legacy helper commands.
`make test-all` validates [the declared suite inventory](tests/local_validation_manifest.json)
and writes a SHA-bound JSON report plus per-tier JUnit and console logs under
`test-artifacts/local-validation/`. The report names all opt-in scopes that were not run.
Counts and runtimes belong to dated validation reports, not static overview tables.
The [web journey matrix](docs/web-journey-matrix.json) inventories every rendered
route and template and binds each workflow family to named happy-path, error, and
permission evidence. Unit validation rejects new web surfaces until that inventory
is updated. Browser recovery tests also cover actionable HTMX validation, preserved
form input after a network failure, rapid duplicate submission, expired sessions,
long labels at phone width and zoom, keyboard access, and authoritative SSE refresh.

### API Test Coverage

API tests exercise event management, conflicts, availability, profiles, teams,
scheduling, organization lifecycle, and authorization. The
[executable API authorization matrix](docs/API_AUTHORIZATION.md) records every
mounted operation and the real-JWT tenant regressions for scheduling routes.
Production acceptance still requires the remaining
[playbook boundaries](docs/playbooks/README.md#known-boundaries-and-release-blockers).

### Scenario Tests

Both API and CLI suites include real-world scenario tests:

**Church ministry** — A coordinator runs a six-week worship and ministry roster
with multi-role volunteers, absences, simultaneous services, shortages,
replacement, regeneration, publication, acceptance, and swaps.

**Basketball team** — A coach runs a six-week game and practice roster with
multi-position players, injuries, simultaneous events, shortages, replacement,
regeneration, publication, acceptance, and swaps.

Roster allocation is not member acceptance. See the
[assignment response contract](docs/ASSIGNMENT_RESPONSES.md) for persisted states,
revision handling, migration behavior, coordinator queues, and replay protection.
Open-shift claims, swap covers, and coordinator roster edits share a serialized
[allocation transaction contract](docs/ALLOCATION_TRANSACTIONS.md). It preserves
draft history, rechecks qualification and availability after locking, prevents
overfill and overlap races, and leaves the prior roster unchanged on failure.

Publishing follows a strict [full-horizon schedule contract](docs/SCHEDULE_PUBLICATION.md).
The server rejects incomplete, stale, ineligible, overlapping, or narrower replacement
rosters before changing member visibility. Generated solutions include every event
in their solve scope, including unfilled events; legacy scope-less solutions must be
regenerated. Explicitly cancel an event, add the next week, regenerate the remaining
horizon, and publish only after every required role is covered.

The [machine-readable coverage manifest](docs/playbooks/coverage.json) binds the
shared BO journeys, every Church/Basketball qualification, stable scenario IDs,
execution tiers, and remaining partial/blocked work. Pytest validates it before
playbook collection so a missing required role or scenario cannot silently pass.

The browser playbooks create each organization and first admin through normal signup,
then invite and accept fourteen baseline members plus a qualified replacement through
the UI. They preserve `admin`/`volunteer` account access separately from custom
scheduling qualifications such as `worship_leader`, `center`, and `scorekeeper`.
The same admin journey creates all six primary and six rehearsal/practice events through
the multi-role browser form, solves the 84-slot horizon, and independently verifies exact
role coverage, distinct qualified assignees, non-overlap, and balanced interchangeable
loads before publication. API and web safety regressions prove incomplete or stale
candidates cannot replace the live roster.
Every Church and Basketball qualification also runs the member availability page at
360px and 1440px: it records Wednesday time off and recurring Sunday unavailability,
rejects peer edits without mutation, and verifies exclusion across twelve API-seeded
events while retaining a complete qualified roster.

The browser playbooks also distinguish recurrence scope at both widths. An administrator
moves one occurrence, cancels a different occurrence, verifies that the remaining event
is unchanged, and uses a separately labeled action to delete the entire series. Moving an
already accepted published event resets that commitment to unanswered, so the assigned
member must review and accept the changed time again.

The rolling-horizon journey starts from an API-seeded, already published six-week
precondition with its first primary and secondary sessions completed. At both browser
widths, each domain administrator adds week seven through the event form, solves and
publishes weeks two through seven through the UI, and verifies the new 84-slot roster.
The independent oracle proves that the completed event records and every original future
commitment remain; fixture seeding is not counted as a browser action.

The local-mail journey runs for Church and Basketball at both browser widths with
all paid providers disabled. It writes real RFC 822 messages to an owned temporary
directory, accepts the invitation through its captured link, and drives both the
administrator and volunteer through logout/login, self-service password change, and
captured single-use reset links. Copied pre-change and pre-reset browser sessions, old
passwords, replayed links, and expired API tokens fail safely. The same run delivers
assignment, schedule-change, and reminder messages from the published roster, reconciles
the member inbox, and opens every notification HTTP link against the owned local server.
This is local business-flow evidence, not proof of external inbox placement or provider
reliability.

The personal-calendar journey also runs for both domains at 360px and 1440px. Draft
work is absent, publication creates one entry, a schedule move updates the same UID in
the member's `America/Toronto` timezone, and cancellation removes it on refresh. Unit
and real-JWT API regressions cover a DST transition, consistent download/feed scope,
declined assignments, and deliberately mismatched foreign-tenant child rows. This proves
local ICS behavior, not the polling interval or rendering of every third-party client.

The two-organization BO-12 journey starts Church and Basketball together in the same
disposable application. Each administrator sees only its own people, and one volunteer
for every declared Church and Basketball scheduling qualification signs in at 360px and
1440px. Volunteers stay out of the administrator surface and cannot invite, publish,
inspect a foreign person, or mutate a peer's availability. API and browser credentials
are bound to the active account's tenant; missing, mismatched, or inactive membership
claims fail authentication. This is local application evidence, not deployment or
infrastructure certification.

The domain late-cover journey is driven by each playbook's declared roles. Church tests
separate sound-operator and children's-leader withdrawals; Basketball tests separate coach
and scorekeeper withdrawals. At both browser widths, the coordinator sees the real gap,
wrong-role and unavailable reserves cannot see it, and one exact qualified available reserve
covers it without changing any other player, ministry, or staff slot.

Domain eligibility changes are fixture-driven too. Church removes a future children's
ministry qualification, reopens only affected live work, preserves completed history, and
shows the exact gap at both browser widths. Basketball records a point guard's multiweek
absence, proves solver exclusion inside the interval, and requires a deliberate member
update before the player becomes schedulable again. Safeguarding and medical clearance
remain explicit human decisions; the application does not infer either one.

Schedule-change operations are fixture-driven at both browser widths as well. Church adds
an usher-only holiday service, minimizes roster changes, compares one added and zero removed
commitments, republishes, reminds the new assignee, and preserves an existing acceptance.
Basketball postpones a point-guard game, resets the affected acceptance, minimizes roster
changes, republishes and reminds, and moves the logical calendar entry under the same UID
even when publication creates a new assignment row. Ministry approval and venue/opponent
coordination remain human decisions outside the application.

Saved REST scheduling rules support hard assignment caps, hard minimum rest gaps,
and a weighted soft cooldown preference. They execute in API solves instead of
being stored as inert text. See the
[validated constraint contract](docs/SCHEDULING_CONSTRAINTS.md) for request shapes,
CLI equivalents, built-in overlap/availability behavior, and unsupported policy.

### Commands

```bash
make setup                # First-time setup
make run                  # Dev server on :8000
make test                 # Complete local Python suite (same as make test-all)
make test-unit            # Python unit tests only
make test-unit-fast       # Skip slow bcrypt tests (~7s)
make test-all             # All Python tiers, including web + contract + Playwright
make test-mobile          # Flutter tests (requires Flutter SDK)
make capture-screenshots  # Recreate public Church/Basketball screenshots locally
make validate-screenshots # Verify image, fixture, UI-source, and caption metadata
make migrate              # Run Alembic migrations
```

Run the provider-free local delivery workflow directly with
`poetry run pytest tests/e2e/test_local_mail_playbooks.py -v`. See the
[local mail capture guide](docs/LOCAL_EMAIL_CAPTURE.md) for its backend contract.

Single test: `poetry run pytest tests/unit/test_events.py::test_create_event -v`

Tests run locally, not in GitHub Actions. `poetry install` installs the locked
Playwright Python dependency; before the first browser run, install Chromium with
`poetry run playwright install chromium` (Linux may also require browser system
dependencies). `make test-all` runs each tier in a separate process, including
both church and basketball playbooks.
Run `make test-mobile` for mobile changes;
set `FLUTTER=/path/to/flutter` if the SDK is not on your PATH.

No CI checks: formatting, lint, type checks, migrations, code review, unit tests,
and E2E tests all run locally. Record commands, results and reviewed head/base
SHAs in the PR before merging. GitHub does not independently attest local runs;
never fabricate a successful status check. Ollama is not a code-review provider.
See the [current production roadmap](docs/ROADMAP.md).

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
2. After explicit branch authorization, create it: `git switch -c codex/my-feature`
3. Write tests first (TDD), implement, verify with `make test-unit`
4. Stage only owned files, then commit and push
5. Open a Pull Request

---

## License

MIT License — see [LICENSE](LICENSE) for details.
