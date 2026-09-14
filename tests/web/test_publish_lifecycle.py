"""Marathon P1.7 — solution unpublish + rollback (web)."""

from __future__ import annotations

from datetime import timedelta

from api.models import Assignment, Event, Organization, Person, Solution
from api.services.publication_service import capture_solution_scope
from api.timeutils import utcnow
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _admin(client, db, *, org, email):
    seed_person(db, person_id=f"{org}_adm", org_id=org, email=email, roles=["admin"])
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def _sol(db, org, *, required=1, assigned=1):
    if db.get(Organization, org) is None:
        db.add(Organization(id=org, name="Web Org", region="Test"))
    event = db.get(Event, f"publish-event-{org}")
    if event is None:
        start = utcnow() + timedelta(days=14)
        event = Event(
            id=f"publish-event-{org}",
            org_id=org,
            type="Service",
            start_time=start,
            end_time=start + timedelta(hours=1),
            extra_data={"role_counts": {"usher": required}},
        )
        db.add(event)
    member = db.get(Person, f"publish-member-{org}")
    if member is None:
        member = Person(
            id=f"publish-member-{org}",
            org_id=org,
            name="Publish Member",
            roles=["usher"],
            status="active",
        )
        db.add(member)
    db.flush()
    scope = capture_solution_scope(
        [event], range_start=event.start_time.date(), range_end=event.start_time.date()
    )
    s = Solution(
        org_id=org,
        hard_violations=0,
        soft_score=1.0,
        health_score=90.0,
        solve_ms=5.0,
        scope_start=scope.range_start,
        scope_end=scope.range_end,
        scope_event_ids=scope.event_ids,
        scope_fingerprint=scope.fingerprint,
    )
    db.add(s)
    db.flush()
    if assigned:
        db.add(
            Assignment(
                solution_id=s.id,
                event_id=event.id,
                person_id=member.id,
                role="usher",
            )
        )
    db.commit()
    db.refresh(s)
    return s


def test_publish_then_unpublish_cycle(client, db):
    tok = _admin(client, db, org="pl_o1", email="pl1@web.test")
    s = _sol(db, "pl_o1")

    pub = client.post(f"/a/solution/{s.id}/publish", cookies={SESSION_COOKIE: tok})
    assert pub.status_code == 200
    assert "Published" in pub.text
    assert "Unpublish" in pub.text
    db.refresh(s)
    assert s.is_published is True

    unp = client.post(f"/a/solution/{s.id}/unpublish", cookies={SESSION_COOKIE: tok})
    assert unp.status_code == 200
    assert "Publish this solution" in unp.text
    db.refresh(s)
    assert s.is_published is False
    # Previously published → rollback now offered.
    assert "Roll back to this version" in unp.text


def test_incomplete_publish_names_missing_event_and_role(client, db):
    tok = _admin(client, db, org="pl_short", email="pl-short@web.test")
    solution = _sol(db, "pl_short", required=2, assigned=1)

    response = client.post(
        f"/a/solution/{solution.id}/publish",
        cookies={SESSION_COOKIE: tok},
    )

    assert response.status_code == 409
    assert 'role="alert"' in response.text
    assert "publish-event-pl_short:usher needs 1" in response.text
    db.refresh(solution)
    assert solution.is_published is False


def test_rollback_restores_previous(client, db):
    tok = _admin(client, db, org="pl_o2", email="pl2@web.test")
    s1 = _sol(db, "pl_o2")
    s2 = _sol(db, "pl_o2")

    client.post(f"/a/solution/{s1.id}/publish", cookies={SESSION_COOKIE: tok})
    # Publishing s2 unpublishes s1.
    client.post(f"/a/solution/{s2.id}/publish", cookies={SESSION_COOKIE: tok})
    db.refresh(s1)
    db.refresh(s2)
    assert s1.is_published is False and s2.is_published is True

    # Roll back to s1 (it was published before → eligible).
    rb = client.post(f"/a/solution/{s1.id}/rollback", cookies={SESSION_COOKIE: tok})
    assert rb.status_code == 200
    assert "Published" in rb.text
    db.refresh(s1)
    db.refresh(s2)
    assert s1.is_published is True
    assert s2.is_published is False


def test_rollback_never_published_rejected(client, db):
    tok = _admin(client, db, org="pl_o3", email="pl3@web.test")
    s = _sol(db, "pl_o3")
    rb = client.post(f"/a/solution/{s.id}/rollback", cookies={SESSION_COOKIE: tok})
    assert rb.status_code == 400
    assert "never been published" in rb.text.lower()
    db.refresh(s)
    assert s.is_published is False


def test_lifecycle_other_org_404(client, db):
    tok = _admin(client, db, org="pl_o4", email="pl4@web.test")
    other = _sol(db, "pl_other")
    for action in ("publish", "unpublish", "rollback"):
        r = client.post(f"/a/solution/{other.id}/{action}", cookies={SESSION_COOKIE: tok})
        assert r.status_code == 404


def test_lifecycle_requires_admin(client, db):
    seed_person(db, person_id="pl_vol", email="plvol@web.test", roles=["volunteer"])
    login = client.post("/auth/login", data={"email": "plvol@web.test", "password": "WebPass123!"})
    tok = login.cookies[SESSION_COOKIE]
    for action in ("publish", "unpublish", "rollback"):
        assert (
            client.post(f"/a/solution/1/{action}", cookies={SESSION_COOKIE: tok}).status_code == 303
        )
        assert client.post(f"/a/solution/1/{action}").status_code == 303
