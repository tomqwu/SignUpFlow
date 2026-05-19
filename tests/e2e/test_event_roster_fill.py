"""Overnight B4 e2e — admin fills a roster gap inline; volunteer sees it."""

from __future__ import annotations

import pytest

from tests.e2e._helpers import accept_invitation, invite_token, no_js_errors, rid, signup_admin

pytestmark = pytest.mark.e2e


def test_admin_fills_roster_gap(live_server, new_context, page, db_path):
    base = live_server
    vol_email = f"vol+{rid()}@hope.e2e"

    signup_admin(page, base)

    page.goto(f"{base}/a/people")
    page.click("button:has-text('Invite person')")
    page.fill("#inv_name", "Pat Vol")
    page.fill("#inv_email", vol_email)
    page.select_option("#inv_role", "volunteer")
    page.click("button:has-text('Send invite')")
    page.wait_for_selector("#invite-result:has-text('Invitation sent')")
    vol_page = accept_invitation(new_context(), base, invite_token(db_path, vol_email))

    page.goto(f"{base}/a/events")
    page.click("button:has-text('New event')")
    page.wait_for_selector("#ev_type", state="visible")
    page.fill("#ev_type", "Sunday 10am Service")
    page.fill("#ev_date", "2026-06-07")
    page.fill("#ev_start", "10:00")
    page.fill("#ev_end", "11:30")
    page.fill("input[name=role_name]", "usher")
    page.fill("input[name=role_count]", "1")
    page.click("button:has-text('Create event')")
    page.wait_for_selector("#events-list:has-text('Sunday 10am Service')")

    # Open the roster — coverage shows the usher gap.
    page.click("a:has-text('Manage')")
    page.wait_for_selector("#role-coverage[data-staffed='no']")
    page.wait_for_selector(".cov-row[data-role='usher'][data-gap='1']")

    # Inline-fill the gap with the volunteer.
    page.select_option(".cov-row[data-role='usher'] select[name=person_id]", label="Pat Vol")
    page.click(".cov-row[data-role='usher'] button:has-text('Fill')")
    page.wait_for_selector("#role-coverage[data-staffed='yes']")

    # Volunteer now sees the shift.
    vol_page.goto(f"{base}/v/schedule")
    vol_page.wait_for_selector("text=Sunday 10am Service")

    no_js_errors(page)
