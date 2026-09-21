# Schedule Publication Contract

Publication activates one complete schedule for an organization. It is a strict
full-horizon operation: there is no shortage, stale-data, or eligibility override.
The API and web app use the same validation and transaction boundary.

## Solve scope

Every API-generated solution stores an immutable snapshot of the solve window:

- `scope_start` and `scope_end` identify the requested date range.
- `scope_event_ids` includes every event in that range, including an event with no
  generated assignment.
- `scope_fingerprint` covers each event's identity, time, resource, required role
  counts, and team links, plus the organization's saved scheduling constraints.

Solutions created before this metadata existed, including manually imported
solutions, cannot prove what was considered. Regenerate them before publish or
rollback. Do not infer a legacy scope from assigned rows because that omits
unfilled events.

## Publication rules

Before changing the live roster, publication locks the organization and reloads
the current events, members, qualifications, availability, manual assignments,
and existing published horizon. It rejects the candidate when:

- any event or requirement in its saved solve window changed;
- any still-existing future event in the active horizon is absent;
- a required role is short or over capacity;
- the solution records a hard violation;
- an assignee is inactive, unqualified, unavailable, duplicated on an event, or
  overlaps another assignment; or
- an event, member, or assignment is outside the organization.

To cancel a future event, delete that event explicitly before solving the full
replacement horizon. A completed past event or an explicitly deleted event does
not have to appear in a rolling replacement. Add week seven, solve all remaining
future events together, review, and then publish.

For a recurring series, the Events page labels move and cancel actions as applying to
one occurrence; editing one marks it as an exception and leaves sibling occurrences
unchanged. The Recurring page labels deletion as applying to the entire series. After
either scope of change, regenerate the full remaining horizon before publication.

## Responses and notifications

A materially unchanged assignment carries forward only a current recorded member
response for the same event, person, and role. New or changed work remains
unanswered. Publication never invents acceptance from an assignment's default
workflow status.

Carry-forward reads the organization's *currently published* solutions. A
replacement published directly over the live roster therefore keeps a matching
acceptance, while unpublishing first and then publishing the same roster finds
no prior solution, leaves the work unanswered, and asks the member again. The
two routes reach the same destination with different results; `tests/api/
test_publication_recovery.py` pins both. Prefer publishing the replacement
directly until that asymmetry is resolved.

Unpublishing sends nothing. A member keeps any assignment notice they already
received while the shift stops appearing in their schedule. Correcting an event
during an unpublished window is likewise silent, yet still resets every response
for that event.

Pending assignment notification intent is stored in the same database transaction
as the active-roster switch and audit record. Already accepted unchanged work does
not receive a redundant assignment notification. External email and paid SMS
delivery remain disabled by default and are outside this contract.

## Failure behavior

Validation returns `409 Conflict` with the affected event, role, or member where
available. A legacy solution also returns `409` and asks the administrator to
regenerate. Rollback to a solution that was never published returns `400`.

A role-capacity refusal caused by a manual assignment names the member holding
it and states the two ways out, removing it or regenerating. This matters after
a coordinator overrides one of the solver's placements: the next solve neither
sees nor preserves that override, so it re-places the person who was removed and
the two together read as over-staffed.

Rollback re-validates the target's scope, so it recovers a bad roster choice but
not a corrected event. Once an event inside the solve window changes, rolling
back to the pre-correction solution returns `409` and asks for regeneration.

Any validation, audit, notification-intent, flush, or commit failure leaves the
previously published solution active. Concurrent publish, rollback, claim, swap,
and roster-edit operations share the organization allocation lock.

## Local verification

Run the focused contract and both domain playbooks:

```bash
poetry run pytest tests/api/test_solution_publication_safety.py tests/api/test_solution_publish.py tests/api/test_solution_compare_rollback.py tests/web/test_publish_lifecycle.py -q
poetry run pytest tests/api/test_domain_playbooks.py -q
poetry run pytest tests/e2e/test_domain_playbooks.py -q
poetry run pytest tests/integration/test_assignment_claim_concurrency.py tests/integration/test_solution_scope_migration.py -q
```

Run `make test-postgres` for owned PostgreSQL 16 publication concurrency and
migration acceptance; do not supply a shared database URL. Run `make test-all` and
`make test-mobile` before merge. GitHub Actions does not run or attest these tests.
