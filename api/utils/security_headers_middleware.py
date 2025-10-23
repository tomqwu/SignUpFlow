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
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all HTTP responses.

    Configured via environment variables:
    - SECURITY_HSTS_ENABLED: Enable HSTS header (default: true in production)
    - SECURITY_HSTS_MAX_AGE: HSTS max-age in seconds (default: 31536000 = 1 year)
    - SECURITY_CSP_ENABLED: Enable CSP header (default: true)
    - SECURITY_FRAME_OPTIONS: X-Frame-Options value (default: DENY)
    """

    def __init__(self, app):
        super().__init__(app)

        # Environment-based configuration
        self.is_production = os.getenv("ENVIRONMENT", "development") == "production"
        self.hsts_enabled = os.getenv("SECURITY_HSTS_ENABLED", str(self.is_production)).lower() == "true"

        # Parse HSTS max-age with fallback for invalid values
        try:
            self.hsts_max_age = int(os.getenv("SECURITY_HSTS_MAX_AGE", "31536000"))  # 1 year
        except ValueError:
            self.hsts_max_age = 31536000  # Default fallback

        self.csp_enabled = os.getenv("SECURITY_CSP_ENABLED", "true").lower() == "true"
        self.frame_options = os.getenv("SECURITY_FRAME_OPTIONS", "DENY")

    async def dispatch(self, request: Request, call_next):
        """Add security headers to response."""
        response = await call_next(request)

        # HSTS - Force HTTPS for 1 year (only in production with HTTPS)
        if self.hsts_enabled:
            response.headers["Strict-Transport-Security"] = f"max-age={self.hsts_max_age}; includeSubDomains"

        # CSP - Prevent XSS and data injection attacks
        if self.csp_enabled:
            csp_policy = self._get_csp_policy()
            response.headers["Content-Security-Policy"] = csp_policy

        # X-Frame-Options - Prevent clickjacking
        response.headers["X-Frame-Options"] = self.frame_options

        # X-Content-Type-Options - Prevent MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Referrer-Policy - Control referrer information leakage
        response.headers["Referrer-Policy"] = "no-referrer"

        # Permissions-Policy - Disable unnecessary browser features
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # X-XSS-Protection - Enable browser XSS protection (legacy, but doesn't hurt)
        response.headers["X-XSS-Protection"] = "1; mode=block"

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
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://www.google.com https://www.gstatic.com",  # Allow i18next CDN and reCAPTCHA
            "style-src 'self' 'unsafe-inline'",  # Allow inline styles (used in app)
            "img-src 'self' data: https:",  # Allow images from same origin, data URIs, and HTTPS
            "font-src 'self' data:",  # Allow fonts from same origin and data URIs
            "connect-src 'self' https://www.google.com",  # Allow API calls to same origin and reCAPTCHA
            "frame-src 'self' https://www.google.com https://www.gstatic.com",  # Allow Google reCAPTCHA iframes
            "frame-ancestors 'none'",  # Prevent embedding (same as X-Frame-Options: DENY)
            "base-uri 'self'",  # Restrict base tag to same origin
            "form-action 'self'",  # Only allow forms to submit to same origin
            "upgrade-insecure-requests",  # Upgrade HTTP to HTTPS automatically
        ]

        return "; ".join(policy_directives)


def add_security_headers_middleware(app):
    """
    Add security headers middleware to FastAPI app.

    Usage:
        from api.utils.security_headers_middleware import add_security_headers_middleware

        app = FastAPI()
        add_security_headers_middleware(app)
    """
    app.add_middleware(SecurityHeadersMiddleware)
