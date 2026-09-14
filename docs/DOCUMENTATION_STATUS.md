# Documentation Reconciliation

Audit date: 2026-09-13. Scope: local-only review and all validation, with no CI checks, test commands
and counts, merge instructions, related specification proposals, documentation
navigation, and router-state claims in active developer entry points.

## Current Sources

- [Testing and merge policy](TESTING.md): current commands and validation boundaries.
- [Repository overview](../README.md) and [contributor workflow](../CONTRIBUTING.md).
- [Agent baseline](../AGENTS.md), [Claude guidance](../CLAUDE.md), and
  [Copilot guidance](../.github/copilot-instructions.md).
- [Local code review](ai-pr-review.md), [playbooks](playbooks/README.md), and
  [mobile testing](../mobile/README.md).

Commands and hosted check behavior were compared with the Makefile and workflow
files, and router claims with `api/main.py`. Removed the README's fixed 413-test
total, obsolete tier counts/timings, and false unregistered-router statements.
Playwright is now locked, `make test` aliases the seven-tier suite, and maintained
guides describe billing/paid SMS as default-off deferred integrations rather than
active setup requirements.
The maintained playbook guides now link a validated machine-readable coverage
manifest; its partial and blocked rows prevent baseline tests from being described
as complete role-by-role business acceptance.
The Church and Basketball guides now match the browser runner: all fourteen members
are invited and accepted through the normal UI with scheduling qualifications kept
separate from account access. Organization bootstrap and repeated-event setup remain
explicit API prerequisites rather than hidden browser-coverage claims.
The maintained API, mobile, agent, and roadmap entry points now describe atomic
organization/first-admin bootstrap, invitation-only membership for existing
organizations, one permission role plus scheduling qualifications, and the
regenerated Dart client. `API_README.md` is explicitly historical.
The maintained assignment-response contract now separates roster allocation from
member acknowledgement, documents revision and migration behavior, and aligns the
coordinator/member surfaces with the Church and Basketball browser playbooks. The
affected dashboard, unanswered schedule, and accepted-detail README screenshots
were recaptured from the 360px Church browser case; the other walkthrough screens
were unaffected by this package.
The maintained allocation transaction contract now documents the shared lock,
eligibility, live-capacity, idempotency, rollback, and disposable PostgreSQL test
boundaries for open shifts, swap coverage/denial, and coordinator roster edits.
This package changes behavior and conflict copy without changing page layout, so
the README walkthrough screenshots remain applicable.
The maintained [schedule publication contract](SCHEDULE_PUBLICATION.md) now records
the strict full-horizon/no-override policy, immutable solve scope, legacy
regeneration, response carry-forward, transaction rollback, explicit cancellation,
and week-seven rollover. The README and playbook coverage no longer claim that an
incomplete roster can publish or that rollover is blocked. Successful publication
keeps the same layout shown in the walkthrough; rejection adds text to the existing
alert component, so the current screenshots remain applicable to this package.
The maintained [API authorization matrix](API_AUTHORIZATION.md) now binds every
mounted operation to an executable policy and records scheduling tenant/export
semantics. This package changes API authorization and generated contracts, not
the web layout; the README walkthrough screenshots therefore remain applicable
and were not recaptured as new visual evidence.
The maintained [scheduling constraint contract](SCHEDULING_CONSTRAINTS.md) now
lists the three executable REST rule mappings, their CLI equivalents, validation
failures, built-in invariants, and unsupported policy. The constraints editor now
offers only those rule names; it is not part of the README screenshot walkthrough,
so the existing walkthrough image set remains applicable.
Aligned contributor commit/merge rules with the agent baseline. The owner's latest
clarification supersedes the previous Ollama review setup: code review runs
locally, no CI checks remain, and Ollama must not review PRs. The later clarification
also retires hosted static analysis and migration checks. The production roadmap
and open issues follow [the current roadmap policy](ROADMAP.md).

## Historical Material

Retain original reports; do not replace old results with new numbers. Historical
notices now cover the old testing strategy, performance guide, comprehensive
suite guide, summary, action plan, quick start, workspace organization, launch
roadmap, next steps, and dated playbook validation. Current guidance takes
precedence over their old commands, CI proposals, and timing estimates.

Email, i18n, and infrastructure specifications that proposed hosted test gates
now carry explicit policy-supersession notices. Their remaining requirements
are specifications, not evidence of implemented behavior. The deployment
guide's Actions example is explicitly labeled an unimplemented historical
proposal; it is not a deployed pipeline or authorization to deploy.

The documentation index now starts with verified current entry points. Its
2025 catalog is labeled historical, and 33 nonexistent link targets are rendered
as unavailable historical references rather than broken navigation.

## Verification Boundaries

Searched tracked Markdown across root docs, developer/agent guidance, mobile
docs, and feature specifications for hosted-test claims, old check names,
static test totals, and unregistered-router statements. Remaining old testing
proposals are labeled historical or superseded. Checked relative links in the
current guide, index, contributor guide, and agent entry points; checked newly
added links in changed files. Existing external URLs and unrelated legacy report
links were not certified as live.

This is not a fresh production, security, deployment, or provider-delivery audit.
Old feature-completion and security reports do not become current proof merely
because their testing policy has been reconciled. Preserve the operational
limitations listed in the playbook guide. Record actual test outcomes and the
source SHA in the reconciliation PR rather than maintaining another live count.
