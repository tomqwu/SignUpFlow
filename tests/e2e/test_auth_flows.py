"""Overnight C1 — e2e backfill for the auth flows.

Regression guards for signup → dashboard, logout + protected-route
gating, login (success + bad password), the non-enumerating
forgot-password response, and invite-accept.
"""

from __future__ import annotations

import pytest

from tests.e2e._helpers import accept_invitation, no_js_errors, rid, signup_admin

pytestmark = pytest.mark.e2e


def test_signup_logout_login_cycle(live_server, page):
    base = live_server
    email = signup_admin(page, base)  # lands on /a/dashboard

    # Sign out → back to the login page.
    page.click("button:has-text('Sign out')")
    page.wait_for_url("**/auth/login")

    # Protected route now bounces to login.
    page.goto(f"{base}/a/dashboard")
    page.wait_for_url("**/auth/login")

    # Log back in via the form.
    page.goto(f"{base}/auth/login")
    page.fill("#email", email)
    page.fill("#password", "HopePass123!")
    page.click("button:has-text('Sign in')")
    page.wait_for_url("**/a/dashboard")

    no_js_errors(page)


def test_login_rejects_bad_password(live_server, page):
    base = live_server
    email = signup_admin(page, base)
    page.click("button:has-text('Sign out')")
    page.wait_for_url("**/auth/login")

    page.fill("#email", email)
    page.fill("#password", "WrongPass999!")
    page.click("button:has-text('Sign in')")
    page.wait_for_selector(".form-error:has-text('Invalid email or password.')")


def test_forgot_password_is_non_enumerating(live_server, page):
    base = live_server
    email = signup_admin(page, base)
    page.click("button:has-text('Sign out')")
    page.wait_for_url("**/auth/login")

    msg = "If an account exists for that email, recovery instructions were processed."

    # Known account → generic message.
    page.goto(f"{base}/auth/forgot")
    page.fill("#email", email)
    page.click("button:has-text('Send reset link')")
    page.wait_for_selector(f"text={msg}")

    # Unknown account → identical message (no user enumeration).
    page.goto(f"{base}/auth/forgot")
    page.fill("#email", f"nobody+{rid()}@nowhere.e2e")
    page.click("button:has-text('Send reset link')")
    page.wait_for_selector(f"text={msg}")


def test_invite_accept_lands_on_schedule(live_server, new_context, page):
    base = live_server
    vol_email = f"vol+{rid()}@hope.e2e"

    signup_admin(page, base)
    page.goto(f"{base}/a/people")
    page.click("button:has-text('Invite person')")
    page.fill("#inv_name", "Casey Vol")
    page.fill("#inv_email", vol_email)
    page.select_option("#inv_role", "volunteer")
    page.click("button:has-text('Send invite')")
    page.wait_for_selector("#invite-result:has-text('Invitation created')")

    link = page.locator("#invite-link")
    link.wait_for()
    invite_url = link.input_value()
    assert invite_url.startswith(f"{base}/auth/invitation/")
    page.context.grant_permissions(["clipboard-read", "clipboard-write"])
    page.get_by_role("button", name="Copy link").click()
    page.get_by_role("button", name="Copied").wait_for()
    assert page.evaluate("navigator.clipboard.readText()") == invite_url
    page.evaluate(
        "() => { navigator.clipboard.writeText = () => Promise.reject(new Error('denied')) }"
    )
    page.get_by_role("button", name="Copied").click()
    page.get_by_role("alert").filter(has_text="Copy unavailable").wait_for()
    page.reload()
    pending = page.locator(".invite-row").filter(has_text=vol_email)
    pending.wait_for()
    recovered_url = pending.locator("input[data-invite-link]").input_value()
    assert recovered_url == invite_url
    tok = recovered_url.rsplit("/", 1)[1]
    vol_page = accept_invitation(new_context(), base, tok)  # asserts /v/schedule
    vol_page.wait_for_selector("text=Schedule")
    no_js_errors(vol_page)


def test_pending_invitation_can_be_cancelled_and_recreated(live_server, page):
    base = live_server
    vol_email = f"cancel+{rid()}@hope.e2e"
    signup_admin(page, base)
    page.goto(f"{base}/a/people")
    page.get_by_role("button", name="Invite person").click()
    page.fill("#inv_name", "Cancel Member")
    page.fill("#inv_email", vol_email)
    page.get_by_role("button", name="Send invite").click()
    page.wait_for_selector("#invite-result:has-text('Invitation created')")

    page.reload()
    pending = page.locator(".invite-row").filter(has_text=vol_email)
    pending.get_by_role("button", name="Cancel invitation").click()
    page.wait_for_url("**/a/people")
    assert page.locator(".invite-row").filter(has_text=vol_email).count() == 0

    page.get_by_role("button", name="Invite person").click()
    page.fill("#inv_name", "Cancel Member")
    page.fill("#inv_email", vol_email)
    page.get_by_role("button", name="Send invite").click()
    page.wait_for_selector("#invite-result:has-text('Invitation created')")
    no_js_errors(page)
