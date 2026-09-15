"""Middleware that attaches an X-Request-ID to every request and response."""

import re
import uuid
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from api.utils.request_context import request_id_var

REQUEST_ID_HEADER = "X-Request-ID"
SAFE_REQUEST_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


def _request_id(value: str | None) -> str:
    """Keep bounded opaque IDs and replace values unsafe for logs or headers."""
    if value and SAFE_REQUEST_ID.fullmatch(value):
        return value
    return str(uuid.uuid4())


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Read or generate X-Request-ID; expose via request.state and ContextVar; echo on response."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = _request_id(request.headers.get(REQUEST_ID_HEADER))
        request.state.request_id = request_id
        token = request_id_var.set(request_id)
        try:
            response = await call_next(request)
        finally:
            request_id_var.reset(token)
        response.headers[REQUEST_ID_HEADER] = request_id
        return response
