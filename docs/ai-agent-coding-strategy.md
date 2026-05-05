# AI-agent coding strategy

## Purpose

Define the operating strategy for using AI coding agents (Claude Code, Codex CLI, GitHub Copilot, Cursor, Aider, Jules, OpenHands, and similar) on the SignUpFlow codebase. This document is the human-facing strategy; the agent-facing rules live in `AGENTS.md`, `CLAUDE.md`, and `.github/copilot-instructions.md`.

The cross-project source for these patterns is `tomqwu/GenAI_Common`.

## When to use this strategy

- Onboarding a new contributor (human or agent) to SignUpFlow.
- Auditing whether the agent instruction files have drifted from the codebase.
- Deciding where a new rule should live (universal, agent-specific, path-specific, or constitution).

## Operating model

1. **Study** how the codebase actually works before proposing changes — read the constitution, `CLAUDE.md`, `AGENTS.md`, and the touched modules.
2. **Plan** non-trivial work as a short patch plan and confirm with the user.
3. **Implement** in small, reviewable edits.
4. **Validate** with the commands in the validation checklist.
5. **Refine** the instruction files when a real task surfaces a gap.

## Layered instructions

Each rule lives at the narrowest layer that still covers its scope.

| Layer | File(s) | Loaded when | Use for |
|---|---|---|---|
| Project principles | `.specify/memory/constitution.md` | Always (read on entry) | Single source of truth for project principles |
| Claude project memory | `CLAUDE.md` | Every Claude Code session | Stack details, architecture, gotchas, Claude addenda |
| Universal baseline | `AGENTS.md` | Codex, Cursor, Aider, Jules, OpenHands sessions | Rules every agent should follow |
| Copilot repo-wide | `.github/copilot-instructions.md` | Every Copilot interaction | Copilot restatement of the baseline |
| Copilot path rules | `.github/instructions/*.instructions.md` with `applyTo:` | When matching files are referenced | Tech- or path-scoped Copilot rules |
| Human strategy | `docs/ai-agent-coding-strategy.md` | Read by humans and on request by agents | This file: rationale and onboarding |
| Research notes | `docs/research-log.md` + `docs/source-repos.md` | On request | Observations from external sources, before promotion |

## Minimum viable workflow

For a feature change:

1. Read the constitution and the relevant section of `CLAUDE.md`.
2. Locate the active routers, dependencies, and tests for the touched domain.
3. Write a failing test in the right tier (`unit/`, `api/`, `cli/`, or `integration/`).
4. Implement to make it pass.
5. Run `make test-unit-fast` during iteration, `make test-all` before commit.
6. If a route was added, register it in `api/main.py` and update the router list in `CLAUDE.md`.
7. If a model field changed, generate an Alembic migration.

## Implementation checklist

- [ ] Every DB query filters by `org_id`. Cross-tenant leaks are a P0 bug.
- [ ] Routes use `Depends(get_current_user)` or `Depends(get_current_admin_user)`.
- [ ] Tests cover the happy path AND at least one negative-path assertion.
- [ ] Disabled features (billing/email/SMS/notifications) remain disabled unless the task says otherwise.
- [ ] Each new or edited agent rule is imperative and verifiable.
- [ ] Each external source is recorded in `docs/source-repos.md` and `docs/research-log.md`.

## Validation checklist

- [ ] `poetry run black --check api tests` clean.
- [ ] `poetry run ruff check api tests` clean.
- [ ] `poetry run mypy api` clean for touched modules.
- [ ] `make test-unit` passes (or `make test-all` before commit).
- [ ] No secrets in the diff.
- [ ] Agent instructions still under ~200 lines per file.
- [ ] Cross-references in instruction files resolve.

## Anti-patterns

- Burying critical constraints inside long prose. Agents skim past them.
- Duplicating the same rule into every agent file. Cross-reference instead.
- Treating exploratory research notes as mandatory rules. Keep `docs/research-log.md` separate.
- Mixing project-specific examples (FastAPI router code) into general agent rules.
- Adding marketing language to instruction files.
- Re-enabling disabled feature routers without an explicit task.

## Single source, multi-host

Cross-project agent patterns originate in `tomqwu/GenAI_Common`. When the same content needs to reach multiple agents in this repo, keep one canonical source and emit per-host delivery files rather than maintaining parallel copies.

- `AGENTS.md` is the canonical baseline. `CLAUDE.md` cross-references it; `.github/copilot-instructions.md` restates the parts Copilot needs.
- When the canonical content changes, list the per-host files that must be updated alongside it. Note the change in `docs/research-log.md` if the rule originated from an external source.

## How rules graduate

```text
Observation in docs/research-log.md
        │
        ▼
Tested on at least one real change in this repo
        │
        ▼
Promoted to AGENTS.md (universal) or per-agent file (specific)
        │
        ▼
Source row in docs/source-repos.md updated to Status = promoted
        │
        ▼
If broadly applicable, opened upstream in tomqwu/GenAI_Common
```

## References

- `AGENTS.md` — universal cross-agent baseline.
- `CLAUDE.md` — Claude Code project memory.
- `.github/copilot-instructions.md` — repo-wide Copilot rules.
- `docs/source-repos.md` — tracked external sources.
- `docs/research-log.md` — observations and promoted rules.
- `.specify/memory/constitution.md` — project principles.
- `tomqwu/GenAI_Common` — upstream cross-project agent guidance.
