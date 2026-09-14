# Operational acceptance playbooks

Run these before calling a church or basketball scheduling release ready:

- [Church: six-week ministry roster](church.md)
- [Basketball: six-week team roster](basketball.md)
- [Executed acceptance results and limitations](validation.md)

These are scheduling acceptance exercises, not certification that a real organization
is operationally ready. Use fictional people and a disposable database. Never run
the fixtures against a customer organization. Email and SMS must remain disabled.

## Reproduce

From the repository root, after installing the development dependencies:

```bash
EMAIL_ENABLED=false SMS_ENABLED=false BILLING_ENABLED=false poetry run pytest tests/api/test_domain_playbooks.py -v
poetry run pytest tests/unit/test_solver_role_slots.py -v
poetry run playwright install chromium
EMAIL_ENABLED=false SMS_ENABLED=false BILLING_ENABLED=false poetry run pytest tests/e2e/test_domain_playbooks.py -v
make test-unit-fast
make test-all
```

The API tier uses real JWT identities and an isolated in-memory SQLite database.
The browser tier starts the real application against a temporary SQLite database.
The default business profile has billing and paid SMS disabled; neither playbook
creates a subscription or contacts an external provider. In each browser variant,
the administrator invites all fourteen members with their scheduling qualification,
each member accepts through the invitation page, and the administrator verifies the
qualification editor. Five repeated weeks are then created by API before the browser
creates the remaining event, solves, reviews, publishes, and records member response.
Organization bootstrap is atomic and the five repeated events remain API setup in
this browser test; normal browser signup has separate web coverage.

`church.json` and `basketball.json` are the executable role/headcount fixtures.
`tests/playbooks/` validates and discovers them for both test tiers. Each run creates new
organizations and invitations with fictional `.example` addresses. Dates start
on a Sunday at least two weeks ahead, avoiding expired-date tests.

[`coverage.json`](coverage.json) is the machine-readable business-flow manifest.
It records BO-01 through BO-12, CH-01 through CH-08, BB-01 through BB-08,
operational actors, preconditions, operations, expected results, execution tiers,
evidence paths, and honest coverage status. Pytest validates it before collecting
playbook cases. Removing a bundled domain, required scenario, administrator,
human boundary, or scheduling qualification fails collection.

## Plug into pytest

The plugin is registered in `tests/conftest.py`. Every test requesting the
`playbook_spec` fixture runs once per discovered definition with a stable ID and
the `playbook` marker. Local `make test-all` automatically runs all bundled
definitions in both API and browser tiers. GitHub Actions does not run tests;
include local results for the pushed revision in each PR.

```bash
# Select one domain; the browser tier still runs both viewport sizes.
poetry run pytest tests/api/test_domain_playbooks.py --playbook church
poetry run pytest tests/e2e/test_domain_playbooks.py --playbook basketball

# Inspect the exact parameterized cases without creating any test data.
poetry run pytest tests/api/test_domain_playbooks.py --collect-only -q

# Load an external directory and run the example through each tier.
poetry run pytest tests/api/test_domain_playbooks.py --playbook-dir tests/playbooks/examples --playbook food-bank
poetry run pytest tests/e2e/test_domain_playbooks.py --playbook-dir tests/playbooks/examples --playbook food-bank

# Filter to playbook tests within one tier; options are repeatable.
poetry run pytest tests/api -m playbook --playbook church --playbook basketball
```

Run API and browser tiers in separate pytest processes, as `make test-all` does. Their event
loop fixtures are different. `--playbook` filters playbook parameters only; use
`-m playbook` or the explicit files to avoid running unrelated tests.

To add a domain permanently, add one JSON file to `docs/playbooks/` using
[the food-bank example](../../tests/playbooks/examples/food-bank.json) as a template.
To load it temporarily, pass its directory with `--playbook-dir`. External
directories augment the bundled definitions and cannot override duplicate IDs.
Unknown selections, missing/empty directories, invalid JSON, unsupported versions,
unsupported workflows, extra fields, and invalid role counts fail collection.
The reserved `coverage.json` metadata file is not treated as an executable domain.

Version 1 requires `id`, `version: 1`, `workflow: six_week_roster`, `name`,
`event`, `secondary_event`, `roles`, and `critical_role`. IDs use lowercase letters,
digits, underscores or hyphens; role codes use lowercase letters, digits or
underscores. Both start with a letter. Role counts are positive integers, not
booleans or numeric strings. The critical role must require exactly one person,
matching the absence/shortage/replacement drill. Definitions contain no passwords,
API keys, executable code or production endpoint settings.

The runtime creates fresh organizations and a deep-copied definition per test.
`tests/playbooks/workflows.py::run_six_week_roster` is reusable with the test
client; `tests/playbooks/runtime.py::Playbook` exposes the lower-level actions and
coverage oracle. A new pytest test can request `playbook_spec` to reuse discovery
and selection without duplicating the list of domains.

Coverage statuses have precise meanings: `automated` has executable local test
evidence; `partial` has useful automated evidence but not the complete manifest
oracle; `manual` is an accepted human operation; `blocked` names missing product
behavior or evidence and includes the manual tier so it cannot look automated.
The manifest currently marks week-seven rollover and owned-mail delivery blocked,
and keeps incomplete all-role/browser journeys partial.

This is a domain-definition plugin for the six-week lifecycle, not an arbitrary
workflow language. Adding a different lifecycle requires implementing and testing
that workflow before accepting its identifier in `PlaybookSpec`. Do not accept
unknown workflow IDs or silently skip unsupported scenarios.

## Coverage map

| Requirement | Automated evidence |
| --- | --- |
| Every required role filled by a distinct eligible person | API journey, every event in all six weeks; browser post-solve oracle |
| Balanced load among interchangeable people | API baseline actual assignment counts, maximum difference one |
| Planned absence uses a qualified reserve | API week 2 |
| Simultaneous services/games use disjoint people | API week 3; overlap unit regression |
| Missing role is reported instead of silently double-counted | API week 4; multi-skilled unit regression |
| Qualified replacement repairs shortage | API week 5 |
| Changed event time reaches regenerated roster | API week 6 |
| Old published roster survives draft generation | API journey |
| Repaired publication replaces old publication | API journey |
| Volunteer, anonymous user, foreign admin cannot publish | API journey |
| Draft invisible, published shift visible, member can accept | Browser journey, both domains |
| Qualified reserve covers a swap without losing role coverage | Browser journey, both domains |
| Draft/replaced assignments cannot be accepted, declined or swapped | API journey and web publication regression |
| Multi-role form preserves exact names/counts | Browser journey, both domains |
| Phone and desktop page width | Browser journey at 360 and 1440 pixels |
| Adjacent events remain legal | Unit regression |

Browser runs save onboarding and accepted-assignment screenshots in pytest's
temporary test directory. Inspect them as well as assertion results. A horizontal
overflow assertion alone is not a comprehensive visual/accessibility audit.

## Known boundaries and release blockers

- Only one solution per organization is published at a time. Regenerate the full
  remaining horizon, not one isolated week, or future published shifts disappear.
- Publication currently allows incomplete rosters. The playbooks require an admin
  to resolve shortages first; the application does not enforce that policy yet.
- Persisted custom constraints are not loaded by the API solver. Do not promise
  maximum weekly load, rest/travel gaps, family grouping, or skill certification.
- Team membership is not a proven eligibility boundary for role-based solving.
  These fixtures use one scheduling organization and explicit role qualifications.
- Scheduling qualifications are stored beside, but are not, permission records.
  Every account has exactly one permission role (`admin` or `volunteer`); use
  `volunteer` plus scheduling qualifications for members.
- The route-policy and two-tenant regressions in
  [API_AUTHORIZATION.md](../API_AUTHORIZATION.md) cover scheduling route
  authentication, resource hiding, and export filtering. This does not replace
  PostgreSQL, provider, deployment, or whole-application security acceptance.
- Role-based solver assignments now retain their selected role. Old solutions
  with null roles need regeneration; no existing data is silently rewritten.
- The role-less team fallback, venue collision checks, DST/timezone transitions,
  recurrence exception handling, real notification delivery, and PostgreSQL
  concurrency require separate acceptance before production use.
- Basketball playing minutes, substitutions during play, scores, standings and
  league eligibility are outside this scheduling application.

## Sign-off record

For each release record: commit, command, date, pass/fail, screenshot location,
scenario deviations, unresolved blockers, and the coordinator's approval.
Do not mark manual scenarios passed merely because the automated suite is green.
