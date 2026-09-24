"""
Security headers middleware.

Adds security-related HTTP headers to all responses:
- HSTS (HTTP Strict Transport Security)
- CSP (Content Security Policy)
- X-Frame-Options (prevent clickjacking)
- X-Content-Type-Options (prevent MIME sniffing)
- Referrer-Policy (control referrer information)
- Permissions-Policy (control browser features)
"""

import os
from collections.abc import Awaitable, Callable

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from api.core.runtime_config import (
    is_production_environment,
    read_boolean_setting,
    security_hsts_max_age,
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all HTTP responses.

    Configured via environment variables:
    - SECURITY_HSTS_ENABLED: Enable HSTS header (default: true in production)
    - SECURITY_HSTS_MAX_AGE: HSTS max-age in seconds (default: 31536000 = 1 year)
    - SECURITY_CSP_ENABLED: Enable CSP header (default: true)
    - SECURITY_FRAME_OPTIONS: X-Frame-Options value (default: DENY)
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

        # Environment-based configuration
        self.is_production = is_production_environment()
        self.hsts_enabled = read_boolean_setting(
            "SECURITY_HSTS_ENABLED",
            default=self.is_production,
        )

        # Development preserves the historical fallback. Production validation
        # rejects malformed values before the application accepts requests.
        try:
            self.hsts_max_age = security_hsts_max_age()
        except ValueError:
            self.hsts_max_age = 31536000

        self.csp_enabled = read_boolean_setting("SECURITY_CSP_ENABLED", default=True)
        self.frame_options = os.getenv("SECURITY_FRAME_OPTIONS", "DENY")

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Add security headers to response."""
        response = await call_next(request)

        # HSTS - Force HTTPS for 1 year (only in production with HTTPS)
        if self.hsts_enabled:
            response.headers[
                "Strict-Transport-Security"
            ] = f"max-age={self.hsts_max_age}; includeSubDomains"

        # CSP - Prevent XSS and data injection attacks
        if self.csp_enabled:
            csp_policy = self._get_csp_policy()
            response.headers["Content-Security-Policy"] = csp_policy

        # X-Frame-Options - Prevent clickjacking
        response.headers["X-Frame-Options"] = self.frame_options

        # X-Content-Type-Options - Prevent MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Preserve an auditable Origin for same-origin form posts without
        # sending referrer details to other origins.
        response.headers["Referrer-Policy"] = "same-origin"

        # Permissions-Policy - Disable unnecessary browser features
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # X-XSS-Protection - Enable browser XSS protection (legacy, but doesn't hurt)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Cross-origin isolation — the app (API + same-origin web UI)
        # never needs to be embedded or read cross-origin.
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"

        # Block legacy Adobe cross-domain policy files outright.
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"

        return response

    def _get_csp_policy(self) -> str:
        """
        Build Content Security Policy.

        This is a strict CSP that:
        - Only allows scripts from same origin and CDNs (i18next, etc.)
        - Only allows styles from same origin and inline styles
        - Only allows connections to same origin
        - Prevents embedding in iframes
        """
        policy_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://www.google.com https://www.gstatic.com",  # 'unsafe-eval' required by Alpine.js (web UI evaluates x-* directive expressions); also i18next CDN + reCAPTCHA
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",  # Allow inline styles and Google Fonts
            "img-src 'self' data: https:",  # Allow images from same origin, data URIs, and HTTPS
            "font-src 'self' data: https://fonts.gstatic.com",  # Allow fonts from same origin, data URIs, and Google Fonts
            "connect-src 'self' https://www.google.com",  # Allow API calls to same origin and reCAPTCHA
            "frame-src 'self' https://www.google.com https://www.gstatic.com",  # Allow Google reCAPTCHA iframes
            "frame-ancestors 'none'",  # Prevent embedding (same as X-Frame-Options: DENY)
            "base-uri 'self'",  # Restrict base tag to same origin
            "form-action 'self'",  # Only allow forms to submit to same origin
        ]
        # Like HSTS, this asserts the site is served over HTTPS. On a plain-http
        # development server it only breaks things: Safari upgrades same-origin
        # stylesheets and scripts to https even on localhost, they fail with TLS
        # errors, and the app renders unstyled with no JavaScript.
        if self.hsts_enabled:
            policy_directives.append("upgrade-insecure-requests")

        return "; ".join(policy_directives)


def add_security_headers_middleware(app: FastAPI) -> None:
    """
    Add security headers middleware to FastAPI app.

    Usage:
        from api.utils.security_headers_middleware import add_security_headers_middleware

        app = FastAPI()
        add_security_headers_middleware(app)
    """
    app.add_middleware(SecurityHeadersMiddleware)
