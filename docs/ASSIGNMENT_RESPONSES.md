# Assignment Response Contract

Assignment allocation and member response are separate facts. A person can be
placed on a roster without having accepted it. New assignments therefore start
unanswered, including assignments created by the solver or an administrator.

## Persisted State

| Field | Meaning |
| --- | --- |
| `status` | Compatibility workflow projection: `pending`, `confirmed`, `declined`, or `swap_requested` |
| `response_status` | Member response truth: `pending`, `accepted`, or `declined` |
| `responded_by_person_id` | Authenticated member who made the response |
| `responded_at` | Time the response was recorded |
| `commitment_revision` | Current version of this person/event/role commitment |
| `response_revision` | Commitment revision acknowledged by the response |
| `response_current` | Derived true only when an accepted or declined response matches the current revision |

## Transition Table

| Operation | Workflow status | Response status | Revision behavior |
| --- | --- | --- | --- |
| Solver or coordinator assigns | `pending` | `pending` | Starts at 1 |
| Assigned member accepts | `confirmed` | `accepted` | Records actor/time against current revision |
| Assigned member declines | `declined` | `declined` | Records actor/time and reason against current revision |
| Assigned member requests replacement | `swap_requested` | `declined` | Records actor/time and optional note against current revision |
| Coordinator denies replacement | `pending` | `pending` | Increments commitment revision and requires a new member response |
| Qualified member claims open work | `confirmed` | `accepted` | The successful claim is that member's explicit response |
| Qualified member covers a replacement | `confirmed` | `accepted` | Reassigns, increments revision, and records the claimant's response |
| Event, time, location, role requirements, person, or role changes | `pending` | `pending` | Increments revision and clears prior response evidence |

Publishing a replacement solution carries a current response only when event,
person, and role are unchanged. Material event edits invalidate the prior source
response before another solution can inherit it.

## API Behavior

`AssignmentResponse` includes all persisted response fields plus
`response_current`. New clients should send `expected_revision` when accepting,
declining, or requesting a replacement. A mismatched revision returns `409` and
does not mutate the assignment or add an audit row. The revision remains optional
for compatibility with existing generated clients; regenerated clients expose it.

Member endpoints load only the caller's current published or manual assignments.
Anonymous callers, other members, foreign organizations, drafts, and replaced
solutions cannot read or mutate the response through member self-service.
Authorized coordinators can inspect response state through the organization
assignment API and the filtered Assignments page.

Response mutation and its audit row commit in one database transaction. Replaying
the same current response succeeds without creating a duplicate audit row or
publishing a duplicate change event. Opening a notification never changes response
state.

## Migration

The migration preserves historical `status` values for allocation compatibility,
but initializes every historical `response_status` to `pending`. Old `confirmed`
rows have no authenticated actor, response time, or acknowledged revision, so they
must not be presented as human acceptance.

## Local Validation

```bash
poetry run pytest tests/api/test_assignment_response_truth.py -q
poetry run pytest tests/integration/test_assignment_response_migration.py -q
poetry run pytest tests/web/test_all_assignments.py tests/web/test_notifications.py -q
poetry run pytest tests/e2e/test_domain_playbooks.py -q
make test-all
make test-mobile
```

The browser playbook runs both Church and Basketball at 360px and 1440px. It
checks unanswered, accepted, replacement-needed, and qualified-cover states in
member and coordinator views. It then changes an accepted event through the admin
browser, verifies that the member returns to unanswered, and records a new acceptance
for the incremented commitment revision.
