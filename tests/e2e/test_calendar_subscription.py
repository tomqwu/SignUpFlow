"""BO-10 calendar acceptance for every discovered domain playbook.

Draft work stays hidden. Published work appears once, keeps its UID when moved,
uses the member's non-UTC timezone, and disappears when the event is cancelled.
"""

from __future__ import annotations

import re
from datetime import timedelta

import pytest
from icalendar import Calendar
from playwright.sync_api import expect

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


def _feed_url(vol_page, base):
    vol_page.goto(f"{base}/v/profile")
    vol_page.wait_for_selector("#calendar-section")
    m = re.search(r"/api/v1/calendar/feed/([A-Za-z0-9_\-]+)", vol_page.content())
    assert m, "calendar feed token not found on /v/profile"
    return f"{base}/api/v1/calendar/feed/{m.group(1)}"


@pytest.mark.parametrize("width", [360, 1440])
def test_subscription_tracks_publish_move_and_cancel(
    live_server,
    new_context,
    page,
    db_path,
    tmp_path,
    playbook_spec,
    width,
):
    base = live_server
    suffix = rid()
    vol_email = f"calendar-{playbook_spec.id}-{suffix}@hope.e2e"
    event_title = f"{playbook_spec.event} calendar drill {suffix}"
    role = playbook_spec.critical_role
    page.set_viewport_size({"width": width, "height": 900})

    signup_admin(page, base, org=f"{playbook_spec.name} calendar {suffix}")

    page.goto(f"{base}/a/people")
    page.click("button:has-text('Invite person')")
    page.fill("#inv_name", "Dana Vol")
    page.fill("#inv_email", vol_email)
    page.select_option("#inv_role", "volunteer")
    page.fill("#inv_qualifications", role)
    with page.expect_response(
        lambda response: response.request.method == "POST"
        and response.url.endswith("/a/people/invite")
    ) as invitation_response:
        page.click("button:has-text('Send invite')")
    assert invitation_response.value.ok, invitation_response.value.text()
    expect(page.locator("#invite-result")).to_contain_text("Invitation created")
    vol_page = accept_invitation(new_context(), base, invite_token(db_path, vol_email))
    vol_page.set_viewport_size({"width": width, "height": 900})
    vol_page.goto(f"{base}/v/profile")
    vol_page.fill("#pf_tz", "America/Toronto")
    vol_page.get_by_role("button", name="Save profile").click()
    expect(vol_page.locator("#profile-form")).to_contain_text("Profile saved")

    ev_date = next_sunday_iso()
    from_date, to_date = solver_window_around(ev_date)
    page.goto(f"{base}/a/events")
    page.click("button:has-text('New event')")
    page.wait_for_selector("#ev_type", state="visible")
    page.fill("#ev_type", event_title)
    page.fill("#ev_date", ev_date)
    page.fill("#ev_start", "10:00")
    page.fill("#ev_end", "11:30")
    page.fill("input[name=role_name]", role)
    page.fill("input[name=role_count]", "1")
    page.click("button:has-text('Create event')")
    page.wait_for_selector(f"#events-list:has-text('{event_title}')")

    # Solve — produces a DRAFT (unpublished) solution + assignment.
    page.goto(f"{base}/a/solver")
    page.fill("#from_date", from_date)
    page.fill("#to_date", to_date)
    page.click("button:has-text('Run solver')")
    page.wait_for_selector("#solver-result:has-text('Review solution')")

    feed_url = _feed_url(vol_page, base)
    draft = vol_page.request.get(feed_url)
    assert draft.status == 200
    assert event_title not in draft.text(), "draft leaked into the ICS feed"

    # Publish.
    page.click("a:has-text('Review solution')")
    page.wait_for_url("**/a/solution/**")
    page.wait_for_selector("#publish-state")
    page.click("button:has-text('Publish this solution')")
    page.wait_for_selector("#publish-state:has-text('Unpublish')")

    published = vol_page.request.get(feed_url)
    assert published.status == 200
    assert event_title in published.text(), "published shift missing from ICS feed"
    published_calendar = Calendar.from_ical(published.body())
    published_events = published_calendar.walk("VEVENT")
    assert len(published_events) == 1
    published_event = published_events[0]
    uid = str(published_event["UID"])
    published_start = published_event.decoded("DTSTART")
    assert getattr(published_start.tzinfo, "key", None) == "America/Toronto"

    page.goto(f"{base}/a/events")
    event_row = page.locator(".event-row", has_text=event_title)
    event_row.get_by_role("button", name="Edit event").click()
    edit_form = page.locator("form.event-edit-form").filter(has=page.locator(f"text={event_title}"))
    if edit_form.count() == 0:
        edit_form = page.locator("form.event-edit-form:visible")
    edit_form.locator('input[name="start_time"]').fill("11:00")
    edit_form.locator('input[name="end_time"]').fill("12:30")
    with page.expect_response(
        lambda response: response.request.method == "POST" and response.url.endswith("/update")
    ) as update_response:
        edit_form.get_by_role("button", name="Save change").click()
    assert update_response.value.ok, update_response.value.text()
    expect(page.locator("#events-list .event-row", has_text=event_title)).to_be_visible()

    moved = vol_page.request.get(feed_url)
    moved_events = Calendar.from_ical(moved.body()).walk("VEVENT")
    assert len(moved_events) == 1
    assert str(moved_events[0]["UID"]) == uid
    moved_start = moved_events[0].decoded("DTSTART")
    assert moved_start - published_start == timedelta(hours=1)
    assert getattr(moved_start.tzinfo, "key", None) == "America/Toronto"

    page.goto(f"{base}/a/events")
    with page.expect_response(
        lambda response: response.request.method == "POST" and response.url.endswith("/delete")
    ) as delete_response:
        page.locator(".event-row", has_text=event_title).get_by_role(
            "button", name="Delete event"
        ).click()
    assert delete_response.value.ok, delete_response.value.text()
    expect(page.locator(".event-row", has_text=event_title)).to_have_count(0)
    cancelled = Calendar.from_ical(vol_page.request.get(feed_url).body())
    assert cancelled.walk("VEVENT") == []

    vol_page.goto(f"{base}/v/profile")
    vol_page.screenshot(
        path=str(tmp_path / f"{playbook_spec.id}-{width}-calendar-current.png"),
        full_page=True,
    )

    no_js_errors(page)
    no_js_errors(vol_page)
