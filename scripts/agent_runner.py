#!/usr/bin/env python3
"""Run one explicitly scoped agent task and verify local delivery evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

COMPLETION_SIGNAL = "<promise>DONE</promise>"
FINISHED_STATES = {"reviewed", "merged"}
VALID_STATES = {"planned", "ready", "running", "blocked", "reviewed", "merged"}


class RunnerError(RuntimeError):
    """Represent a policy or evidence failure."""


@dataclass(frozen=True)
class WorkItem:
    path: Path
    id: str
    title: str
    phase: str
    state: str
    priority: int
    hard_dependencies: tuple[str, ...]
    acceptance: tuple[str, ...]
    owned_paths: tuple[str, ...]


def _validate_owned_paths(path: Path, values: Any) -> tuple[str, ...]:
    if not isinstance(values, list):
        raise RunnerError(f"owned_paths must be a list in {path}")
    owned_paths = tuple(map(str, values))
    for value in owned_paths:
        candidate = Path(value)
        if (
            not value
            or value == "."
            or candidate.is_absolute()
            or ".." in candidate.parts
            or candidate.parts[:1] == (".git",)
        ):
            raise RunnerError(f"Unsafe owned path in {path}: {value!r}")
    return owned_paths


def _load_work_item(path: Path) -> WorkItem:
    try:
        payload = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise RunnerError(f"Invalid work-item file {path}: {error}") from error
    if not isinstance(payload, dict):
        raise RunnerError(f"Work-item root must be an object in {path}")
    required = {
        "schema_version",
        "id",
        "title",
        "phase",
        "state",
        "priority",
        "hard_dependencies",
        "acceptance",
        "owned_paths",
    }
    missing = required - payload.keys()
    if missing or payload["schema_version"] != 1:
        raise RunnerError(f"Invalid work-item schema in {path}; missing={sorted(missing)}")
    if not isinstance(payload["state"], str) or payload["state"] not in VALID_STATES:
        raise RunnerError(f"Invalid work-item state in {path}: {payload['state']}")
    if any(not str(payload[field]).strip() for field in ("id", "title", "phase")):
        raise RunnerError(f"Work-item identity fields must be nonempty in {path}")
    if not isinstance(payload["hard_dependencies"], list):
        raise RunnerError(f"hard_dependencies must be a list in {path}")
    if not isinstance(payload["acceptance"], list) or not payload["acceptance"]:
        raise RunnerError(f"acceptance must be a nonempty list in {path}")
    try:
        item = WorkItem(
            path=path,
            id=str(payload["id"]),
            title=str(payload["title"]),
            phase=str(payload["phase"]),
            state=str(payload["state"]),
            priority=int(payload["priority"]),
            hard_dependencies=tuple(map(str, payload["hard_dependencies"])),
            acceptance=tuple(map(str, payload["acceptance"])),
            owned_paths=_validate_owned_paths(path, payload["owned_paths"]),
        )
    except (TypeError, ValueError) as error:
        raise RunnerError(f"Invalid work-item value in {path}: {error}") from error
    if item.priority < 0:
        raise RunnerError(f"Work-item priority must be nonnegative in {path}")
    if item.id in item.hard_dependencies:
        raise RunnerError(f"Work item {item.id} cannot depend on itself")
    return item


def discover_work_items(root: Path) -> list[WorkItem]:
    """Recursively load only versioned work-item documents."""
    if not root.exists():
        return []
    items = [_load_work_item(path) for path in sorted(root.rglob("work-item.json"))]
    ids = [item.id for item in items]
    duplicates = sorted({item_id for item_id in ids if ids.count(item_id) > 1})
    if duplicates:
        raise RunnerError(f"Duplicate work-item IDs: {duplicates}")
    return items


def select_ready_work_item(items: list[WorkItem], phase: str) -> WorkItem:
    """Select the first ready item whose declared hard dependencies finished."""
    states = {item.id: item.state for item in items}
    ready = [
        item
        for item in items
        if item.phase == phase
        and item.state == "ready"
        and all(states.get(dep) in FINISHED_STATES for dep in item.hard_dependencies)
    ]
    if not ready:
        raise RunnerError(f"No ready work item with satisfied dependencies in phase {phase}")
    return sorted(ready, key=lambda item: (item.priority, item.id, str(item.path)))[0]


def _require_satisfied_dependencies(item: WorkItem, items: list[WorkItem]) -> None:
    states = {candidate.id: candidate.state for candidate in items}
    unmet = [
        dependency
        for dependency in item.hard_dependencies
        if states.get(dependency) not in FINISHED_STATES
    ]
    if unmet:
        raise RunnerError(f"Work item {item.id} has unmet hard dependencies: {unmet}")


def _command_output(command: list[str], repo: Path) -> str:
    result = subprocess.run(command, cwd=repo, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RunnerError(f"Command failed ({' '.join(command)}): {result.stderr.strip()}")
    return result.stdout.strip()


def _dirty_paths(git: str, repo: Path) -> set[str]:
    result = subprocess.run(
        [git, "status", "--porcelain=v1", "-z"],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RunnerError(f"Unable to inspect worktree: {result.stderr.strip()}")
    records = [record for record in result.stdout.split("\0") if record]
    paths: set[str] = set()
    index = 0
    while index < len(records):
        record = records[index]
        if len(record) < 4 or record[2] != " ":
            raise RunnerError(f"Unexpected git status record: {record!r}")
        paths.add(record[3:])
        if record[0] in {"R", "C"} or record[1] in {"R", "C"}:
            index += 1
            if index >= len(records):
                raise RunnerError("Incomplete rename record from git status")
            paths.add(records[index])
        index += 1
    return paths


def _fingerprint(repo: Path, paths: set[str]) -> dict[str, str | None]:
    result: dict[str, str | None] = {}
    for relative in paths:
        path = repo / relative
        if path.is_file() and not path.is_symlink():
            result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        elif path.is_dir() and not path.is_symlink():
            digest = hashlib.sha256()
            for child in sorted(
                candidate for candidate in path.rglob("*") if not candidate.is_symlink()
            ):
                digest.update(str(child.relative_to(path)).encode())
                if child.is_file():
                    digest.update(child.read_bytes())
            result[relative] = digest.hexdigest()
        elif path.exists():
            result[relative] = "present"
        else:
            result[relative] = None
    return result


def _item_payload(item: WorkItem) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "id": item.id,
        "title": item.title,
        "phase": item.phase,
        "state": item.state,
        "priority": item.priority,
        "hard_dependencies": list(item.hard_dependencies),
        "acceptance": list(item.acceptance),
        "owned_paths": list(item.owned_paths),
        "source": str(item.path),
    }


def _render_prompt(mode: str, prompt: Path, item: WorkItem) -> str:
    policy = f"""# SignUpFlow delegated {mode} task

Work only on the explicit versioned item below. Current user scope and the
`phase: {item.phase}` roadmap lane overrides historical priority text. Run tests
first for implementation changes and keep all review and validation local.
No CI checks or hosted reviewers are used. Ollama is an application voice
model only and must not be used for code review. Never deploy, activate a paid
provider, purge real data, bypass hooks, force-merge, or delete a branch.

Planning and reviewer modes may not commit, push, create or merge a PR.
Reviewer agents never merge. A builder may touch and stage only `owned_paths`;
merging is performed by this runner only after current local test and review
evidence matches HEAD and GitHub reports the PR mergeable and clean.

Completion text is only a hint. Return `{COMPLETION_SIGNAL}` only after the
work-item acceptance is complete. The runner independently checks command exit,
guarded tool calls, owned diffs, evidence SHAs, and GitHub mergeability.

## Work Item

```json
{json.dumps(_item_payload(item), indent=2, sort_keys=True)}
```

## Task Prompt

"""
    return policy + prompt.read_text()


def _read_guard_log(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def _validate_evidence(evidence_path: Path, item: WorkItem, repo: Path, git: str, gh: str) -> None:
    if not evidence_path.is_file():
        raise RunnerError(f"Evidence file is missing: {evidence_path}")
    try:
        evidence = json.loads(evidence_path.read_text())
    except json.JSONDecodeError as error:
        raise RunnerError(f"Evidence is not valid JSON: {error}") from error
    head = _command_output([git, "rev-parse", "HEAD"], repo)
    for key in ("source_sha", "base_sha", "tests", "review"):
        if key not in evidence:
            raise RunnerError(f"Evidence is missing {key}")
    if evidence.get("schema_version") != 1:
        raise RunnerError("Evidence schema_version must be 1")
    if evidence["source_sha"] != head:
        raise RunnerError("Evidence source_sha is stale or does not match HEAD")
    if evidence["tests"].get("status") != "passed":
        raise RunnerError("Local tests are not recorded as passed")
    report_value = evidence["tests"].get("report_path")
    if not report_value:
        raise RunnerError("Local tests evidence is missing report_path")
    report_path = Path(report_value)
    if not report_path.is_absolute():
        report_path = repo / report_path
    try:
        report = json.loads(report_path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise RunnerError(f"Local test report is missing or invalid: {error}") from error
    if report.get("status") != "passed" or report.get("source_sha") != head:
        raise RunnerError("Local test report is failed or stale for HEAD")
    if report.get("tracked_tree_clean") is not True:
        raise RunnerError("Local test report was not produced from a clean tracked tree")
    expected_tiers = {"unit", "api", "cli", "integration", "web", "contract", "e2e"}
    tiers = {tier.get("id"): tier for tier in report.get("tiers", [])}
    if set(tiers) != expected_tiers or any(
        tier.get("status") != "passed" or tier.get("counts", {}).get("tests", 0) < 1
        for tier in tiers.values()
    ):
        raise RunnerError("Local test report does not contain seven passed nonempty default tiers")
    totals = report.get("totals", {})
    if totals.get("tests", 0) < 7 or totals.get("failures") != 0 or totals.get("errors") != 0:
        raise RunnerError("Local test report totals are incomplete or failing")
    review = evidence["review"]
    if review.get("status") != "passed" or review.get("reviewed_head_sha") != head:
        raise RunnerError("Local review is missing, failed, or stale for HEAD")
    if review.get("reviewed_base_sha") != evidence["base_sha"]:
        raise RunnerError("Local review base SHA does not match evidence base_sha")
    changed = set(
        filter(
            None,
            _command_output(
                [git, "diff", "--name-only", f"{evidence['base_sha']}..{head}"], repo
            ).splitlines(),
        )
    )
    if not changed or not changed <= set(item.owned_paths):
        raise RunnerError(
            f"Committed diff includes unowned paths: {sorted(changed - set(item.owned_paths))}"
        )
    try:
        pr = json.loads(
            _command_output(
                [gh, "pr", "view", "--json", "mergeable,mergeStateStatus,headRefOid"], repo
            )
        )
    except json.JSONDecodeError as error:
        raise RunnerError(f"GitHub PR state is not valid JSON: {error}") from error
    if pr.get("headRefOid") != head:
        raise RunnerError("GitHub PR head is stale relative to local evidence")
    if pr.get("mergeable") != "MERGEABLE" or pr.get("mergeStateStatus") != "CLEAN":
        raise RunnerError(
            "GitHub PR is not mergeable and clean: "
            f"{pr.get('mergeable')}/{pr.get('mergeStateStatus')}"
        )


def _parse_args(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--provider", choices=("claude", "gemini"), default="claude")
    parser.add_argument("--mode", choices=("plan", "review", "build"), required=True)
    parser.add_argument("--prompt", type=Path, required=True)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--work-item", type=Path)
    source.add_argument("--select-next", action="store_true")
    parser.add_argument("--work-root", type=Path, default=Path(".agent/work-items"))
    parser.add_argument("--phase", default="business-flow")
    parser.add_argument("--agent-command")
    parser.add_argument("--git-command", default=shutil.which("git") or "git")
    parser.add_argument("--gh-command", default=shutil.which("gh") or "gh")
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--max-iterations", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--merge", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(arguments)
    if args.max_iterations < 1 or args.max_iterations > 20:
        parser.error("--max-iterations must be between 1 and 20")
    if args.merge and args.mode != "build":
        parser.error("--merge is available only in build mode")
    if args.mode == "build" and not args.evidence and not args.dry_run:
        parser.error("build mode requires --evidence")
    return args


def run(arguments: list[str] | None = None) -> int:
    args = _parse_args(arguments)
    repo = args.repo.resolve()
    prompt = args.prompt.resolve()
    if not repo.is_dir():
        raise RunnerError(f"Repository path does not exist: {repo}")
    if not prompt.is_file():
        raise RunnerError(f"Prompt file does not exist: {prompt}")
    if args.work_item:
        item = _load_work_item(args.work_item.resolve())
        root = args.work_root if args.work_root.is_absolute() else repo / args.work_root
        if item.hard_dependencies:
            _require_satisfied_dependencies(item, discover_work_items(root))
    else:
        root = args.work_root if args.work_root.is_absolute() else repo / args.work_root
        item = select_ready_work_item(discover_work_items(root), args.phase)
    if item.phase != args.phase:
        raise RunnerError(
            f"Work item phase {item.phase} does not match requested phase {args.phase}"
        )
    if item.state != "ready":
        raise RunnerError(f"Work item {item.id} is not ready: {item.state}")
    rendered = _render_prompt(args.mode, prompt, item)
    if args.dry_run:
        print(rendered)
        return 0

    command = shlex.split(args.agent_command or args.provider)
    if args.provider == "claude":
        command.append("-p")
        agent_input: str | None = rendered
    else:
        command.append(rendered)
        agent_input = None
    git = str(Path(args.git_command).resolve())
    gh = str(Path(args.gh_command).resolve())
    before_head = _command_output([git, "rev-parse", "HEAD"], repo)
    before_dirty = _dirty_paths(git, repo)
    before_staged = _command_output([git, "diff", "--cached", "--binary"], repo)
    unowned_dirty = before_dirty - set(item.owned_paths)
    before_unowned = _fingerprint(repo, unowned_dirty)
    if args.evidence:
        evidence_path = args.evidence.resolve()
        if evidence_path.exists():
            raise RunnerError(f"Refusing stale pre-existing evidence file: {evidence_path}")
    else:
        evidence_path = repo / ".agent-review-evidence-unused.json"

    guard = Path(__file__).with_name("agent_tool_guard.py").resolve()
    with tempfile.TemporaryDirectory(prefix="signupflow-agent-guard-") as temporary:
        guard_dir = Path(temporary)
        (guard_dir / "git").symlink_to(guard)
        (guard_dir / "gh").symlink_to(guard)
        guard_log = guard_dir / "calls.jsonl"
        environment = {
            **os.environ,
            "PATH": f"{guard_dir}{os.pathsep}{os.environ.get('PATH', '')}",
            "SIGNUPFLOW_AGENT_MODE": args.mode,
            "SIGNUPFLOW_REAL_GIT": git,
            "SIGNUPFLOW_REAL_GH": gh,
            "SIGNUPFLOW_TOOL_GUARD_LOG": str(guard_log),
            "SIGNUPFLOW_OWNED_PATHS": json.dumps(list(item.owned_paths)),
            "SIGNUPFLOW_EVIDENCE_PATH": str(evidence_path),
        }
        completed = False
        for iteration in range(1, args.max_iterations + 1):
            try:
                result = subprocess.run(
                    command,
                    cwd=repo,
                    env=environment,
                    input=agent_input,
                    text=True,
                    capture_output=True,
                    timeout=args.timeout,
                    check=False,
                )
            except subprocess.TimeoutExpired as error:
                raise RunnerError(f"Agent timed out after {args.timeout} seconds") from error
            sys.stdout.write(result.stdout)
            sys.stderr.write(result.stderr)
            if result.returncode != 0:
                raise RunnerError(f"Agent command exit status was {result.returncode}")
            denied = [entry for entry in _read_guard_log(guard_log) if not entry["allowed"]]
            if denied:
                raise RunnerError(f"Forbidden tool call attempted: {denied[-1]}")
            if COMPLETION_SIGNAL in result.stdout:
                completed = True
                break
            print(f"Iteration {iteration} incomplete: missing {COMPLETION_SIGNAL}", file=sys.stderr)
        if not completed:
            raise RunnerError("Agent did not produce a verified completion signal")

    after_head = _command_output([git, "rev-parse", "HEAD"], repo)
    if args.mode in {"plan", "review"} and after_head != before_head:
        raise RunnerError(f"{args.mode} mode changed Git HEAD")
    if _fingerprint(repo, unowned_dirty) != before_unowned:
        raise RunnerError("Agent modified an unrelated pre-existing dirty path")
    after_dirty = _dirty_paths(git, repo)
    new_dirty = after_dirty - before_dirty
    if new_dirty - set(item.owned_paths):
        raise RunnerError(
            f"Agent created unrelated dirty paths: {sorted(new_dirty - set(item.owned_paths))}"
        )
    if args.mode == "review" and after_dirty != before_dirty:
        raise RunnerError("Reviewer mode modified the working tree")
    if (
        args.mode in {"plan", "review"}
        and _command_output([git, "diff", "--cached", "--binary"], repo) != before_staged
    ):
        raise RunnerError(f"{args.mode} mode modified the Git index")
    staged = set(
        filter(None, _command_output([git, "diff", "--cached", "--name-only"], repo).splitlines())
    )
    if staged - set(item.owned_paths):
        raise RunnerError(f"Agent staged unrelated paths: {sorted(staged - set(item.owned_paths))}")
    if args.mode == "build":
        _validate_evidence(evidence_path, item, repo, git, gh)
        if args.merge:
            merge = subprocess.run(
                [gh, "pr", "merge", "--squash"],
                cwd=repo,
                text=True,
                capture_output=True,
                check=False,
            )
            if merge.returncode != 0:
                raise RunnerError(f"GitHub merge failed: {merge.stderr.strip()}")
            print("Builder merge completed after local evidence and GitHub mergeability checks.")
    print(f"Agent workflow complete for work item {item.id} in {args.mode} mode.")
    return 0


def main() -> int:
    try:
        return run()
    except RunnerError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
