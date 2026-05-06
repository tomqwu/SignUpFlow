"""API tests for /api/v1/people/bulk (Sprint 4 PR 4.3)."""

import pytest

from api.models import AuditAction, AuditLog, Person
from api.utils.bulk_import import MAX_BULK_IMPORT_ITEMS
from tests.api.conftest import auth_headers, seed_org, seed_user


def _admin_for(client, org_id: str, suffix: str):
    seed_user(client, org_id, email=f"admin-{suffix}@o.org", name="Admin", password="AdminPass1!")
    return auth_headers(client, email=f"admin-{suffix}@o.org", password="AdminPass1!")


def _post_bulk(client, headers, org_id: str, items: list[dict]):
    return client.post(
        f"/api/v1/people/bulk?org_id={org_id}",
        json={"items": items},
        headers=headers,
    )


@pytest.mark.no_mock_auth
class TestBulkImportPeopleHappy:
    def test_admin_can_create_two(self, client, db):
        org_id = "bulk-happy"
        seed_org(client, org_id)
        hdrs = _admin_for(client, org_id, "happy")

        resp = _post_bulk(
            client,
            hdrs,
            org_id,
            [
                {"id": "p1", "name": "Alice", "email": "alice@org.example"},
                {"id": "p2", "name": "Bob", "email": "bob@org.example"},
            ],
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["created"] == 2
        assert body["skipped"] == 0
        assert body["errors"] == []
        assert db.query(Person).filter(Person.id.in_(["p1", "p2"])).count() == 2

    def test_skips_duplicate_existing_id(self, client, db):
        org_id = "bulk-dup"
        seed_org(client, org_id)
        hdrs = _admin_for(client, org_id, "dup")

        client.post(
            "/api/v1/people/",
            json={"id": "p1", "org_id": org_id, "name": "Existing"},
            headers=hdrs,
        )

        resp = _post_bulk(
            client,
            hdrs,
            org_id,
            [
                {"id": "p1", "name": "Should be skipped"},
                {"id": "p2", "name": "Brand new"},
            ],
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["created"] == 1
        assert body["skipped"] == 1
        assert body["errors"] == []

    def test_intra_payload_duplicate_skipped(self, client, db):
        org_id = "bulk-intra"
        seed_org(client, org_id)
        hdrs = _admin_for(client, org_id, "intra")

        resp = _post_bulk(
            client,
            hdrs,
            org_id,
            [
                {"id": "x", "name": "First"},
                {"id": "x", "name": "Second"},
            ],
        )
        body = resp.json()
        assert body["created"] == 1
        assert body["skipped"] == 1


@pytest.mark.no_mock_auth
class TestBulkImportAuth:
    def test_volunteer_blocked(self, client, db):
        org_id = "bulk-vol"
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

        resp = _post_bulk(client, vol_hdrs, org_id, [{"id": "p1", "name": "Alice"}])
        assert resp.status_code == 403

    def test_no_auth_rejected(self, client, db):
        org_id = "bulk-noauth"
        seed_org(client, org_id)
        _admin_for(client, org_id, "noauth")

        resp = client.post(
            f"/api/v1/people/bulk?org_id={org_id}",
            json={"items": [{"id": "p1", "name": "Alice"}]},
        )
        assert resp.status_code in (401, 403)

    def test_cross_org_admin_blocked(self, client, db):
        seed_org(client, "bulk-a")
        seed_org(client, "bulk-b")
        a_hdrs = _admin_for(client, "bulk-a", "a")

        resp = _post_bulk(client, a_hdrs, "bulk-b", [{"id": "p1", "name": "X"}])
        assert resp.status_code == 403


@pytest.mark.no_mock_auth
class TestBulkImportValidation:
    def test_missing_items_key_400(self, client, db):
        org_id = "bulk-noitems"
        seed_org(client, org_id)
        hdrs = _admin_for(client, org_id, "noitems")

        resp = client.post(
            f"/api/v1/people/bulk?org_id={org_id}",
            json={},
            headers=hdrs,
        )
        assert resp.status_code == 400

    def test_bad_row_recorded_in_errors(self, client, db):
        org_id = "bulk-bad"
        seed_org(client, org_id)
        hdrs = _admin_for(client, org_id, "bad")

        resp = _post_bulk(
            client,
            hdrs,
            org_id,
            [
                {"id": "ok", "name": "OK"},
                {"name": "missing-id"},
            ],
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["created"] == 1
        assert len(body["errors"]) == 1
        assert body["errors"][0]["index"] == 1

    def test_org_id_mismatch_in_row(self, client, db):
        org_id = "bulk-mismatch"
        seed_org(client, "evil-org")
        seed_org(client, org_id)
        hdrs = _admin_for(client, org_id, "mismatch")

        resp = _post_bulk(
            client,
            hdrs,
            org_id,
            [{"id": "p1", "name": "Alice", "org_id": "evil-org"}],
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["created"] == 0
        assert len(body["errors"]) == 1
        assert "org_id mismatch" in body["errors"][0]["reason"]

    def test_cap_enforced(self, client, db):
        org_id = "bulk-cap"
        seed_org(client, org_id)
        hdrs = _admin_for(client, org_id, "cap")

        too_many = [{"id": f"p{i}", "name": f"P{i}"} for i in range(MAX_BULK_IMPORT_ITEMS + 1)]
        resp = _post_bulk(client, hdrs, org_id, too_many)
        assert resp.status_code == 400
        assert "exceeds cap" in resp.json()["detail"]


@pytest.mark.no_mock_auth
class TestBulkImportAudit:
    def test_audit_row_emitted(self, client, db):
        org_id = "bulk-audit"
        seed_org(client, org_id)
        hdrs = _admin_for(client, org_id, "audit")

        before = db.query(AuditLog).filter(AuditLog.action == AuditAction.BULK_IMPORT).count()
        resp = _post_bulk(client, hdrs, org_id, [{"id": "p1", "name": "Alice"}])
        assert resp.status_code == 200
        after = db.query(AuditLog).filter(AuditLog.action == AuditAction.BULK_IMPORT).count()
        assert after == before + 1
