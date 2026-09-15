# GitHub Copilot repository instructions

Repo-wide instructions for GitHub Copilot. Path- or topic-scoped rules live in `.github/instructions/*.instructions.md` with `applyTo:` glob frontmatter.

The universal baseline is in `AGENTS.md`. This file restates the parts that matter for Copilot and adds Copilot-specific guidance.

## Repository purpose

SignUpFlow is a volunteer scheduling API, CLI, and web app using FastAPI, SQLAlchemy 2.0, and Pydantic 2.x on Python 3.11+. Email and its signed SendGrid callback, billing and its signed Stripe callback, and SMS code are registered but feature-gated off by default. Core scheduling must not require an external provider. Do not enable external provider delivery without an explicit task. See `docs/TESTING.md` for current validation scope.

## House style

- Use imperative voice. `Filter every query by org_id.`
- Each rule must be verifiable.
- Prefer concrete, runnable commands over prose.
- Keep instruction files under ~200 lines.
- Markdown only.

## Editing rules

- Inspect existing files before proposing edits.
- For non-trivial changes, propose a short patch plan in the chat first.
- Prefer append-and-refine over replacing whole documents.
- Do not invent file paths, function names, route paths, commands, URLs, or identifiers — grep the repo first.

## Safety

- Never suggest committing secrets, JWT signing keys, database URLs, API keys, or customer-identifiable data.
- Never suggest destructive git or shell operations (`rm -rf`, `git push --force`, `git reset --hard`, dropping tables) without an explicit user request for that specific action.
- Never bypass commit hooks (`--no-verify`).

## Multi-tenancy and auth (project-critical)

- Every database query MUST filter by `org_id`. Use `verify_org_member(person, org_id)` from `api/dependencies.py`.
- Protect routes with `Depends(get_current_user)` or `Depends(get_current_admin_user)`. Never read user state from the request body.
- `/auth/signup` atomically creates a new organization and its first `admin`; existing organizations are invitation-only.
- Grant exactly one permission role, `volunteer` or `admin`. Preserve scheduling qualifications in the role array and validate input with `api.roles.normalize_roles`.

## Code style

- Python 3.11. Four-space indent. Max line 100. Black + Ruff + mypy (strict on `api/`).
- Pydantic 2.x and SQLAlchemy 2.0 idioms. No legacy `Query` API.
- Descriptive action-based names.

## Build, test, and dependencies

```bash
make setup          # Poetry install + migrate + seed
make run            # uvicorn --reload on :8000
make test-unit      # Fast unit tests
make test-unit-fast # Skip bcrypt slow tests
make test-all       # All Python tiers, including web + contract + Playwright
make test-postgres  # Owned PostgreSQL migration/business/race acceptance
make test-redis     # Owned Redis quota, event-bus, and broker acceptance
make test-load      # Bounded source-identified local load validation
make test-artifact  # Owned production image acceptance
make test-security  # Same-SHA source/image security and SBOM evidence
make test-docs      # Documentation ledger plus current local paths and anchors
make test-mobile    # Flutter tests (requires Flutter SDK)
make test-mobile-generated # Generated Dart analysis and tests
make mobile-codegen-check # Verify generated Dart client matches OpenAPI snapshot
make migrate        # Alembic upgrade head
```

- Do not suggest installing or updating packages without a clear reason.
- Add new dependencies with `poetry add <pkg>` and update lockfile in the same commit.

## PR rules

1. Run tests after every code change. After any edit to code or tests, run `make test-unit` (or `make test-unit-fast` during iteration). The change is not "done" until local tests pass. Run `make test-all` before pushing a PR.
2. No CI checks. Run formatting, lint, type checks, migration validation, all tests and local code review locally. Run `make test-all` for every PR and `make test-mobile` for mobile changes; record the local report path, commands, outcomes, limitations and the pushed head SHA.
3. Merge only after successful local validation and review are recorded for the pushed head/base and GitHub reports mergeable. Resolve blocking findings; never fabricate checks, bypass protections, or treat missing evidence as success.
4. Require local code review for the current PR head/base and record findings and their resolution in the PR; see `docs/ai-pr-review.md`. Do not configure hosted checks or use Ollama for code review. Missing review is not approval.
5. Builder agents may merge only when GitHub reports mergeable, local evidence is complete, and any required reviews are satisfied. Do not add required CI checks. Reviewer agents must not merge.

## Testing rules

- Write tests first (TDD).
- `tests/unit/` mocks auth via `conftest.py`. `tests/api/` and `tests/security/` use real JWT against an isolated test DB. `tests/cli/` runs the CLI as a subprocess. `tests/integration/` hits a real DB.
- Mark tests with `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`, `@pytest.mark.no_mock_auth`.
- Add negative-path assertions (unauthorized, missing org_id, malformed input).

## PR and commit format

Before declaring done, reconcile affected docs and agent instructions, label
historical guidance, verify changed links, and report merged/unmerged state.

Commit titles: imperative mood plain English (matching recent history). No mandatory Conventional Commit prefix.

Body and PR descriptions:

```text
Summary:
- one-line per change

Changed files:
- path: reason

Validation:
- commands run and result

Follow-ups:
- known gaps or open questions
```

PR titles under 70 characters. Detail goes in the body.

## When to defer

- If the request is ambiguous, ask a clarifying question or offer 2-3 differentiated options.
- If the change touches the solver, constraint DSL, or auth, link the relevant section in `CLAUDE.md`.
- If the change enables external provider delivery or mounts a provider router, confirm the requested scope first.

## Anti-patterns

- Suggesting queries without an `org_id` filter.
- Mocking the DB in integration tests.
- Hard-coding env var names, route paths, or schema fields from memory.
- Mixing project-specific examples into general agent rules.
- Marketing language in instruction files.

## References

- `AGENTS.md` for the cross-agent baseline.
- `CLAUDE.md` for Claude-specific addenda.
- `docs/ai-agent-coding-strategy.md` for the human-facing strategy.
- `.specify/memory/constitution.md` for project principles.
