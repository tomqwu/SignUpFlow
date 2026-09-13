# Local Code Review

The owner's current policy is local code review and local test execution.
GitHub Actions does not perform AI review or execute test suites. Ollama is
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
   See [testing setup and scope](TESTING.md). Green hosted CI is not test evidence.
5. Record the local review outcome and reviewed head/base SHAs in the PR.
   Invalidate stale evidence after source changes and recheck affected behavior.
6. Merge only after successful local tests and completed review are recorded,
   hosted static checks pass, blocking findings are resolved, and GitHub reports
   mergeable. Honor any required GitHub reviews. Never bypass a failed check.

Reviewer agents must not merge. Builder agents may merge only after the above
conditions hold. Local results are procedural evidence, not GitHub-attested
execution or proof of production readiness.

## Hosted Configuration

Keep `Lint and type-check` and path-scoped `Flutter analyze`. The backend job
includes formatting, lint, scoped blocking mypy, advisory whole-API mypy, and
PostgreSQL migration validation. The Pages publishing workflow is unchanged.

The Ollama review and legacy Playwright E2E workflows were disabled in GitHub
on 2026-09-13. The review workflow and its provider-specific tests are removed
from source. Local policy regression tests live in
`tests/unit/test_local_validation_policy.py` and run through `make test-all`.
These inventory checks are regression guards, not a security boundary against
arbitrary workflow changes; inspect workflow commands during local review.

At removal, the main protection API returned 404 (branch not protected), and
the rulesets API returned an empty array. No protection settings were changed.
Recheck live settings before changing enforcement later. Do not require retired
AI or hosted-test statuses. Existing GitHub secrets are not read or deleted by
this change; the remaining workflows do not reference the Ollama credential.
