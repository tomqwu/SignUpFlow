"""Route-auth conformance test.

Walks every ``APIRoute`` registered on the FastAPI ``app`` and asserts that
all API endpoints either:
  - appear in an explicit public-endpoint allowlist, **or**
  - depend (directly or transitively) on ``get_current_user``,
    ``get_current_admin_user``, or ``verify_admin_access`` from
    ``api.dependencies``.

A failure here means a new route was added without authentication — a
potential security gap that must be resolved before merge.

Existing routes that pre-date this test and are known to lack JWT auth
live in ``_KNOWN_UNPROTECTED_ENDPOINTS``.  Each entry is a tech-debt
item; removing an entry from the set *and* adding proper auth to the
route is how you retire the debt.  Adding new entries is forbidden in
review — new routes must use ``get_current_user`` or
``get_current_admin_user``.
"""

import pytest
from fastapi.routing import APIRoute

from api.dependencies import get_current_admin_user, get_current_user, verify_admin_access
from api.main import app

pytestmark = [pytest.mark.api, pytest.mark.no_mock_auth]


# ---------------------------------------------------------------------------
# Override root conftest autouse fixtures (same pattern as conftest.py)
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def mock_authentication():
    """Suppress root conftest auth mocking — this test inspects route metadata only."""
    yield


@pytest.fixture(autouse=True)
def reset_database_between_tests():
    """Suppress root conftest DB reset — no DB needed for metadata inspection."""
    yield


# ---------------------------------------------------------------------------
# Allowlist of intentionally unauthenticated endpoints
# ---------------------------------------------------------------------------

# Keyed as (method, path) tuples.  Paths use the FastAPI *route* path
# (with ``{param}`` placeholders, not concrete values).
_PUBLIC_ENDPOINTS: set[tuple[str, str]] = {
    # Auth
    ("POST", "/api/v1/auth/signup"),
    ("POST", "/api/v1/auth/login"),
    ("POST", "/api/v1/auth/check-email"),
    ("GET", "/api/v1/auth/recaptcha-site-key"),
    ("POST", "/api/v1/auth/refresh"),
    # Password reset (public by design — uses email token, not JWT)
    ("POST", "/api/v1/auth/forgot-password"),
    ("POST", "/api/v1/auth/reset-password"),
    # Organization creation (first step of signup flow, before auth exists)
    ("POST", "/api/v1/organizations/"),
    # Invitations (token-based auth, not JWT)
    ("GET", "/api/v1/invitations/{token}"),
    ("POST", "/api/v1/invitations/{token}/accept"),
    # Calendar public feed (token-based, not JWT)
    ("GET", "/api/v1/calendar/feed/{token}"),
    # Config / health / info
    ("GET", "/api/config/safe-flags"),
    ("GET", "/health"),
    ("GET", "/ready"),
    ("GET", "/api"),
    ("GET", "/api/v1"),
    # Pricing / marketing pages (if served from API)
    ("GET", "/pricing"),
}

# Prefix patterns for paths that are public by convention.
_PUBLIC_PATH_PREFIXES: tuple[str, ...] = (
    "/site/",
)

# Substring patterns — any route whose path contains one of these tokens
# is considered public (webhooks use their own auth mechanism).
_PUBLIC_PATH_SUBSTRINGS: tuple[str, ...] = (
    "webhook",
)

# ---------------------------------------------------------------------------
# Known-unprotected endpoints (tech debt — do NOT add new entries)
# ---------------------------------------------------------------------------
# These routes pre-date the conformance test and lack JWT-based auth
# (get_current_user / get_current_admin_user).  Some use the weaker
# verify_admin_access (person_id query param, no token verification)
# or have no auth at all.
#
# Each entry should be paired with a backlog ticket to add proper auth.
# To retire an entry: add auth to the route, then remove it from this set.
# New routes MUST NOT be added here — they must use proper JWT auth.

_KNOWN_UNPROTECTED_ENDPOINTS: set[tuple[str, str]] = {
    # Events router — read endpoints lack auth
    ("GET", "/api/v1/events/"),
    ("GET", "/api/v1/events/{event_id}"),
    ("GET", "/api/v1/events/{event_id}/available-people"),
    ("GET", "/api/v1/events/{event_id}/validation"),
    ("GET", "/api/v1/events/assignments/all"),
    # Solutions router — some endpoints lack auth
    ("GET", "/api/v1/solutions/{solution_id}/assignments"),
    ("POST", "/api/v1/solutions/"),
    ("POST", "/api/v1/solutions/{solution_id}/export"),
    ("DELETE", "/api/v1/solutions/{solution_id}"),
    # Availability router — all endpoints lack auth
    ("POST", "/api/v1/availability/"),
    ("GET", "/api/v1/availability/{person_id}/timeoff"),
    ("POST", "/api/v1/availability/{person_id}/timeoff"),
    ("PATCH", "/api/v1/availability/{person_id}/timeoff/{timeoff_id}"),
    ("GET", "/api/v1/availability/{person_id}/exceptions"),
    ("POST", "/api/v1/availability/{person_id}/exceptions"),
    ("DELETE", "/api/v1/availability/{person_id}/exceptions/{exception_id}"),
    ("GET", "/api/v1/availability/{person_id}/rrule"),
    ("PUT", "/api/v1/availability/{person_id}/rrule"),
    ("DELETE", "/api/v1/availability/{person_id}/rrule"),
    ("DELETE", "/api/v1/availability/{person_id}/timeoff/{timeoff_id}"),
    # Calendar org export — uses manual person_id param, no JWT
    ("GET", "/api/v1/calendar/org/export"),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_AUTH_CALLABLES = frozenset({get_current_user, get_current_admin_user, verify_admin_access})


def _has_auth_dependency(dependant) -> bool:
    """Recursively walk a FastAPI ``Dependant`` tree looking for an auth dep."""
    for dep in dependant.dependencies:
        if dep.call in _AUTH_CALLABLES:
            return True
        # Sub-dependencies live on dep.dependency (a nested Dependant)
        if hasattr(dep, "dependencies") and dep.dependencies:
            if _has_auth_dependency(dep):
                return True
    return False


def _is_allowlisted(method: str, path: str) -> bool:
    """Return True if (method, path) is in the public allowlist."""
    if (method, path) in _PUBLIC_ENDPOINTS:
        return True
    for prefix in _PUBLIC_PATH_PREFIXES:
        if path.startswith(prefix):
            return True
    for substr in _PUBLIC_PATH_SUBSTRINGS:
        if substr in path.lower():
            return True
    return False


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_all_api_routes_require_auth():
    """Every /api/ route must require JWT auth unless explicitly allowlisted.

    Routes in ``_KNOWN_UNPROTECTED_ENDPOINTS`` are tracked separately; they
    represent tech debt but are not treated as new regressions.
    """

    violations: list[str] = []

    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue

        path = route.path
        methods = sorted(route.methods or [])

        # We only care about API routes and top-level operational endpoints
        # (/health, /ready).  Web (HTML) routes, docs, openapi.json, and
        # static mounts are out of scope.
        is_api_route = path.startswith("/api")
        is_ops_route = path in ("/health", "/ready")
        if not is_api_route and not is_ops_route:
            continue

        for method in methods:
            # HEAD is auto-generated by FastAPI for every GET; skip it.
            if method == "HEAD":
                continue

            if _is_allowlisted(method, path):
                continue

            # Skip known-unprotected endpoints (tech debt).
            if (method, path) in _KNOWN_UNPROTECTED_ENDPOINTS:
                continue

            # Walk the dependency tree for auth.
            if not _has_auth_dependency(route.dependant):
                violations.append(f"  {method:7s} {path}")

    if violations:
        header = (
            f"Found {len(violations)} NEW API route(s) missing authentication "
            f"(get_current_user / get_current_admin_user).\n"
            f"Every new route must use Depends(get_current_user) or "
            f"Depends(get_current_admin_user).\n"
            f"Violations:\n"
        )
        pytest.fail(header + "\n".join(violations))


def test_known_unprotected_endpoints_are_not_stale():
    """Entries in ``_KNOWN_UNPROTECTED_ENDPOINTS`` must correspond to
    real routes that still lack auth.  If a route gains proper auth or
    is removed, its entry should be cleaned up.
    """
    # Build a set of all (method, path) pairs on the app.
    all_routes: set[tuple[str, str]] = set()
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        for method in (route.methods or []):
            if method == "HEAD":
                continue
            all_routes.add((method, route.path))

    stale: list[str] = []
    for method, path in sorted(_KNOWN_UNPROTECTED_ENDPOINTS):
        if (method, path) not in all_routes:
            stale.append(f"  {method:7s} {path}  (route no longer exists)")
            continue
        # Check if the route now has auth (someone fixed it without
        # removing the known-unprotected entry).
        for route in app.routes:
            if not isinstance(route, APIRoute):
                continue
            if route.path == path and method in (route.methods or set()):
                if _has_auth_dependency(route.dependant):
                    stale.append(f"  {method:7s} {path}  (now has auth — remove from known list)")
                break

    if stale:
        header = (
            f"Found {len(stale)} stale entries in _KNOWN_UNPROTECTED_ENDPOINTS.\n"
            f"Remove them from the set:\n"
        )
        pytest.fail(header + "\n".join(stale))
