"""Keep the browser journey audit complete as routes and templates evolve."""

from __future__ import annotations

import ast
import json
from pathlib import Path

from web.app import router

ROOT = Path(__file__).resolve().parents[2]
MATRIX_PATH = ROOT / "docs" / "web-journey-matrix.json"


def _load_matrix():
    return json.loads(MATRIX_PATH.read_text(encoding="utf-8"))


def _test_functions(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
        and node.name.startswith("test_")
    }


def test_matrix_covers_every_web_route_and_template():
    matrix = _load_matrix()
    documented_routes = {
        (entry["method"], entry["path"], entry["name"]) for entry in matrix["routes"]
    }
    actual_routes = {
        (method, route.path, route.name)
        for route in router.routes
        for method in (route.methods or set()) - {"HEAD", "OPTIONS"}
    }
    assert documented_routes == actual_routes

    documented_templates = set(matrix["templates"])
    actual_templates = {
        str(path.relative_to(ROOT)) for path in (ROOT / "web" / "templates").rglob("*.html")
    }
    assert documented_templates == actual_templates


def test_every_matrix_case_has_resolvable_happy_error_and_permission_evidence():
    matrix = _load_matrix()
    case_ids = set(matrix["cases"])
    assert {entry["case"] for entry in matrix["routes"]} <= case_ids
    assert set(matrix["templates"].values()) <= case_ids

    parsed_files: dict[Path, set[str]] = {}
    for case_id, case in matrix["cases"].items():
        assert case["title"], case_id
        for evidence_kind in ("happy", "error", "permission"):
            evidence = case[evidence_kind]
            assert evidence, f"{case_id} lacks {evidence_kind} evidence"
            for item in evidence:
                if item.startswith("limitation:"):
                    assert len(item.removeprefix("limitation:").strip()) >= 20
                    continue
                relative_path, separator, function_name = item.partition("::")
                assert separator, f"{case_id} has invalid evidence: {item}"
                path = ROOT / relative_path
                assert path.is_file(), item
                parsed_files.setdefault(path, _test_functions(path))
                assert function_name in parsed_files[path], item
