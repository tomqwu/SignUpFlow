"""Safety and browser contracts for the opt-in staging acceptance runner."""

from __future__ import annotations

import httpx
import pytest

from scripts.run_staging_acceptance import (
    validate_approval_reference,
    validate_staging_target,
    verify_browser_session,
    verify_target_identity,
)

RELEASE_SHA = "a" * 40


def test_staging_target_requires_explicit_https_remote_authorization() -> None:
    assert validate_staging_target("https://127.0.0.1:8123") == "https://127.0.0.1:8123"

    with pytest.raises(ValueError, match="HTTPS"):
        validate_staging_target("http://127.0.0.1:8123")

    with pytest.raises(ValueError, match="explicit authorization"):
        validate_staging_target("https://staging.example.com")
    with pytest.raises(ValueError, match="HTTPS"):
        validate_staging_target(
            "http://staging.example.com",
            allow_authorized_remote=True,
        )
    with pytest.raises(ValueError, match="origin only"):
        validate_staging_target(
            "https://staging.example.com/login",
            allow_authorized_remote=True,
        )
    with pytest.raises(ValueError, match="credentials"):
        validate_staging_target(
            "https://user:secret@staging.example.com",
            allow_authorized_remote=True,
        )

    assert (
        validate_staging_target(
            "https://staging.example.com/",
            allow_authorized_remote=True,
        )
        == "https://staging.example.com"
    )


def test_remote_approval_reference_must_be_specific_and_bounded() -> None:
    assert (
        validate_approval_reference(
            "https://github.com/tomqwu/SignUpFlow/issues/265#issuecomment-1"
        )
        == "https://github.com/tomqwu/SignUpFlow/issues/265#issuecomment-1"
    )

    for value in ("", "approved", "x" * 501):
        with pytest.raises(ValueError, match="approval reference"):
            validate_approval_reference(value)


def test_target_identity_requires_exact_release_and_readiness() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/health":
            return httpx.Response(200, headers={"X-Release-SHA": RELEASE_SHA})
        if request.url.path == "/ready":
            return httpx.Response(200, headers={"X-Release-SHA": RELEASE_SHA})
        raise AssertionError(request.url.path)

    with httpx.Client(
        base_url="https://staging.example.com",
        transport=httpx.MockTransport(handler),
    ) as client:
        result = verify_target_identity(client, RELEASE_SHA)

    assert result == {
        "health_status": 200,
        "readiness_status": 200,
        "observed_release_sha": RELEASE_SHA,
    }


def test_target_identity_rejects_mismatch_before_writes() -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        return httpx.Response(200, headers={"X-Release-SHA": "b" * 40})

    with httpx.Client(
        base_url="https://staging.example.com",
        transport=httpx.MockTransport(handler),
    ) as client:
        with pytest.raises(RuntimeError, match="identity mismatch"):
            verify_target_identity(client, RELEASE_SHA)

    assert calls == ["/health"]


def test_browser_session_requires_secure_cookies_and_headers() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.method == "GET" and request.url.path == "/auth/login":
            return httpx.Response(
                200,
                headers={
                    "set-cookie": "signupflow_csrf=csrf-value; Path=/; SameSite=lax; Secure",
                    "X-Release-SHA": RELEASE_SHA,
                },
            )
        if request.method == "POST" and request.url.path == "/auth/login":
            assert request.headers["origin"] == "https://staging.example.com"
            assert b"password=GeneratedPass123%21" in request.content
            return httpx.Response(
                303,
                headers=[
                    ("location", "/a/dashboard"),
                    (
                        "set-cookie",
                        "signupflow_session=session-value; HttpOnly; Path=/; "
                        "SameSite=lax; Secure",
                    ),
                    ("X-Release-SHA", RELEASE_SHA),
                ],
            )
        if request.method == "GET" and request.url.path == "/a/dashboard":
            return httpx.Response(
                200,
                headers={
                    "content-security-policy": "default-src 'self'",
                    "strict-transport-security": "max-age=31536000",
                    "x-content-type-options": "nosniff",
                    "x-frame-options": "DENY",
                    "X-Release-SHA": RELEASE_SHA,
                },
            )
        raise AssertionError(f"Unexpected request: {request.method} {request.url.path}")

    with httpx.Client(
        base_url="https://staging.example.com",
        transport=httpx.MockTransport(handler),
        follow_redirects=False,
    ) as client:
        result = verify_browser_session(
            client,
            email="admin@synthetic.example",
            password="GeneratedPass123!",
            expected_release_sha=RELEASE_SHA,
        )

    assert result["login_status"] == 303
    assert result["dashboard_status"] == 200
    assert result["csrf_cookie"]["secure"] is True
    assert result["session_cookie"]["http_only"] is True
    assert [request.url.path for request in requests] == [
        "/auth/login",
        "/auth/login",
        "/a/dashboard",
    ]


def test_browser_session_rejects_insecure_session_cookie() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "GET":
            return httpx.Response(
                200,
                headers={
                    "set-cookie": "signupflow_csrf=csrf; Path=/; SameSite=lax; Secure",
                    "X-Release-SHA": RELEASE_SHA,
                },
            )
        return httpx.Response(
            303,
            headers={
                "location": "/a/dashboard",
                "set-cookie": ("signupflow_session=session; HttpOnly; Path=/; SameSite=lax"),
                "X-Release-SHA": RELEASE_SHA,
            },
        )

    with httpx.Client(
        base_url="https://staging.example.com",
        transport=httpx.MockTransport(handler),
        follow_redirects=False,
    ) as client:
        with pytest.raises(RuntimeError, match="signupflow_session"):
            verify_browser_session(
                client,
                email="admin@synthetic.example",
                password="GeneratedPass123!",
                expected_release_sha=RELEASE_SHA,
            )
