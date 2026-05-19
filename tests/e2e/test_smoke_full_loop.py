"""Canonical end-to-end loop — proves the harness + blocking lane.

signup → dashboard → invite volunteer → accept invite → create event
with a role → run solver → review solution → publish → volunteer sees
the shift → accepts it → admin review shows them.
"""

from __future__ import annotations

import pytest

from tests.e2e._helpers import accept_invitation, invite_token, no_js_errors, rid, signup_admin

pytestmark = pytest.mark.e2e


def test_full_loop(live_server, new_context, page, db_path):
    base = live_server
    r = rid()
    vol_email = f"jamie+{r}@hope.e2e"

    signup_admin(page, base)

    # Invite a volunteer.
    page.goto(f"{base}/a/people")
    page.click("button:has-text('Invite person')")
    page.fill("#inv_name", "Jamie Park")
    page.fill("#inv_email", vol_email)
    page.select_option("#inv_role", "volunteer")
    page.click("button:has-text('Send invite')")
    page.wait_for_selector("#invite-result:has-text('Invitation sent')")

    tok = invite_token(db_path, vol_email)
    assert tok, "invitation token not found in DB"
    # Volunteer gets an isolated context so accepting the invite does not
    # overwrite the admin's session cookie.
    vol_page = accept_invitation(new_context(), base, tok)

    # Admin creates an event with a role the solver can fill.
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

    # Solve.
    page.goto(f"{base}/a/solver")
    page.fill("#from_date", "2026-05-19")
    page.fill("#to_date", "2026-06-30")
    page.click("button:has-text('Run solver')")
    page.wait_for_selector("#solver-result:has-text('Review solution')")
    page.click("a:has-text('Review solution')")
    page.wait_for_url("**/a/solution/**")
    page.wait_for_selector("#publish-state")

    # Publish.
    page.click("button:has-text('Publish this solution')")
    page.wait_for_selector("#publish-state:has-text('Unpublish')")

    # Volunteer sees and accepts the published shift.
    vol_page.goto(f"{base}/v/schedule")
    vol_page.wait_for_selector("text=Sunday 10am Service")
    vol_page.click("a:has-text('Sunday 10am Service')")
    vol_page.wait_for_selector("#assignment-card")
    vol_page.click("button:has-text('Accept')")
    vol_page.wait_for_selector("#assignment-card .status-text.confirmed")

    # Admin review reflects the assignee.
    page.reload()
    page.wait_for_selector("text=Jamie Park")

    no_js_errors(page)
