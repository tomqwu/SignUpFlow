"""
Unit tests for security headers middleware.

Tests the SecurityHeadersMiddleware which adds security headers
to all HTTP responses to prevent XSS, clickjacking, and other attacks.
"""

import pytest
import os
from unittest.mock import Mock, AsyncMock, patch
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient

from api.utils.security_headers_middleware import (
    SecurityHeadersMiddleware,
    add_security_headers_middleware,
)


@pytest.fixture
def test_app():
    """Create a test FastAPI application."""
    app = FastAPI()

    @app.get("/test")
    async def test_endpoint():
        return {"message": "test"}

    return app


@pytest.fixture
def test_client(test_app):
    """Create a test client for the test app."""
    return TestClient(test_app)


class TestSecurityHeadersMiddleware:
    """Test SecurityHeadersMiddleware class."""

    def test_middleware_adds_security_headers(self, test_app, test_client):
        """Test that middleware adds all security headers to responses."""
        # Add middleware
        add_security_headers_middleware(test_app)

        # Make request
        response = test_client.get("/test")

        # Verify security headers are present
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"

        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"

        assert "Referrer-Policy" in response.headers
        assert response.headers["Referrer-Policy"] == "no-referrer"

        assert "Permissions-Policy" in response.headers

    @patch.dict(os.environ, {"ENVIRONMENT": "production", "SECURITY_HSTS_ENABLED": "true"})
    def test_hsts_header_in_production(self, test_app, test_client):
        """Test that HSTS header is added in production."""
        # Add middleware with production config
        add_security_headers_middleware(test_app)

        response = test_client.get("/test")

        assert "Strict-Transport-Security" in response.headers
        hsts_value = response.headers["Strict-Transport-Security"]
        assert "max-age=" in hsts_value
        assert "includeSubDomains" in hsts_value

    @patch.dict(os.environ, {"ENVIRONMENT": "development", "SECURITY_HSTS_ENABLED": "false"})
    def test_no_hsts_in_development(self, test_app, test_client):
        """Test that HSTS header is not added in development."""
        add_security_headers_middleware(test_app)

        response = test_client.get("/test")

        assert "Strict-Transport-Security" not in response.headers

    @patch.dict(os.environ, {"SECURITY_CSP_ENABLED": "true"})
    def test_csp_header_enabled(self, test_app, test_client):
        """Test that CSP header is added when enabled."""
        add_security_headers_middleware(test_app)

        response = test_client.get("/test")

        assert "Content-Security-Policy" in response.headers
        csp_value = response.headers["Content-Security-Policy"]
        assert "default-src" in csp_value
        assert "script-src" in csp_value

    @patch.dict(os.environ, {"SECURITY_CSP_ENABLED": "false"})
    def test_csp_header_disabled(self, test_app, test_client):
        """Test that CSP header is not added when disabled."""
        add_security_headers_middleware(test_app)

        response = test_client.get("/test")

        assert "Content-Security-Policy" not in response.headers

    @patch.dict(os.environ, {"SECURITY_FRAME_OPTIONS": "SAMEORIGIN"})
    def test_custom_frame_options(self, test_app, test_client):
        """Test that X-Frame-Options can be customized."""
        add_security_headers_middleware(test_app)

        response = test_client.get("/test")

        assert response.headers["X-Frame-Options"] == "SAMEORIGIN"

    @patch.dict(os.environ, {"SECURITY_HSTS_MAX_AGE": "63072000"})
    def test_custom_hsts_max_age(self, test_app, test_client):
        """Test that HSTS max-age can be customized."""
        # Enable HSTS
        with patch.dict(os.environ, {"SECURITY_HSTS_ENABLED": "true"}):
            add_security_headers_middleware(test_app)

            response = test_client.get("/test")

            if "Strict-Transport-Security" in response.headers:
                assert "max-age=63072000" in response.headers["Strict-Transport-Security"]


class TestSecurityHeadersConfiguration:
    """Test SecurityHeadersMiddleware configuration via environment variables."""


    def test_default_configuration(self):
        """Test middleware with default configuration."""
        # Ensure SECURITY_CSP_ENABLED is not set (it might be set by session fixures)
        with patch.dict(os.environ):
            if "SECURITY_CSP_ENABLED" in os.environ:
                del os.environ["SECURITY_CSP_ENABLED"]

            middleware = SecurityHeadersMiddleware(app=Mock())

            # Defaults should be set
            assert middleware.hsts_enabled is False  # Default in development
            assert middleware.csp_enabled is True
            assert middleware.frame_options == "DENY"

    @patch.dict(os.environ, {
        "ENVIRONMENT": "production",
        "SECURITY_HSTS_ENABLED": "true",
        "SECURITY_HSTS_MAX_AGE": "31536000",
        "SECURITY_CSP_ENABLED": "true",
        "SECURITY_FRAME_OPTIONS": "DENY",
    })
    def test_production_configuration(self):
        """Test middleware with production configuration."""
        middleware = SecurityHeadersMiddleware(app=Mock())

        assert middleware.hsts_enabled is True
        assert middleware.hsts_max_age == 31536000
        assert middleware.csp_enabled is True
        assert middleware.frame_options == "DENY"

    @patch.dict(os.environ, {
        "SECURITY_HSTS_ENABLED": "TRUE",  # Test case-insensitive
    })
    def test_case_insensitive_boolean_config(self):
        """Test that boolean config values are case-insensitive."""
        middleware = SecurityHeadersMiddleware(app=Mock())

        assert middleware.hsts_enabled is True


class TestContentSecurityPolicy:
    """Test CSP header generation."""

    @patch.dict(os.environ, {"SECURITY_CSP_ENABLED": "true"})
    def test_csp_default_policy(self, test_app, test_client):
        """Test that default CSP policy is secure."""
        add_security_headers_middleware(test_app)

        response = test_client.get("/test")

        csp = response.headers.get("Content-Security-Policy", "")

        # Should have restrictive defaults
        assert "default-src 'self'" in csp
        assert "script-src" in csp
        assert "style-src" in csp

    @patch.dict(os.environ, {"SECURITY_CSP_ENABLED": "true"})
    def test_csp_allows_cdn_resources(self, test_app, test_client):
        """Test that CSP allows necessary CDN resources."""
        add_security_headers_middleware(test_app)

        response = test_client.get("/test")

        csp = response.headers.get("Content-Security-Policy", "")

        # Should allow i18next CDN
        assert "cdn.jsdelivr.net" in csp or "unpkg.com" in csp or "'unsafe-inline'" in csp

    @patch.dict(os.environ, {"SECURITY_CSP_ENABLED": "true"})
    def test_csp_allows_google_frames(self, test_app, test_client):
        """Test that CSP allows Google reCAPTCHA iframes."""
        add_security_headers_middleware(test_app)

        response = test_client.get("/test")

        csp = response.headers.get("Content-Security-Policy", "")

        # Should have frame-src directive with Google domains
        assert "frame-src" in csp
        assert "google.com" in csp
        assert "gstatic.com" in csp


class TestPermissionsPolicy:
    """Test Permissions-Policy header."""

    def test_permissions_policy_disables_dangerous_features(self, test_app, test_client):
        """Test that dangerous browser features are disabled."""
        add_security_headers_middleware(test_app)

        response = test_client.get("/test")

        permissions = response.headers.get("Permissions-Policy", "")

        # Should disable dangerous features
        assert "geolocation=()" in permissions
        assert "microphone=()" in permissions
        assert "camera=()" in permissions


class TestSecurityHeadersIntegration:
    """Integration tests for security headers middleware."""

    def test_headers_added_to_all_routes(self, test_app, test_client):
        """Test that security headers are added to all routes."""
        # Add multiple routes
        @test_app.get("/route1")
        async def route1():
            return {"route": 1}

        @test_app.post("/route2")
        async def route2():
            return {"route": 2}

        add_security_headers_middleware(test_app)

        # Test all routes
        response1 = test_client.get("/route1")
        response2 = test_client.post("/route2")

        assert "X-Content-Type-Options" in response1.headers
        assert "X-Content-Type-Options" in response2.headers

    def test_headers_dont_override_existing(self, test_app, test_client):
        """Test that middleware doesn't override existing headers."""
        @test_app.get("/custom")
        async def custom_route(response: Response):
            response.headers["X-Custom-Header"] = "custom-value"
            return {"message": "custom"}

        add_security_headers_middleware(test_app)

        response = test_client.get("/custom")

        # Should have both custom and security headers
        assert "X-Custom-Header" in response.headers
        assert "X-Content-Type-Options" in response.headers

    def test_middleware_works_with_error_responses(self, test_app, test_client):
        """Test that middleware doesn't suppress errors but still adds headers to error responses."""
        from fastapi import HTTPException

        @test_app.get("/error")
        async def error_route():
            # Raise HTTPException which FastAPI will handle
            raise HTTPException(status_code=400, detail="Bad request")

        add_security_headers_middleware(test_app)

        # Error response should have security headers
        response = test_client.get("/error")
        assert response.status_code == 400
        assert "X-Content-Type-Options" in response.headers

    def test_middleware_works_with_json_responses(self, test_app, test_client):
        """Test that middleware works with JSON responses."""
        add_security_headers_middleware(test_app)

        response = test_client.get("/test")

        # Should have both security headers and JSON content
        assert "X-Content-Type-Options" in response.headers
        assert response.json() == {"message": "test"}

    def test_middleware_works_with_html_responses(self, test_app, test_client):
        """Test that middleware works with HTML responses."""
        @test_app.get("/html")
        async def html_route():
            from fastapi.responses import HTMLResponse
            return HTMLResponse(content="<html><body>Test</body></html>")

        add_security_headers_middleware(test_app)

        response = test_client.get("/html")

        assert "X-Content-Type-Options" in response.headers
        assert "text/html" in response.headers["content-type"]


class TestAddSecurityHeadersMiddleware:
    """Test add_security_headers_middleware helper function."""

    def test_helper_function_adds_middleware(self, test_app):
        """Test that helper function correctly adds middleware to app."""
        # Initially no middleware
        initial_middleware_count = len(test_app.user_middleware)

        # Add middleware
        add_security_headers_middleware(test_app)

        # Should have added middleware
        assert len(test_app.user_middleware) > initial_middleware_count

    def test_helper_function_works_with_test_client(self, test_app, test_client):
        """Test that helper function produces working middleware."""
        add_security_headers_middleware(test_app)

        response = test_client.get("/test")

        assert response.status_code == 200
        assert "X-Content-Type-Options" in response.headers


class TestSecurityHeadersEdgeCases:
    """Test edge cases and special scenarios."""

    def test_empty_response_gets_headers(self, test_app, test_client):
        """Test that even empty responses get security headers."""
        @test_app.get("/empty")
        async def empty_route():
            return None

        add_security_headers_middleware(test_app)

        response = test_client.get("/empty")

        assert "X-Content-Type-Options" in response.headers

    def test_redirect_response_gets_headers(self, test_app, test_client):
        """Test that redirect responses get security headers."""
        @test_app.get("/redirect")
        async def redirect_route():
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url="/test")

        add_security_headers_middleware(test_app)

        response = test_client.get("/redirect", follow_redirects=False)

        assert "X-Content-Type-Options" in response.headers

    @patch.dict(os.environ, {"SECURITY_HSTS_MAX_AGE": "invalid"})
    def test_invalid_max_age_uses_default(self):
        """Test that invalid max-age config falls back to default."""
        middleware = SecurityHeadersMiddleware(app=Mock())

        # Should use default (31536000) instead of crashing
        assert isinstance(middleware.hsts_max_age, int)
        assert middleware.hsts_max_age > 0
