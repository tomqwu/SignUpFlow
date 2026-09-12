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
EMAIL_ENABLED=false SMS_ENABLED=false poetry run pytest tests/api/test_domain_playbooks.py -v
poetry run pytest tests/unit/test_solver_role_slots.py -v
poetry run playwright install chromium
EMAIL_ENABLED=false SMS_ENABLED=false poetry run pytest tests/e2e/test_domain_playbooks.py -v
make test-unit-fast
make test-all
```

The API tier uses real JWT identities and an isolated in-memory SQLite database.
The browser tier starts the real application against a temporary SQLite database.
It uses API setup for the bulk roster and five repeated weeks, then browser login,
multi-role event creation, solve, review, publish, and member acceptance. It is not
a claim that every setup step is achievable through the current browser forms.
The existing `test_onboarding_wizard.py` separately covers signup and invitation
acceptance through the browser.

`church.json` and `basketball.json` are the executable role/headcount fixtures.
`tests/playbook_support.py` reads them in both test tiers. Each run creates new
organizations and invitations with fictional `.example` addresses. Dates start
on a Sunday at least two weeks ahead, avoiding expired-date tests.

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
- Scheduling role strings are not separate permission records. Use `admin` only
  for administrators, `volunteer` plus scheduling roles for members. Browser
  invitation controls do not expose the complete custom-role setup used here.
- These tests prove publish authorization, not complete tenant security. Several
  solution-read and availability routes still need authentication/isolation work.
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
