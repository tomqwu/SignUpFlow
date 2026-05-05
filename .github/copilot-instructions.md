# GitHub Copilot repository instructions

Repo-wide instructions for GitHub Copilot. Path- or topic-scoped rules live in `.github/instructions/*.instructions.md` with `applyTo:` glob frontmatter.

The universal baseline is in `AGENTS.md`. This file restates the parts that matter for Copilot and adds Copilot-specific guidance.

## Repository purpose

SignUpFlow is a headless volunteer scheduling and sign-up management API + CLI. FastAPI + SQLAlchemy 2.0 + Pydantic 2.x backend on Python 3.11+, with a YAML-in/JSON-out CLI. Stripe billing, SendGrid email, Twilio SMS, and notification routers exist but are **disabled** — do not suggest re-enabling them without an explicit task.

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
- Roles are `volunteer` or `admin`, stored as a JSON array on `Person`.

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
make test-all       # Unit + api + cli + integration
make migrate        # Alembic upgrade head
```

- Do not suggest installing or updating packages without a clear reason.
- Add new dependencies with `poetry add <pkg>` and update lockfile in the same commit.

## PR rules

1. Run tests after every code change. After any edit to code or tests, run `make test-unit` (or `make test-unit-fast` during iteration). The change is not "done" until local tests pass. Run `make test-all` before pushing a PR.
2. Commit and let CI run. After local tests pass, commit and push. Do not declare a change shippable based on local results alone — wait for CI on the branch.
3. Merge only when CI is green. A PR may merge only after CI passes. If CI is red, fix the cause before merging. Do not bypass, force-merge, or skip required checks.

## Testing rules

- Write tests first (TDD).
- `tests/unit/` mocks auth via `conftest.py`. `tests/api/` uses real JWT. `tests/cli/` runs the CLI as a subprocess. `tests/integration/` hits a real DB.
- Mark tests with `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`, `@pytest.mark.no_mock_auth`.
- Add negative-path assertions (unauthorized, missing org_id, malformed input).

## PR and commit format

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
- If the change would re-enable a disabled feature (billing, email, SMS, notifications), confirm with the user before suggesting code.

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
