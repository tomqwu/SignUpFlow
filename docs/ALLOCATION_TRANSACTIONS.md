# Allocation Transaction Contract

Open-shift claims, swap covers, swap denials, and coordinator roster edits use
`api/services/allocation_service.py` as their authoritative mutation boundary.
Each operation locks the owning organization before it reads capacity or member
eligibility, applies the roster change and audit record in one transaction, and
commits once at the request boundary.

## Live allocation rules

- A manual assignment is live immediately.
- A solver assignment is live only while its solution is published.
- Unpublished and superseded solution assignments remain historical records and
  do not consume open-shift capacity or block a live claim.
- A declined live assignment does not consume role capacity.
- A claimant must be an active member of the organization, hold the exact
  scheduling qualification, and have no vacation, exception, recurring block,
  same-event assignment, or overlapping live assignment.
- Adjacent events are allowed. Strictly overlapping events are rejected.
- A successful self-claim or swap cover records an accepted response for the
  current commitment revision. A winner retry is idempotent.

PostgreSQL serializes competing writers with a no-op update of the organization
row. SQLite takes its write lock at the same point, before authoritative reads.
This tenant-wide lock favors correctness and simple lock ordering; finer-grained
locking requires measured contention evidence before it replaces this contract.

## Failure behavior

Expected stale, full, ineligible, or overlapping requests return a controlled
conflict. Request handlers roll back before rendering the current roster. An
audit failure also rolls back the assignment change, and no notification is
created by a failed claim. A global `(event_id, person_id)` uniqueness constraint
is deliberately absent because draft and historical solutions may contain the
same person and event.

## Local verification

Run the focused web/API and SQLite concurrency tests:

```bash
poetry run pytest tests/web/test_open_shifts.py tests/web/test_swap_marketplace.py tests/web/test_event_roster_fill.py tests/api/test_assignment_self_service.py tests/integration/test_assignment_claim_concurrency.py -q
poetry run pytest tests/e2e/test_open_shifts.py tests/e2e/test_swap_marketplace.py -q
```

Run PostgreSQL migration, claim, and publication concurrency acceptance through the
owned runner. It creates a unique loopback-only container and migration-built databases,
then verifies ownership before removing that container. Do not pass a shared database URL.

```bash
make test-postgres
```

Run `make test-all` before merge. Record the exact tested commit, database
version, command, pass count, skips, and any limitations in the pull request.
GitHub Actions does not run or attest these tests.
