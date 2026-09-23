"""Every screen of the demo has something on it.

The first version of the demo loaded people and events and nothing else, and
was "verified" by checking rows and one API login. Signed in, every page was
empty. These tests sign in through the real web login as the printed demo
accounts and read each page the README points people at, failing on the empty
state that page would otherwise show.
"""

import pytest

from api.demo_seed import DEMO_ADMIN_EMAIL, DEMO_PASSWORD, email_for, seed_demo
from web.deps import SESSION_COOKIE


@pytest.fixture
def demo(client, monkeypatch):
    monkeypatch.setenv("DISABLE_RATE_LIMITS", "true")
    monkeypatch.setenv("EMAIL_ENABLED", "false")
    return seed_demo(client)


def _session(client, email):
    response = client.post("/auth/login", data={"email": email, "password": DEMO_PASSWORD})
    assert SESSION_COOKIE in response.cookies, f"{email} could not sign in"
    return {SESSION_COOKIE: response.cookies[SESSION_COOKIE]}


def _page(client, cookies, path):
    response = client.get(path, cookies=cookies)
    assert response.status_code == 200, (path, response.status_code)
    return response.text


ADMIN_PAGES = [
    ("/a/dashboard", ["No assignments in the last 30 days yet."], ["Most active", "Grace Park"]),
    ("/a/events", ["No upcoming events.", "No past events."], ["Sunday worship"]),
    ("/a/assignments", ["No assignments."], ["Mia Chen"]),
    ("/a/teams", ["No teams yet."], ["Worship team", "Kids ministry"]),
    ("/a/constraints", ["No constraints yet."], ["two-services-per-week"]),
    ("/a/swaps", ["No swap requests."], ["Priya Nair"]),
    ("/a/analytics", ["No assignments in this window."], ["Top volunteers", "Grace Park"]),
    ("/a/people", [], ["Mia Chen", "Ava Thompson"]),
    ("/a/recurring", ["No recurring series yet."], ["Sunday worship"]),
]


@pytest.mark.parametrize("path, empty_states, expected", ADMIN_PAGES)
def test_admin_screen_is_populated(client, demo, path, empty_states, expected):
    html = _page(client, _session(client, DEMO_ADMIN_EMAIL), path)
    for empty in empty_states:
        assert empty not in html, f"{path} shows its empty state: {empty!r}"
    for text in expected:
        assert text in html, f"{path} is missing {text!r}"


def test_admin_onboarding_checklist_is_complete(client, demo):
    """The demo has done every first-run step, so none should read as to-do."""
    html = _page(client, _session(client, DEMO_ADMIN_EMAIL), "/a/onboarding")
    assert "4 of 4" in html or "4/4" in html, html[:2000]


def test_volunteer_sees_a_confirmed_schedule(client, demo):
    html = _page(client, _session(client, email_for("Grace Park")), "/v/schedule")
    assert "No assignments yet." not in html
    assert "Sunday worship" in html or "Band rehearsal" in html


def test_volunteer_with_time_off_sees_it(client, demo):
    cookies = _session(client, email_for("Mia Chen"))
    assert "No assignments yet." not in _page(client, cookies, "/v/schedule")
    availability = _page(client, cookies, "/v/availability")
    assert "Family visit" in availability


def test_declined_shift_is_offered_to_the_sample_musician(client, demo):
    """Luis declined a musician slot; the printed musician login can pick it up."""
    html = _page(client, _session(client, email_for("Mia Chen")), "/v/open")
    assert "No open shifts right now." not in html
    assert "musician" in html.lower()


def test_swap_request_is_visible_to_the_other_sound_volunteer(client, demo):
    html = _page(client, _session(client, email_for("Ethan Brooks")), "/v/swaps")
    assert "No swap requests to cover right now." not in html


def test_published_schedule_reached_the_inbox(client, demo):
    html = _page(client, _session(client, email_for("Grace Park")), "/v/inbox")
    assert "No notifications yet." not in html
    assert "Sunday worship ·" in html or "Band rehearsal ·" in html
    assert "event_" not in html, "an internal event id leaked into the inbox"
