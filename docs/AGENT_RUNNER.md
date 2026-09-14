# Guarded Agent Runner

The Claude and Gemini shell entry points share `scripts/agent_runner.py`. The
runner executes one explicit work item with bounded retries and guarded Git and
GitHub commands. It never chooses arbitrary Markdown, historical research, a
completed spec, or a deferred lane.

## Work Item

Store versioned items as `work-item.json`. See
`docs/examples/agent-work-item.json`. Required fields are:

- `schema_version`: `1`
- `id`, `title`, `phase`, `state`, and numeric `priority`
- `hard_dependencies`: work-item IDs that must be `reviewed` or `merged`
- `acceptance`: objective completion statements
- `owned_paths`: the only paths a builder may stage or commit

Discovery is recursive but matches only `work-item.json`. `--select-next`
selects a `ready` item in the requested phase with satisfied hard dependencies,
ordered by priority, ID, then path. The default phase is `business-flow`.
An explicitly selected item with hard dependencies must still resolve them from
`--work-root`; explicit selection does not bypass readiness.

## Modes

Planning and reviewer modes allow read-only Git/GitHub commands. A forbidden
mutation fails the run even if the agent ignores the command error and prints
DONE. Reviewer mode never merges.

Builder mode permits explicit `git add <owned path>`, commits containing only
owned paths, pushes, and PR creation. It blocks broad staging, branch mutation,
force operations, issue mutation, and agent-issued merges. A pre-existing
unrelated dirty path is fingerprinted and must remain unchanged and unstaged.

## Commands

Inspect the rendered prompt without running an agent:

```bash
./scripts/ralph-loop.sh --mode plan --prompt task.md \
  --work-item docs/examples/agent-work-item.json --dry-run
```

See `docs/examples/agent-rendered-prompt.md` for the stable generated policy
prefix. Work-item details and the task body are appended for each run.

Run one Claude planning iteration:

```bash
./scripts/ralph-loop.sh --mode plan --prompt task.md \
  --work-item path/to/work-item.json
```

Run one Gemini builder iteration:

```bash
./scripts/ralph-loop-gemini.sh --mode build --prompt task.md \
  --work-item path/to/work-item.json --evidence path/to/local-evidence.json
```

The default is one iteration and the maximum is 20. `--timeout` bounds each
agent invocation. The runner does not add model or reasoning flags, enable
auto-approval, or switch to a more expensive model.

## Completion Evidence

DONE text is necessary but insufficient. Builder completion also requires a
new schema-v1 evidence file, shown in `docs/examples/agent-local-evidence.json`,
whose source and reviewed head/base SHAs match the current commit. Its test
record must link the passed, clean-tracked-tree `make test-all` report produced
by the #281 local validator for that same source SHA. The committed base-to-head
diff must contain only owned paths. Finally, `gh pr view` must report the same
head as `MERGEABLE` and `CLEAN`.

Pass `--merge` only for a builder run whose user scope includes merging. The
runner performs the merge after validation. It never deletes the branch. There
are no CI checks or Ollama code-review requirements.

## Offline Validation

Run fixture tests; they do not start live agents or mutate GitHub:

```bash
poetry run pytest tests/unit/test_agent_runner.py -q
```

The fixtures use temporary repositories and fake GitHub/agent commands to cover
planning, reviewer, builder, dirty worktrees, dependency selection, command
failure, stale evidence, failed tests, and nonmergeable PRs.
