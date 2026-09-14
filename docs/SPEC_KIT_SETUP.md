# SpecKit Workflow

SpecKit structures feature requirements under `specs/`. It does not override
the current user request, `docs/ROADMAP.md`, issue acceptance, `AGENTS.md`, or
the local validation policy.

## Command Order

1. Run `/speckit.specify` to create or update `spec.md`.
2. Run `/speckit.clarify` when business decisions remain unresolved.
3. Run `/speckit.plan` to create design artifacts.
4. Run `/speckit.tasks` to create dependency-ordered tasks and required tests.
5. Run `/speckit.analyze` for a read-only consistency review.
6. Run `/speckit.implement` to execute tests first, implementation, local
   review, and local validation.

`/speckit.checklist` checks whether requirements are complete and testable. It
does not replace implementation tests.

## Feature Creation

Create specification files without changing branches:

```bash
.specify/scripts/bash/create-new-feature.sh --json \
  --short-name role-responses "Add explicit assignment responses"
```

The command returns `FEATURE_ID`, the proposed `codex/` branch name,
`BRANCH_CREATED: false`, and the spec path. Export the feature ID before later
commands when the current branch does not identify the spec:

```bash
export SPECIFY_FEATURE=025-role-responses
```

Only pass `--create-branch` when the current user explicitly authorized branch
creation. The generator never commits, pushes, opens a PR, merges, or deletes a
branch.

## Delivery Contract

- Treat current roadmap and issue scope as authoritative over old spec priority.
- Write a failing regression before implementation.
- Run review, static checks, and all applicable tests locally.
- Record exact head/base SHAs and any blocked or not-run tiers.
- Do not add CI checks or use Ollama for code review.
- Stage only owned paths. Preserve unrelated dirty files.
- Reviewer agents never merge. Builders require current local evidence and a
  GitHub PR reported as mergeable and clean.

Use [the guarded agent runner](AGENT_RUNNER.md) when executing a SpecKit package
through Claude or Gemini.
