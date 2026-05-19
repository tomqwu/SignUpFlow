"""Overnight C4 — e2e backfill: analytics, recurring, all-assignments, swap review.

Regression guards for existing admin flows that lacked committed e2e.
"""

from __future__ import annotations

import pytest

from tests.e2e._helpers import accept_invitation, invite_token, no_js_errors, rid, signup_admin

pytestmark = pytest.mark.e2e


def _new_event(page, base, etype):
    page.goto(f"{base}/a/events")
    page.click("button:has-text('New event')")
    page.wait_for_selector("#ev_type", state="visible")
    page.fill("#ev_type", etype)
    page.fill("#ev_date", "2026-06-07")
    page.fill("#ev_start", "10:00")
    page.fill("#ev_end", "11:30")
    page.fill("input[name=role_name]", "volunteer")
    page.fill("input[name=role_count]", "1")
    page.click("button:has-text('Create event')")
    page.wait_for_selector(f"#events-list:has-text('{etype}')")


def _solve_and_publish(page, base):
    page.goto(f"{base}/a/solver")
    page.fill("#from_date", "2026-05-19")
    page.fill("#to_date", "2026-06-30")
    page.click("button:has-text('Run solver')")
    page.wait_for_selector("#solver-result:has-text('Review solution')")
    page.click("a:has-text('Review solution')")
    page.wait_for_url("**/a/solution/**")
    page.wait_for_selector("#publish-state")
    page.click("button:has-text('Publish this solution')")
    page.wait_for_selector("#publish-state:has-text('Unpublish')")


def test_analytics_page_loads_and_filters(live_server, page):
    base = live_server
    signup_admin(page, base)
    page.goto(f"{base}/a/analytics")
    page.wait_for_selector(".page-title:has-text('Analytics')")
    page.wait_for_selector(".kpi-grid")
    page.fill("#an_days", "60")
    page.fill("#an_thr", "3")
    page.click("button:has-text('Apply filters')")
    page.wait_for_selector(".kpi-grid")
    no_js_errors(page)


def test_recurring_series_create_and_delete(live_server, page):
    base = live_server
    signup_admin(page, base)
    page.goto(f"{base}/a/recurring")
    page.wait_for_selector("#recurring-list")
    page.click("button:has-text('New series')")
    page.fill("#rs_title", "Weekly Worship")
    page.check("input[name=selected_days][value=sunday]")
    page.fill("#rs_sd", "2026-07-05")
    page.fill("#rs_st", "10:00")
    page.click("button:has-text('Create series')")
    page.wait_for_selector("#recurring-list:has-text('Weekly Worship')")

    page.click("#recurring-list button:has-text('Delete')")
    page.wait_for_selector("#recurring-list:has-text('Weekly Worship')", state="detached")
    no_js_errors(page)


def test_all_assignments_view(live_server, page):
    base = live_server
    signup_admin(page, base)
    _new_event(page, base, "Midweek Prayer")
    page.click("a:has-text('Manage')")
    page.wait_for_selector("#event-assignments")
    page.select_option("#ea_person", label="Admin Dana")
    page.click("button:has-text('Add to event')")
    page.wait_for_selector("#event-assignments:has-text('Admin Dana')")

    page.goto(f"{base}/a/assignments")
    page.wait_for_selector(".page-title:has-text('Assignments')")
    page.wait_for_selector("text=Midweek Prayer")
    no_js_errors(page)


def test_swap_review_approve(live_server, new_context, page, db_path):
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

    _new_event(page, base, "Sunday 10am Service")
    _solve_and_publish(page, base)

    vol_page.goto(f"{base}/v/schedule")
    vol_page.click("a:has-text('Sunday 10am Service')")
    vol_page.wait_for_selector("#assignment-card")
    vol_page.click("button:has-text('Request swap')")
    vol_page.wait_for_selector("#assignment-card .status-text.swap_requested")

    page.goto(f"{base}/a/swaps")
    page.wait_for_selector("#swaps-list:has-text('Sunday 10am Service')")
    page.click("button:has-text('Approve (unassign)')")
    page.wait_for_selector("#swaps-list:has-text('No swap requests')")
    no_js_errors(page)
