"""Deterministic public screenshot capture and manifest validation."""

from __future__ import annotations

import hashlib
import json
import os
import struct
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from pydantic import BaseModel, ConfigDict, Field

CAPTURE_DIRECTORY_ENV = "SIGNUPFLOW_SCREENSHOT_CAPTURE_DIR"
CAPTURE_SOURCE_ENV = "SIGNUPFLOW_SCREENSHOT_SOURCE_REF"
CAPTURE_DATE = "2030-01-09"
CAPTURE_START_DATE = "2030-01-13"
CAPTURE_NOW = "2030-01-09T12:00:00+00:00"
CAPTURE_WIDTHS = (360, 1440)
CAPTURE_DOMAINS = ("basketball", "church")


@dataclass(frozen=True)
class CaptureState:
    scenario: str | dict[str, str]
    actor: str
    caption: str | dict[str, str]
    asserted_state: str
    source_files: tuple[str, ...]

    def value(self, field: str, domain: str) -> str:
        value = getattr(self, field)
        return cast(str, value[domain] if isinstance(value, dict) else value)


_COMMON = ("web/templates/base.html", "web/static/css/styles.css")
CAPTURE_STATES = {
    "dashboard": CaptureState(
        scenario="BO-01",
        actor="administrator",
        caption={
            "church": "Church administrator dashboard",
            "basketball": "Basketball manager dashboard",
        },
        asserted_state="Fresh organization is tenant-scoped and commerce is absent",
        source_files=(*_COMMON, "web/templates/admin/dashboard.html"),
    ),
    "onboarding": CaptureState(
        scenario="BO-01",
        actor="administrator",
        caption={
            "church": "Church setup checklist",
            "basketball": "Basketball setup checklist",
        },
        asserted_state="Fresh administrator sees zero of four setup steps complete",
        source_files=(*_COMMON, "web/templates/admin/onboarding.html"),
    ),
    "qualified": CaptureState(
        scenario="BO-02",
        actor="administrator",
        caption={
            "church": "Church qualified member directory",
            "basketball": "Basketball qualified member directory",
        },
        asserted_state="Every fixture role is represented by invited qualified members",
        source_files=(
            *_COMMON,
            "web/templates/admin/people.html",
            "web/templates/partials/people_list.html",
        ),
    ),
    "six-week-solution": CaptureState(
        scenario="BO-04",
        actor="administrator",
        caption={
            "church": "Church six-week solution",
            "basketball": "Basketball six-week solution",
        },
        asserted_state="All twelve events have exact qualified staffing and zero hard violations",
        source_files=(
            *_COMMON,
            "web/templates/admin/solution_review.html",
            "web/templates/partials/solution_assignments.html",
        ),
    ),
    "unanswered": CaptureState(
        scenario="BO-05",
        actor="member",
        caption={
            "church": "Church member unanswered schedule",
            "basketball": "Basketball player unanswered schedule",
        },
        asserted_state="Published work remains unanswered until the member explicitly responds",
        source_files=(*_COMMON, "web/templates/volunteer/schedule.html"),
    ),
    "accepted": CaptureState(
        scenario="BO-05",
        actor="member",
        caption={
            "church": "Church member accepted commitment",
            "basketball": "Basketball player accepted commitment",
        },
        asserted_state="Current commitment revision is explicitly accepted and survives login",
        source_files=(
            *_COMMON,
            "web/templates/volunteer/assignment_detail.html",
            "web/templates/partials/assignment_detail_card.html",
        ),
    ),
    "replacement-needed": CaptureState(
        scenario={"church": "CH-D01", "basketball": "BB-D02"},
        actor="administrator",
        caption={
            "church": "Church qualified replacement needed",
            "basketball": "Basketball qualified replacement needed",
        },
        asserted_state="A late withdrawal exposes the exact role as unresolved",
        source_files=(
            *_COMMON,
            "web/templates/admin/swaps.html",
            "web/templates/partials/swaps_list.html",
        ),
    ),
    "replacement-covered": CaptureState(
        scenario={"church": "CH-D01", "basketball": "BB-D02"},
        actor="reserve",
        caption={
            "church": "Church reserve covered assignment",
            "basketball": "Basketball reserve covered assignment",
        },
        asserted_state="One available exact-role reserve owns the accepted replacement",
        source_files=(
            *_COMMON,
            "web/templates/volunteer/schedule.html",
            "web/templates/volunteer/assignment_detail.html",
            "web/templates/partials/assignment_detail_card.html",
        ),
    ),
    "schedule-change-admin": CaptureState(
        scenario={"church": "CH-D03", "basketball": "BB-D03"},
        actor="administrator",
        caption={
            "church": "Church holiday service published",
            "basketball": "Basketball postponed game published",
        },
        asserted_state="Changed schedule is minimized, compared, published, and notified",
        source_files=(
            *_COMMON,
            "web/templates/admin/solution_review.html",
            "web/templates/partials/publish_state.html",
        ),
    ),
    "schedule-change-member": CaptureState(
        scenario={"church": "CH-D03", "basketball": "BB-D03"},
        actor="member",
        caption={
            "church": "Church member holiday commitment",
            "basketball": "Basketball player postponed commitment",
        },
        asserted_state="Member sees and explicitly accepts the current changed commitment",
        source_files=(
            *_COMMON,
            "web/templates/volunteer/assignment_detail.html",
            "web/templates/partials/assignment_detail_card.html",
        ),
    ),
    "week-seven-rollover": CaptureState(
        scenario="BO-08",
        actor="administrator",
        caption={
            "church": "Church week-seven rollover",
            "basketball": "Basketball week-seven rollover",
        },
        asserted_state="Completed history remains while the next six-week horizon is published",
        source_files=(
            *_COMMON,
            "web/templates/admin/events.html",
            "web/templates/partials/events_list.html",
        ),
    ),
}


class ScreenshotEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    domain: str
    viewport: dict[str, int]
    scenario: str
    actor: str
    caption: str
    asserted_state: str
    image_sha256: str
    fixture_path: str
    fixture_sha256: str
    source_files: dict[str, str]


class ScreenshotManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: int = 1
    source_ref: str = Field(pattern=r"^[0-9a-f]{40}$")
    scenario_date: str
    captured_at: datetime
    browser: str
    entries: list[ScreenshotEntry]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as image:
        header = image.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Not a PNG image: {path}")
    return struct.unpack(">II", header[16:24])


def expected_capture_keys() -> set[tuple[str, int, str]]:
    return {
        (domain, width, state)
        for domain in CAPTURE_DOMAINS
        for width in CAPTURE_WIDTHS
        for state in CAPTURE_STATES
    }


def capture_screenshot(page: Any, tmp_path: Path, domain: str, width: int, state: str) -> Path:
    """Capture to pytest temp storage, or to the owned public capture directory."""
    if state not in CAPTURE_STATES:
        raise ValueError(f"Unknown screenshot state: {state}")
    root_value = os.getenv(CAPTURE_DIRECTORY_ENV)
    if root_value:
        source_ref = os.getenv(CAPTURE_SOURCE_ENV, "")
        if len(source_ref) != 40:
            raise ValueError(f"{CAPTURE_SOURCE_ENV} must be a full commit SHA")
        root = Path(root_value)
        path = root / domain / str(width) / f"{state}.png"
        record_path = root / ".records" / f"{domain}-{width}-{state}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        record_path.parent.mkdir(parents=True, exist_ok=True)
        browser = page.context.browser
        record = {
            "domain": domain,
            "width": width,
            "state": state,
            "browser": f"Chromium {browser.version if browser else 'unknown'}",
            "captured_at": datetime.now(UTC).isoformat(),
            "source_ref": source_ref,
        }
        record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    else:
        path = tmp_path / f"{domain}-{width}-{state}.png"
    page.screenshot(path=str(path), full_page=True)
    return path


def finalize_capture(capture_root: Path, repo_root: Path, source_ref: str) -> Path:
    """Validate capture records and write one reproducible public manifest."""
    records = [
        json.loads(path.read_text()) for path in sorted((capture_root / ".records").glob("*.json"))
    ]
    actual = {(record["domain"], record["width"], record["state"]) for record in records}
    missing = expected_capture_keys() - actual
    unexpected = actual - expected_capture_keys()
    if missing or unexpected:
        raise ValueError(
            f"Screenshot matrix mismatch; missing={sorted(missing)}, unexpected={sorted(unexpected)}"
        )
    if any(record["source_ref"] != source_ref for record in records):
        raise ValueError("Capture records do not match the requested source commit")

    entries = []
    for record in records:
        domain = record["domain"]
        width = record["width"]
        state_name = record["state"]
        state = CAPTURE_STATES[state_name]
        image_path = capture_root / domain / str(width) / f"{state_name}.png"
        image_width, image_height = _png_dimensions(image_path)
        if image_width != width or image_height < 900:
            raise ValueError(
                f"Unexpected screenshot dimensions for {image_path}: {image_width}x{image_height}"
            )
        fixture_path = Path("docs/playbooks") / f"{domain}.json"
        entries.append(
            {
                "path": image_path.relative_to(repo_root).as_posix(),
                "domain": domain,
                "viewport": {"width": width, "height": 900},
                "scenario": state.value("scenario", domain),
                "actor": state.actor,
                "caption": state.value("caption", domain),
                "asserted_state": state.asserted_state,
                "image_sha256": _sha256(image_path),
                "fixture_path": fixture_path.as_posix(),
                "fixture_sha256": _sha256(repo_root / fixture_path),
                "source_files": {path: _sha256(repo_root / path) for path in state.source_files},
            }
        )

    captured_at = max(datetime.fromisoformat(record["captured_at"]) for record in records)
    browsers = {record["browser"] for record in records}
    if len(browsers) != 1:
        raise ValueError(f"Capture used multiple browser versions: {sorted(browsers)}")
    manifest = ScreenshotManifest(
        source_ref=source_ref,
        scenario_date=CAPTURE_DATE,
        captured_at=captured_at,
        browser=browsers.pop(),
        entries=[ScreenshotEntry.model_validate(entry) for entry in entries],
    )
    manifest_path = capture_root / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    for path in (capture_root / ".records").glob("*.json"):
        path.unlink()
    (capture_root / ".records").rmdir()
    validate_manifest(manifest_path, repo_root)
    return manifest_path


def validate_manifest(
    manifest_path: Path,
    repo_root: Path,
    *,
    expected_keys: set[tuple[str, int, str]] | None = None,
) -> ScreenshotManifest:
    """Reject missing, altered, stale, or semantically mislabeled captures."""
    manifest = ScreenshotManifest.model_validate_json(manifest_path.read_text())
    expected = expected_capture_keys() if expected_keys is None else expected_keys
    actual = set()
    for entry in manifest.entries:
        image_path = repo_root / entry.path
        state_name = image_path.stem
        key = (entry.domain, entry.viewport["width"], state_name)
        actual.add(key)
        state = CAPTURE_STATES.get(state_name)
        if state is None:
            raise ValueError(f"Unknown screenshot state in manifest: {state_name}")
        if entry.scenario != state.value("scenario", entry.domain):
            raise ValueError(f"Scenario mismatch for {entry.path}")
        if entry.actor != state.actor or entry.caption != state.value("caption", entry.domain):
            raise ValueError(f"Actor or caption mismatch for {entry.path}")
        if not image_path.is_file() or _sha256(image_path) != entry.image_sha256:
            raise ValueError(f"Missing or altered screenshot: {entry.path}")
        image_width, image_height = _png_dimensions(image_path)
        if image_width != entry.viewport["width"] or image_height < entry.viewport["height"]:
            raise ValueError(f"Viewport mismatch for {entry.path}")
        fixture_path = repo_root / entry.fixture_path
        if not fixture_path.is_file() or _sha256(fixture_path) != entry.fixture_sha256:
            raise ValueError(f"Fixture drift for {entry.path}")
        for source_path, expected_hash in entry.source_files.items():
            path = repo_root / source_path
            if not path.is_file() or _sha256(path) != expected_hash:
                raise ValueError(f"UI source drift for {entry.path}: {source_path}")
    if actual != expected:
        raise ValueError(
            f"Manifest matrix mismatch; missing={sorted(expected - actual)}, unexpected={sorted(actual - expected)}"
        )
    return manifest


def validate_readme_references(readme_path: Path, manifest: ScreenshotManifest) -> None:
    """Require every README screenshot alt caption to match its manifest entry."""
    import re

    references = re.findall(
        r"!\[([^]]+)]\((docs/screenshots/current/[^)]+\.png)\)", readme_path.read_text()
    )
    if not references:
        raise ValueError("README does not reference current screenshot captures")
    by_path = {entry.path: entry for entry in manifest.entries}
    for caption, path in references:
        if path not in by_path:
            raise ValueError(f"README references screenshot outside the manifest: {path}")
        if caption != by_path[path].caption:
            raise ValueError(f"README caption mismatch for {path}")
