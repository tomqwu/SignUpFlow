"""Keep every mounted API route in the reviewed authentication policy."""

from fastapi.routing import APIRoute

from api.main import app
from api.route_auth_policy import ROUTE_AUTH_POLICY


def _dependency_names(route: APIRoute) -> set[str]:
    names: set[str] = set()
    pending = list(route.dependant.dependencies)
    while pending:
        dependency = pending.pop()
        names.add(getattr(dependency.call, "__name__", str(dependency.call)))
        pending.extend(dependency.dependencies)
    return names


def test_every_api_route_matches_the_explicit_auth_policy():
    routes = {
        route.name: route
        for route in app.routes
        if isinstance(route, APIRoute)
        and (route.path.startswith("/api") or route.path in {"/health", "/ready"})
    }

    assert set(ROUTE_AUTH_POLICY) == set(routes)

    for operation_name, policy in ROUTE_AUTH_POLICY.items():
        dependencies = _dependency_names(routes[operation_name])
        if policy == "admin":
            assert "get_current_admin_user" in dependencies, operation_name
        elif policy == "member":
            assert "get_current_user" in dependencies, operation_name
        else:
            assert policy in {"public", "public-token", "public-callback"}
            assert not dependencies & {"get_current_user", "get_current_admin_user"}
