"""Solution compare + rollback tests for /api/v1/solutions/.

Sprint 5 PR 5.5 adds two admin-only endpoints on top of the existing
publish/unpublish flow (Sprint 4 PR 4.2):

- ``GET /solutions/{a}/compare/{b}`` — diff two solutions in the same org;
  returns added/removed assignment changes keyed by ``(event_id, person_id, role)``.
- ``POST /solutions/{id}/rollback`` — republish a previously-published
  solution. The target must have ``published_at IS NOT NULL``. Whatever is
  currently published in the org is unpublished. Audited as
  ``solution.rolled_back``.
"""

from datetime import datetime, timedelta

import pytest

from api.models import Assignment, AuditAction, AuditLog, Event, Person, Solution
from api.timeutils import utcnow
from tests.api.conftest import auth_headers, seed_org, seed_user


def _admin_for(client, org_id: str, suffix: str):
    seed_user(
        client,
        org_id,
        email=f"admin-{suffix}@o.org",
        name="Admin",
        password="AdminPass1!",
    )
    return auth_headers(client, email=f"admin-{suffix}@o.org", password="AdminPass1!")


def _seed_solution(db, org_id: str, *, published: bool = False) -> Solution:
    sol = Solution(
        org_id=org_id,
        solve_ms=10.0,
        hard_violations=0,
        soft_score=1.0,
        health_score=1.0,
        metrics={},
    )
    if published:
        sol.is_published = True
        sol.published_at = utcnow()
    db.add(sol)
    db.commit()
    db.refresh(sol)
    return sol


def _seed_person(db, org_id: str, person_id: str) -> Person:
    p = Person(id=person_id, org_id=org_id, name=person_id.title(), roles=[])
    db.add(p)
    db.commit()
    return p


def _seed_event(db, org_id: str, event_id: str) -> Event:
    start = datetime(2026, 6, 1, 10, 0, 0)
    e = Event(
        id=event_id,
        org_id=org_id,
        type="Service",
        start_time=start,
        end_time=start + timedelta(hours=1),
    )
    db.add(e)
    db.commit()
    return e


def _seed_assignment(
    db, *, solution_id: int, event_id: str, person_id: str, role: str | None
) -> Assignment:
    a = Assignment(
        solution_id=solution_id,
        event_id=event_id,
        person_id=person_id,
        role=role,
    )
    db.add(a)
    db.commit()
    return a


# ---------------------------------------------------------------------------
# Compare
# ---------------------------------------------------------------------------


@pytest.mark.no_mock_auth
class TestCompareSolutions:
    def test_admin_can_compare_returns_correct_diff(self, client, db):
        org_id = "cmp-ok"
        seed_org(client, org_id)
        hdrs = _admin_for(client, org_id, "cmp-ok")

        for pid in ("p1", "p2", "p3"):
            _seed_person(db, org_id, pid)
        for eid in ("e1", "e2"):
            _seed_event(db, org_id, eid)

        sol_a = _seed_solution(db, org_id)
        sol_b = _seed_solution(db, org_id)

        # A: (e1,p1,usher), (e1,p2,greeter)
        _seed_assignment(db, solution_id=sol_a.id, event_id="e1", person_id="p1", role="usher")
        _seed_assignment(db, solution_id=sol_a.id, event_id="e1", person_id="p2", role="greeter")

        # B: (e1,p1,usher), (e2,p3,sound)
        _seed_assignment(db, solution_id=sol_b.id, event_id="e1", person_id="p1", role="usher")
        _seed_assignment(db, solution_id=sol_b.id, event_id="e2", person_id="p3", role="sound")

        resp = client.get(f"/api/v1/solutions/{sol_a.id}/compare/{sol_b.id}", headers=hdrs)
        assert resp.status_code == 200, resp.text
        body = resp.json()

        assert body["solution_a_id"] == sol_a.id
        assert body["solution_b_id"] == sol_b.id
        assert body["unchanged_count"] == 1
        assert body["moves"] == 2

        removed = {(c["event_id"], c["person_id"], c["role"]) for c in body["removed"]}
        added = {(c["event_id"], c["person_id"], c["role"]) for c in body["added"]}
        assert removed == {("e1", "p2", "greeter")}
        assert added == {("e2", "p3", "sound")}
        assert set(body["affected_persons"]) == {"p2", "p3"}

    def test_compare_role_difference_counts_as_remove_add(self, client, db):
        org_id = "cmp-role"
        seed_org(client, org_id)
        hdrs = _admin_for(client, org_id, "cmp-role")
        _seed_person(db, org_id, "p1")
        _seed_event(db, org_id, "e1")
        sol_a = _seed_solution(db, org_id)
        sol_b = _seed_solution(db, org_id)

        _seed_assignment(db, solution_id=sol_a.id, event_id="e1", person_id="p1", role="usher")
        _seed_assignment(db, solution_id=sol_b.id, event_id="e1", person_id="p1", role="greeter")

        resp = client.get(f"/api/v1/solutions/{sol_a.id}/compare/{sol_b.id}", headers=hdrs)
        assert resp.status_code == 200
        body = resp.json()
        assert body["moves"] == 2
        assert body["unchanged_count"] == 0
        assert {c["role"] for c in body["removed"]} == {"usher"}
        assert {c["role"] for c in body["added"]} == {"greeter"}

    def test_compare_volunteer_blocked(self, client, db):
        org_id = "cmp-vol"
        seed_org(client, org_id)
        _admin_for(client, org_id, "cmp-vol-admin")
        seed_user(
            client,
            org_id,
            email="vol@o.org",
            name="Vol",
            password="VolPass1!",
            roles=["volunteer"],
        )
        vol_hdrs = auth_headers(client, email="vol@o.org", password="VolPass1!")
        sol_a = _seed_solution(db, org_id)
        sol_b = _seed_solution(db, org_id)

        resp = client.get(f"/api/v1/solutions/{sol_a.id}/compare/{sol_b.id}", headers=vol_hdrs)
        assert resp.status_code == 403

    def test_compare_cross_org_blocked(self, client, db):
        seed_org(client, "cmp-a")
        seed_org(client, "cmp-b")
        a_hdrs = _admin_for(client, "cmp-a", "cmp-a")
        sol_a = _seed_solution(db, "cmp-a")
        sol_b = _seed_solution(db, "cmp-b")

        resp = client.get(f"/api/v1/solutions/{sol_a.id}/compare/{sol_b.id}", headers=a_hdrs)
        assert resp.status_code == 403

    def test_compare_missing_solution_404(self, client, db):
        org_id = "cmp-missing"
        seed_org(client, org_id)
        hdrs = _admin_for(client, org_id, "cmp-missing")
        sol = _seed_solution(db, org_id)

        resp = client.get(f"/api/v1/solutions/{sol.id}/compare/9999999", headers=hdrs)
        assert resp.status_code == 404

    def test_compare_requires_auth(self, client, db):
        org_id = "cmp-noauth"
        seed_org(client, org_id)
        _admin_for(client, org_id, "cmp-noauth")
        sol_a = _seed_solution(db, org_id)
        sol_b = _seed_solution(db, org_id)

        resp = client.get(f"/api/v1/solutions/{sol_a.id}/compare/{sol_b.id}")
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# Rollback
# ---------------------------------------------------------------------------


@pytest.mark.no_mock_auth
class TestRollbackSolution:
    def test_admin_can_rollback_to_prior_published(self, client, db):
        org_id = "rb-ok"
        seed_org(client, org_id)
        hdrs = _admin_for(client, org_id, "rb-ok")
        sol_a = _seed_solution(db, org_id)
        sol_b = _seed_solution(db, org_id)

        # Publish a, then b (which unpublishes a). a now has published_at != None
        # but is_published = False — eligible for rollback.
        client.post(f"/api/v1/solutions/{sol_a.id}/publish", headers=hdrs)
        client.post(f"/api/v1/solutions/{sol_b.id}/publish", headers=hdrs)

        resp = client.post(f"/api/v1/solutions/{sol_a.id}/rollback", headers=hdrs)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["is_published"] is True
        assert body["published_at"] is not None

        a_after = client.get(f"/api/v1/solutions/{sol_a.id}", headers=hdrs).json()
        b_after = client.get(f"/api/v1/solutions/{sol_b.id}", headers=hdrs).json()
        assert a_after["is_published"] is True
        assert b_after["is_published"] is False

    def test_rollback_to_never_published_400(self, client, db):
        org_id = "rb-never"
        seed_org(client, org_id)
        hdrs = _admin_for(client, org_id, "rb-never")
        sol = _seed_solution(db, org_id)  # published_at IS NULL

        resp = client.post(f"/api/v1/solutions/{sol.id}/rollback", headers=hdrs)
        assert resp.status_code == 400

    def test_rollback_volunteer_blocked(self, client, db):
        org_id = "rb-vol"
        seed_org(client, org_id)
        admin_hdrs = _admin_for(client, org_id, "rb-vol-admin")
        seed_user(
            client,
            org_id,
            email="vol@o.org",
            name="Vol",
            password="VolPass1!",
            roles=["volunteer"],
        )
        vol_hdrs = auth_headers(client, email="vol@o.org", password="VolPass1!")
        sol = _seed_solution(db, org_id)
        client.post(f"/api/v1/solutions/{sol.id}/publish", headers=admin_hdrs)

        resp = client.post(f"/api/v1/solutions/{sol.id}/rollback", headers=vol_hdrs)
        assert resp.status_code == 403

    def test_rollback_cross_org_blocked(self, client, db):
        seed_org(client, "rb-a")
        seed_org(client, "rb-b")
        a_hdrs = _admin_for(client, "rb-a", "rb-a")
        b_hdrs = _admin_for(client, "rb-b", "rb-b")
        sol_b = _seed_solution(db, "rb-b")
        client.post(f"/api/v1/solutions/{sol_b.id}/publish", headers=b_hdrs)

        resp = client.post(f"/api/v1/solutions/{sol_b.id}/rollback", headers=a_hdrs)
        assert resp.status_code == 403

    def test_rollback_emits_audit_row(self, client, db):
        org_id = "rb-audit"
        seed_org(client, org_id)
        hdrs = _admin_for(client, org_id, "rb-audit")
        sol_a = _seed_solution(db, org_id)
        sol_b = _seed_solution(db, org_id)
        client.post(f"/api/v1/solutions/{sol_a.id}/publish", headers=hdrs)
        client.post(f"/api/v1/solutions/{sol_b.id}/publish", headers=hdrs)

        before = (
            db.query(AuditLog).filter(AuditLog.action == AuditAction.SOLUTION_ROLLED_BACK).count()
        )
        client.post(f"/api/v1/solutions/{sol_a.id}/rollback", headers=hdrs)
        after = (
            db.query(AuditLog).filter(AuditLog.action == AuditAction.SOLUTION_ROLLED_BACK).count()
        )
        assert after == before + 1

    def test_rollback_missing_solution_404(self, client, db):
        org_id = "rb-missing"
        seed_org(client, org_id)
        hdrs = _admin_for(client, org_id, "rb-missing")

        resp = client.post("/api/v1/solutions/9999999/rollback", headers=hdrs)
        assert resp.status_code == 404

    def test_rollback_requires_auth(self, client, db):
        org_id = "rb-noauth"
        seed_org(client, org_id)
        _admin_for(client, org_id, "rb-noauth")
        sol = _seed_solution(db, org_id)

        resp = client.post(f"/api/v1/solutions/{sol.id}/rollback")
        assert resp.status_code in (401, 403)
