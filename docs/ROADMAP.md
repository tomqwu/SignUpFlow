# Production Roadmap

Current policy, 2026-09-13. The owner directs: **no CI checks; everything is
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
  BO-02 is automated: each domain browser flow invites and accepts fourteen members
  with explicit qualifications and verifies the admin-only qualification editor at
  360px and 1440px. Full browser bootstrap remains partial in BO-01.
- #255: atomic organization/first-admin bootstrap, invitation-only later
  membership, shared role normalization, request-override rejection, and
  concurrent acceptance protection are implemented with local API/integration
  evidence. PostgreSQL migration/concurrency acceptance remains under #253/#260.
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
- #260: per-run SQLite database isolation exists. PostgreSQL business/concurrency
  and migration parity remain unverified release work; run that validation locally.
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
