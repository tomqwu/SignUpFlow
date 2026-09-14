"""Real-browser request-integrity coverage for standard forms and HTMX."""

from __future__ import annotations

import pytest
from playwright.sync_api import expect

from tests.e2e._helpers import rid

pytestmark = pytest.mark.e2e


def test_browser_propagates_csrf_and_rejects_foreign_origin(live_server, page):
    base = live_server
    page.goto(f"{base}/auth/signup")

    signup_form = page.locator('form[action="/auth/signup"]')
    expect(signup_form.locator('input[name="csrf_token"]')).to_have_count(1)
    browser_token = page.locator('meta[name="csrf-token"]').get_attribute("content")
    assert browser_token
    expect(signup_form.locator('input[name="csrf_token"]')).to_have_value(browser_token)

    page.fill("#org_name", "Protected Org")
    page.fill("#name", "Protected Admin")
    page.fill("#email", f"protected+{rid()}@hope.e2e")
    page.fill("#password", "HopePass123!")
    with page.expect_response(lambda response: response.url.endswith("/auth/signup")) as info:
        page.click("button[type=submit]")
    signup_response = info.value
    assert signup_response.status == 303, {
        "headers": signup_response.request.headers,
        "post_data": signup_response.request.post_data,
        "response": signup_response.text(),
    }
    page.wait_for_url("**/a/dashboard")
    page.goto(f"{base}/v/profile")

    rejected = page.request.post(
        f"{base}/v/profile",
        form={"name": "Cross-origin rename", "timezone": "UTC", "language": "en"},
        headers={
            "Origin": "https://attacker.example",
            "X-CSRF-Token": browser_token,
        },
    )
    assert rejected.status == 403

    page.reload()
    expect(page.locator("#pf_name")).to_have_value("Protected Admin")

    htmx_request_headers: list[dict[str, str]] = []

    def record_profile_request(request):
        if request.method == "POST" and request.url.endswith("/v/profile"):
            htmx_request_headers.append(request.headers)

    page.on("request", record_profile_request)
    page.fill("#pf_name", "Same-origin rename")
    page.get_by_role("button", name="Save profile").click()
    expect(page.locator("#profile-form")).to_contain_text("Profile saved")

    assert htmx_request_headers
    assert htmx_request_headers[-1]["x-csrf-token"] == page.locator(
        'meta[name="csrf-token"]'
    ).get_attribute("content")
    expect(page.locator("#pf_name")).to_have_value("Same-origin rename")
