"""Walk the demo the way a person does, in every browser engine.

Things shipped broken that every other test passed: a demo with nothing on
any screen, and a Safari-only policy that left the whole UI unstyled with no
JavaScript. Each test here signs in through the real login form as a printed
demo account, opens the pages the README points at, and requires that each
one is styled, has its scripts, loaded all its assets, raised no JavaScript
error, and is not showing its empty state.

By default it runs against the suite's own server with the demo seeded into
its database. Set SIGNUPFLOW_STACK_URL (``make test-stack`` does) to run the
same tour against an app already started with ``make setup`` and ``make up``,
which is the only way to cover the Docker path people actually use.
"""

from __future__ import annotations

import pytest

from tests.e2e.conftest import (
    DEMO_ADMIN,
    DEMO_LEADER,
    DEMO_MUSICIAN,
    ENGINES,
    assert_page_health,
    assert_page_works,
    track_page_health,
)

ADMIN, MUSICIAN, LEADER = DEMO_ADMIN, DEMO_MUSICIAN, DEMO_LEADER

#: (account, path, empty state that must not show, text that must show)
TOUR = [
    (ADMIN, "/a/dashboard", "No assignments in the last 30 days yet.", "Most active"),
    (ADMIN, "/a/events", "No upcoming events.", "Sunday worship"),
    (ADMIN, "/a/recurring", "No recurring series yet.", "Sunday worship"),
    (ADMIN, "/a/assignments", "No assignments.", "Accepted"),
    (ADMIN, "/a/swaps", "No swap requests.", "Priya Nair"),
    (ADMIN, "/a/people", None, "Awaiting acceptance"),
    (ADMIN, "/a/teams", "No teams yet.", "Worship team"),
    (ADMIN, "/a/analytics", "No assignments in this window.", "Top volunteers"),
    (MUSICIAN, "/v/schedule", "No assignments yet.", "Sunday worship"),
    (MUSICIAN, "/v/open", "No open shifts right now.", "Claim"),
    (MUSICIAN, "/v/availability", "No time-off booked.", "Family visit"),
    (LEADER, "/v/inbox", "No notifications yet.", "New assignment"),
]


@pytest.mark.parametrize("engine", ENGINES)
def test_sign_in_page_works(engine, engine_browser, demo_base):
    context = engine_browser(engine).new_context()
    track_page_health(context)
    try:
        page = context.new_page()
        page.goto(f"{demo_base}/auth/login")
        page.wait_for_load_state("networkidle")
        assert_page_works(page, f"{engine} /auth/login")
        assert_page_health(context)
    finally:
        context.close()


@pytest.mark.parametrize("engine", ENGINES)
@pytest.mark.parametrize("account", sorted({row[0] for row in TOUR}))
def test_demo_pages_work_in_every_browser(
    engine, account, engine_browser, demo_base, demo_sessions
):
    context = engine_browser(engine).new_context(
        viewport={"width": 1280, "height": 900}, storage_state=demo_sessions[account]
    )
    track_page_health(context)
    try:
        page = context.new_page()
        for tour_account, path, empty, shown in TOUR:
            if tour_account != account:
                continue
            page.goto(f"{demo_base}{path}")
            page.wait_for_load_state("networkidle")
            where = f"{engine} {account} {path}"
            assert "/auth/login" not in page.url, f"{where}: the session was not accepted"
            assert_page_works(page, where)
            text = page.inner_text("body")
            if empty:
                assert empty not in text, f"{where} shows its empty state: {empty!r}"
            assert shown.lower() in text.lower(), f"{where} is missing {shown!r}"
        assert_page_health(context)
    finally:
        context.close()
