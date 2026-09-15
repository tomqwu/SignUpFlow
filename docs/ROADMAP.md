# Production Roadmap

Current policy, 2026-09-14. The owner directs: **no CI checks; everything is
validated locally**. This supersedes every older hosted-test, hosted-review,
static-CI, migration-CI and required-status proposal, including historical issue
comments. Ollama is not a code-review provider.

## Source of Truth

Track scope and progress in [roadmap issue #252](https://github.com/tomqwu/SignUpFlow/issues/252).
Use [TESTING.md](TESTING.md) for local commands and [local review](ai-pr-review.md)
for review evidence. Old specifications describe proposals, not automatically
authorized work. Check current code and issue status before implementation.

## Delivery Order

| Phase | Work | Exit evidence |
| --- | --- | --- |
| A: Security | Tenant isolation, membership, billing/SMS authorization, safe configuration, browser protections | Local negative-path tests and reviewed fixes; no unresolved core security blockers |
| B: Scheduling and reliability | Persisted constraints, atomic claims, PostgreSQL parity, reset delivery, reliable notifications | Local API/browser church and basketball playbooks plus PostgreSQL concurrency and delivery evidence |
| C: Release artifact and operations | Reproducible image, private data stores, migration control, monitoring, backup/restore, scans | Locally produced artifact digest and recorded release drills |
| D: Invited pilot | Approved release scope, real workflow acceptance, measured load, support/rollback ownership | Local operator validation records, accepted risks and owner go/no-go |
| E: Optional releases | Paid billing/SMS and native mobile | Separate sandbox/provider/device evidence and explicit enablement approval |

Run every automated validation locally, including lint, type checks, unit/API/
CLI/integration/web/contract/Playwright tests, mobile analysis/tests/builds,
migrations, PostgreSQL races, dependency scans and artifact checks. Operator
scripts also run locally; interacting with staging, providers or physical devices
requires their explicit authorized scope. Do not replace real device or release
evidence with a local mock. Do not deploy or enable providers from a roadmap alone.

## Progress Reconciliation

- #281: `make test` now aliases the complete seven-tier suite, Playwright is
  locked, provider credentials are stripped from test processes, and browser
  contexts fail on JavaScript errors. Broader legacy/manifest work remains open.
- #288: billing and paid SMS now default off behind shared API/web feature gates;
  the scheduling flow and both domain playbooks run without provider credentials.
- #279/#289 FLOW-1: the machine-readable playbook coverage manifest now binds
  BO-01..12, CH-01..08, BB-01..08, every scheduling qualification, evidence tier,
  and partial/blocked status; pytest rejects omitted bundled roles or scenarios.
  BO-01 through BO-07 are automated: each domain browser flow creates its organization
  and first admin through normal signup, starts from the empty onboarding state,
  invites and accepts fourteen baseline members plus a qualified replacement with
  explicit qualifications, and verifies the admin-only qualification editor at 360px
  and 1440px. A separate role-parameterized browser flow records one-off and recurring
  unavailability for every qualification, rejects peer edits without mutation, and
  proves solver exclusion across twelve API-seeded events. The primary admin journey
  creates all twelve six-week events through the multi-role browser form, solves and
  reviews all 84 slots, and proves exact qualified coverage, non-overlap, and balanced
  loads. API/web publication regressions reject incomplete and stale candidates. A
  recurrence-scope browser drill moves one occurrence, cancels another, preserves its
  sibling, and distinguishes whole-series deletion. The published-roster journey proves
  that an accepted commitment becomes unanswered after its event time changes.
- #255: atomic organization/first-admin bootstrap, invitation-only later
  membership, shared role normalization, request-override rejection, and
  concurrent acceptance protection are implemented. An owned PostgreSQL 16 run
  proves one bootstrap owner, one invitation winner, and inactive API/browser
  session rejection. Cancellation preserves an authenticated administrator restore
  path while hiding the organization from normal listings.
- #253: organization authorization and audit fixes merged in PR #272; retain
  remaining PostgreSQL cascade/release evidence, not the old unmerged-PR blocker.
- #254: the scheduling API now has an executable route policy, real-JWT
  two-tenant event/conflict/availability/solution regressions, and pre-serialization
  person/team export filtering. Local full-suite and PR evidence are required
  before treating this source milestone as merged.
- #263: assignment roles persist in API and CLI output; saved assignment caps,
  minimum gaps, and cooldown preferences now validate and execute in API solves.
  Broader team/league eligibility policy remains separate product scope.
- #287: assignment allocation is separate from persisted member response truth;
  new and historical ambiguous assignments remain unanswered, member actions are
  revision-aware and atomic with audit, unchanged publication carries proven
  responses, material changes reset them, and coordinator/member browser states
  run through both domain playbooks at 360px and 1440px.
- #264: open-shift claims, swap covers/denials, and coordinator roster edits now
  share one organization-scoped transaction boundary. Synchronized independent
  connections prove one winner for capacity, overlap, and swap races on SQLite
  and an owned local PostgreSQL 16 database; qualification, availability,
  idempotency, audit rollback, and unpublished history are covered locally.
- #286/#289 FLOW-3: generated solutions persist an immutable full solve scope,
  including unfilled events. Publication and rollback revalidate current events,
  qualifications, availability, exact role coverage, and the existing future
  horizon under the shared organization lock. Incomplete, stale, legacy, or
  narrower candidates leave the prior roster active; audit and local notification
  intent commit with the roster switch. Church/Basketball shortage repair and the
  cancellation/week-seven rollover contract have local API evidence. BO-08 also
  runs the week-seven add, shifted solve/review, and publish operations in both
  domain browsers at phone and desktop widths while independently preserving
  completed history and every original future event.
- #262/#266/#289 BO-09: a provider-free local RFC 822 sink now carries actual
  invitation, password-recovery, assignment, event-change, and reminder content.
  Durable unique delivery keys prevent repeated publish/change/reminder operations
  from sending the same intent twice; disabled delivery remains pending and is labeled
  disabled rather than sent. Church and Basketball critical-role members execute the
  full captured-link and in-app reconciliation flow at 360px and 1440px. External
  inbox placement, provider webhooks, multi-worker queue recovery, and approved
  production delivery remain later acceptance under #262/#266.
- #254/#285/#289 BO-10: personal calendar download and token feeds now share one
  current-assignment policy: draft, declined, deleted, and foreign-tenant child rows
  stay out. UTC storage converts to the member's resolvable IANA rendering zone,
  including DST transitions, while a moved assignment retains one stable UID. Church
  and Basketball publish, move, refresh, and cancel the calendar entry at 360px and
  1440px. External calendar-client polling behavior remains device/provider acceptance.
- #255/#261/#262/#289 BO-11: Church and Basketball administrators and volunteers
  now run logout/login, self-service password change, copied-session revocation, and
  real captured reset-link recovery at 360px and 1440px. Old passwords, replayed links,
  expired tokens, and short API reset passwords fail without consuming a usable token.
  External mailbox/provider delivery and distributed abuse controls remain later work.
- #254/#255/#285/#289 BO-12: every API access token and browser session is bound to
  the active account tenant. Church and Basketball coexist in one local server; each
  administrator sees only its own directory, and every declared scheduling qualification
  runs as a volunteer at 360px and 1440px. Missing/mismatched tenant claims, inactive
  memberships, admin-surface access, invitations, publication, foreign-person reads, and
  peer availability writes fail locally. Deployment and infrastructure isolation remain
  separate release evidence.
- #260: `make test-postgres` owns a loopback-only, tmpfs PostgreSQL 16 container per
  invocation and refuses unverified cleanup. Alembic alone creates fresh and historical
  schemas; startup rejects a stale non-SQLite migration head. Local acceptance covers
  bootstrap, invitation, inactive/cancelled membership, claim, and publication races,
  and records server version, source SHA, and JUnit counts. Managed infrastructure,
  backup/restore, and complete release migration/cascade parity remain under #253/#268.
- #261: every unsafe browser request under `/auth/`, `/a/`, and `/v/` now requires an
  exact allowed origin plus a signed double-submit token. Forms and HTMX share the same
  middleware, rejected requests cannot mutate state, and browser authentication routes
  use the existing per-operation rate limits. Forwarded client addresses affect limits
  and audit logs only from configured proxy peers; loopback has no production bypass.
  Distributed limiter storage, multi-worker quotas and outage behavior, and deployed
  proxy/TLS acceptance remain later work in the same issue.
- #258: production startup now rejects known sample signing keys, SQLite or sample
  database settings, unsafe origins/CORS, test and debug bypasses, malformed proxy/
  lifetime/boolean settings, and incoherent enabled-provider configuration before
  database initialization. JWT and browser cookies share one lifetime; Compose passes
  canonical settings, defaults providers off, and the image enforces one worker until
  #261/#266 add shared-state acceptance. This is local configuration evidence, not a
  deployed artifact, TLS/proxy, provider, backup, or rollback result.
- #265: the production image no longer migrates from each replica or copies builder
  executables into the runtime. Compose runs one migration job, keeps PostgreSQL and
  authenticated Redis private, and starts non-root read-only single-worker replicas
  without source mounts. The opt-in `make test-artifact` harness binds a fresh image to
  the committed SHA, scans its contents/history, proves unmigrated startup fails without
  schema mutation, starts two replicas, runs a provider-free Basketball publish/export,
  verifies SIGTERM, and records immutable image identity. An authorized staging target,
  managed-service/TLS evidence, and release-owner approval remain outside local proof.
- #267: `/health` is dependency-free process liveness while `/ready` performs one
  context-managed database probe and returns only a generic failure. Production logs
  are structured stdout records correlated to the required release SHA and redact
  credential-shaped values. A configured Sentry sink initializes with PII/tracing off;
  invalid initialization fails visibly without exposing its DSN. Bounded local rules
  and fake sinks prove one trigger plus recovery for readiness, notification queue, and
  backup freshness. Real signal producers beyond readiness, external operator receipt,
  retention, thresholds measured under staging load, and escalation ownership remain.
- #268: the supported local SQLite recovery tool uses the backup API to retain committed
  WAL data, requires a marker-bound workspace plus separate owner-only key, emits an
  authenticated AES-GCM bundle with plaintext/ciphertext checksums, and restores only to
  a new isolated destination after integrity, foreign-key, and Alembic-head verification.
  `make test-recovery` measures a fictional restore and re-runs Church/Basketball login,
  tenant, publication/response, inbox, and completed-notification replay checks. Scheduled
  PostgreSQL/PITR, off-site storage, production key custody, backup freshness delivery,
  approved RPO/RTO, retention/holds/purge, and cutover remain unproven.
- #269: local release security validation uses an immutable Trivy container without a
  host install or Docker-socket mount. It hashes the Python, Flutter, Ruby/CocoaPods,
  Gradle, vendored JavaScript, image, and Pages inputs; scans a committed archive and
  same-SHA retained image; writes source/image CycloneDX and license inventory; and
  rejects missing advisory data, undetected harmless fixtures, expired exceptions, and
  unaccepted image findings. The release image uses a digest-pinned upgraded Alpine base,
  hash-locked application environment, no runtime package manager/build toolchain, direct
  PyJWT, and remediated Python and Fastlane/Rubyzip locks. This is exact local artifact
  evidence, not a hosted check, deployment scan, native artifact scan, or production risk
  acceptance; rerun it for each candidate because advisory data changes.
- #259: repurpose the obsolete AI/CI gate ticket as local validation and evidence
  hygiene. No workflow, secret, provider or required status is needed for review.
- #191: the Dart client is regenerated from the current OpenAPI snapshot and
  Flutter signup uses atomic bootstrap. Native build/device acceptance remains.
- ICS solution export remains explicitly unsupported with `501`; calendar ICS
  export is separate. Do not represent unsupported solution ICS as shipped.

These are verified partial milestones, not blanket closure of their tickets.
Retire old effort totals until remaining acceptance criteria are re-estimated.

## Merge and Release

1. Complete local code review; record reviewed head/base SHAs and resolve findings.
2. Run applicable local checks and all test tiers; record commands, environment,
   counts, skips and limitations against the pushed revision.
3. Merge only when that evidence is complete and GitHub reports mergeable.
   Reviewer agents never merge. Never fabricate CI statuses or bypass protection.
4. Verify the merge and update local main. Keep deployed artifact/device evidence
   separate from source test evidence and obtain release-owner approval.

GitHub hosts source, issues, PRs and the static Pages publication. It does not
execute or attest validation. No required CI checks are part of this roadmap.

## Documentation Maintenance

Use this roadmap instead of stale completion percentages, unavailable guides,
old CI prerequisites or unchecked historical feature plans. Security and
operations documentation still needs the broader reconciliation identified in
the audit; do not interpret historical readiness claims as production sign-off.
