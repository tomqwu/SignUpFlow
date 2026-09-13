"""Guard the owner-approved local review and test policy."""

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github/workflows"


@pytest.mark.unit
def test_hosted_workflow_inventory_is_explicit():
    assert {path.name for path in WORKFLOWS.glob("*.y*ml")} == {
        "pages.yml",
    }


@pytest.mark.unit
@pytest.mark.parametrize("filename", ["pages.yml"])
def test_hosted_workflows_do_not_run_tests_or_external_review(filename):
    workflow = yaml.safe_load((WORKFLOWS / filename).read_text())
    source = yaml.safe_dump(workflow)
    assert workflow["jobs"]
    for forbidden in (
        "pytest",
        "make test",
        "flutter test",
        "playwright test",
        "codex-pr-review-gate",
        "OLLAMA_",
        "openai/codex-action",
        "black --check",
        "ruff check",
        "mypy",
        "flutter analyze",
        "alembic upgrade",
    ):
        assert forbidden not in source, f"{filename} contains {forbidden}"


@pytest.mark.unit
@pytest.mark.parametrize("filename", ["AGENTS.md", "CLAUDE.md", ".github/copilot-instructions.md"])
def test_agent_instructions_require_local_review(filename):
    source = (ROOT / filename).read_text()
    assert "local code review" in source
    assert "No CI checks" in source
    assert "Require successful Ollama AI review" not in source
    assert "codex-pr-review-gate" not in source
