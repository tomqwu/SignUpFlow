"""Overnight B3 e2e — a fresh admin completes the first-run wizard.

signup → /a/onboarding shows 0/4 → invite → create event → solve →
publish, with the wizard's progress advancing at each step and ending
in the complete state.
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


def _progress(page, text):
    page.wait_for_selector(f"#onboarding-progress:has-text('{text}')")


def _open_onboarding_from_dashboard(page, text):
    page.wait_for_url("**/a/dashboard")
    page.wait_for_selector(f"#onboarding-banner:has-text('{text}')")
    page.click("#onboarding-banner")
    page.wait_for_url("**/a/onboarding")
    _progress(page, text.replace("/", " of ") + " done")


def _return_to_onboarding(page, text):
    page.locator('a[href="/a/dashboard"]').first.click()
    _open_onboarding_from_dashboard(page, text)


def _follow_step(page, key, expected_path):
    page.locator(f'.ob-step[data-key="{key}"] .btn').click()
    page.wait_for_url(f"**{expected_path}")


def _assert_responsive_step_layout(page):
    first_step = page.locator(".ob-step").first
    content = first_step.locator(".row-main")
    action = first_step.locator(".btn")

    content_box = content.bounding_box()
    action_box = action.bounding_box()
    assert content_box is not None and action_box is not None
    assert content_box["width"] >= 160
    assert action_box["x"] >= content_box["x"] + content_box["width"]

    page.set_viewport_size({"width": 360, "height": 800})
    content_box = content.bounding_box()
    action_box = action.bounding_box()
    assert content_box is not None and action_box is not None
    assert action_box["y"] >= content_box["y"] + content_box["height"]
    assert action_box["width"] >= content_box["width"] - 1


def test_fresh_admin_completes_wizard(live_server, new_context, page, db_path):
    base = live_server
    vol_email = f"vol+{rid()}@hope.e2e"

    signup_admin(page, base)

    # Follow the same dashboard banner and onboarding actions a new admin sees.
    _open_onboarding_from_dashboard(page, "0/4")
    _assert_responsive_step_layout(page)
    page.set_viewport_size({"width": 430, "height": 932})

    # 1) Invite a teammate.
    _follow_step(page, "invite", "/a/people")
    page.click("button:has-text('Invite person')")
    page.fill("#inv_name", "Jamie Park")
    page.fill("#inv_email", vol_email)
    page.select_option("#inv_role", "volunteer")
    page.click("button:has-text('Send invite')")
    page.wait_for_selector("#invite-result:has-text('Invitation sent')")
    accept_invitation(new_context(), base, invite_token(db_path, vol_email))
    _return_to_onboarding(page, "1/4")

    # 2) Create an event.
    ev_date = next_sunday_iso()
    from_date, to_date = solver_window_around(ev_date)
    _follow_step(page, "event", "/a/events")
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
    _return_to_onboarding(page, "2/4")

    # 3) Generate a schedule, 4) review and publish it — one uninterrupted
    # sequence (the solver page only holds the result until you navigate
    # away, so the review link must be clicked without leaving).
    _follow_step(page, "solve", "/a/solver")
    page.fill("#from_date", from_date)
    page.fill("#to_date", to_date)
    page.click("button:has-text('Run solver')")
    page.wait_for_selector("#solver-result:has-text('Review solution')")
    page.click("a:has-text('Review solution')")
    page.wait_for_url("**/a/solution/**")
    page.wait_for_selector("#publish-state")
    page.click("button:has-text('Publish this solution')")
    page.wait_for_selector("#publish-state:has-text('Unpublish')")

    # Wizard is complete and no longer appears as unfinished on the dashboard.
    page.locator('a[href="/a/dashboard"]').first.click()
    page.wait_for_url("**/a/dashboard")
    page.wait_for_selector("#onboarding-banner", state="detached")
    page.goto(f"{base}/a/onboarding")
    page.wait_for_selector("#onboarding-complete")
    _progress(page, "4 of 4 done")

    no_js_errors(page)
