# Acceptance evidence - 2026-09-12

Run in the `SignUpFlow-production` worktree, starting from `9f94d56`, with
Python 3.11, SQLite, real JWT/cookie sessions and Chromium. External email/SMS
delivery was disabled. No customer organization was used.

## Failures reproduced and repaired

1. Both domain journeys initially failed because solution assignments omitted the
   selected role. Preserve the solver's per-person role, save it in the existing
   assignment column, and expose it as an optional response field.
2. A multi-skilled person could conceal an unfilled role: coverage was counted
   from qualifications rather than selected slots. Count actual selected roles.
3. A person could be scheduled for overlapping events without explicit custom
   constraints. Reject overlapping candidates; keep adjacent events legal.
4. Browser members could see unpublished solver assignments. Apply the same
   publication filter to member schedule lists, detail pages and self-service
   API actions. Keep immediate manual assignments visible. Test that old
   assignments become hidden/non-actionable after replacement publication.

The existing SSE tests now explicitly publish their seeded solutions before
testing member actions. An older recurring-event browser test exposed a click
race; wait for HTMX settling before clicking its newly rendered Delete control.

## Validation results

| Check | Result |
| --- | --- |
| New church/basketball six-week API journeys | 2 passed inside the full API tier |
| New domain browser journeys, 360px and 1440px | 4 passed, including qualified swaps |
| Complete unit tier | 399 passed, 21 skipped |
| Complete API tier | 444 passed |
| Complete CLI tier | 16 passed |
| Complete integration tier | 325 passed |
| Complete web tier | 225 passed |
| Complete browser tier | 33 passed on full rerun after timing repair |
| OpenAPI snapshot contract | 1 passed after reviewed optional-field update |
| Black / Ruff | Passed |
| Strict mypy scope (`api/utils api/core api/schemas`) | Passed, 61 files |
| Full API mypy | Existing debt: 835 errors in 40 files; not a pass |

Total across the separate backend, web, browser and contract runs: 1,443 passed,
21 skipped. `make test-all` completed successfully.

The first full browser run had 32 passes and one recurring-delete timing failure.
The targeted rerun and repaired full rerun passed; this initial failure is not
omitted from the evidence. The first contract run failed on the intentional
optional `role` addition, then passed with the reviewed snapshot.

Inspected rendered phone onboarding and desktop basketball acceptance screenshots.
The automated runs also save screenshots for both domains at both widths under
pytest's temporary directories. Those images are disposable, not release archives.

## Compatibility and limits

The response adds an optional nullable `role`; existing required fields are unchanged.
The current generated Dart deserializer ignores unknown fields (its `unhandled`
collection is not rejected), so this does not require a mobile rollout. Exposing
the new role in the mobile solution-review screen remains separate work.
No database migration is needed: the assignment role column already exists.

This is local acceptance evidence, not a production-readiness declaration or
GitHub merge approval. See [remaining release blockers](README.md#known-boundaries-and-release-blockers).
Do not count manual operational drills, external delivery, PostgreSQL, DST,
venue scheduling or full tenant isolation as verified by these runs.
