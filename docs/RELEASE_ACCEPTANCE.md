# Release Acceptance Matrix

This is the canonical preparation record for issue
[#271](https://github.com/tomqwu/SignUpFlow/issues/271). It does not authorize a
deployment, provider call, production-data operation, store submission, or public
release. Complete every in-scope row against one frozen source revision and one
immutable runtime artifact before an owner go/no-go decision.

## Status Vocabulary

| Status | Meaning |
| --- | --- |
| `PASS_LOCAL` | Reproducible local evidence exists for the named source and scope. |
| `BLOCKED_OWNER` | The owner must supply or approve a product or operating decision. |
| `BLOCKED_TARGET` | An explicitly authorized disposable release-equivalent target or operator is required. |
| `BLOCKED_PROVIDER` | A provider sandbox or delivery recipient requires explicit authorization. |
| `EXCLUDED` | The feature is visibly unavailable for this release candidate. |
| `INVALIDATED` | Useful earlier evidence exists, but it is not bound to the candidate revision or artifact. |
| `NOT_RUN` | No acceptable execution evidence exists yet. |

A status is evidence only for its named row. Local source tests do not prove a built
artifact, local fake alerts do not prove operator receipt, and local email capture does
not prove external delivery. A self-signed loopback TLS rehearsal does not prove an
external ingress, managed certificate, DNS, or deployed-environment configuration.

## Historical Preparation Snapshot

The dated pre-release preparation evidence below is retained as a historical baseline,
not a frozen release candidate. Record current candidate evidence in #271 and its PR
receipts instead of treating this table as a moving status dashboard:

| Evidence | Identity | Result | Boundary |
| --- | --- | --- | --- |
| Complete local suite | `e6bc24b6a0df4b585f3ed797e90ec22435619872` | 1,985 passed, 21 skipped, 0 failed/errors, including 73 Playwright tests | Source tree before this document; not artifact or deployment evidence |
| Local report | `test-artifacts/local-validation/20260915T183125.899040Z-48293-4928b80a/report.json` | `tracked_tree_clean=true` | Local machine artifact, not GitHub-attested CI |
| Merged source containing that tree | `924fc0351166bebb9870fed0e44b737ff7234bb5` | PR #334 merged after GitHub reported `MERGEABLE` and `CLEAN` | Documentation merge SHA differs from the tested PR head |
| Production image exercise | `cb6a8fdb393f954a9ce2a358f5a1bc351f49d8d5` / `sha256:fb00fdfbac4306eb736058572fed555efb9bc7a482d29532633972ec34b62416` | Local artifact checks passed | `INVALIDATED` for a later release candidate |
| PostgreSQL acceptance | See #253 and #265 receipts | Owned local PostgreSQL 16 exercises passed | `INVALIDATED` for a later release candidate |
| Redis acceptance | See #261 and #266 receipts | Owned local Redis 7 exercises passed | `INVALIDATED` for a later release candidate |
| Recovery exercise | See #268 receipt | Encrypted isolated fictional SQLite restore passed | Not PostgreSQL backup, retention, PITR, or cutover evidence |

When release work starts, record the candidate source SHA, image digest, migration
revision, configuration fingerprint, database/Redis versions, target identifier, and
operator in #271. Any source or configuration change invalidates affected rows.

## Owner Decisions

| Decision | Current status | Required recorded answer |
| --- | --- | --- |
| Church/Basketball business workflow | `PASS` | Accepted in #289 on 2026-09-15 for merged main `cb77a9f`; the recorded limitations remain in force. |
| Pilot cohort | `BLOCKED_OWNER` | Name organizations, participant count, invitation owner, and whether all data is fictional. |
| Region and data handling | `BLOCKED_OWNER` | Name hosting region, data classification, retention basis, and approved access roles. |
| Support | `BLOCKED_OWNER` | Name support owner, hours, contact path, severity rules, and response expectations. |
| Release operations | `BLOCKED_OWNER` | Name deploy operator, incident owner, rollback authority, and final decision maker. |
| Recovery policy | `BLOCKED_OWNER` | Approve RPO, RTO, backup retention, legal hold, key custody, and deletion policy. |
| Capacity target | `BLOCKED_OWNER` | Approve target hardware, representative data size, traffic mix, duration, latency/error limits, and solver bounds. |
| Pilot exit | `BLOCKED_OWNER` | Approve pilot duration, success metrics, stop conditions, accepted risks, and go/no-go date. |

Do not invent defaults for these decisions. A suggested workload in an issue is not an
approved capacity promise.

## Candidate Scope

| Surface | Candidate disposition | Exit evidence |
| --- | --- | --- |
| Web and API scheduling | In scope; #289 accepted | Built-artifact Church and Basketball journeys on the frozen candidate |
| In-app notifications and calendar export | In scope | Built-artifact publish/change/reminder and calendar checks |
| Invitation and password-reset delivery | `BLOCKED_PROVIDER` | Authorized external recipient receives usable links; local capture remains development evidence |
| Billing | `EXCLUDED` | `BILLING_ENABLED=false`; routes and UI remain unavailable |
| Paid SMS | `EXCLUDED` | `SMS_ENABLED=false`; routes and UI remain unavailable |
| Native mobile release | `EXCLUDED` unless separately authorized | #191 device, signing, store, and backend evidence |
| Public/general availability | `EXCLUDED` until pilot exit | Owner go/no-go after stable invited pilot evidence |

## Release Matrix

| Row | Current status | Required candidate evidence | Owner issue |
| --- | --- | --- | --- |
| Business acceptance | `PASS` | Owner accepted #289 and its limitations on 2026-09-15 | #289 |
| Source validation and local review | `INVALIDATED` after the next source change | `make test-all`, applicable mobile checks, local review, and exact head/base SHAs | #271 |
| Immutable runtime artifact | `INVALIDATED` | Same-SHA image digest, migration revision, package/assets/probes, nonroot runtime, and retained report | #265 |
| PostgreSQL and Redis | `INVALIDATED` | Same-candidate migration, tenant, concurrency, notification, and shared-state exercises | #253, #261, #266 |
| Security scan | `INVALIDATED` | Same-SHA source/image scan, SBOM/license review, exceptions, and retained scanner provenance | #269 |
| Production configuration | `BLOCKED_TARGET` | HTTPS origins, secure cookies, trusted proxy, private stores, secrets, and all test/debug bypasses disabled | #265, #284 |
| Built-artifact business journeys | `NOT_RUN` | Both complete weekly playbooks, disruptions, local state, and calendar against the candidate artifact | #271 |
| Capacity/load | `NOT_RUN` | Owner-approved workload on named hardware; raw results and pass/fail against agreed thresholds | #271 |
| Alert delivery | `BLOCKED_TARGET` | Controlled failure reaches named operator with environment, release SHA, dependency, and runbook | #267 |
| Backup, retention, and restore | `BLOCKED_OWNER` | Scheduled PostgreSQL backup, approved retention/key custody, isolated restore, measured RPO/RTO, and operator acknowledgement | #268 |
| Rollback | `BLOCKED_TARGET` | Same target rolls back to a compatible prior image without destructive automatic downgrade or data loss | #265, #268, #284 |
| External email | `BLOCKED_PROVIDER` | Authorized invitation/reset/change/reminder delivery and link use; failure remains visible | #271 |
| Optional billing/SMS | `EXCLUDED` | Disabled-state regression; separate #270 sandbox and owner approval before inclusion | #270 |
| Optional native | `EXCLUDED` | Separate #191 physical-device, signed-artifact, backend, and store evidence before inclusion | #191 |
| Invited pilot | `BLOCKED_OWNER` | Dated observations, support incidents, metrics, accepted risks, and stable exit period | #271 |
| Release decision | `BLOCKED_OWNER` | Release notes, residual-risk register, rollback owner, and explicit owner go/no-go | #271 |

## Execution Order

1. Preserve the accepted #289 limitations and record every remaining owner decision above.
2. Freeze one candidate source revision. Build one immutable artifact and record its
   image digest, migration revision, configuration fingerprint, and toolchain.
3. Run all applicable local source, PostgreSQL, Redis, artifact, security, recovery,
   mobile, documentation, and screenshot checks against that revision.
4. Start the same artifact on an explicitly authorized disposable release-equivalent
   target with billing and paid SMS disabled.
5. Run both built-artifact domain journeys and the owner-approved load profile.
6. Trigger and acknowledge alert, backup/restore, and rollback drills. Preserve the
   original target and data until the operator accepts the result.
7. Run only explicitly authorized external email or optional provider/device checks.
8. Publish release notes and the residual-risk register, then operate the invited pilot.
9. Ask the named owner for go/no-go. A failed or invalidated required row is a no-go.

## Local Commands

Run commands only from a clean committed candidate. Each generated report must name the
same source revision; keep API and browser tiers in separate processes as implemented by
`make test-all`.

```bash
make test-all
make test-postgres
make test-redis
make test-artifact
make test-staging  # only with the required STAGING_* authorization variables
make test-security
make test-recovery
make test-mobile
make test-mobile-generated
make test-docs
make validate-screenshots
make test-load
```

`make test-load` runs the checked-in bounded local-smoke profile against an owned source
server, verifies the exact commit through `X-Release-SHA`, and retains raw request results.
That run is `PASS_LOCAL` engineering evidence only. It is not the sustained,
representative, owner-approved load evidence required by #271. Release-candidate capacity
requires a separately approved profile and target, an immutable artifact, exact target SHA,
and explicit remote authorization. The legacy `make test-performance` endpoint assertions
remain compatibility checks and do not satisfy the capacity row.

`make test-staging` is separately opt-in and refuses remote traffic unless the operator
supplies an HTTPS origin, exact deployed SHA, specific approval receipt and explicit
remote authorization. It runs the pluggable Church/Basketball API workflows and verifies
TLS, readiness, browser cookies and security headers. A passing report covers only those
rows for the observed SHA; it does not prove deployment provenance, rollback, alert
receipt, recovery/retention, capacity, external delivery, pilot operation or go/no-go.

## Decision Rules

- Any unmet core row, mismatched source/image/configuration identity, tenant leak,
  overfilled role, lost future schedule, failed restore, failed rollback, or unreceived
  required alert is a no-go.
- Never average away a failed drill. Attach the reproduction and keep the row open.
- A new source, image, migration, or relevant configuration invalidates affected evidence.
- Disabled billing, SMS, or native scope must remain visibly unavailable; exclusion is
  not acceptance of that feature.
- Reviewer agents do not merge. Builder agents merge only after local evidence is
  recorded and GitHub reports the PR mergeable.
- GitHub Actions does not run validation, and Ollama is not a code-review provider.
