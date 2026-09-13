# Local Code Review

The owner's current policy is local code review and local test execution.
No CI checks: GitHub Actions does not perform review, tests, static analysis,
or migration validation. Ollama is
not a code-review provider. Keep application voice-provider configuration
separate; this policy does not change application configuration or credentials.

This document retains its path for existing links. It supersedes the former
Ollama PR-review setup; do not recreate that workflow or require its retired
`codex-pr-review-gate` status. Do not replace it with another hosted AI provider.

## Local Review Checklist

1. Record the PR head and base SHAs. Inspect the complete diff locally, along
   with affected source, tests, workflow definitions, and agent instructions.
2. Check correctness, security, organization isolation, authorization, API
   contracts, migrations, user workflows, and negative-path test coverage.
3. Report findings with severity and file/line references. Fix blocking issues
   and review the final diff again after changes. Do not claim independent
   review when the builder performed the review itself.
4. Run `make test-all` locally; run `make test-mobile` for mobile changes.
   Record actual commands, results, skips, and limitations for the pushed head.
   See [testing setup and scope](TESTING.md). All validation, including static analysis and migrations, runs locally.
5. Record the local review outcome and reviewed head/base SHAs in the PR.
   Invalidate stale evidence after source changes and recheck affected behavior.
6. Merge only after successful local tests and completed review are recorded,
   all applicable local checks pass, blocking findings are resolved, and GitHub reports
   mergeable. Honor any required GitHub reviews. Never bypass a failed check.

Reviewer agents must not merge. Builder agents may merge only after the above
conditions hold. Local results are procedural evidence, not GitHub-attested
execution or proof of production readiness.

## GitHub Configuration

No CI checks or required CI statuses. Backend CI, mobile analysis, Ollama review
and the legacy E2E workflow are retired. Only the Pages publishing workflow
remains; it is not a validation or merge gate. Do not fabricate GitHub checks
from local reports. Keep local review and test results bound to head/base SHAs.

Local policy regression tests live in
`tests/unit/test_local_validation_policy.py` and run through `make test-all`.
These inventory guards are not a security boundary against arbitrary workflow
changes; inspect workflow commands during local review.

Main protection returned 404 and rulesets were empty when checked on 2026-09-13.
No protection settings or credentials are changed by this policy. If stale
required checks are found later, report the settings mismatch and obtain a
policy-aligned administrative correction; never bypass it.
