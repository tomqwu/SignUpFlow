"""Overnight B2 e2e — one volunteer covers another's swap, end-to-end."""

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


def test_cover_a_swap_end_to_end(live_server, new_context, page, db_path):
    base = live_server
    a_email = f"a+{rid()}@hope.e2e"
    b_email = f"b+{rid()}@hope.e2e"

    signup_admin(page, base)

    _invite(page, base, "Vol A", a_email)
    a_page = accept_invitation(new_context(), base, invite_token(db_path, a_email))
    _invite(page, base, "Vol B", b_email)
    b_page = accept_invitation(new_context(), base, invite_token(db_path, b_email))

    # Admin creates an event with one open role.
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

    # Vol A claims it, then requests a swap.
    a_page.goto(f"{base}/v/open")
    a_page.wait_for_selector("#open-list:has-text('Sunday 10am Service')")
    a_page.click("button:has-text('Claim')")
    a_page.goto(f"{base}/v/schedule")
    a_page.click("a:has-text('Sunday 10am Service')")
    a_page.wait_for_selector("#assignment-card")
    a_page.click("button:has-text('Request swap')")
    a_page.wait_for_selector("#assignment-card .status-text.swap_requested")

    # Vol B covers it.
    b_page.goto(f"{base}/v/swaps")
    b_page.wait_for_selector("#swaps-open-list:has-text('Sunday 10am Service')")
    b_page.click("button:has-text('Cover this shift')")
    b_page.wait_for_selector("#swaps-open-list:has-text('No swap requests to cover')")

    # B now has the shift; A no longer does.
    b_page.goto(f"{base}/v/schedule")
    b_page.wait_for_selector("text=Sunday 10am Service")
    a_page.goto(f"{base}/v/schedule")
    a_page.wait_for_selector("text=No assignments yet")

    no_js_errors(b_page)
