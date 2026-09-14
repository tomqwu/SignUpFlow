"""Exercise agent-runner policy with isolated repositories and fake tools."""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.agent_runner import RunnerError, discover_work_items, select_ready_work_item

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts/agent_runner.py"


def _run(*args: str, cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(RUNNER), *args],
        cwd=cwd,
        env={**os.environ, **(env or {})},
        text=True,
        capture_output=True,
        check=False,
    )


def _executable(path: Path, source: str) -> Path:
    path.write_text(source)
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def _fake_git(repository: Path) -> Path:
    real_git = shutil.which("git")
    assert real_git
    source = f"""#!/usr/bin/env python3
import pathlib
import subprocess
import sys

pathlib.Path("git-calls.log").open("a").write(" ".join(sys.argv[1:]) + "\\n")
raise SystemExit(subprocess.run([{real_git!r}, *sys.argv[1:]], check=False).returncode)
"""
    return _executable(repository / "fake-git", source)


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "runner@example.invalid"], cwd=tmp_path, check=True
    )
    subprocess.run(["git", "config", "user.name", "Runner Test"], cwd=tmp_path, check=True)
    (tmp_path / "owned.txt").write_text("before\n")
    (tmp_path / "unrelated.txt").write_text("keep me\n")
    (tmp_path / ".gitignore").write_text(
        ".agent/\nevidence.json\nfake-*\ngh-calls.log\ngit-calls.log\n"
        "local-test-report.json\nprompt.md\n"
    )
    subprocess.run(
        ["git", "add", ".gitignore", "owned.txt", "unrelated.txt"], cwd=tmp_path, check=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial"], cwd=tmp_path, check=True, capture_output=True
    )
    (tmp_path / "prompt.md").write_text("Complete the explicit work item.\n")
    return tmp_path


@pytest.mark.parametrize("mode", ["plan", "review"])
def test_read_only_modes_reject_git_mutation(repository: Path, mode: str):
    agent = _executable(
        repository / "fake-agent",
        "#!/bin/sh\ngit add -A >/dev/null 2>&1 || true\nprintf '<promise>DONE</promise>\\n'\n",
    )

    result = _run(
        "--repo",
        str(repository),
        "--mode",
        mode,
        "--prompt",
        str(repository / "prompt.md"),
        "--agent-command",
        str(agent),
        "--git-command",
        str(_fake_git(repository)),
        "--work-item",
        str(_write_work_item(repository, owned_paths=[])),
        cwd=repository,
    )

    assert result.returncode != 0
    assert "forbidden tool call" in (result.stdout + result.stderr).lower()
    assert (
        subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=repository) == b""
    )
    assert (
        subprocess.check_output(
            ["git", "log", "-1", "--pretty=%s"], cwd=repository, text=True
        ).strip()
        == "Initial"
    )
    assert "add -A" not in (repository / "git-calls.log").read_text()


def test_read_only_mode_cannot_create_a_branch(repository: Path):
    agent = _executable(
        repository / "fake-agent",
        "#!/bin/sh\ngit branch forbidden >/dev/null 2>&1 || true\nprintf '<promise>DONE</promise>\\n'\n",
    )
    result = _run(
        "--repo",
        str(repository),
        "--mode",
        "review",
        "--prompt",
        str(repository / "prompt.md"),
        "--agent-command",
        str(agent),
        "--work-item",
        str(_write_work_item(repository, owned_paths=[])),
        cwd=repository,
    )

    assert result.returncode != 0
    assert "forbidden tool call" in (result.stdout + result.stderr).lower()
    assert (
        "forbidden"
        not in subprocess.check_output(
            ["git", "branch", "--format=%(refname:short)"], cwd=repository, text=True
        ).splitlines()
    )


def test_unsupported_mode_and_missing_prompt_fail_before_agent_runs(repository: Path):
    marker = repository / "agent-ran"
    agent = _executable(repository / "fake-agent", f"#!/bin/sh\ntouch {marker}\n")
    work_item = _write_work_item(repository)

    unsupported = _run("--mode", "deploy", cwd=repository)
    missing = _run(
        "--repo",
        str(repository),
        "--mode",
        "build",
        "--prompt",
        str(repository / "missing.md"),
        "--agent-command",
        str(agent),
        "--work-item",
        str(work_item),
        cwd=repository,
    )

    assert unsupported.returncode != 0
    assert missing.returncode != 0
    assert "prompt" in (missing.stdout + missing.stderr).lower()
    assert not marker.exists()


def _write_work_item(
    repository: Path,
    *,
    item_id: str = "282",
    state: str = "ready",
    priority: int = 3,
    dependencies: list[str] | None = None,
    owned_paths: list[str] | None = None,
    directory: str = ".agent/work-items/282",
) -> Path:
    target = repository / directory / "work-item.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "id": item_id,
                "title": f"Work {item_id}",
                "phase": "business-flow",
                "state": state,
                "priority": priority,
                "hard_dependencies": dependencies or [],
                "acceptance": ["Evidence is current"],
                "owned_paths": owned_paths if owned_paths is not None else ["owned.txt"],
            }
        )
    )
    return target


def test_discovery_uses_structured_nested_items_and_satisfied_dependencies(tmp_path: Path):
    _write_work_item(tmp_path, item_id="100", state="merged", directory="nested/100")
    _write_work_item(tmp_path, item_id="200", state="blocked", directory="nested/200")
    expected = _write_work_item(
        tmp_path,
        item_id="300",
        priority=2,
        dependencies=["100"],
        directory="nested/deeper/300",
    )
    _write_work_item(
        tmp_path,
        item_id="400",
        priority=1,
        dependencies=["200"],
        directory="nested/deeper/400",
    )
    completed_spec = tmp_path / "specs/COMPLETED-999-history/spec.md"
    completed_spec.parent.mkdir(parents=True)
    completed_spec.write_text("## Status: COMPLETE\n")
    research = tmp_path / "specs/001-feature/research.md"
    research.parent.mkdir(parents=True)
    research.write_text("P0 historical proposal\n")

    items = discover_work_items(tmp_path)
    selected = select_ready_work_item(items, phase="business-flow")

    assert selected.path == expected
    assert selected.id == "300"


def test_work_item_rejects_paths_outside_the_owned_repository_scope(tmp_path: Path):
    unsafe = _write_work_item(tmp_path, owned_paths=["../outside.txt"])

    with pytest.raises(RunnerError, match="Unsafe owned path"):
        discover_work_items(unsafe.parent.parent.parent)


def test_explicit_work_item_does_not_bypass_unmet_dependencies(repository: Path):
    item = _write_work_item(repository, dependencies=["missing"])
    result = _run(
        "--repo",
        str(repository),
        "--mode",
        "plan",
        "--prompt",
        str(repository / "prompt.md"),
        "--agent-command",
        str(_executable(repository / "fake-agent", "#!/bin/sh\nexit 0\n")),
        "--work-item",
        str(item),
        cwd=repository,
    )

    assert result.returncode != 0
    assert "unmet hard dependencies" in (result.stdout + result.stderr).lower()


def _builder_agent(repository: Path, *, test_status: str = "passed", stale: bool = False) -> Path:
    source = f"""#!/usr/bin/env python3
import json
import os
import pathlib
import subprocess

pathlib.Path("owned.txt").write_text("after\\n")
subprocess.run(["git", "add", "owned.txt"], check=True)
subprocess.run(["git", "commit", "-m", "Implement owned change"], check=True)
head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
base = subprocess.check_output(["git", "rev-parse", "HEAD^"], text=True).strip()
report_path = pathlib.Path("local-test-report.json").resolve()
report_path.write_text(json.dumps({{
    "schema_version": 1,
    "status": "passed" if {test_status!r} == "passed" else "failed",
    "source_sha": head,
    "tracked_tree_clean": True,
    "totals": {{"tests": 7, "passed": 7, "failures": 0, "errors": 0, "skipped": 0}},
    "tiers": [
        {{"id": tier, "status": "passed", "counts": {{"tests": 1}}}}
        for tier in ("unit", "api", "cli", "integration", "web", "contract", "e2e")
    ],
}}))
evidence = {{
    "schema_version": 1,
    "source_sha": "stale" if {stale!r} else head,
    "base_sha": base,
    "tests": {{
        "status": {test_status!r},
        "command": "make test-all",
        "report_path": str(report_path),
    }},
    "review": {{"status": "passed", "reviewed_head_sha": head, "reviewed_base_sha": base}},
}}
pathlib.Path(os.environ["SIGNUPFLOW_EVIDENCE_PATH"]).write_text(json.dumps(evidence))
print("<promise>DONE</promise>")
"""
    return _executable(repository / "fake-builder", source)


def _fake_gh(repository: Path, *, mergeable: str = "MERGEABLE") -> Path:
    source = f"""#!/usr/bin/env python3
import json
import pathlib
import subprocess
import sys

pathlib.Path("gh-calls.log").open("a").write(" ".join(sys.argv[1:]) + "\\n")
if sys.argv[1:3] == ["pr", "view"]:
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    print(json.dumps({{"mergeable": {mergeable!r}, "mergeStateStatus": "CLEAN", "headRefOid": head}}))
    raise SystemExit(0)
raise SystemExit(0)
"""
    return _executable(repository / "fake-gh", source)


def _run_builder(
    repository: Path,
    *,
    test_status: str = "passed",
    stale: bool = False,
    mergeable: str = "MERGEABLE",
):
    evidence = repository / "evidence.json"
    (repository / "unrelated.txt").write_text("user change\n")
    return _run(
        "--repo",
        str(repository),
        "--mode",
        "build",
        "--prompt",
        str(repository / "prompt.md"),
        "--agent-command",
        str(_builder_agent(repository, test_status=test_status, stale=stale)),
        "--gh-command",
        str(_fake_gh(repository, mergeable=mergeable)),
        "--git-command",
        str(_fake_git(repository)),
        "--work-item",
        str(_write_work_item(repository)),
        "--evidence",
        str(evidence),
        cwd=repository,
    )


def test_builder_accepts_current_evidence_and_preserves_unrelated_dirty_file(repository: Path):
    result = _run_builder(repository)

    assert result.returncode == 0, result.stdout + result.stderr
    assert (repository / "unrelated.txt").read_text() == "user change\n"
    assert (
        subprocess.check_output(["git", "diff", "--name-only"], cwd=repository, text=True).strip()
        == "unrelated.txt"
    )
    assert (
        subprocess.check_output(
            ["git", "show", "--pretty=", "--name-only", "HEAD"], cwd=repository, text=True
        ).strip()
        == "owned.txt"
    )
    git_calls = (repository / "git-calls.log").read_text()
    assert "add owned.txt" in git_calls
    assert "commit -m Implement owned change" in git_calls
    assert (
        "pr view --json mergeable,mergeStateStatus,headRefOid"
        in (repository / "gh-calls.log").read_text()
    )


@pytest.mark.parametrize(
    ("test_status", "stale", "mergeable", "message"),
    [
        ("failed", False, "MERGEABLE", "tests"),
        ("passed", True, "MERGEABLE", "source_sha"),
        ("passed", False, "CONFLICTING", "mergeable"),
    ],
)
def test_builder_rejects_failed_stale_or_nonmergeable_evidence(
    repository: Path, test_status: str, stale: bool, mergeable: str, message: str
):
    result = _run_builder(repository, test_status=test_status, stale=stale, mergeable=mergeable)

    assert result.returncode != 0
    assert message in (result.stdout + result.stderr).lower()


def test_done_text_does_not_override_agent_failure(repository: Path):
    agent = _executable(
        repository / "fake-agent",
        "#!/bin/sh\nprintf '<promise>DONE</promise>\\n'\nexit 7\n",
    )
    result = _run(
        "--repo",
        str(repository),
        "--mode",
        "plan",
        "--prompt",
        str(repository / "prompt.md"),
        "--agent-command",
        str(agent),
        "--work-item",
        str(_write_work_item(repository, owned_paths=[])),
        cwd=repository,
    )

    assert result.returncode != 0
    assert "exit" in (result.stdout + result.stderr).lower()


def test_runner_and_speckit_sources_preserve_local_tdd_policy():
    sources = [
        ROOT / ".claude/commands/speckit.tasks.md",
        ROOT / ".claude/commands/speckit.implement.md",
        ROOT / ".specify/templates/tasks-template.md",
        ROOT / ".specify/templates/feature-progress-template.md",
        ROOT / ".specify/templates/agent-file-template.md",
    ]
    combined = "\n".join(path.read_text() for path in sources)

    assert "Tests are OPTIONAL" not in combined
    assert "tests are optional" not in combined.lower()
    assert "No CI checks" in combined
    assert "Ollama code review" in combined
    assert "tests first" in combined.lower() or "test-driven" in combined.lower()
    assert "Delete feature branch" not in combined


@pytest.mark.parametrize(
    ("wrapper", "provider", "uses_prompt_argument"),
    [("ralph-loop.sh", "claude", False), ("ralph-loop-gemini.sh", "gemini", True)],
)
def test_public_runner_variants_render_the_same_guarded_contract(
    repository: Path, wrapper: str, provider: str, uses_prompt_argument: bool
):
    agent = _executable(
        repository / "fake-agent",
        "#!/usr/bin/env python3\n"
        "import json, pathlib, sys\n"
        "pathlib.Path('agent-argv.json').write_text(json.dumps(sys.argv[1:]))\n"
        "print('<promise>DONE</promise>')\n",
    )
    result = subprocess.run(
        [
            str(ROOT / "scripts" / wrapper),
            "--repo",
            str(repository),
            "--mode",
            "plan",
            "--prompt",
            str(repository / "prompt.md"),
            "--agent-command",
            str(agent),
            "--work-item",
            str(_write_work_item(repository, owned_paths=["agent-argv.json"])),
        ],
        cwd=repository,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Agent workflow complete" in result.stdout
    arguments = json.loads((repository / "agent-argv.json").read_text())
    if uses_prompt_argument:
        assert len(arguments) == 1
        assert "SignUpFlow delegated plan task" in arguments[0]
    else:
        assert arguments == ["-p"]
    assert provider not in result.stderr


def test_feature_generator_does_not_create_a_branch_without_explicit_opt_in(tmp_path: Path):
    fixture = tmp_path / "fixture"
    fixture.mkdir()
    subprocess.run(["git", "init", "-b", "main"], cwd=fixture, check=True, capture_output=True)
    scripts = fixture / ".specify/scripts/bash"
    templates = fixture / ".specify/templates"
    scripts.mkdir(parents=True)
    templates.mkdir(parents=True)
    for name in ("create-new-feature.sh", "common.sh"):
        (scripts / name).write_text((ROOT / ".specify/scripts/bash" / name).read_text())
        (scripts / name).chmod(0o755)
    (templates / "spec-template.md").write_text("# Feature\n")

    result = subprocess.run(
        [str(scripts / "create-new-feature.sh"), "A local workflow"],
        cwd=fixture,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert (
        subprocess.check_output(["git", "branch", "--show-current"], cwd=fixture, text=True).strip()
        == "main"
    )
    assert (fixture / "specs/001-local-workflow/spec.md").is_file()
    assert "BRANCH_CREATED: false" in result.stdout

    opted_in = subprocess.run(
        [str(scripts / "create-new-feature.sh"), "--create-branch", "Another workflow"],
        cwd=fixture,
        text=True,
        capture_output=True,
        check=False,
    )

    assert opted_in.returncode == 0, opted_in.stdout + opted_in.stderr
    assert (
        subprocess.check_output(["git", "branch", "--show-current"], cwd=fixture, text=True).strip()
        == "codex/002-another-workflow"
    )
    assert (fixture / "specs/002-another-workflow/spec.md").is_file()
    assert "BRANCH_CREATED: true" in opted_in.stdout
