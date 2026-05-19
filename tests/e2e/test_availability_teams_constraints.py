"""Overnight C2 — e2e backfill: availability, teams, constraints.

Regression guards for existing admin/volunteer management flows that
only had web/unit coverage.
"""

from __future__ import annotations

import pytest

from tests.e2e._helpers import no_js_errors, signup_admin

pytestmark = pytest.mark.e2e


def test_timeoff_add_and_remove(live_server, page):
    base = live_server
    signup_admin(page, base)

    page.goto(f"{base}/v/availability")
    page.wait_for_selector("#start_date")
    page.fill("#start_date", "2026-07-01")
    page.fill("#end_date", "2026-07-05")
    page.fill("#reason", "Holiday")
    page.click("button:has-text('Add time-off')")
    page.wait_for_selector("#timeoff-list:has-text('Holiday')")

    # hx-confirm dialog is auto-accepted by the page fixture.
    page.click("button:has-text('Remove')")
    page.wait_for_selector("#timeoff-list:has-text('No time-off booked')")

    no_js_errors(page)


def test_rrule_preset_set_and_clear(live_server, page):
    base = live_server
    signup_admin(page, base)

    page.goto(f"{base}/v/availability")
    page.wait_for_selector("#rrule-section")
    page.click("#rrule-section button:has-text('Every Sunday')")
    page.wait_for_selector("#rrule-section .mono-data:has-text('FREQ=WEEKLY;BYDAY=SU')")

    page.click("#rrule-section button:has-text('Clear recurring rule')")
    page.wait_for_selector("#rrule-section:has-text('No recurring rule')")

    no_js_errors(page)


def test_team_create_and_add_member(live_server, page):
    base = live_server
    signup_admin(page, base)  # admin is also a person → a valid member candidate

    page.goto(f"{base}/a/teams")
    page.wait_for_selector("#teams-list")
    page.click("button:has-text('New team')")
    page.fill("#tm_name", "Worship Team")
    page.fill("#tm_desc", "Sunday music")
    page.click("button:has-text('Create team')")
    page.wait_for_selector("#teams-list:has-text('Worship Team')")

    page.select_option("#teams-list select[name=person_id]", label="Admin Dana")
    page.click("#teams-list button:has-text('Add member')")
    page.wait_for_selector("#teams-list:has-text('Admin Dana')")

    no_js_errors(page)


def test_constraint_create(live_server, page):
    base = live_server
    signup_admin(page, base)

    page.goto(f"{base}/a/constraints")
    page.wait_for_selector("#constraints-list")
    page.click("button:has-text('New constraint')")
    page.fill("#c_key", "min_gap")
    page.select_option("#c_type", "soft")
    page.fill("#c_weight", "10")
    page.fill("#c_pred", "min_gap_hours_satisfied(person_id, 12)")
    page.click("button:has-text('Create constraint')")
    page.wait_for_selector("#constraints-list:has-text('min_gap')")

    no_js_errors(page)
