"""Keep the documentation disposition ledger complete and actionable."""

from pathlib import Path

import pytest
import yaml

from scripts.validate_documentation import validate_documentation

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "docs" / "documentation_ledger.yaml"


@pytest.mark.unit
def test_documentation_ledger_covers_every_tracked_markdown_file() -> None:
    result = validate_documentation(ROOT, LEDGER)

    assert result.errors == [], "\n".join(result.errors)
    assert result.manual_count == 189
    assert result.generated_count == 138


@pytest.mark.unit
def test_new_manual_document_without_disposition_fails(tmp_path: Path) -> None:
    ledger = yaml.safe_load(LEDGER.read_text(encoding="utf-8"))
    ledger["files"].pop("README.md")
    incomplete = tmp_path / "ledger.yaml"
    incomplete.write_text(yaml.safe_dump(ledger), encoding="utf-8")

    result = validate_documentation(ROOT, incomplete)

    assert "README.md: tracked manual document is missing from the ledger" in result.errors


@pytest.mark.unit
def test_missing_current_relative_link_reports_source_and_target(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    docs = root / "docs"
    docs.mkdir(parents=True)
    (root / "README.md").write_text("[missing](docs/not-there.md)\n", encoding="utf-8")
    (docs / "current.md").write_text("# Present heading\n", encoding="utf-8")
    (docs / "historical.md").write_text("[old](retired.md)\n", encoding="utf-8")
    (root / "README.md").write_text(
        "[missing](docs/not-there.md)\n[anchor](docs/current.md#absent-heading)\n",
        encoding="utf-8",
    )
    ledger = docs / "ledger.yaml"
    ledger.write_text(
        yaml.safe_dump(
            {
                "schema_version": 1,
                "review": {"date": "2026-09-15", "source_sha": "test"},
                "generated_cohorts": [],
                "files": {
                    "README.md": {
                        "status": "current",
                        "canonical": "README.md",
                        "owner": "#277",
                        "sources": ["README.md"],
                        "outcome": "reviewed",
                    },
                    "docs/historical.md": {
                        "status": "historical",
                        "canonical": "README.md",
                        "owner": "#277",
                        "sources": ["README.md"],
                        "outcome": "retained with historical-link exception",
                    },
                    "docs/current.md": {
                        "status": "current",
                        "canonical": "docs/current.md",
                        "owner": "#277",
                        "sources": ["README.md"],
                        "outcome": "reviewed",
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    result = validate_documentation(root, ledger)

    assert "README.md: missing relative target docs/not-there.md" in result.errors
    assert "README.md: missing anchor docs/current.md#absent-heading" in result.errors
    assert not any("retired.md" in error for error in result.errors)
