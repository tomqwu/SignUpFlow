"""Smoke tests for the OpenAPI schema, focused on codegen-friendly operation IDs."""

import re

from fastapi.routing import APIRoute, RouteContext, iter_route_contexts

from api.main import app


def _all_api_routes():
    # Only schema routes: these checks are about the OpenAPI / Dart-codegen
    # surface. The web app (Sprint 11) mounts HTML routes with
    # include_in_schema=False — they're not API endpoints and correctly
    # carry no codegen operationId, so they're excluded here just as they
    # are from /openapi.json and the contract snapshot.
    return [
        route
        for route in iter_route_contexts(app.routes)
        if isinstance(route.original_route, APIRoute) and route.include_in_schema
    ]


def _operation_id(route: RouteContext) -> str:
    return route.operation_id or route.unique_id


def test_every_api_route_has_operation_id():
    """No route is left with the FastAPI default `<name>_<method>_<path>` slug."""
    for route in _all_api_routes():
        assert _operation_id(route), f"Missing operation_id on {route.path}"


def test_operation_ids_are_camel_case():
    """Operation IDs start lowercase, contain no underscores, and aren't slug-style."""
    pattern = re.compile(r"^[a-z][a-zA-Z0-9]*$")
    for route in _all_api_routes():
        operation_id = _operation_id(route)
        assert pattern.match(
            operation_id
        ), f"operation_id {operation_id!r} on {route.path} is not camelCase"
        # Reject FastAPI auto-generated slugs which end in _get/_post/etc.
        assert not operation_id.endswith(("_get", "_post", "_put", "_delete", "_patch"))


def test_operation_ids_are_unique():
    """openapi-generator emits one method per operationId; collisions break codegen."""
    ids = [_operation_id(route) for route in _all_api_routes()]
    assert len(ids) == len(set(ids)), "Duplicate operationIds detected"


def test_well_known_operation_ids_exist():
    """Canonical names the Flutter client will reach for."""
    ids = {_operation_id(route) for route in _all_api_routes()}
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
