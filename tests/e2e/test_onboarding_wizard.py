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


def _progress(page, base, text):
    page.goto(f"{base}/a/onboarding")
    page.wait_for_selector(f"#onboarding-progress:has-text('{text}')")


def test_fresh_admin_completes_wizard(live_server, new_context, page, db_path):
    base = live_server
    vol_email = f"vol+{rid()}@hope.e2e"

    signup_admin(page, base)

    # Fresh org — nothing done yet.
    _progress(page, base, "0 of 4 done")

    # 1) Invite a teammate.
    page.goto(f"{base}/a/people")
    page.click("button:has-text('Invite person')")
    page.fill("#inv_name", "Jamie Park")
    page.fill("#inv_email", vol_email)
    page.select_option("#inv_role", "volunteer")
    page.click("button:has-text('Send invite')")
    page.wait_for_selector("#invite-result:has-text('Invitation sent')")
    accept_invitation(new_context(), base, invite_token(db_path, vol_email))
    _progress(page, base, "1 of 4 done")

    # 2) Create an event.
    ev_date = next_sunday_iso()
    from_date, to_date = solver_window_around(ev_date)
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
    _progress(page, base, "2 of 4 done")

    # 3) Generate a schedule, 4) review and publish it — one uninterrupted
    # sequence (the solver page only holds the result until you navigate
    # away, so the review link must be clicked without leaving).
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

    # Wizard is complete.
    page.goto(f"{base}/a/onboarding")
    page.wait_for_selector("#onboarding-complete")
    page.wait_for_selector("#onboarding-progress:has-text('4 of 4 done')")

    no_js_errors(page)
