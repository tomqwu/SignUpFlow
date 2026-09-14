"""Public documentation and site claims stay aligned with executable product behavior."""

from __future__ import annotations

import re
import tomllib
from html.parser import HTMLParser
from pathlib import Path

from fastapi.routing import APIRoute

from api.main import app

ROOT = Path(__file__).resolve().parents[2]


class _LinkParser(HTMLParser):
    """Collect links and element IDs from the small static site."""

    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"] or "")
        if tag == "a" and values.get("href"):
            self.hrefs.append(values["href"] or "")


def _read(path: str) -> str:
    return (ROOT / path).read_text()


def test_cli_entry_point_and_click_are_direct_dependencies() -> None:
    """A clean Poetry install exposes the CLI without a transitive Click dependency."""
    config = tomllib.loads(_read("pyproject.toml"))

    assert config["tool"]["poetry"]["scripts"]["signupflow"] == "api.cli.main:main"
    assert "click" in config["tool"]["poetry"]["dependencies"]


def test_readme_links_each_domain_scenario_and_current_evidence() -> None:
    """The primary README makes every Church and Basketball scenario discoverable."""
    readme = _read("README.md")
    readme_flat = " ".join(readme.split())

    for prefix, playbook in (("CH", "church"), ("BB", "basketball")):
        for number in range(1, 9):
            scenario_id = f"{prefix}-{number:02d}"
            pattern = rf"\[{scenario_id}\]\(docs/playbooks/{playbook}\.md#six-week-exercise\)"
            assert re.search(pattern, readme), f"README does not link {scenario_id}"

    assert "docs/screenshots/current/manifest.json" in readme
    assert "make test-all" in readme
    assert "GitHub Actions is not test or code-review evidence" in readme_flat


def test_readme_documents_canonical_registered_route_groups() -> None:
    """The route inventory names every mounted API group and no stale solver path."""
    readme = _read("README.md")
    mounted_prefixes = {
        route.path.split("/")[3]
        for route in app.routes
        if isinstance(route, APIRoute) and route.path.startswith("/api/v1/")
    }

    for prefix in mounted_prefixes:
        assert f"/api/v1/{prefix}" in readme, f"README omits mounted route group {prefix}"

    assert "POST /api/v1/solver/solve" in readme
    assert "POST /api/solver/solve" not in readme
    assert "/api/sms" in readme
    assert "webhook" in readme.lower()


def test_readme_badges_and_local_scope_are_truthful() -> None:
    """Badges advertise maintained local evidence without implying hosted test CI."""
    readme = _read("README.md")
    readme_flat = " ".join(readme.split())

    assert "python-3.11--3.13" in readme
    assert "validation-local" in readme
    assert "playbooks-Church_%2B_Basketball" in readme
    assert "actions/workflows" not in readme
    assert "No hosted service, paid plan, or production deployment is included" in readme_flat


def test_public_site_has_no_unavailable_pricing_or_constraint_language_claim() -> None:
    """The static site presents the local product instead of an unavailable service."""
    site = _read("site/index.html")

    for stale_claim in (
        "Plans that scale",
        "Start free",
        "Choose Starter",
        "Choose Pro",
        "API calls / day",
        "Constraints DSL",
        "constraint-based optimization",
    ):
        assert stale_claim not in site

    assert "Church" in site
    assert "Basketball" in site
    assert "Run locally" in site
    assert "No hosted service or paid plan" in site
    assert "docs/playbooks/README.md" in site


def test_retained_examples_do_not_reference_removed_or_retired_surfaces() -> None:
    """Supported examples use SignUpFlow modules and the two accepted domains."""
    example_files = [
        path
        for path in (ROOT / "examples").rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    ]
    combined = "\n".join(path.read_text() for path in example_files)

    assert "roster_cli" not in combined
    assert "Rostio" not in combined
    assert "cricket" not in combined.lower()
    retired_cricket = ROOT / "test_data" / "cricket_custom"
    assert not retired_cricket.exists() or not any(
        path.is_file() for path in retired_cricket.rglob("*")
    )
    assert (ROOT / "examples" / "church" / "org.yaml").is_file()
    assert (ROOT / "examples" / "basketball" / "org.yaml").is_file()


def test_readme_and_static_site_local_links_resolve() -> None:
    """Every repository-relative README link and static-site anchor has a target."""
    readme = _read("README.md")
    local_targets = re.findall(r"!?\[[^]]*]\((?!https?://|mailto:|#)([^)#]+)", readme)
    missing = [target for target in local_targets if not (ROOT / target).exists()]
    assert not missing, f"README links to missing local paths: {missing}"

    parser = _LinkParser()
    parser.feed(_read("site/index.html"))
    missing_anchors = [
        href for href in parser.hrefs if href.startswith("#") and href[1:] not in parser.ids
    ]
    assert not missing_anchors, f"Static site links to missing anchors: {missing_anchors}"
