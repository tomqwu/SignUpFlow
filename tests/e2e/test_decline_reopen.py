"""Overnight B8 e2e — declining a shift re-opens it for another volunteer.

Alice self-claims an open shift, then declines it. The slot must
re-appear in /v/open so Bob can claim it.
"""

from __future__ import annotations

import pytest

from tests.e2e._helpers import accept_invitation, invite_token, no_js_errors, rid, signup_admin

pytestmark = pytest.mark.e2e


def _invite(page, base, name, email):
    page.goto(f"{base}/a/people")
    page.click("button:has-text('Invite person')")
    page.fill("#inv_name", name)
    page.fill("#inv_email", email)
    page.select_option("#inv_role", "volunteer")
    page.click("button:has-text('Send invite')")
    page.wait_for_selector("#invite-result:has-text('Invitation sent')")


def test_decline_reopens_slot(live_server, new_context, page, db_path):
    base = live_server
    a_email = f"alice+{rid()}@hope.e2e"
    b_email = f"bob+{rid()}@hope.e2e"

    signup_admin(page, base)

    _invite(page, base, "Alice Vol", a_email)
    a_page = accept_invitation(new_context(), base, invite_token(db_path, a_email))
    _invite(page, base, "Bob Vol", b_email)
    b_page = accept_invitation(new_context(), base, invite_token(db_path, b_email))

    page.goto(f"{base}/a/events")
    page.click("button:has-text('New event')")
    page.wait_for_selector("#ev_type", state="visible")
    page.fill("#ev_type", "Sunday 10am Service")
    page.fill("#ev_date", "2026-06-07")
    page.fill("#ev_start", "10:00")
    page.fill("#ev_end", "11:30")
    page.fill("input[name=role_name]", "volunteer")
    page.fill("input[name=role_count]", "1")
    page.click("button:has-text('Create event')")
    page.wait_for_selector("#events-list:has-text('Sunday 10am Service')")

    # Alice claims the only open slot.
    a_page.goto(f"{base}/v/open")
    a_page.wait_for_selector("#open-list:has-text('Sunday 10am Service')")
    a_page.click("button:has-text('Claim')")
    a_page.wait_for_selector("#open-list:has-text('No open shifts')")

    # With the slot filled, Bob does not see it.
    b_page.goto(f"{base}/v/open")
    b_page.wait_for_selector("#open-list:has-text('No open shifts')")

    # Alice declines the shift.
    a_page.goto(f"{base}/v/schedule")
    a_page.click("a:has-text('Sunday 10am Service')")
    a_page.wait_for_selector("#assignment-card")
    a_page.click("button:text-is('Decline')")
    a_page.fill("#decline_reason", "Schedule conflict")
    a_page.click("button:text-is('Confirm decline')")
    a_page.wait_for_selector("#assignment-card .status-text.declined")

    # The slot re-opens — Bob can now see and claim it.
    b_page.goto(f"{base}/v/open")
    b_page.wait_for_selector("#open-list:has-text('Sunday 10am Service')")
    b_page.click("button:has-text('Claim')")
    b_page.wait_for_selector("#open-list:has-text('No open shifts')")

    b_page.goto(f"{base}/v/schedule")
    b_page.wait_for_selector("text=Sunday 10am Service")

    no_js_errors(b_page)
