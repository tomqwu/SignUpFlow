"""Overnight B7 e2e — admin bulk-notifies the published schedule.

publish → admin clicks "Notify assignees" → the assignee's inbox shows
the reminder (alongside the auto publish notification).
"""

from __future__ import annotations

import pytest

from tests.e2e._helpers import accept_invitation, invite_token, no_js_errors, rid, signup_admin

pytestmark = pytest.mark.e2e


def test_notify_published_schedule_reaches_inbox(live_server, new_context, page, db_path):
    base = live_server
    vol_email = f"vol+{rid()}@hope.e2e"

    signup_admin(page, base)

    page.goto(f"{base}/a/people")
    page.click("button:has-text('Invite person')")
    page.fill("#inv_name", "Robin Vol")
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
    page.fill("input[name=role_name]", "volunteer")
    page.fill("input[name=role_count]", "1")
    page.click("button:has-text('Create event')")
    page.wait_for_selector("#events-list:has-text('Sunday 10am Service')")

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

    # Explicit bulk reminder.
    page.click("button:has-text('Notify assignees')")
    page.wait_for_selector("#notify-result:has-text('Reminder sent to 1 assignee(s)')")

    # The volunteer's inbox carries both the auto publish notice and the reminder.
    vol_page.goto(f"{base}/v/inbox")
    vol_page.wait_for_selector("#inbox-list:has-text('Reminder')")
    vol_page.wait_for_selector("#inbox-list:has-text('New assignment')")
    vol_page.wait_for_selector("#inbox-list:has-text('unread')")

    no_js_errors(page)
