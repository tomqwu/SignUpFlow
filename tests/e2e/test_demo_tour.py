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

import os
import subprocess
import sys
from pathlib import Path

import pytest

from api.demo_seed import DEMO_ADMIN_EMAIL, DEMO_PASSWORD, email_for
from tests.e2e.conftest import ENGINES, assert_page_health, track_page_health
from tests.test_environment import build_test_environment

REPO_ROOT = Path(__file__).resolve().parents[2]

ADMIN, MUSICIAN, LEADER = DEMO_ADMIN_EMAIL, email_for("Mia Chen"), email_for("Grace Park")

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


@pytest.fixture(scope="session")
def demo_base(request, db_path) -> str:
    stack = os.getenv("SIGNUPFLOW_STACK_URL")
    if stack:
        return stack.rstrip("/")
    base = request.getfixturevalue("live_server")
    environment = build_test_environment(
        os.environ,
        database_url=f"sqlite:///{db_path}",
        secret_key="e2e-overnight-secret-key-min-32-chars-long-xx",
    )
    seeded = subprocess.run(
        [sys.executable, "-m", "api.cli.main", "seed-demo"],
        cwd=REPO_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert seeded.returncode == 0, seeded.stdout + seeded.stderr
    return base


#: Each account submits the real login form once, in a different engine, and
#: the other engines reuse that session. That keeps a tour of a stack started
#: with 'make up' inside the login rate limit (5 per 5 minutes), while every
#: engine still loads and checks the sign-in page itself.
SIGN_IN_ENGINE = {ADMIN: "webkit", MUSICIAN: "firefox", LEADER: "chromium"}


def _assert_page_works(page, where: str) -> None:
    # Styled: the app's stylesheet sets Inter on the body. Unstyled pages fall
    # back to the browser default, as in the Safari bug.
    font = page.evaluate("getComputedStyle(document.body).fontFamily")
    assert "Inter" in font, f"{where} is unstyled (font: {font})"
    # Scripted: HTMX drives every interactive list and form.
    assert page.evaluate("typeof window.htmx !== 'undefined'"), f"{where}: no HTMX"


@pytest.fixture(scope="session")
def demo_sessions(engine_browser, demo_base) -> dict:
    """Sign each demo account in once through the login form; keep the session."""
    sessions = {}
    for account, engine in SIGN_IN_ENGINE.items():
        context = engine_browser(engine).new_context()
        track_page_health(context)
        try:
            page = context.new_page()
            page.goto(f"{demo_base}/auth/login")
            page.wait_for_load_state("networkidle")
            _assert_page_works(page, f"{engine} /auth/login")
            page.fill("input[name=email]", account)
            page.fill("input[name=password]", DEMO_PASSWORD)
            page.click("button[type=submit]")
            page.wait_for_load_state("networkidle")
            assert "/auth/login" not in page.url, f"{account} could not sign in in {engine}"
            assert_page_health(context)
            sessions[account] = context.storage_state()
        finally:
            context.close()
    return sessions


@pytest.mark.parametrize("engine", ENGINES)
def test_sign_in_page_works(engine, engine_browser, demo_base):
    context = engine_browser(engine).new_context()
    track_page_health(context)
    try:
        page = context.new_page()
        page.goto(f"{demo_base}/auth/login")
        page.wait_for_load_state("networkidle")
        _assert_page_works(page, f"{engine} /auth/login")
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
            _assert_page_works(page, where)
            text = page.inner_text("body")
            if empty:
                assert empty not in text, f"{where} shows its empty state: {empty!r}"
            assert shown.lower() in text.lower(), f"{where} is missing {shown!r}"
        assert_page_health(context)
    finally:
        context.close()
