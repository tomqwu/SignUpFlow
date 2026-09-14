# Documentation Reconciliation

Audit date: 2026-09-14. Scope: local-only review and all validation, with no CI checks, test commands
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
separate from account access. Organization bootstrap and all twelve baseline events run
through normal browser forms; only the role-by-role availability drill uses API-seeded
members and events, and the guide labels that boundary explicitly.
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
The event and recurrence guides now distinguish one-occurrence move/cancel from
whole-series deletion. Browser evidence covers both domains at 360px and 1440px and
proves that a changed accepted commitment returns to unanswered. Advanced recurrence
rule editing, re-materialization, timezone, and DST behavior remain separate gaps.
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
The focused BO-08 browser acceptance now adds both week-seven sessions, solves,
reviews, and publishes the shifted horizon for Church and Basketball at 360px and
1440px. Its setup is explicitly labeled API-seeded; the oracle preserves completed
history and every original future event instead of crediting fixture construction as
a browser action. The flow uses existing event, solver, and solution-review surfaces,
so it does not invalidate the maintained walkthrough screenshots.
The maintained local-mail guide and BO-09 manifest row now match the executable
provider-free workflow. Church and Basketball each run invitation acceptance, password
recovery, publication, event change, reminder delivery, and member-inbox reconciliation
at both browser widths. The application no longer labels disabled delivery as sent, and
template links target real member pages. These changes affect transient status copy and
email content, not the README walkthrough layout, so existing screenshots remain
applicable. External provider delivery remains unverified and explicitly deferred.
The maintained README, roadmap, testing guide, and both domain playbooks now describe
BO-10's executable calendar contract. Personal download and token feeds share current,
non-declined, tenant-scoped rows; moved entries retain one UID; cancellations disappear;
and `America/Toronto` output crosses DST correctly. The browser case runs both domains
at phone and desktop widths and saves a current profile/calendar screenshot in pytest's
owned temporary directory. This changes generated ICS rather than the walkthrough UI,
so the existing committed README screenshots remain applicable.
The maintained account-recovery contract now matches BO-11. Both access levels in both
domains run logout/login, password change, copied-session invalidation, captured-link
reset, old-password rejection, and replay rejection at phone and desktop widths. API
regressions cover expiry and reject short reset passwords before consuming the token.
The browser run saves administrator/member recovery screens in pytest's temporary
directory. Existing committed walkthrough screenshots remain applicable because this
package changes validation and acceptance coverage, not page layout.
The maintained [API authorization matrix](API_AUTHORIZATION.md) now binds every
mounted operation to an executable policy and records scheduling tenant/export
semantics. This package changes API authorization and generated contracts, not
the web layout; the README walkthrough screenshots therefore remain applicable
and were not recaptured as new visual evidence.
BO-12 now adds active-tenant binding to every API access token and browser session.
Church and Basketball run together in one local application; their administrator
directories remain isolated, and each declared scheduling qualification proves volunteer
boundaries at phone and desktop widths. The browser run saves new tenant-directory and
every-role screenshots in pytest's temporary directory. The committed walkthrough images
remain current because the package changes authentication and acceptance coverage, not
the rendered pages or their layout.
The maintained [scheduling constraint contract](SCHEDULING_CONSTRAINTS.md) now
lists the three executable REST rule mappings, their CLI equivalents, validation
failures, built-in invariants, and unsupported policy. The constraints editor now
offers only those rule names; it is not part of the README screenshot walkthrough,
so the existing walkthrough image set remains applicable.
The maintained README, plugin guide, coverage manifest, and both domain playbooks now
describe CH-D03 and BB-D03 as fixture-driven browser operations. Church adds a holiday
service while preserving prior staffing and acceptance; Basketball postpones one game,
requires a fresh response, and keeps one logical calendar UID across publication rows.
Both run at phone and desktop widths and save administrator/member schedule-change
screenshots in pytest's temporary directory. They reuse the maintained event, comparison,
solution, inbox, schedule, and calendar surfaces, so the committed walkthrough images
remain applicable. Ministry approval and venue/opponent coordination remain human work.
The screenshot evidence package supersedes all earlier statements that the May walkthrough
images remained current. `make capture-screenshots` now reproduces 44 asserted Church and
Basketball states at phone and desktop widths from a fixed local clock and synthetic data.
The manifest binds each image to its captured source commit, browser, fixture, actor,
scenario, caption, viewport, image hash, and relevant UI hashes; local unit validation
rejects missing or stale evidence. The former ten README images are explicitly retired
under `docs/screenshots/legacy/`, and README now shows both complete operating scenarios.
The maintained README, testing guide, and documentation index now link the machine-checked
web journey matrix. It covers every current HTML/HTMX route and Jinja template with named
happy, error, and permission evidence or an explicit product limitation. Shared browser
recovery now renders validation fragments, preserves user input across transport failure,
prevents rapid duplicate submission, navigates expired HTMX sessions, and refetches
solution state after SSE reconnect. Phone-width long-label, zoom, keyboard, JavaScript-error,
and changed-database recovery cases run in local Chromium; cross-browser and production
network claims remain outside this evidence.
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
