import json
import struct
import zlib
from hashlib import sha256
from pathlib import Path

import pytest

from tests.playbooks.screenshots import (
    CAPTURE_STATES,
    ScreenshotManifest,
    validate_manifest,
    validate_readme_references,
)

pytestmark = pytest.mark.unit


def _png(path: Path, width: int = 360, height: int = 900) -> None:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
        )

    row = b"\x00" + b"\xff\xff\xff" * width
    payload = zlib.compress(row * height)
    path.parent.mkdir(parents=True)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", payload)
        + chunk(b"IEND", b"")
    )


def _manifest(tmp_path: Path) -> tuple[Path, Path, dict]:
    repo = tmp_path / "repo"
    image = repo / "docs/screenshots/current/church/360/dashboard.png"
    fixture = repo / "docs/playbooks/church.json"
    source = repo / "web/templates/base.html"
    _png(image)
    fixture.parent.mkdir(parents=True)
    fixture.write_text("{}")
    source.parent.mkdir(parents=True)
    source.write_text("base")
    state = CAPTURE_STATES["dashboard"]
    data = {
        "schema_version": 1,
        "source_ref": "a" * 40,
        "scenario_date": "2030-01-06",
        "captured_at": "2030-01-01T00:00:00Z",
        "browser": "Chromium test",
        "entries": [
            {
                "path": image.relative_to(repo).as_posix(),
                "domain": "church",
                "viewport": {"width": 360, "height": 900},
                "device_scale_factor": 1,
                "pixel_size": {"width": 360, "height": 900},
                "scenario": state.value("scenario", "church"),
                "actor": state.actor,
                "caption": state.value("caption", "church"),
                "asserted_state": state.asserted_state,
                "image_sha256": sha256(image.read_bytes()).hexdigest(),
                "fixture_path": fixture.relative_to(repo).as_posix(),
                "fixture_sha256": sha256(fixture.read_bytes()).hexdigest(),
                "source_files": {
                    source.relative_to(repo).as_posix(): sha256(source.read_bytes()).hexdigest()
                },
            }
        ],
    }
    manifest = image.parents[2] / "manifest.json"
    manifest.write_text(json.dumps(data))
    return repo, manifest, data


def test_manifest_rejects_missing_image(tmp_path):
    repo, manifest, _ = _manifest(tmp_path)
    (repo / "docs/screenshots/current/church/360/dashboard.png").unlink()
    with pytest.raises(ValueError, match="Missing or altered screenshot"):
        validate_manifest(manifest, repo, expected_keys={("church", 360, "dashboard")})


def test_manifest_rejects_ui_source_drift(tmp_path):
    repo, manifest, _ = _manifest(tmp_path)
    (repo / "web/templates/base.html").write_text("changed")
    with pytest.raises(ValueError, match="UI source drift"):
        validate_manifest(manifest, repo, expected_keys={("church", 360, "dashboard")})


def test_manifest_rejects_wrong_scenario(tmp_path):
    repo, manifest, data = _manifest(tmp_path)
    data["entries"][0]["scenario"] = "BB-D03"
    manifest.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="Scenario mismatch"):
        validate_manifest(manifest, repo, expected_keys={("church", 360, "dashboard")})


def test_readme_caption_must_match_manifest(tmp_path):
    repo, manifest_path, _ = _manifest(tmp_path)
    manifest = ScreenshotManifest.model_validate_json(manifest_path.read_text())
    readme = repo / "README.md"
    readme.write_text("![Wrong caption](docs/screenshots/current/church/360/dashboard.png)")
    with pytest.raises(ValueError, match="caption mismatch"):
        validate_readme_references(readme, manifest)


def test_committed_screenshot_manifest_is_current():
    repo = Path(__file__).resolve().parents[2]
    manifest = validate_manifest(repo / "docs/screenshots/current/manifest.json", repo)
    validate_readme_references(repo / "README.md", manifest)
