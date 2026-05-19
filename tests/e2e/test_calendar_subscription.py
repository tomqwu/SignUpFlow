"""Overnight B5 e2e — the calendar subscription only carries published work.

Solve (draft) → the volunteer's ICS feed must NOT contain the shift.
Publish → fetching the same subscribe URL now returns the shift.
"""

from __future__ import annotations

import re

import pytest

from tests.e2e._helpers import accept_invitation, invite_token, no_js_errors, rid, signup_admin

pytestmark = pytest.mark.e2e


def _feed_url(vol_page, base):
    vol_page.goto(f"{base}/v/profile")
    vol_page.wait_for_selector("#calendar-section")
    m = re.search(r"/api/v1/calendar/feed/([A-Za-z0-9_\-]+)", vol_page.content())
    assert m, "calendar feed token not found on /v/profile"
    return f"{base}/api/v1/calendar/feed/{m.group(1)}"


def test_subscription_gates_on_publish(live_server, new_context, page, db_path):
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

    # Solve — produces a DRAFT (unpublished) solution + assignment.
    page.goto(f"{base}/a/solver")
    page.fill("#from_date", "2026-05-19")
    page.fill("#to_date", "2026-06-30")
    page.click("button:has-text('Run solver')")
    page.wait_for_selector("#solver-result:has-text('Review solution')")

    feed_url = _feed_url(vol_page, base)
    draft = vol_page.request.get(feed_url)
    assert draft.status == 200
    assert "Sunday 10am Service" not in draft.text(), "draft leaked into the ICS feed"

    # Publish.
    page.click("a:has-text('Review solution')")
    page.wait_for_url("**/a/solution/**")
    page.wait_for_selector("#publish-state")
    page.click("button:has-text('Publish this solution')")
    page.wait_for_selector("#publish-state:has-text('Unpublish')")

    published = vol_page.request.get(feed_url)
    assert published.status == 200
    assert "Sunday 10am Service" in published.text(), "published shift missing from ICS feed"

    no_js_errors(vol_page)
