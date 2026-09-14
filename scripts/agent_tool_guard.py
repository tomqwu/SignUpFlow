#!/usr/bin/env python3
"""Constrain Git and GitHub commands executed by delegated agents."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

READ_ONLY_GIT = {
    "branch",
    "diff",
    "grep",
    "log",
    "ls-files",
    "merge-base",
    "rev-parse",
    "show",
    "status",
}
READ_ONLY_GH = {
    ("issue", "list"),
    ("issue", "view"),
    ("pr", "checks"),
    ("pr", "diff"),
    ("pr", "list"),
    ("pr", "status"),
    ("pr", "view"),
    ("repo", "view"),
}


def _record(tool: str, arguments: list[str], allowed: bool, reason: str) -> None:
    log_path = Path(os.environ["SIGNUPFLOW_TOOL_GUARD_LOG"])
    payload = {
        "tool": tool,
        "arguments": arguments,
        "allowed": allowed,
        "reason": reason,
    }
    with log_path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(payload, sort_keys=True) + "\n")


def _owned_paths() -> set[str]:
    return set(json.loads(os.environ.get("SIGNUPFLOW_OWNED_PATHS", "[]")))


def _git_allowed(mode: str, arguments: list[str]) -> tuple[bool, str]:
    if not arguments:
        return False, "missing git subcommand"
    if arguments[0].startswith("-"):
        return False, "git global options are not delegated"
    command = arguments[0]
    if command in READ_ONLY_GIT:
        if command == "branch" and any(
            arg not in {"--show-current", "--list", "-a", "--all", "-r", "--remotes", "-v", "-vv"}
            for arg in arguments[1:]
        ):
            return False, "branch mutation is not delegated"
        if any(arg == "--output" or arg.startswith("--output=") for arg in arguments[1:]):
            return False, "read command output files are not delegated"
        return True, "read-only git command"
    if mode != "build":
        return False, f"git {command} is forbidden in {mode} mode"
    if command == "add":
        requested = [arg for arg in arguments[1:] if arg != "--"]
        if not requested or any(arg.startswith("-") or arg in {".", ".."} for arg in requested):
            return False, "git add requires explicit owned paths"
        if not set(requested) <= _owned_paths():
            return False, "git add includes an unowned path"
        return True, "explicit owned paths"
    if command == "commit":
        if any(arg in {"-a", "--all", "--amend"} for arg in arguments[1:]):
            return False, "commit may not stage implicitly or amend history"
        real_git = os.environ["SIGNUPFLOW_REAL_GIT"]
        staged = subprocess.run(
            [real_git, "diff", "--cached", "--name-only"],
            text=True,
            capture_output=True,
            check=False,
        )
        staged_paths = {line for line in staged.stdout.splitlines() if line}
        if staged.returncode != 0 or not staged_paths or not staged_paths <= _owned_paths():
            return False, "commit contains no owned changes or includes unowned paths"
        return True, "owned staged changes"
    if command == "push":
        current_branch = subprocess.run(
            [os.environ["SIGNUPFLOW_REAL_GIT"], "branch", "--show-current"],
            text=True,
            capture_output=True,
            check=False,
        ).stdout.strip()
        positional = [arg for arg in arguments[1:] if arg not in {"-u", "--set-upstream"}]
        allowed_refs = {
            current_branch,
            "HEAD",
            f"HEAD:{current_branch}",
            f"HEAD:refs/heads/{current_branch}",
        }
        if (
            not current_branch
            or any(arg.startswith("-") for arg in positional)
            or positional[:1] not in ([], ["origin"])
            or any(ref not in allowed_refs for ref in positional[1:])
        ):
            return False, "push must target only the current branch on origin without force"
        return True, "current builder branch push"
    return False, f"git {command} is not delegated"


def _gh_allowed(mode: str, arguments: list[str]) -> tuple[bool, str]:
    pair = tuple(arguments[:2])
    if pair in READ_ONLY_GH:
        return True, "read-only GitHub command"
    api_mutation_prefixes = (
        "--method",
        "-X",
        "-f",
        "--field",
        "-F",
        "--raw-field",
        "--input",
    )
    if (
        arguments[:1] == ["api"]
        and arguments[1:2] != ["graphql"]
        and not any(arg.startswith(api_mutation_prefixes) for arg in arguments[1:])
    ):
        return True, "read-only GitHub API request"
    if mode == "build" and pair == ("pr", "create"):
        return True, "builder PR creation"
    return False, "GitHub mutation is not delegated"


def main() -> int:
    tool = Path(sys.argv[0]).name
    arguments = sys.argv[1:]
    mode = os.environ["SIGNUPFLOW_AGENT_MODE"]
    if tool == "git":
        allowed, reason = _git_allowed(mode, arguments)
        real_tool = os.environ["SIGNUPFLOW_REAL_GIT"]
    elif tool == "gh":
        allowed, reason = _gh_allowed(mode, arguments)
        real_tool = os.environ["SIGNUPFLOW_REAL_GH"]
    else:
        print(f"Unsupported guarded tool: {tool}", file=sys.stderr)
        return 97

    _record(tool, arguments, allowed, reason)
    if not allowed:
        print(f"Forbidden tool call: {tool} {' '.join(arguments)} ({reason})", file=sys.stderr)
        return 97
    return subprocess.run([real_tool, *arguments], check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
