"""Marathon P1.13 — UX polish: status parity + a11y labels."""

from __future__ import annotations

from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _admin(client, db, *, org, email):
    seed_person(db, person_id=f"{org}_adm", org_id=org, email=email, roles=["admin"])
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def test_swap_requested_status_styled(client):
    css = client.get("/web/static/css/styles.css")
    assert css.status_code == 200
    # New status colour added so swap_requested isn't an unstyled dot,
    # and it uses a theme var so dark mode is covered automatically.
    assert ".status-text.swap_requested" in css.text
    assert "var(--warning)" in css.text
    assert 'html[data-theme="dark"]' in css.text  # dark theme still present


def test_aria_labels_on_bare_selects(client, db):
    tok = _admin(client, db, org="ux_o1", email="ux1@web.test")

    # A team must exist (with an addable person) for the member select.
    client.post(
        "/a/teams/create", data={"name": "Ushers"}, cookies={SESSION_COOKIE: tok}
    )
    teams = client.get("/a/teams", cookies={SESSION_COOKIE: tok})
    assert teams.status_code == 200
    assert 'aria-label="Member to add"' in teams.text

    rec = client.get("/a/recurring", cookies={SESSION_COOKIE: tok})
    assert rec.status_code == 200
    assert 'aria-label="Which week of the month"' in rec.text
    assert 'aria-label="Weekday"' in rec.text

    cons = client.get("/a/constraints", cookies={SESSION_COOKIE: tok})
    assert cons.status_code == 200
    # Create-form select is always present and label-bound; the edit
    # select (per card) carries the new aria-label.
    assert 'id="c_type"' in cons.text
