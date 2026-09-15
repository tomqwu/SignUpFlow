"""Generate and verify the Dart OpenAPI client without partial worktree writes."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "tests" / "contract" / "openapi.snapshot.json"
GENERATOR_CONFIG = ROOT / "openapitools.json"
CLIENT_DIR = ROOT / "mobile" / "api_client"
WRAPPER_VERSION = "2.20.2"
IGNORED_DIRECTORIES = {".dart_tool", ".git", "build"}
IGNORED_FILES = {".packages", "pubspec.lock"}


class CodegenError(RuntimeError):
    """Describe a preflight, generation, or reproducibility failure."""


@dataclass(frozen=True)
class CodegenTools:
    java: str
    npx: str
    flutter: str
    dart: str
    generator_version: str


def resolve_tool(
    label: str,
    override_name: str,
    *,
    environ: Mapping[str, str] | None = None,
    candidates: Sequence[str] = (),
    which: Callable[[str], str | None] = shutil.which,
) -> str:
    """Resolve an executable from an override, known paths, or PATH."""

    environment = os.environ if environ is None else environ
    override = environment.get(override_name, "").strip()
    attempted = [override] if override else []
    attempted.extend(candidates)
    for candidate in attempted:
        path = Path(candidate).expanduser()
        if path.is_file() and os.access(path, os.X_OK):
            return str(path.resolve())
        resolved = which(candidate)
        if resolved:
            return str(Path(resolved).resolve())
    raise CodegenError(f"{label} executable not found. Set {override_name} to an executable path.")


def prepare_generator_schema(source: Path, destination: Path) -> None:
    """Copy the canonical schema and apply the one documented generator workaround."""

    try:
        schema = json.loads(source.read_text(encoding="utf-8"))
        signup = schema["components"]["schemas"]["SignupRequest"]
    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError) as error:
        raise CodegenError(f"Cannot prepare OpenAPI snapshot {source}: {error}") from error
    if not isinstance(signup, dict):
        raise CodegenError("SignupRequest must be an OpenAPI schema object")
    signup.pop("additionalProperties", None)
    destination.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")


def _generated_files(root: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    if not root.exists():
        return files
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if not path.is_file():
            continue
        if any(part in IGNORED_DIRECTORIES for part in relative.parts):
            continue
        if path.name in IGNORED_FILES:
            continue
        files[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def diff_generated_trees(left: Path, right: Path) -> list[str]:
    """Return stable, human-readable differences between generated trees."""

    left_files = _generated_files(left)
    right_files = _generated_files(right)
    differences: list[str] = []
    for path in sorted(left_files.keys() | right_files.keys()):
        if path not in left_files:
            differences.append(f"new: {path}")
        elif path not in right_files:
            differences.append(f"missing from regenerated output: {path}")
        elif left_files[path] != right_files[path]:
            differences.append(f"changed: {path}")
    return differences


def normalize_generated_text(root: Path) -> None:
    """Remove generator-only whitespace noise without changing binary files."""

    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if not path.is_file() or any(part in IGNORED_DIRECTORIES for part in relative.parts):
            continue
        try:
            source = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        lines = [line.rstrip(" \t") for line in source.splitlines()]
        while lines and not lines[-1]:
            lines.pop()
        normalized = "\n".join(lines)
        if normalized:
            normalized += "\n"
        if normalized != source:
            path.write_text(normalized, encoding="utf-8")


def _run(
    command: Sequence[str],
    *,
    cwd: Path = ROOT,
    env: Mapping[str, str] | None = None,
    capture: bool = False,
) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(command))
    result = subprocess.run(
        list(command),
        cwd=cwd,
        env=dict(env) if env is not None else None,
        text=True,
        capture_output=capture,
        check=False,
    )
    if result.returncode:
        details = ""
        if capture:
            details = f"\n{result.stdout}{result.stderr}".rstrip()
        raise CodegenError(
            f"Command failed with exit {result.returncode}: {' '.join(command)}{details}"
        )
    return result


def _generator_environment(java: str) -> dict[str, str]:
    environment = dict(os.environ)
    environment["PATH"] = f"{Path(java).parent}{os.pathsep}{environment.get('PATH', '')}"
    return environment


def _configured_generator_version() -> str:
    try:
        config = json.loads(GENERATOR_CONFIG.read_text(encoding="utf-8"))
        version = config["generator-cli"]["version"]
    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError) as error:
        raise CodegenError(
            f"Cannot read generator version from {GENERATOR_CONFIG}: {error}"
        ) from error
    if not isinstance(version, str) or not version:
        raise CodegenError("openapitools.json must pin generator-cli.version")
    return version


def preflight() -> CodegenTools:
    """Resolve tools, verify pinned versions, and validate the canonical schema."""

    java = resolve_tool(
        "Java",
        "JAVA_BIN",
        candidates=(
            "/opt/homebrew/opt/openjdk@17/bin/java",
            "/opt/homebrew/opt/openjdk/bin/java",
            "/usr/local/opt/openjdk@17/bin/java",
            "/usr/local/opt/openjdk/bin/java",
            "java",
        ),
    )
    npx = resolve_tool("npx", "NPX", candidates=("npx",))
    flutter = resolve_tool("Flutter", "FLUTTER", candidates=("flutter",))
    dart = resolve_tool(
        "Dart",
        "DART",
        candidates=(str(Path(flutter).with_name("dart")), "dart"),
    )
    generator_version = _configured_generator_version()
    environment = _generator_environment(java)

    _run([java, "-version"], env=environment)
    version_result = _run(
        [npx, "-y", f"@openapitools/openapi-generator-cli@{WRAPPER_VERSION}", "version"],
        env=environment,
        capture=True,
    )
    actual_version = version_result.stdout.strip().splitlines()[-1]
    if actual_version != generator_version:
        raise CodegenError(
            f"Generator version mismatch: expected {generator_version}, got {actual_version}"
        )
    _run(
        [
            npx,
            "-y",
            f"@openapitools/openapi-generator-cli@{WRAPPER_VERSION}",
            "validate",
            "-i",
            str(SNAPSHOT),
        ],
        env=environment,
    )
    print(
        "Preflight passed: "
        f"generator wrapper {WRAPPER_VERSION}, generator {generator_version}, "
        f"Java {java}, Flutter {flutter}, Dart {dart}"
    )
    return CodegenTools(java, npx, flutter, dart, generator_version)


def _generate_once(tools: CodegenTools, destination: Path) -> None:
    destination.mkdir(parents=True)
    prepared_schema = destination.parent / f"{destination.name}-openapi.json"
    prepare_generator_schema(SNAPSHOT, prepared_schema)
    environment = _generator_environment(tools.java)
    _run(
        [
            tools.npx,
            "-y",
            f"@openapitools/openapi-generator-cli@{WRAPPER_VERSION}",
            "generate",
            "-i",
            str(prepared_schema),
            "-g",
            "dart-dio",
            "-o",
            str(destination),
            "--additional-properties=pubName=signupflow_api,pubVersion=0.0.1,"
            "nullSafe=true,nullableFields=true",
        ],
        env=environment,
    )
    _run([tools.dart, "pub", "get"], cwd=destination)
    _run([tools.dart, "run", "build_runner", "build"], cwd=destination)
    normalize_generated_text(destination)


def _sync_generated_tree(source: Path, destination: Path) -> None:
    source_files = _generated_files(source)
    destination_files = _generated_files(destination)
    for relative in sorted(destination_files.keys() - source_files.keys(), reverse=True):
        (destination / relative).unlink()
    for relative in sorted(source_files):
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / relative, target)
    for directory in sorted(destination.rglob("*"), reverse=True):
        if directory.is_dir() and directory.name not in IGNORED_DIRECTORIES:
            try:
                directory.rmdir()
            except OSError:
                pass


def generate(*, check: bool) -> None:
    """Generate twice, prove determinism, then check or update the tracked client."""

    tools = preflight()
    with tempfile.TemporaryDirectory(prefix="signupflow-mobile-codegen-") as temporary:
        temp_root = Path(temporary)
        first = temp_root / "first"
        second = temp_root / "second"
        _generate_once(tools, first)
        _generate_once(tools, second)
        deterministic_diff = diff_generated_trees(first, second)
        if deterministic_diff:
            joined = "\n".join(deterministic_diff[:100])
            raise CodegenError(f"Two generation runs differ:\n{joined}")
        print("Determinism passed: two generated trees are identical.")

        tracked_diff = diff_generated_trees(CLIENT_DIR, first)
        if check:
            if tracked_diff:
                joined = "\n".join(tracked_diff[:100])
                raise CodegenError(f"Generated client drift detected:\n{joined}")
            print("Generated client matches the canonical OpenAPI snapshot.")
            return

        _sync_generated_tree(first, CLIENT_DIR)
        _run([tools.flutter, "pub", "get"], cwd=ROOT / "mobile")
        print(f"Updated generated client at {CLIENT_DIR}.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--preflight", action="store_true")
    action.add_argument("--check", action="store_true")
    action.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        if args.preflight:
            preflight()
        else:
            generate(check=args.check)
    except CodegenError as error:
        print(f"Mobile codegen failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
