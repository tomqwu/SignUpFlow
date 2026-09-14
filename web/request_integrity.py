"""Same-origin and CSRF enforcement for the server-rendered browser app."""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from collections.abc import Awaitable, Callable
from urllib.parse import parse_qs, urlsplit

from fastapi import Request
from fastapi.responses import HTMLResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from api.core.runtime_config import is_production_environment
from api.security import SECRET_KEY

CSRF_COOKIE = "signupflow_csrf"
CSRF_FORM_FIELD = "csrf_token"
CSRF_HEADER = "X-CSRF-Token"
CSRF_MAX_AGE = 60 * 60 * 24
UNSAFE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})
PROTECTED_BROWSER_PREFIXES = ("/auth/", "/a/", "/v/")


def is_protected_browser_path(path: str) -> bool:
    """Return whether a path belongs to the cookie/form browser surface."""
    return path.startswith(PROTECTED_BROWSER_PREFIXES)


def issue_csrf_token() -> str:
    """Create a random token signed by the application secret."""
    nonce = secrets.token_urlsafe(32)
    signature = hmac.new(
        SECRET_KEY.encode("utf-8"),
        nonce.encode("ascii"),
        hashlib.sha256,
    ).hexdigest()
    return f"{nonce}.{signature}"


def is_valid_csrf_token(token: str | None) -> bool:
    if not token or "." not in token:
        return False
    nonce, supplied_signature = token.rsplit(".", 1)
    if not nonce or not supplied_signature:
        return False
    expected_signature = hmac.new(
        SECRET_KEY.encode("utf-8"),
        nonce.encode("ascii", errors="ignore"),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(supplied_signature, expected_signature)


def configured_browser_origin(request: Request) -> str:
    """Resolve the one origin authorized to submit browser mutations."""
    configured = os.getenv("FRONTEND_URL") or os.getenv("APP_URL")
    if configured:
        return _normalize_origin(configured)
    if is_production_environment():
        return ""
    return _normalize_origin(str(request.base_url))


def _normalize_origin(value: str) -> str:
    parsed = urlsplit(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return ""
    port = parsed.port
    if (
        port is None
        or (parsed.scheme == "http" and port == 80)
        or (parsed.scheme == "https" and port == 443)
    ):
        authority = parsed.hostname.lower()
    else:
        authority = f"{parsed.hostname.lower()}:{port}"
    return f"{parsed.scheme.lower()}://{authority}"


def _presented_token(request: Request, body: bytes) -> str | None:
    header_token = request.headers.get(CSRF_HEADER)
    if header_token:
        return header_token
    content_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    if content_type != "application/x-www-form-urlencoded":
        return None
    try:
        values = parse_qs(body.decode("utf-8"), keep_blank_values=True)
    except UnicodeDecodeError:
        return None
    candidates = values.get(CSRF_FORM_FIELD, [])
    return candidates[0] if len(candidates) == 1 else None


def _reject_request() -> HTMLResponse:
    return HTMLResponse(
        (
            '<div class="alert alert-error" role="alert">'
            "This form could not be verified. Reload the page and try again."
            "</div>"
        ),
        status_code=403,
        headers={
            "Cache-Control": "no-store",
            "HX-Retarget": "#request-status",
            "HX-Reswap": "innerHTML",
        },
    )


def _set_csrf_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=CSRF_COOKIE,
        value=token,
        max_age=CSRF_MAX_AGE,
        httponly=False,
        secure=is_production_environment(),
        samesite="lax",
        path="/",
    )


class BrowserRequestIntegrityMiddleware(BaseHTTPMiddleware):
    """Require a signed token and the configured origin on browser writes."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        cookie_token = request.cookies.get(CSRF_COOKIE)
        cookie_is_valid = is_valid_csrf_token(cookie_token)
        if cookie_is_valid:
            assert cookie_token is not None
            active_token = cookie_token
        else:
            active_token = issue_csrf_token()
        request.state.csrf_token = active_token

        is_unsafe_browser_request = (
            request.method.upper() in UNSAFE_METHODS and is_protected_browser_path(request.url.path)
        )
        if is_unsafe_browser_request:
            origin = _normalize_origin(request.headers.get("origin", ""))
            body = await request.body()
            presented = _presented_token(request, body)
            if (
                origin != configured_browser_origin(request)
                or not cookie_is_valid
                or presented is None
                or not hmac.compare_digest(presented, cookie_token or "")
            ):
                rejected_response = _reject_request()
                if not cookie_is_valid:
                    _set_csrf_cookie(rejected_response, active_token)
                return rejected_response

        response = await call_next(request)
        if not cookie_is_valid:
            _set_csrf_cookie(response, active_token)
        return response
