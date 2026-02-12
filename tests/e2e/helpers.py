"""Shared helpers for Playwright-based E2E tests."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import re
import time
import uuid
from typing import Any, Dict, Iterable, Optional

import requests
from playwright.sync_api import Page, Response, expect


@dataclass(frozen=True)
class AppConfig:
    """Shared application endpoints for GUI and API entrypoints."""

    app_url: str
    api_base: str


class ApiTestClient:
    """Thin wrapper around requests.Session with helpful factory methods."""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def close(self) -> None:
        self.session.close()

    def create_org(
        self,
        *,
        org_id: Optional[str] = None,
        name: Optional[str] = None,
        region: str = "Test",
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        org_id = org_id or self._unique_id("org")
        payload = {
            "id": org_id,
            "name": name or f"Test Org {org_id}",
            "region": region,
            "config": config or {},
        }
        response = self._request("post", "/organizations/", json=payload)
        data = response.json() if response.content else {}
        data.setdefault("id", org_id)
        data.setdefault("name", payload["name"])
        return data

    def create_user(
        self,
        *,
        org_id: str,
        email: Optional[str] = None,
        password: Optional[str] = None,
        name: Optional[str] = None,
        roles: Optional[Iterable[str]] = None,
    ) -> Dict[str, Any]:
        timestamp = int(time.time() * 1000)
        email = email or f"user_{timestamp}_{uuid.uuid4().hex[:4]}@test.com"
        password = password or "TestPassword123!"
        name = name or f"Test User {timestamp}"
        roles = list(roles or ["admin"])

        payload = {
            "org_id": org_id,
            "name": name,
            "email": email,
            "password": password,
            "roles": roles,
        }
        response = self._request("post", "/auth/signup", json=payload)
        data = response.json()
        data.update(
            {
                "email": email,
                "password": password,
                "name": name,
                "org_id": org_id,
                "roles": roles,
            }
        )
        return data

    def login(self, *, email: str, password: str) -> Dict[str, Any]:
        response = self._request(
            "post",
            "/auth/login",
            json={"email": email, "password": password},
            expected_status=(200, 201),
        )
        return response.json()

    def create_invitation(
        self,
        *,
        admin_token: str,
        org_id: str,
        email: str,
        name: str,
        roles: Iterable[str],
    ) -> Dict[str, Any]:
        response = self._request(
            "post",
            f"/invitations?org_id={org_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"email": email, "name": name, "roles": list(roles)},
        )
        return response.json()

    def create_event(
        self,
        *,
        admin_token: str,
        org_id: str,
        event_id: Optional[str] = None,
        event_type: str = "Sunday Service",
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        extra_payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        event_id = event_id or self._unique_id("event")
        # Use tomorrow 9am as base time to ensure it falls in future range
        now = datetime.now()
        base_time = (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
        start_time = start_time or base_time.isoformat()
        end_time = end_time or (base_time + timedelta(hours=2)).isoformat()

        payload: Dict[str, Any] = {
            "id": event_id,
            "org_id": org_id,
            "type": event_type,
            "start_time": start_time,
            "end_time": end_time,
        }
        if extra_payload:
            payload.update(extra_payload)

        response = self._request(
            "post",
            f"/events/?org_id={org_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=payload,
        )
        data = response.json() if response.content else {}
        data.setdefault("id", event_id)
        data.setdefault("org_id", org_id)
        return data

    def assign_person_to_event(
        self,
        *,
        admin_token: str,
        org_id: str,
        event_id: str,
        person_id: str,
        role: str,
    ) -> None:
        self._request(
            "post",
            f"/events/{event_id}/assignments",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"person_id": person_id, "action": "assign", "role": role, "org_id": org_id},
            expected_status=(200, 201, 204),
        )

    def _request(
        self,
        method: str,
        path: str,
        *,
        expected_status: Iterable[int] = (200, 201),
        timeout: float = 10,
        **kwargs: Any,
    ) -> requests.Response:
        url = f"{self.base_url}{path}"
        response = self.session.request(method, url, timeout=timeout, **kwargs)
        if expected_status and response.status_code not in expected_status:
            raise AssertionError(
                f"{method.upper()} {url} failed with status "
                f"{response.status_code}: {response.text}"
            )
        return response

    @staticmethod
    def _unique_id(prefix: str) -> str:
        return f"{prefix}_{int(time.time() * 1000)}_{uuid.uuid4().hex[:6]}"


def navigate_to_login(page: Page, app_url: str) -> None:
    """Ensure the login screen is visible, regardless of landing page state."""
    page.goto(app_url, wait_until="networkidle")
    login_screen = page.locator("#login-screen")
    if login_screen.count() == 0 or not _is_locator_visible(login_screen):
        sign_in_link = page.get_by_role("link", name="Sign in")
        if sign_in_link.count():
            sign_in_link.first.click()
        else:
            page.goto(f"{app_url}/login", wait_until="networkidle")
        login_screen = page.locator("#login-screen")
    expect(login_screen).to_be_visible()


def submit_login_form(page: Page, email: str, password: str) -> Response:
    """Fill and submit the login form, returning the network response."""
    email_input = page.locator("#login-email")
    password_input = page.locator("#login-password")
    expect(email_input).to_be_visible()
    expect(password_input).to_be_visible()

    email_input.fill(email)
    password_input.fill(password)

    with page.expect_response(
        lambda response: response.request.method == "POST"
        and "/auth/login" in response.url
    ) as login_response:
        page.locator('#login-screen button[type="submit"]').click()
    return login_response.value


def skip_onboarding(page: Page, token: str) -> None:
    """Skip onboarding for the currently-authenticated user.

    This endpoint is used in E2E to avoid flaky redirects to /wizard.
    """
    if not token:
        return

    page.evaluate(
        """async (token) => {
            await fetch('/api/onboarding/skip', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });
        }""",
        token,
    )


def skip_onboarding_from_storage(page: Page) -> None:
    """Skip onboarding using authToken stored in localStorage (best-effort)."""
    try:
        token = page.evaluate("localStorage.getItem('authToken')")
    except Exception:
        token = None

    if token:
        skip_onboarding(page, token)


def login_via_ui(page: Page, app_url: str, email: str, password: str) -> Response:
    """Perform a full login via the UI.

    Note: for brand new orgs/users, the app may route into onboarding first which keeps
    #main-app hidden. To keep E2E tests stable, we auto-skip onboarding when needed.
    """
    navigate_to_login(page, app_url)
    response = submit_login_form(page, email, password)
    if response.status not in (200, 201):
        raise AssertionError(f"Login failed with status {response.status}")

    # Prefer the login response token to skip onboarding deterministically.
    token = None
    try:
        payload = response.json()
        if isinstance(payload, dict):
            token = payload.get("token")
    except Exception:
        pass

    if token:
        skip_onboarding(page, token)
    else:
        # Fallback: try localStorage token.
        skip_onboarding_from_storage(page)

    page.goto(f"{app_url}/app/schedule", wait_until="networkidle")
    expect(page.locator("#main-app")).to_be_visible(timeout=10000)
    return response


def open_invitation(page: Page, app_url: str, token: str) -> None:
    """Open an invitation link and ensure the profile screen is visible."""
    invitation_url = f"{app_url}/join?token={token}"
    page.goto(invitation_url, wait_until="networkidle")
    expect(page.locator("#profile-screen")).to_be_visible(timeout=5000)


def complete_invitation_signup(page: Page, password: str) -> Response:
    """Fill the invitation signup form and wait for completion.

    Similar to login, a freshly invited user may be routed to onboarding first.
    """
    password_input = page.locator("#user-password")
    expect(password_input).to_be_visible()
    password_input.fill(password)

    submit_button = page.locator('#profile-screen button[type="submit"]')
    expect(submit_button).to_be_enabled()

    with page.expect_response(
        lambda response: response.request.method == "POST"
        and (
            "/invitations/" in response.url and response.url.endswith("/accept")
            or "/auth/invitation/complete" in response.url
            or "/auth/signup" in response.url
        ),
        timeout=15000,
    ) as invitation_response:
        submit_button.click()

    response = invitation_response.value

    try:
        expect(page.locator("#main-app")).to_be_visible(timeout=1500)
        return response
    except Exception:
        pass

    # If the backend returned a token (signup), use it to skip onboarding.
    token = None
    try:
        payload = response.json()
        if isinstance(payload, dict):
            token = payload.get("token")
    except Exception:
        pass

    if token:
        page.evaluate(
            """async (token) => {
                await fetch('/api/onboarding/skip', {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` }
                });
            }""",
            token,
        )

    # Refresh current page; callers can navigate afterward.
    page.reload(wait_until="networkidle")
    expect(page.locator("#main-app")).to_be_visible(timeout=5000)
    return response


def _is_locator_visible(locator) -> bool:
    """Safely determine locator visibility without raising on zero count."""
    try:
        return locator.first.is_visible()
    except AssertionError:
        return False
    except Exception:
        return False


def safe_artifact_name(name: str) -> str:
    """Sanitise a pytest node name for filesystem usage."""
    return re.sub(r"[^A-Za-z0-9_.-]", "_", name)
