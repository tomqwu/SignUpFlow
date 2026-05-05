# AGENTS.md

Cross-agent baseline rules for SignUpFlow. Consumed by Codex CLI, Cursor, Aider, Jules, OpenHands, Sourcegraph Amp, Factory, and other tools that read `AGENTS.md`.

Claude Code does not read this file natively; [`CLAUDE.md`](./CLAUDE.md) cross-references it via a markdown link at the top. GitHub Copilot has its own file at [`.github/copilot-instructions.md`](./.github/copilot-instructions.md) which restates the rules below for Copilot.

The cross-project source for these patterns is `tomqwu/GenAI_Common`. When a rule below could apply to other projects, consider promoting it upstream.

## Repository purpose

SignUpFlow is a headless volunteer scheduling and sign-up management API + CLI for churches, sports leagues, and non-profits. A greedy heuristic solver with constraint-based optimization auto-generates fair schedules.

- Backend: FastAPI + SQLAlchemy 2.0 + Pydantic 2.x (Python 3.11+)
- CLI: YAML workspace in, JSON solution out (`api.cli.main`)
- Database: SQLite (dev), PostgreSQL (prod)
- Auth: JWT (HS256, 24h expiry) + bcrypt

Billing (Stripe), email (SendGrid), SMS (Twilio), and notification routers exist in the codebase but are **not registered** in `api/main.py`. Tests for those features are skipped via `pytestmark`.

## Operating loop

1. Inspect `README.md`, `AGENTS.md`, `CLAUDE.md`, and the relevant source files before editing.
2. Identify whether the request is code, tests, migration, docs, or repo hygiene.
3. For non-trivial changes, propose a short patch plan first.
4. Make small, reviewable edits.
5. Run the validation commands below before declaring done.
6. Summarize changed files and validation performed.

## House style

- Use imperative voice. `Run X before committing.` Not `It is recommended to run X.`
- Each rule must be verifiable. `Filter every query by org_id.` Not `Be careful with multi-tenancy.`
- Prefer concrete, runnable commands over prose.
- Keep each instruction file under ~200 lines. Split by topic rather than nest.
- Markdown only in instruction files. No HTML except block comments for human-only notes.

## Code style

- Python 3.11. Four-space indent. Max line length 100.
- Format with Black: `poetry run black api tests`.
- Lint with Ruff: `poetry run ruff check api tests`.
- Type-check with mypy: `poetry run mypy api`.
- Use descriptive action-based names (`send_invitation_email`, not `process`).
- Pydantic 2.x and SQLAlchemy 2.0 idioms only — no legacy `Query` API or `BaseConfig` shims.

## Safety

- Never commit secrets, API keys, JWT signing keys, database URLs, or customer-identifiable data. Read them from environment variables.
- Never run destructive operations (`rm -rf`, `DROP TABLE`, `git push --force`, `git reset --hard`, `make clean` against shared dirs, branch deletion) without explicit user authorization for that specific action.
- Never bypass commit hooks (`--no-verify`, `--no-gpg-sign`) unless the user explicitly asks.
- Never amend or rewrite published commits without explicit confirmation.
- When unsure whether an action is reversible, stop and ask.

## Multi-tenancy and auth (project-critical)

- Every database query MUST filter by `org_id`. Use `verify_org_member(person, org_id)` from `api/dependencies.py` to enforce org isolation.
- Protect routes with `Depends(get_current_user)` or `Depends(get_current_admin_user)`. Never read user state from the request body.
- Two roles only: `volunteer` and `admin`. Roles are a JSON array on the `Person` model.
- A missing `org_id` filter is a cross-tenant data leak. Treat it as a P0 bug.

## Anti-hallucination

- Do not invent file paths, function names, route paths, commands, URLs, or identifiers. Grep the repo before referencing.
- Do not represent unverified research as established best practice.
- When extracting facts (schema fields, config values, env var names), read them from the canonical source. Do not recall from memory.
- When the request is ambiguous, present 2-3 differentiated options rather than guessing.
- For research-style tasks, encode a hard-stop checklist (`≥3 angles covered? sources read in full? limitations included?`). If any answer is `no`, keep researching.

## Validation

Before declaring a change done:

- [ ] Code formats clean: `poetry run black --check api tests`.
- [ ] Lint passes: `poetry run ruff check api tests`.
- [ ] Type-check passes for touched modules: `poetry run mypy api`.
- [ ] Unit tests pass: `make test-unit` (or `make test-unit-fast` during iteration).
- [ ] Full suite passes when shipping: `make test-all`.
- [ ] No secrets in the diff: `git diff --cached | grep -iE 'api[_-]?key|secret|token|password|sk_'` returns nothing meaningful.
- [ ] If a route was added or moved, the router is registered in `api/main.py` and the path is documented in `CLAUDE.md`.
- [ ] If a model field was added or changed, an Alembic migration exists in `alembic/versions/`.

## Testing rules

- Write tests first (TDD): write the failing test, implement to make it pass, run `make test-unit` to confirm no regressions.
- Use the right tier:
  - `tests/unit/` — fast, auto-mocked auth via `conftest.py`.
  - `tests/api/` — real HTTP + JWT against in-memory DB.
  - `tests/cli/` — subprocess CLI: YAML in, JSON out.
  - `tests/integration/` — real DB.
- Mark tests with `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`, `@pytest.mark.no_mock_auth`.
- Add negative-path assertions for every new feature (unauthorized access, missing org_id, malformed input).
- Slow bcrypt tests: skip during iteration with `make test-unit-fast`; run before commit.

## Dev environment

```bash
make setup            # First-time: install Poetry deps, run migrations, seed data
make run              # Dev server on :8000 (uvicorn --reload)
make migrate          # Run Alembic migrations
make test             # Comprehensive backend tests
make test-all         # Full suite: unit + api + cli + integration
make test-unit        # Python unit tests only
make test-unit-fast   # Unit tests excluding slow bcrypt tests (~7s)
make clean            # Remove caches, temp DBs, coverage
```

Reset local DB: `rm roster.db && make migrate`.

## PR and commit format

Commit titles use imperative-mood plain English matching recent history (e.g., `Add event CRUD, conflict detection, and availability tests`). No required prefix; do not invent a Conventional Commit prefix unless the user asks.

Commit body and PR descriptions follow:

```text
Summary:
- one-line per change

Changed files:
- path: reason

Validation:
- what you ran (commands and result)

Follow-ups:
- known gaps, deferred work, or open questions
```

PR titles under 70 characters. Detail goes in the body.

## Agent instruction hierarchy

When rules overlap, follow the more specific and safer one. Precedence:

1. The user's request in the current task.
2. Repository-specific rules in `CLAUDE.md` and `AGENTS.md`.
3. Path-scoped rules under `.github/instructions/` (Copilot).
4. General guidance in `docs/ai-agent-coding-strategy.md`.
5. Inferred best practice.

## Anti-patterns

- Skipping the `org_id` filter "for simplicity" — every query, every time.
- Mocking the database in integration tests. Use the real test DB tier.
- Fixing code without investigating root cause first.
- Replacing a whole document when an append-and-refine edit would do.
- Marketing language in instruction files.
- Re-enabling disabled feature routers (billing/email/SMS/notifications) without an explicit task to do so.
- Hard-coding values from memory (env var names, route paths, schema fields). Read them from the canonical source.

## File-by-file scope notes

- `CLAUDE.md` — Claude Code only. Cross-references this file at the top and adds Claude-specific addenda for stack/architecture.
- `AGENTS.md` — this file. Universal baseline.
- `.github/copilot-instructions.md` — GitHub Copilot only.
- `docs/ai-agent-coding-strategy.md` — human-facing strategy, not enforced as rules.
- `docs/research-log.md` — observations vs. promoted rules, sourced from external repos.
- `docs/source-repos.md` — external sources studied for agent practices.
- `.specify/memory/constitution.md` — project-level principles, single source of truth above all agent files.

## References

- `tomqwu/GenAI_Common` — upstream cross-project agent guidance.
- AGENTS.md spec — https://agents.md/
- Claude Code memory — https://docs.claude.com/en/docs/claude-code/memory
- GitHub Copilot custom instructions — https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions
