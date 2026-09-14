<div align="center">

# SignUpFlow

### Church and Basketball Scheduling, Run Locally

*Week-to-week roster operations for coordinators, volunteers, players, and staff*

[![Python](https://img.shields.io/badge/python-3.11--3.13-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Validation](https://img.shields.io/badge/validation-local_only-167D8D?style=for-the-badge)](docs/TESTING.md)
[![Playbooks](https://img.shields.io/badge/playbooks-Church_%2B_Basketball-0F766E?style=for-the-badge)](docs/playbooks/README.md)
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
- **Browser request integrity** — signed CSRF tokens and exact-origin checks protect form and HTMX writes
- **Truthful responses** — unanswered, accepted, declined, and replacement-needed work stay distinct from roster allocation
- **Availability tracking** — volunteers block dates, time-off with reasons
- **Calendar export** — ICS files and webcal subscriptions

---

## Quick Start

SignUpFlow is an open-source application you run yourself. No hosted service,
paid plan, or production deployment is included. Billing and paid SMS stay disabled
by default and are not required for the Church or Basketball workflows.
Production-like startup is fail-closed for signing keys, database/origin settings,
test bypasses, and enabled-provider coherence; see the
[configuration contract](docs/PRODUCTION_CONFIGURATION.md). This is a configuration
guard, not deployment or provider acceptance.

```bash
git clone https://github.com/tomqwu/SignUpFlow.git
cd SignUpFlow
make setup
poetry run signupflow --help
```

---

## CLI Examples

Run either maintained six-week YAML workspace without a database or API server:

```bash
poetry run signupflow solve examples/church
poetry run signupflow solve examples/basketball
```

Create a new sample or use the equivalent module command:

```bash
poetry run signupflow init /tmp/my-church
poetry run signupflow solve /tmp/my-church --json-output
poetry run python -m api.cli.main solve examples/church --json-output
```

The examples are deliberately compact. The complete role-by-role business workflow
is the API/browser playbook described below and in [examples](examples/README.md).

## Local API Example

Start an owned local server and run the executable Basketball workflow. It creates
an organization and admin atomically, accepts seven member invitations, creates one
fully staffed event, solves it, and publishes it through canonical `/api/v1` routes.

```bash
EMAIL_ENABLED=false SMS_ENABLED=false BILLING_ENABLED=false make run
curl http://127.0.0.1:8000/health
poetry run python examples/api_client_example.py
```

Existing organizations reject public signup. Every later member joins through an
administrator-created invitation. The script accepts loopback endpoints only, uses
synthetic `.example` identities, and contains no real token or provider credential.
Interactive API docs are at http://127.0.0.1:8000/docs.

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
The executable scenario catalog covers
[CH-01](docs/playbooks/church.md#six-week-exercise),
[CH-02](docs/playbooks/church.md#six-week-exercise),
[CH-03](docs/playbooks/church.md#six-week-exercise),
[CH-04](docs/playbooks/church.md#six-week-exercise),
[CH-05](docs/playbooks/church.md#six-week-exercise),
[CH-06](docs/playbooks/church.md#six-week-exercise),
[CH-07](docs/playbooks/church.md#six-week-exercise), and
[CH-08](docs/playbooks/church.md#six-week-exercise).

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
The executable scenario catalog covers
[BB-01](docs/playbooks/basketball.md#six-week-exercise),
[BB-02](docs/playbooks/basketball.md#six-week-exercise),
[BB-03](docs/playbooks/basketball.md#six-week-exercise),
[BB-04](docs/playbooks/basketball.md#six-week-exercise),
[BB-05](docs/playbooks/basketball.md#six-week-exercise),
[BB-06](docs/playbooks/basketball.md#six-week-exercise),
[BB-07](docs/playbooks/basketball.md#six-week-exercise), and
[BB-08](docs/playbooks/basketball.md#six-week-exercise).

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
POST /api/v1/solver/solve      →  api/routers/solver.py (HTTP + DB)
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
/api/v1/assignments    — member responses, open-shift claims, swaps
/api/v1/audit-logs     — tenant-scoped administrative audit history
/api/v1/recurring-series — recurring-event series and occurrence operations
/api/v1/resources      — venues and capacity records
/api/v1/holidays       — organization holiday records
/api/v1/notifications  — in-app notification inbox and reconciliation
/api/v1/billing        — disabled by default; deferred commercial surface
```

### Provider-backed Features

Notification routes are registered under `/api/v1`. Billing routes remain in the
codebase under `/api/v1`, and SMS routes under `/api/sms`, but both return 404 by
default behind `BILLING_ENABLED=false` and `SMS_ENABLED=false`. Paid billing and
SMS are deferred; the complete scheduling workflow does not require them. Stripe
and SendGrid webhook handlers exist in `api/routers/webhooks.py` but are intentionally
not mounted. The SMS webhook paths share the disabled `/api/sms` router.

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
make test-postgres                   # Opt-in owned PostgreSQL migration/business/race checks
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
Browser request-integrity tests inventory every unsafe rendered route, reject missing or
forged tokens and foreign origins without mutation, verify configured proxy boundaries,
and exercise a real same-origin profile save in Chromium.

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
make test-postgres        # Owned ephemeral PostgreSQL acceptance (requires Docker)
make test-mobile          # Flutter tests (requires Flutter SDK)
make capture-screenshots  # Recreate public Church/Basketball screenshots locally
make validate-screenshots # Verify image, fixture, UI-source, and caption metadata
make migrate              # Run Alembic migrations
```

Run the provider-free local delivery workflow directly with
`poetry run pytest tests/e2e/test_local_mail_playbooks.py -v`. See the
[local mail capture guide](docs/LOCAL_EMAIL_CAPTURE.md) for its backend contract.

Single test: `poetry run pytest tests/unit/test_events.py::test_create_event -v`

Tests run locally. GitHub Actions is not test or code-review evidence.
`poetry install` installs the locked Playwright Python dependency; before the first browser run, install Chromium with
`poetry run playwright install chromium` (Linux may also require browser system
dependencies). `make test-all` runs each tier in a separate process, including
both church and basketball playbooks.
Run `make test-postgres` for database or migration changes. It creates and removes its
own loopback-only PostgreSQL 16 container and writes versioned JUnit/report evidence;
never substitute a shared or customer database.
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
