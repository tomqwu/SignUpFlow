"""Smoke tests for the OpenAPI schema, focused on codegen-friendly operation IDs."""

import re

from fastapi.routing import APIRoute

from api.main import app


def _all_api_routes():
    return [r for r in app.routes if isinstance(r, APIRoute)]


def test_every_api_route_has_operation_id():
    """No route is left with the FastAPI default `<name>_<method>_<path>` slug."""
    for route in _all_api_routes():
        assert route.operation_id, f"Missing operation_id on {route.path}"


def test_operation_ids_are_camel_case():
    """Operation IDs start lowercase, contain no underscores, and aren't slug-style."""
    pattern = re.compile(r"^[a-z][a-zA-Z0-9]*$")
    for route in _all_api_routes():
        assert pattern.match(
            route.operation_id
        ), f"operation_id {route.operation_id!r} on {route.path} is not camelCase"
        # Reject FastAPI auto-generated slugs which end in _get/_post/etc.
        assert not route.operation_id.endswith(("_get", "_post", "_put", "_delete", "_patch"))


def test_operation_ids_are_unique():
    """openapi-generator emits one method per operationId; collisions break codegen."""
    ids = [r.operation_id for r in _all_api_routes()]
    assert len(ids) == len(set(ids)), "Duplicate operationIds detected"


def test_well_known_operation_ids_exist():
    """Canonical names the Flutter client will reach for."""
    ids = {r.operation_id for r in _all_api_routes()}
    expected = {
        "getCurrentPerson",
        "listPeople",
        "createPerson",
        "getPerson",
        "updatePerson",
        "deletePerson",
        "createEvent",
        "listEvents",
        "solveSchedule",
        "login",
        "signup",
    }
    missing = expected - ids
    assert not missing, f"Missing expected operation IDs: {missing}"


def test_openapi_schema_renders():
    """app.openapi() must succeed and include /api/v1 paths."""
    schema = app.openapi()
    assert schema["openapi"].startswith("3.")
    assert any(p.startswith("/api/v1") for p in schema["paths"])
