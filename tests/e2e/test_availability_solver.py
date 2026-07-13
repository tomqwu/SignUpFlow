"""Overnight B6 e2e — the solver must not assign a volunteer on time-off.

Regression guard for an existing correctness property that had unit
coverage but no end-to-end enforcement: a volunteer whose time-off
covers the only event date must be left unassigned (the role stays
open) rather than double-booked.
"""

from __future__ import annotations

import pytest

from tests.e2e._helpers import (
    accept_invitation,
    invite_token,
    next_sunday_iso,
    no_js_errors,
    rid,
    signup_admin,
    solver_window_around,
)

pytestmark = pytest.mark.e2e


def test_timeoff_blocks_solver_assignment(live_server, new_context, page, db_path):
    base = live_server
    vol_email = f"vol+{rid()}@hope.e2e"

    signup_admin(page, base)

    page.goto(f"{base}/a/people")
    page.click("button:has-text('Invite person')")
    page.fill("#inv_name", "Dana Vol")
    page.fill("#inv_email", vol_email)
    page.select_option("#inv_role", "volunteer")
    page.click("button:has-text('Send invite')")
    page.wait_for_selector("#invite-result:has-text('Invitation sent')")
    vol_page = accept_invitation(new_context(), base, invite_token(db_path, vol_email))

    # Volunteer books time-off covering the event date.
    ev_date = next_sunday_iso()
    from_date, to_date = solver_window_around(ev_date)
    vol_page.goto(f"{base}/v/availability")
    vol_page.wait_for_selector("#start_date")
    vol_page.fill("#start_date", ev_date)
    vol_page.fill("#end_date", ev_date)
    vol_page.fill("#reason", "Vacation")
    vol_page.click("button:has-text('Add time-off')")
    vol_page.wait_for_selector("#timeoff-list:has-text('Vacation')")

    # Admin creates the only event on that exact date, one open role.
    page.goto(f"{base}/a/events")
    page.click("button:has-text('New event')")
    page.wait_for_selector("#ev_type", state="visible")
    page.fill("#ev_type", "Sunday 10am Service")
    page.fill("#ev_date", ev_date)
    page.fill("#ev_start", "10:00")
    page.fill("#ev_end", "11:30")
    page.fill("input[name=role_name]", "volunteer")
    page.fill("input[name=role_count]", "1")
    page.click("button:has-text('Create event')")
    page.wait_for_selector("#events-list:has-text('Sunday 10am Service')")

    # Solve, then publish.
    page.goto(f"{base}/a/solver")
    page.fill("#from_date", from_date)
    page.fill("#to_date", to_date)
    page.click("button:has-text('Run solver')")
    page.wait_for_selector("#solver-result:has-text('Review solution')")
    page.click("a:has-text('Review solution')")
    page.wait_for_url("**/a/solution/**")
    page.wait_for_selector("#publish-state")
    page.click("button:has-text('Publish this solution')")
    page.wait_for_selector("#publish-state:has-text('Unpublish')")

    # The on-time-off volunteer was NOT scheduled.
    vol_page.goto(f"{base}/v/schedule")
    vol_page.wait_for_selector("text=No assignments yet")

    no_js_errors(vol_page)
