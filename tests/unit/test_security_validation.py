"""Policy and failure-path tests for local release security validation."""

from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
import yaml

import scripts.run_security_validation as security_validation
from scripts.run_security_validation import (
    SCANNER_IMAGE,
    SecurityValidationError,
    apply_exceptions,
    component_names,
    inventory_inputs,
    license_inventory,
    sanitize_trivy_report,
    validate_exceptions,
)

ROOT = Path(__file__).resolve().parents[2]


def test_scanner_is_an_immutable_trivy_release() -> None:
    assert SCANNER_IMAGE == (
        "ghcr.io/aquasecurity/trivy@"
        "sha256:62b1e65e8869bc4b4c6aa4fa2b21595256c7c2f6018a9d9ad61caf87187c1969"
    )


def test_inventory_covers_runtime_mobile_vendored_and_publication_inputs() -> None:
    inventory = inventory_inputs(ROOT)

    assert set(inventory) >= {
        ".dockerignore",
        "Dockerfile",
        "Dockerfile.dev",
        "docker-compose.yml",
        "docker-compose.dev.yml",
        "poetry.lock",
        "pyproject.toml",
        "mobile/pubspec.lock",
        "mobile/Gemfile.lock",
        "mobile/ios/Podfile.lock",
        "mobile/android/settings.gradle.kts",
        "mobile/android/gradle/wrapper/gradle-wrapper.properties",
        "web/static/js/alpine.min.js",
        "web/static/js/htmx.min.js",
        ".github/workflows/pages.yml",
        "security/trivy-secret.yaml",
    }
    assert all(len(record["sha256"]) == 64 for record in inventory.values())


def test_secret_policy_scans_test_paths_but_preserves_other_builtin_allow_rules() -> None:
    policy = yaml.safe_load((ROOT / "security" / "trivy-secret.yaml").read_text(encoding="utf-8"))

    assert policy == {"disable-allow-rules": ["tests"]}


def test_expired_exception_blocks_and_future_exception_is_usable() -> None:
    now = datetime(2026, 9, 15, tzinfo=UTC)
    base = {
        "id": "SEC-001",
        "finding_key": "image|app|vulnerability|CVE-TEST|pkg|1.0",
        "owner": "repository-owner",
        "rationale": "Harmless test fixture",
        "mitigation": "Not present in a shipped artifact",
    }

    with pytest.raises(SecurityValidationError, match="expired"):
        validate_exceptions(
            {"schema_version": 1, "exceptions": [{**base, "expires_at": "2026-09-14"}]},
            now=now,
        )

    active = validate_exceptions(
        {
            "schema_version": 1,
            "exceptions": [{**base, "expires_at": (now + timedelta(days=7)).date().isoformat()}],
        },
        now=now,
    )
    assert active[0]["id"] == "SEC-001"


def test_exception_expiry_rejects_timestamp_instead_of_date() -> None:
    record = {
        "id": "SEC-001",
        "finding_key": "image|app|vulnerability|CVE-TEST|pkg|1.0",
        "owner": "repository-owner",
        "rationale": "Harmless test fixture",
        "mitigation": "Not present in a shipped artifact",
        "expires_at": "2026-09-30T12:00:00",
    }

    with pytest.raises(SecurityValidationError, match="YYYY-MM-DD"):
        validate_exceptions({"schema_version": 1, "exceptions": [record]})


def test_missing_pinned_scanner_blocks_validation(monkeypatch: pytest.MonkeyPatch) -> None:
    def missing_image(
        command: list[str], *, check: bool = True, timeout: float = 900
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 1, "", "image unavailable")

    monkeypatch.setattr(security_validation, "_run", missing_image)

    with pytest.raises(SecurityValidationError, match="Pinned scanner is unavailable"):
        security_validation._ensure_scanner()


def test_exception_requires_exact_finding_and_does_not_hide_another_package() -> None:
    finding = {
        "key": "image|app|vulnerability|CVE-TEST|pkg|1.0",
        "severity": "HIGH",
        "blocking": True,
    }
    other = {
        "key": "image|app|vulnerability|CVE-TEST|other|1.0",
        "severity": "HIGH",
        "blocking": True,
    }
    exception = {"id": "SEC-001", "finding_key": finding["key"]}

    accepted, blocked = apply_exceptions([finding, other], [exception])

    assert accepted == [{**finding, "exception_id": "SEC-001", "blocking": False}]
    assert blocked == [other]


def test_image_only_component_is_visible_even_when_source_sbom_is_clean() -> None:
    source = {"components": [{"name": "fastapi", "version": "1"}]}
    image = {
        "components": [
            {"name": "fastapi", "version": "1"},
            {"name": "libpq5", "version": "16"},
        ]
    }

    assert component_names(image) - component_names(source) == {"libpq5@16"}


def test_license_inventory_preserves_known_expressions_and_unknowns() -> None:
    sbom = {
        "components": [
            {
                "name": "known",
                "version": "1",
                "licenses": [
                    {"license": {"id": "MIT"}},
                    {"expression": "Apache-2.0 OR BSD-3-Clause"},
                ],
            },
            {"name": "unknown", "version": "2"},
        ]
    }

    assert license_inventory(sbom) == [
        {
            "component": "known@1",
            "licenses": ["Apache-2.0 OR BSD-3-Clause", "MIT"],
        },
        {"component": "unknown@2", "licenses": ["UNKNOWN"]},
    ]


def test_secret_report_is_sanitized_before_persistence() -> None:
    raw = {
        "Results": [
            {
                "Target": "fixture/config.env",
                "Secrets": [
                    {
                        "RuleID": "github-pat",
                        "Category": "GitHub",
                        "Severity": "HIGH",
                        "Match": "ghp_not-for-a-report",
                        "Code": {"Lines": [{"Content": "token=ghp_not-for-a-report"}]},
                    }
                ],
            }
        ]
    }

    findings = sanitize_trivy_report(raw, scope="source")
    encoded = json.dumps(findings)

    assert len(findings) == 1
    assert findings[0]["finding_id"] == "github-pat"
    assert "not-for-a-report" not in encoded
    assert "Match" not in encoded
    assert "Code" not in encoded


def test_dry_run_requires_no_scanner_or_artifact_and_writes_nothing() -> None:
    artifact_root = ROOT / "test-artifacts" / "security-validation"
    before = sorted(artifact_root.iterdir()) if artifact_root.exists() else []

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/run_security_validation.py"), "--dry-run"],
        cwd=ROOT,
        env={"PATH": ""},
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert '"host_install": false' in result.stdout
    assert '"docker_socket": false' in result.stdout
    after = sorted(artifact_root.iterdir()) if artifact_root.exists() else []
    assert after == before


def test_pages_actions_are_pinned_to_reviewed_commits() -> None:
    source = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
    expected = {
        "actions/checkout": "11d5960a326750d5838078e36cf38b85af677262",
        "actions/configure-pages": "983d7736d9b0ae728b81ab479565c72886d7745b",
        "actions/upload-pages-artifact": "56afc609e74202658d3ffba0e8f6dda462b719fa",
        "actions/deploy-pages": "d6db90164ac5ed86f2b6aed7e0febac5b3c0c03e",
    }

    for action, sha in expected.items():
        assert f"uses: {action}@{sha}" in source


def test_pages_publication_uses_only_required_permissions() -> None:
    source = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")

    assert "permissions:\n  contents: read\n  pages: write\n  id-token: write\n" in source
    assert "pull_request:" not in source


def test_production_image_pins_base_and_copies_only_application_virtualenv() -> None:
    source = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    pinned_base = (
        "python:3.11-alpine@"
        "sha256:0d55920083f1ce1e38ac292e2772f924b4f8bb4188d336c79bf66963039e6146"
    )

    assert source.count(f"FROM {pinned_base}") == 2
    assert "COPY --from=builder /opt/venv /opt/venv" in source
    assert "COPY --from=builder /usr/local/lib/python3.11/site-packages" not in source
    assert source.count("apk upgrade --no-cache") == 2
    assert "apk add --no-cache libpq" in source
    assert "install.python-poetry.org" not in source
    assert '"poetry==${POETRY_VERSION}"' in source
    assert '"poetry-plugin-export==1.6.0"' in source
    assert "/opt/venv/bin/pip*" in source
    assert "/opt/venv/lib/python3.11/site-packages/setuptools*" in source
    assert "/usr/local/lib/python3.11/site-packages/setuptools*" in source


def test_development_image_pins_base_and_avoids_remote_installer_script() -> None:
    source = (ROOT / "Dockerfile.dev").read_text(encoding="utf-8")
    pinned_base = (
        "python:3.11-alpine@"
        "sha256:0d55920083f1ce1e38ac292e2772f924b4f8bb4188d336c79bf66963039e6146"
    )

    assert f"FROM {pinned_base}" in source
    assert "apk upgrade --no-cache" in source
    assert "install.python-poetry.org" not in source
    assert "USER signupflow" in source


def test_runtime_jwt_dependency_does_not_ship_unfixed_ecdsa_chain() -> None:
    payload = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = payload["tool"]["poetry"]["dependencies"]

    assert dependencies["pyjwt"] == "^2.14.0"
    assert "python-jose" not in dependencies


def test_python_lock_keeps_remediated_runtime_dependencies() -> None:
    payload = tomllib.loads((ROOT / "poetry.lock").read_text(encoding="utf-8"))
    versions = {package["name"]: package["version"] for package in payload["package"]}

    assert versions["idna"] == "3.19"
    assert versions["python-dotenv"] == "1.2.3"
    assert versions["requests"] == "2.34.2"
    assert versions["werkzeug"] == "3.1.8"


def test_mobile_release_tool_lock_keeps_remediated_fastlane_chain() -> None:
    lock = (ROOT / "mobile" / "Gemfile.lock").read_text(encoding="utf-8")

    assert "    fastlane (2.240.0)" in lock
    assert "    jwt (3.3.0)" in lock
    assert "    rubyzip (3.6.0)" in lock
