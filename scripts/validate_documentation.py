"""Validate the tracked documentation inventory and current local links."""

from __future__ import annotations

import argparse
import fnmatch
import re
import subprocess
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

import yaml

REQUIRED_FIELDS = {"status", "canonical", "owner", "sources", "outcome"}
VALID_STATUSES = {"current", "historical"}
EXTERNAL_SCHEMES = {"data", "http", "https", "mailto", "tel"}


@dataclass(frozen=True)
class DocumentationValidation:
    manual_count: int
    generated_count: int
    errors: list[str]


class _HtmlLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.targets: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        attribute = "src" if tag in {"img", "source"} else "href"
        if values.get(attribute):
            self.targets.append(str(values[attribute]))
        if values.get("id"):
            self.ids.add(str(values["id"]))


def _tracked_markdown(root: Path) -> set[str]:
    if (root / ".git").exists():
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "*.md", "*.md.disabled"],
            check=True,
            capture_output=True,
            text=True,
        )
        return {line for line in result.stdout.splitlines() if line}
    return {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and (path.name.endswith(".md") or path.name.endswith(".md.disabled"))
    }


def _generated_files(tracked: set[str], cohorts: list[dict[str, Any]]) -> set[str]:
    generated: set[str] = set()
    for cohort in cohorts:
        pattern = str(cohort.get("pattern", ""))
        if not pattern or cohort.get("status") != "generated" or not cohort.get("owner"):
            continue
        generated.update(path for path in tracked if fnmatch.fnmatch(path, pattern))
    return generated


def _markdown_targets(source: str) -> list[str]:
    targets: list[str] = []
    index = 0
    while index < len(source):
        start = source.find("](", index)
        if start < 0:
            break
        cursor = start + 2
        depth = 1
        escaped = False
        while cursor < len(source) and depth:
            char = source[cursor]
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
            cursor += 1
        if depth == 0:
            value = source[start + 2 : cursor - 1].strip()
            if value.startswith("<") and value.endswith(">"):
                value = value[1:-1]
            elif " " in value and not value.startswith(("http://", "https://")):
                value = value.split(" ", 1)[0]
            targets.append(value)
        index = max(cursor, start + 2)

    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and "]:" in stripped:
            _, value = stripped.split("]:", 1)
            target = value.strip().split(" ", 1)[0]
            if target:
                targets.append(target)

    parser = _HtmlLinkParser()
    parser.feed(source)
    targets.extend(parser.targets)
    return targets


def _heading_anchors(path: Path) -> set[str]:
    source = path.read_text(encoding="utf-8")
    parser = _HtmlLinkParser()
    parser.feed(source)
    anchors = set(parser.ids)
    seen: dict[str, int] = {}
    in_fence = False
    for line in source.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = re.match(r"^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        heading = re.sub(r"<[^>]+>", "", match.group(1))
        heading = re.sub(r"!?\[([^]]+)]\([^)]*\)", r"\1", heading)
        heading = heading.replace("`", "").lower()
        slug = re.sub(r"[^\w\- ]", "", heading, flags=re.UNICODE).replace(" ", "-")
        duplicate = seen.get(slug, 0)
        anchors.add(slug if duplicate == 0 else f"{slug}-{duplicate}")
        seen[slug] = duplicate + 1
    return anchors


def _target_error(root: Path, source_path: Path, target: str) -> str | None:
    if not target or target.startswith(("{{", "${", "<")):
        return None
    split = urlsplit(target)
    if split.scheme.lower() in EXTERNAL_SCHEMES or split.netloc:
        return None
    raw_path = unquote(split.path).replace("\\", "/")
    candidate = source_path
    if raw_path:
        candidate = (
            root / raw_path.lstrip("/")
            if raw_path.startswith("/")
            else source_path.parent / raw_path
        )
    try:
        candidate.resolve().relative_to(root.resolve())
    except ValueError:
        return f"missing relative target {target}"
    if not candidate.exists():
        return f"missing relative target {target}"
    if split.fragment and candidate.is_file():
        fragment = unquote(split.fragment)
        if fragment not in _heading_anchors(candidate):
            return f"missing anchor {target}"
    return None


def validate_documentation(root: Path, ledger_path: Path) -> DocumentationValidation:
    errors: list[str] = []
    if not ledger_path.exists():
        return DocumentationValidation(0, 0, [f"{ledger_path}: documentation ledger is missing"])

    ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8")) or {}
    if ledger.get("schema_version") != 1:
        errors.append("ledger: schema_version must be 1")
    review = ledger.get("review") or {}
    if not review.get("date") or not review.get("source_sha"):
        errors.append("ledger: review date and source_sha are required")

    tracked = _tracked_markdown(root)
    cohorts = ledger.get("generated_cohorts") or []
    generated = _generated_files(tracked, cohorts)
    manual = tracked - generated
    records = ledger.get("files") or {}

    for path in sorted(manual - set(records)):
        errors.append(f"{path}: tracked manual document is missing from the ledger")
    for path in sorted(set(records) - manual):
        errors.append(f"{path}: ledger row is not a tracked manual document")

    for path in sorted(manual & set(records)):
        record = records[path]
        if not isinstance(record, dict):
            errors.append(f"{path}: ledger row must be a mapping")
            continue
        missing_fields = REQUIRED_FIELDS - set(record)
        if missing_fields:
            errors.append(f"{path}: missing fields {', '.join(sorted(missing_fields))}")
            continue
        if record["status"] not in VALID_STATUSES:
            errors.append(f"{path}: unsupported status {record['status']}")
        if not record["outcome"]:
            errors.append(f"{path}: outcome is required")
        if not isinstance(record["sources"], list) or not record["sources"]:
            errors.append(f"{path}: at least one verified source is required")
        else:
            for source in record["sources"]:
                source_ref = str(source)
                if source_ref.startswith(("#", "command:")):
                    continue
                source_target = root / source_ref.split("#", 1)[0]
                if not source_target.exists():
                    errors.append(f"{path}: verified source {source_ref} is missing")
        canonical = root / str(record["canonical"])
        if not canonical.exists():
            errors.append(f"{path}: canonical target {record['canonical']} is missing")

        if record["status"] != "current":
            if "historical" not in str(record["outcome"]).lower():
                errors.append(f"{path}: historical link exception must be explicit in outcome")
            continue
        source_path = root / path
        for target in _markdown_targets(source_path.read_text(encoding="utf-8")):
            target_error = _target_error(root, source_path, target)
            if target_error:
                errors.append(f"{path}: {target_error}")

    return DocumentationValidation(len(manual), len(generated), errors)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--ledger", type=Path)
    args = parser.parse_args()
    ledger = args.ledger or args.root / "docs" / "documentation_ledger.yaml"
    result = validate_documentation(args.root, ledger)
    if result.errors:
        for error in result.errors:
            print(error)
        return 1
    print(
        f"Documentation validation passed: {result.manual_count} manual, "
        f"{result.generated_count} generated"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
