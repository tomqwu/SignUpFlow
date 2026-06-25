"""Overnight B1 e2e — volunteer self-claims an open shift end-to-end."""

from __future__ import annotations

import pytest

from tests.e2e._helpers import (
    accept_invitation,
    invite_token,
    next_sunday_iso,
    no_js_errors,
    rid,
    signup_admin,
)

pytestmark = pytest.mark.e2e


def test_volunteer_claims_open_shift(live_server, new_context, page, db_path):
    base = live_server
    vol_email = f"vol+{rid()}@hope.e2e"

    signup_admin(page, base)

    # Invite + accept a volunteer (isolated context).
    page.goto(f"{base}/a/people")
    page.click("button:has-text('Invite person')")
    page.fill("#inv_name", "Sam Lee")
    page.fill("#inv_email", vol_email)
    page.select_option("#inv_role", "volunteer")
    page.click("button:has-text('Send invite')")
    page.wait_for_selector("#invite-result:has-text('Invitation sent')")
    tok = invite_token(db_path, vol_email)
    assert tok
    vol_page = accept_invitation(new_context(), base, tok)

    # Admin creates an event with one open 'volunteer' role.
    page.goto(f"{base}/a/events")
    page.click("button:has-text('New event')")
    page.wait_for_selector("#ev_type", state="visible")
    page.fill("#ev_type", "Sunday 10am Service")
    page.fill("#ev_date", next_sunday_iso())
    page.fill("#ev_start", "10:00")
    page.fill("#ev_end", "11:30")
    page.fill("input[name=role_name]", "volunteer")
    page.fill("input[name=role_count]", "1")
    page.click("button:has-text('Create event')")
    page.wait_for_selector("#events-list:has-text('Sunday 10am Service')")

    # Volunteer sees it on /v/open and claims it.
    vol_page.goto(f"{base}/v/open")
    vol_page.wait_for_selector("#open-list:has-text('Sunday 10am Service')")
    assert "1 of 1 open" in vol_page.content()
    vol_page.click("button:has-text('Claim')")
    vol_page.wait_for_selector("#open-list:has-text('No open shifts')")

    # It now appears on their schedule.
    vol_page.goto(f"{base}/v/schedule")
    vol_page.wait_for_selector("text=Sunday 10am Service")

    no_js_errors(vol_page)
