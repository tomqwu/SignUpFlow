"""Overnight C3 — e2e backfill: notifications, manual assign, unpublish.

Regression guards for existing flows: inbox mark-all-read + email
preference save, admin manual per-event assign/remove, and the
publish → unpublish → rollback state machine.
"""

from __future__ import annotations

import pytest

from tests.e2e._helpers import accept_invitation, invite_token, no_js_errors, rid, signup_admin

pytestmark = pytest.mark.e2e


def _new_event(page, base, etype="Sunday 10am Service", role="volunteer", count="1"):
    page.goto(f"{base}/a/events")
    page.click("button:has-text('New event')")
    page.wait_for_selector("#ev_type", state="visible")
    page.fill("#ev_type", etype)
    page.fill("#ev_date", "2026-06-07")
    page.fill("#ev_start", "10:00")
    page.fill("#ev_end", "11:30")
    page.fill("input[name=role_name]", role)
    page.fill("input[name=role_count]", count)
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


def test_inbox_mark_all_read_and_save_prefs(live_server, new_context, page, db_path):
    base = live_server
    vol_email = f"vol+{rid()}@hope.e2e"
    signup_admin(page, base)
    page.goto(f"{base}/a/people")
    page.click("button:has-text('Invite person')")
    page.fill("#inv_name", "Jess Vol")
    page.fill("#inv_email", vol_email)
    page.select_option("#inv_role", "volunteer")
    page.click("button:has-text('Send invite')")
    page.wait_for_selector("#invite-result:has-text('Invitation sent')")
    vol_page = accept_invitation(new_context(), base, invite_token(db_path, vol_email))

    _new_event(page, base)
    _solve_and_publish(page, base)  # auto-creates an inbox notification

    vol_page.goto(f"{base}/v/inbox")
    vol_page.wait_for_selector("#inbox-list button:has-text('Mark all read')")
    vol_page.click("#inbox-list button:has-text('Mark all read')")
    vol_page.wait_for_selector("#inbox-list button:has-text('Mark all read')", state="detached")

    # Email preferences save.
    vol_page.select_option("#np_freq", "weekly")
    vol_page.click("#notif-prefs button:has-text('Save preferences')")
    vol_page.wait_for_selector("#notif-prefs:has-text('Preferences saved.')")

    no_js_errors(vol_page)


def test_manual_assign_and_remove(live_server, page):
    base = live_server
    signup_admin(page, base)  # admin is a person → assignable candidate
    _new_event(page, base, etype="Midweek Prayer")

    page.click("a:has-text('Manage')")
    page.wait_for_selector("#event-assignments")
    page.select_option("#ea_person", label="Admin Dana")
    page.click("button:has-text('Add to event')")
    page.wait_for_selector("#event-assignments:has-text('Admin Dana')")

    page.click("button:has-text('Remove')")
    page.wait_for_selector("#event-assignments:has-text('No one assigned yet')")

    no_js_errors(page)


def test_publish_then_unpublish_state(live_server, page):
    base = live_server
    signup_admin(page, base)
    _new_event(page, base, etype="Service A")
    _solve_and_publish(page, base)

    # Unpublish returns the control to its pre-publish state; because the
    # solution was previously published, rollback is now offered.
    page.click("#publish-state button:has-text('Unpublish')")
    page.wait_for_selector("#publish-state:has-text('Publish this solution')")
    page.wait_for_selector("#publish-state:has-text('Roll back to this version')")

    no_js_errors(page)
