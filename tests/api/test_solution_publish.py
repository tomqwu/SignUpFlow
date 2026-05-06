"""Solution publish/unpublish tests for /api/v1/solutions/.

Sprint 4 PR 4.2 adds an `is_published`/`published_at` flag to Solution and
admin-only POST `/solutions/{id}/publish` and `/solutions/{id}/unpublish`
endpoints. Publishing a solution unpublishes any previously published one in
the same organization. Both transitions are audited.
"""

import pytest

from api.models import AuditAction, AuditLog, Solution
from tests.api.conftest import auth_headers, seed_org, seed_user


def _admin_for(client, org_id: str, suffix: str):
    seed_user(client, org_id, email=f"admin-{suffix}@o.org", name="Admin", password="AdminPass1!")
    return auth_headers(client, email=f"admin-{suffix}@o.org", password="AdminPass1!")


def _seed_solution(db, org_id: str) -> Solution:
    sol = Solution(
        org_id=org_id,
        solve_ms=10.0,
        hard_violations=0,
        soft_score=1.0,
        health_score=1.0,
        metrics={},
    )
    db.add(sol)
    db.commit()
    db.refresh(sol)
    return sol


@pytest.mark.no_mock_auth
class TestPublishSolution:
    def test_admin_can_publish(self, client, db):
        org_id = "pub-admin-ok"
        seed_org(client, org_id)
        hdrs = _admin_for(client, org_id, "ok")
        sol = _seed_solution(db, org_id)

        resp = client.post(f"/api/v1/solutions/{sol.id}/publish", headers=hdrs)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["is_published"] is True
        assert body["published_at"] is not None

    def test_volunteer_cannot_publish(self, client, db):
        org_id = "pub-vol"
        seed_org(client, org_id)
        _admin_for(client, org_id, "vol-admin")
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

        resp = client.post(f"/api/v1/solutions/{sol.id}/publish", headers=vol_hdrs)
        assert resp.status_code == 403

    def test_publish_requires_auth(self, client, db):
        org_id = "pub-noauth"
        seed_org(client, org_id)
        _admin_for(client, org_id, "noauth")
        sol = _seed_solution(db, org_id)

        resp = client.post(f"/api/v1/solutions/{sol.id}/publish")
        # HTTPBearer without credentials returns 403 by FastAPI default.
        assert resp.status_code in (401, 403)

    def test_cross_org_admin_blocked(self, client, db):
        seed_org(client, "pub-a")
        seed_org(client, "pub-b")
        a_hdrs = _admin_for(client, "pub-a", "a")
        sol_b = _seed_solution(db, "pub-b")

        resp = client.post(f"/api/v1/solutions/{sol_b.id}/publish", headers=a_hdrs)
        assert resp.status_code == 403

    def test_publish_unpublishes_prior(self, client, db):
        """Publishing one solution should unpublish any prior published in the same org."""
        org_id = "pub-replace"
        seed_org(client, org_id)
        hdrs = _admin_for(client, org_id, "replace")
        sol_a = _seed_solution(db, org_id)
        sol_b = _seed_solution(db, org_id)

        client.post(f"/api/v1/solutions/{sol_a.id}/publish", headers=hdrs)
        client.post(f"/api/v1/solutions/{sol_b.id}/publish", headers=hdrs)

        a_after = client.get(f"/api/v1/solutions/{sol_a.id}", headers=hdrs).json()
        b_after = client.get(f"/api/v1/solutions/{sol_b.id}", headers=hdrs).json()
        assert a_after["is_published"] is False
        assert b_after["is_published"] is True

    def test_publish_emits_audit_row(self, client, db):
        org_id = "pub-audit"
        seed_org(client, org_id)
        hdrs = _admin_for(client, org_id, "pub-audit")
        sol = _seed_solution(db, org_id)

        before = (
            db.query(AuditLog).filter(AuditLog.action == AuditAction.SOLUTION_PUBLISHED).count()
        )
        client.post(f"/api/v1/solutions/{sol.id}/publish", headers=hdrs)
        after = db.query(AuditLog).filter(AuditLog.action == AuditAction.SOLUTION_PUBLISHED).count()
        assert after == before + 1


@pytest.mark.no_mock_auth
class TestUnpublishSolution:
    def test_admin_can_unpublish(self, client, db):
        org_id = "unpub-ok"
        seed_org(client, org_id)
        hdrs = _admin_for(client, org_id, "unpub-ok")
        sol = _seed_solution(db, org_id)
        client.post(f"/api/v1/solutions/{sol.id}/publish", headers=hdrs)

        resp = client.post(f"/api/v1/solutions/{sol.id}/unpublish", headers=hdrs)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["is_published"] is False
        assert body["published_at"] is None

    def test_unpublish_emits_audit_row(self, client, db):
        org_id = "unpub-audit"
        seed_org(client, org_id)
        hdrs = _admin_for(client, org_id, "unpub-audit")
        sol = _seed_solution(db, org_id)
        client.post(f"/api/v1/solutions/{sol.id}/publish", headers=hdrs)

        before = (
            db.query(AuditLog).filter(AuditLog.action == AuditAction.SOLUTION_UNPUBLISHED).count()
        )
        client.post(f"/api/v1/solutions/{sol.id}/unpublish", headers=hdrs)
        after = (
            db.query(AuditLog).filter(AuditLog.action == AuditAction.SOLUTION_UNPUBLISHED).count()
        )
        assert after == before + 1

    def test_volunteer_cannot_unpublish(self, client, db):
        org_id = "unpub-vol"
        seed_org(client, org_id)
        admin_hdrs = _admin_for(client, org_id, "unpub-vol-admin")
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

        resp = client.post(f"/api/v1/solutions/{sol.id}/unpublish", headers=vol_hdrs)
        assert resp.status_code == 403
