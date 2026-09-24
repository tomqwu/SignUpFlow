"""Overnight B4 — event roster fill view (needed vs filled + inline fill)."""

from __future__ import annotations

from datetime import datetime, timedelta

from api.models import Assignment, Event
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _admin(client, db, *, org, email):
    seed_person(db, person_id=f"{org}_adm", org_id=org, email=email, roles=["admin"])
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def _event(db, org, *, eid="rev1", role_counts=None):
    start = datetime(2026, 6, 7, 10, 0, 0)
    db.add(
        Event(
            id=eid,
            org_id=org,
            type="Sunday Service",
            start_time=start,
            end_time=start + timedelta(hours=1),
            extra_data={"role_counts": role_counts} if role_counts else None,
        )
    )
    db.commit()


def test_roster_shows_gap(client, db):
    tok = _admin(client, db, org="rf_o1", email="rf1@web.test")
    _event(db, "rf_o1", role_counts={"usher": 2})
    r = client.get("/a/events/rev1/assignments", cookies={SESSION_COOKIE: tok})
    assert r.status_code == 200
    assert 'id="role-coverage"' in r.text
    assert 'data-staffed="no"' in r.text
    assert "0/2 filled" in r.text and "2 needed" in r.text


def test_fill_gap_closes_coverage(client, db):
    tok = _admin(client, db, org="rf_o2", email="rf2@web.test")
    _event(db, "rf_o2", role_counts={"usher": 1})
    seed_person(
        db,
        person_id="rf_v",
        org_id="rf_o2",
        email="v@rf.test",
        roles=["volunteer", "usher"],
    )
    r = client.post(
        "/a/events/rev1/assignments/add",
        data={"person_id": "rf_v", "role": "usher"},
        cookies={SESSION_COOKIE: tok},
    )
    assert r.status_code == 200
    assert 'data-staffed="yes"' in r.text
    assert "1/1 filled" in r.text and "covered" in r.text
    a = (
        db.query(Assignment)
        .filter(Assignment.event_id == "rev1", Assignment.person_id == "rf_v")
        .first()
    )
    assert a is not None and a.role == "usher"


def test_no_role_counts_hides_coverage(client, db):
    tok = _admin(client, db, org="rf_o3", email="rf3@web.test")
    _event(db, "rf_o3")  # no role_counts
    r = client.get("/a/events/rev1/assignments", cookies={SESSION_COOKIE: tok})
    assert r.status_code == 200
    assert 'id="role-coverage"' not in r.text


def test_fill_gap_rejects_unqualified_member_without_mutation(client, db):
    tok = _admin(client, db, org="rf_o4", email="rf4@web.test")
    _event(db, "rf_o4", role_counts={"usher": 1})
    seed_person(db, person_id="rf_v4", org_id="rf_o4", email="v4@rf.test", roles=["volunteer"])

    response = client.post(
        "/a/events/rev1/assignments/add",
        data={"person_id": "rf_v4", "role": "usher"},
        cookies={SESSION_COOKIE: tok},
    )

    assert response.status_code == 400
    assert "not qualified" in response.text.lower()
    assert (
        db.query(Assignment)
        .filter(Assignment.event_id == "rev1", Assignment.person_id == "rf_v4")
        .first()
        is None
    )


def _assign(db, org, pid, name, role, *, status="confirmed", response="accepted"):
    person = seed_person(
        db, person_id=pid, org_id=org, email=f"{pid}@rf.test", roles=["volunteer", role]
    )
    person.name = name
    db.add(
        Assignment(
            event_id="rev1",
            person_id=pid,
            role=role,
            status=status,
            response_status=response,
            commitment_revision=1,
            response_revision=1 if response != "pending" else None,
        )
    )
    db.commit()


def _coverage_row(html, role):
    start = html.index(f'data-role="{role}"')
    return html[
        start : html.index('class="row cov-row"', start + 1)
        if 'class="row cov-row"' in html[start + 1 :]
        else len(html)
    ]


def test_each_role_names_who_holds_it(client, db):
    """ "1/1 filled" alone does not say who is coming."""
    tok = _admin(client, db, org="rf_names", email="rfn@web.test")
    _event(db, "rf_names", role_counts={"usher": 2, "sound": 1})
    _assign(db, "rf_names", "rf_ada", "Ada Lovelace", "usher")
    _assign(db, "rf_names", "rf_bo", "Bo Diddley", "usher", status="pending", response="pending")
    _assign(db, "rf_names", "rf_cy", "Cy Twombly", "sound")

    html = client.get("/a/events/rev1/assignments", cookies={SESSION_COOKIE: tok}).text
    usher = _coverage_row(html, "usher")
    assert "Ada Lovelace" in usher and "Accepted" in usher
    assert "Bo Diddley" in usher and "Unanswered" in usher
    assert "Cy Twombly" not in usher
    assert "Cy Twombly" in _coverage_row(html, "sound")


def test_a_decline_leaves_the_role_open(client, db):
    """A declined assignment used to count as filled, so the role read
    "covered" and the Fill option was hidden while nobody was coming."""
    tok = _admin(client, db, org="rf_decl", email="rfd@web.test")
    _event(db, "rf_decl", role_counts={"musician": 2})
    _assign(db, "rf_decl", "rf_mia", "Mia Chen", "musician")
    _assign(
        db, "rf_decl", "rf_luis", "Luis Romero", "musician", status="declined", response="declined"
    )
    free = seed_person(
        db,
        person_id="rf_hannah",
        org_id="rf_decl",
        email="hannah@rf.test",
        roles=["volunteer", "musician"],
    )
    free.name = "Hannah Lee"
    db.commit()

    html = client.get("/a/events/rev1/assignments", cookies={SESSION_COOKIE: tok}).text
    musician = _coverage_row(html, "musician")
    assert "1/2 filled" in musician and "1 needed" in musician
    assert "Luis Romero" in musician and "Declined" in musician
    assert 'data-staffed="no"' in html
    assert _fill_options(html, "musician") == ["Hannah Lee"]


def test_a_swap_request_still_holds_the_role_until_covered(client, db):
    tok = _admin(client, db, org="rf_swap", email="rfs@web.test")
    _event(db, "rf_swap", role_counts={"sound": 1})
    _assign(
        db,
        "rf_swap",
        "rf_priya",
        "Priya Nair",
        "sound",
        status="swap_requested",
        response="declined",
    )

    html = client.get("/a/events/rev1/assignments", cookies={SESSION_COOKIE: tok}).text
    sound = _coverage_row(html, "sound")
    assert "1/1 filled" in sound
    assert "Priya Nair" in sound and "Replacement needed" in sound


def _fill_options(html, role):
    row = _coverage_row(html, role)
    if f'aria-label="Fill {role}"' not in row:
        return None
    select = row[row.index(f'aria-label="Fill {role}"') :]
    select = select[: select.index("</select>")]
    import re

    return re.findall(r"<option[^>]*>([^<]+)</option>", select)


def test_fill_offers_only_people_who_can_take_the_role(client, db):
    """The Fill list offered everyone not on the event, admin included, so the
    default choice was often someone the server would then refuse."""
    tok = _admin(client, db, org="rf_fill", email="rff@web.test")
    _event(db, "rf_fill", role_counts={"musician": 1})
    musician = seed_person(
        db,
        person_id="rf_mus",
        org_id="rf_fill",
        email="mus@rf.test",
        roles=["volunteer", "musician"],
    )
    musician.name = "Mia Chen"
    usher = seed_person(
        db, person_id="rf_ush", org_id="rf_fill", email="ush@rf.test", roles=["volunteer", "usher"]
    )
    usher.name = "Noah Kim"
    db.commit()

    html = client.get("/a/events/rev1/assignments", cookies={SESSION_COOKIE: tok}).text
    assert _fill_options(html, "musician") == ["Mia Chen"]


def test_a_role_nobody_can_take_says_so(client, db):
    tok = _admin(client, db, org="rf_none", email="rfnone@web.test")
    _event(db, "rf_none", role_counts={"sound": 1})
    html = client.get("/a/events/rev1/assignments", cookies={SESSION_COOKIE: tok}).text
    assert _fill_options(html, "sound") is None
    assert "No one qualified is free" in _coverage_row(html, "sound")
