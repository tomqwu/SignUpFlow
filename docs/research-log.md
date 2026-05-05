# Research log

Observations from external sources, before they graduate into agent rules. Keep observations separate from promoted rules.

Workflow:

1. New source → row in `docs/source-repos.md` with `Status = pending`.
2. Observations recorded here under **Observations** with a dated heading.
3. Stable, actionable observations promoted into `AGENTS.md`, `CLAUDE.md`, or `.github/copilot-instructions.md`.
4. Promoted observations summarized under **Promoted** with the target file noted.
5. Source row updated to `Status = extracted` then `promoted`.

## Observations

### 2026-05-05 — tomqwu/GenAI_Common

Source: https://github.com/tomqwu/GenAI_Common

- Layered instruction model: universal baseline in `AGENTS.md`, agent-specific addenda in `CLAUDE.md` and `.github/copilot-instructions.md`, path-scoped Copilot rules under `.github/instructions/*.instructions.md`, human-facing strategy in `docs/`.
- House style emphasizes imperative voice, verifiable rules, runnable commands, and ~200-line file cap.
- Anti-hallucination checklist is enforced at the agent-rule level (`do not invent paths/commands/URLs`, `read facts from canonical source`, `present 2-3 differentiated options when ambiguous`).
- Safety rules call out destructive shell/git operations and bypassing commit hooks as defaults to refuse.
- PR and commit body format is structured: `Summary / Changed files / Validation / Follow-ups`.
- Research handling separates `source-repos.md` (tracking) from `research-log.md` (observations) so that exploratory notes never become silent rules.
- The "single source, multi-host" pattern (one canonical file, per-host delivery files) avoids the drift that comes from copying rules into every agent file.

## Promoted

### 2026-05-05 — From tomqwu/GenAI_Common

- Layered instruction model + agent instruction hierarchy → `AGENTS.md`, `CLAUDE.md`.
- House style (imperative voice, verifiable rules, ~200-line cap) → `AGENTS.md`, `.github/copilot-instructions.md`.
- Anti-hallucination checklist → `AGENTS.md`.
- Validation checklist (Black/Ruff/mypy/tests/secrets-grep) → `AGENTS.md`, adapted with SignUpFlow's actual commands.
- PR and commit body format (`Summary / Changed files / Validation / Follow-ups`) → `AGENTS.md`, `.github/copilot-instructions.md`. Note: kept the existing imperative-mood plain-English commit *titles* used in this repo's history (no Conventional Commit prefix).
- Single source, multi-host pattern → `docs/ai-agent-coding-strategy.md`.
- Research handling workflow (`source-repos.md` + `research-log.md`) → adopted as `docs/source-repos.md` and this file.
