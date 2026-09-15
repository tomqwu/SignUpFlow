# Documentation Reconciliation

Audit date: 2026-09-15. Scope: local-only review and all validation, with no CI checks, test commands
and counts, merge instructions, related specification proposals, documentation
navigation, and router-state claims in active developer entry points.

## Current Sources

- [Testing and merge policy](TESTING.md): current commands and validation boundaries.
- [Local validation inventory](../tests/local_validation_manifest.json): machine-checked
  default and opt-in test ownership used to produce SHA-bound local reports.
- [Tool safety ledger](TOOLS.md): current supported, delegated, and retired script contracts.
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
The retained Stripe plan is now explicitly historical and no longer presents its old
prices or launch sequence as current decisions. The mounted, default-off billing surface
requires authenticated tenant administrators; checkout return verifies provider customer
and organization ownership without changing entitlement, and payment-method attachment
checks ownership before provider mutation. The default-off Stripe callback is mounted
behind `BILLING_ENABLED`, fails closed without a signing secret, and accepts no
cross-tenant identity inference. Durable event receipts, monotonic subscription/invoice
transitions, uncertain checkout reconciliation, trial expiry, and truthful HTML/text
invoice exports are covered with provider fakes. Pricing, refunds, quotas, provider
sandbox delivery, support ownership, and live enablement remain the separately
authorized #270.4 boundary.
The mounted, default-off SMS surface now uses canonical string identifiers and checks
tenant ownership plus assignment/event/person consistency before queue or provider work.
Twilio callbacks require signatures over the configured external URLs, process incoming
message IDs once, and reject delivery-state regressions. OpenAPI and the generated Dart
request models carry the corrected string-ID contract. Provider delivery remains deferred
to #270. These provider-safety packages change no Church or Basketball template or layout,
so the committed walkthrough screenshots remain current and were not recaptured.
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
The older `API.md` and `API_QUICKSTART.md` Python-library examples are now also
explicitly historical because they import the removed `roster_cli` package. Current
REST discovery uses the live `/docs` schema and `API_AUTHORIZATION.md`; current CLI
examples live in the root README. The mobile smoke guide now matches create/resend
invitation delivery: owned local mail capture is available, external provider receipt
requires authorization, and the response-token fallback proves only deep-link plumbing.
The older date/time, Docker-development, and YAML-environment guides are also
explicitly historical. They reference removed source paths or a profile loader the
application does not use. Current startup follows the root README, while effective
production settings and fail-closed validation live in `PRODUCTION_CONFIGURATION.md`.
The maintained API authorization matrix now records the complete organization
lifecycle actor contract. Local real-JWT tests cover anonymous, owning-member,
owning-admin, and foreign-admin reads and mutations plus transactional audit rollback.
The owned PostgreSQL drill deletes a representative scheduling/delivery child graph,
retains denormalized deletion audit evidence, and proves a foreign tenant survives.
Cancellation remains reversible; no automated retention purge or production policy is
claimed. This backend-only package does not change rendered pages, so the asserted
Church and Basketball screenshot set remains current.
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
The maintained testing guide, README, contributor/agent commands, roadmap, and tool
ledger now expose one `make test-postgres` contract. Its owned ephemeral PostgreSQL 16
runner covers fresh and historical Alembic upgrades, active/cancelled membership,
bootstrap/invitation races, last-slot claims, and concurrent publication. This backend
and test-infrastructure package does not change rendered pages; the captured Church and
Basketball screenshot set remains current.
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
The maintained browser-security contract now inventories every unsafe rendered route and
requires an exact origin plus a signed double-submit token for forms and HTMX requests.
Browser authentication routes carry the existing local rate-limit dependencies, and both
rate limits and audit records ignore forwarded addresses from untrusted peers. A real
Chromium case covers rejection without mutation and same-origin success. The package adds
only hidden request metadata and does not alter the rendered walkthrough, so the committed
Church and Basketball screenshots remain current. Production request limits now use
atomic Redis storage shared by application workers; an owned Redis 7 drill covers shared
quota and expiring hashed keys, while unit tests cover fail-closed 503 and recovery. The
existing request-integrity browser evidence plus production configuration tests cover
local cookie, exact-origin, expiry, and revocation behavior. Deployed edge/proxy/TLS
behavior remains external release evidence under #271; it is not represented as local
application work still missing.
The durable notification package commits scheduling intents before dispatch, claims them
with tenant-scoped atomic leases, recovers abandoned work, bounds retries, and surfaces
dead-letter or uncertain provider outcomes to administrators. Compose now runs one
notification worker and exactly one beat scheduler. The owned Redis drill covers shared
quota, cross-worker tenant-scoped refresh delivery, and broker outage/recovery; the owned
PostgreSQL drill proves exactly one winner in a simultaneous lease race. Invitation and
password-reset transport remains direct best-effort, and no external provider, deployed
broker, inbox, or operator alert receipt is claimed. These backend and infrastructure
changes do not alter rendered Church/Basketball pages, so committed screenshots remain current.
All 24 scheduling email templates now contain localized visible copy and matching HTML
language metadata; localized subject tests cover the same four message types and six languages.
The maintained production-configuration contract now maps effective environment readers,
defaults, fail-closed rules, provider gates, and current container limits. Production
rejects unsafe settings before database initialization; the Compose/reference profiles
keep paid providers off, use Redis shared state, and retain one conservative API worker. The
operations runbook now labels backup, restore, rollback, TLS/proxy, and deployment work
as unresolved instead of presenting untested commands as accepted. Clean subprocess
tests use only synthetic values and do not activate a provider or deployment.
The release-artifact package separates Alembic from application startup, keeps
PostgreSQL and Redis private, and removes source bind mounts and builder executables
from the non-root read-only runtime. `make test-artifact` is the maintained opt-in local
proof for image contents, immutable revision identity, one-shot migration failure,
two replicas, provider-free Basketball publication/export, graceful shutdown, and
self-signed loopback TLS termination. The TLS rehearsal verifies negotiated protocol,
secure browser cookies, same-origin writes, and security headers through an owned proxy.
Its report explicitly records that staging, managed services, external ingress/managed
TLS, providers, backup/restore, and operator release approval were not exercised.
The separate `make test-staging` command is prepared for an owner-authorized HTTPS target.
It requires the exact deployed SHA and approval receipt, runs every pluggable API playbook
plus browser-session checks, and emits a sanitized report. No staging receipt exists yet,
so this tooling does not change any blocked release-matrix row.
The monitoring package separates dependency-free `/health` liveness from sanitized
database `/ready` readiness and closes probe sessions on every failure. Production
stdout logs are structured, release-correlated, and redact credential-shaped values.
An optional Sentry DSN now initializes a real error hook with PII and tracing disabled;
local fake sinks prove database, notification-queue, and backup-freshness trigger/recovery
state. No external alert recipient, staging delivery, or retention policy is claimed.
The SQLite recovery foundation replaces the retired raw-copy wrappers with explicit
owned-workspace commands. It includes committed WAL rows through SQLite's backup API,
encrypts/authenticates bundles with a separately stored owner-only key, checks both
plaintext and ciphertext, and can publish only a new isolated verified target. The
source-bound `make test-recovery` drill covers restored Church/Basketball login, tenant
separation, published response/inbox state, and terminal-notification replay safety.
No scheduled PostgreSQL backup, off-site copy, production key custody, retention/purge,
cutover, operator receipt, or approved RPO/RTO is claimed.
The maintained [local release security guide](SECURITY_VALIDATION.md) inventories every
locked, vendored, container, native-build, and Pages publication input. The local runner
binds findings, license inventory, and CycloneDX source/image SBOMs to a clean Git SHA and
same-SHA retained artifact, records pinned scanner and advisory database provenance, sanitizes secret
matches, and proves expected failure for a generated secret and missing database. The
production and development images now pin the same reviewed Alpine manifest; the release
image upgrades OS packages, installs hash-locked runtime dependencies into an isolated
environment, and excludes Poetry, package managers, and build tools. The Python JWT and
vulnerable dependency chains and the mobile Fastlane/Rubyzip lock are updated. The Pages
publisher uses reviewed action commit SHAs. No hosted validation, Ollama review, native
artifact scan, deployed-environment scan, or blanket production acceptance is claimed.
This package changes tooling and publication provenance, not rendered product UI, so the
current Church/Basketball screenshots remain applicable.
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
The documentation-control package replaces the stale 176-manual/120-generated inventory with
Git-derived counts. It recorded 188 manual records and 139 generated mobile documents at its
reviewed source; issue #191's deterministic regeneration removes one obsolete generated model,
leaving 188 manual records and 138 generated mobile documents after codegen. The
current release-acceptance matrix increases the current manual inventory to 189.
Every manual file has a current or historical disposition, canonical destination, owner, verified
source set, and outcome. `make test-docs` checks current Markdown and HTML local paths and anchors;
historical files carry an explicit file-level link exception, and generated documents remain under
#191 so the validator cannot legitimize hand edits. The first run repaired two maintained setup links
and the README workflow anchor.
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
