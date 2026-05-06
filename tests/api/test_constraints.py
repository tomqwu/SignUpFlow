"""Tests for /api/v1/constraints/ — admin-only CRUD with auth and tenancy enforcement."""

import pytest

from tests.api.conftest import auth_headers, seed_org, seed_user


@pytest.fixture
def admin_setup(client):
    """Create an org and an admin, return (org_id, admin_hdrs)."""
    org_id = "constraint-test-org"
    seed_org(client, org_id)
    seed_user(client, org_id, email="admin@c.org", name="Admin", password="AdminPass1!")
    return org_id, auth_headers(client, email="admin@c.org", password="AdminPass1!")


@pytest.mark.no_mock_auth
class TestConstraintAuth:
    def test_unauthenticated_create_rejected(self, client, db, admin_setup):
        org_id, _ = admin_setup
        resp = client.post(
            "/api/v1/constraints/",
            json={
                "org_id": org_id,
                "key": "x",
                "type": "hard",
                "weight": 1,
                "predicate": "p",
                "params": {},
            },
        )
        assert resp.status_code in (401, 403)

    def test_volunteer_cannot_create(self, client, db, admin_setup):
        org_id, _ = admin_setup
        seed_user(
            client,
            org_id,
            email="vol@c.org",
            name="Vol",
            password="VolPass1!",
            roles=["volunteer"],
        )
        vol_hdrs = auth_headers(client, email="vol@c.org", password="VolPass1!")
        resp = client.post(
            "/api/v1/constraints/",
            json={
                "org_id": org_id,
                "key": "x",
                "type": "hard",
                "weight": 1,
                "predicate": "p",
                "params": {},
            },
            headers=vol_hdrs,
        )
        assert resp.status_code == 403

    def test_admin_cross_org_create_blocked(self, client, db, admin_setup):
        org_a, admin_a_hdrs = admin_setup
        # Create another org
        seed_org(client, "constraint-other-org")
        resp = client.post(
            "/api/v1/constraints/",
            json={
                "org_id": "constraint-other-org",
                "key": "x",
                "type": "hard",
                "weight": 1,
                "predicate": "p",
                "params": {},
            },
            headers=admin_a_hdrs,
        )
        assert resp.status_code == 403


@pytest.mark.no_mock_auth
class TestConstraintCrud:
    def test_create_hard_constraint(self, client, db, admin_setup):
        org_id, hdrs = admin_setup
        resp = client.post(
            "/api/v1/constraints/",
            json={
                "org_id": org_id,
                "key": "no_double_book",
                "type": "hard",
                "weight": 1,
                "predicate": "no_overlap",
                "params": {},
            },
            headers=hdrs,
        )
        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["key"] == "no_double_book"
        assert body["type"] == "hard"

    def test_create_rejects_invalid_type(self, client, db, admin_setup):
        org_id, hdrs = admin_setup
        resp = client.post(
            "/api/v1/constraints/",
            json={
                "org_id": org_id,
                "key": "bad",
                "type": "fizzbuzz",
                "weight": 1,
                "predicate": "x",
                "params": {},
            },
            headers=hdrs,
        )
        assert resp.status_code == 400

    def test_create_rejects_unknown_org(self, client, db, admin_setup):
        # Even an admin can't target an org they don't belong to
        _, hdrs = admin_setup
        resp = client.post(
            "/api/v1/constraints/",
            json={
                "org_id": "no-such-org",
                "key": "x",
                "type": "hard",
                "weight": 1,
                "predicate": "x",
                "params": {},
            },
            headers=hdrs,
        )
        # verify_org_member fires before the org-existence check, so 403 is correct
        assert resp.status_code in (403, 404)

    def test_list_filter_by_org(self, client, db, admin_setup):
        org_id, hdrs = admin_setup
        for key in ("a", "b"):
            client.post(
                "/api/v1/constraints/",
                json={
                    "org_id": org_id,
                    "key": key,
                    "type": "soft",
                    "weight": 1,
                    "predicate": "p",
                    "params": {},
                },
                headers=hdrs,
            )

        resp = client.get(f"/api/v1/constraints/?org_id={org_id}", headers=hdrs)
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] >= 2
        assert all(item["org_id"] == org_id for item in body["items"])

    def test_list_filter_by_type(self, client, db, admin_setup):
        org_id, hdrs = admin_setup
        client.post(
            "/api/v1/constraints/",
            json={
                "org_id": org_id,
                "key": "h1",
                "type": "hard",
                "weight": 1,
                "predicate": "p",
                "params": {},
            },
            headers=hdrs,
        )
        client.post(
            "/api/v1/constraints/",
            json={
                "org_id": org_id,
                "key": "s1",
                "type": "soft",
                "weight": 1,
                "predicate": "p",
                "params": {},
            },
            headers=hdrs,
        )
        resp = client.get(
            f"/api/v1/constraints/?org_id={org_id}&constraint_type=hard", headers=hdrs
        )
        assert resp.status_code == 200
        body = resp.json()
        assert all(item["type"] == "hard" for item in body["items"])

    def test_get_by_id(self, client, db, admin_setup):
        org_id, hdrs = admin_setup
        created = client.post(
            "/api/v1/constraints/",
            json={
                "org_id": org_id,
                "key": "g",
                "type": "hard",
                "weight": 1,
                "predicate": "p",
                "params": {},
            },
            headers=hdrs,
        ).json()
        cid = created["id"]
        resp = client.get(f"/api/v1/constraints/{cid}", headers=hdrs)
        assert resp.status_code == 200
        assert resp.json()["id"] == cid

    def test_get_returns_404_for_unknown(self, client, db, admin_setup):
        _, hdrs = admin_setup
        resp = client.get("/api/v1/constraints/999999", headers=hdrs)
        assert resp.status_code == 404

    def test_delete_constraint(self, client, db, admin_setup):
        org_id, hdrs = admin_setup
        created = client.post(
            "/api/v1/constraints/",
            json={
                "org_id": org_id,
                "key": "d",
                "type": "soft",
                "weight": 1,
                "predicate": "p",
                "params": {},
            },
            headers=hdrs,
        ).json()
        cid = created["id"]
        resp = client.delete(f"/api/v1/constraints/{cid}", headers=hdrs)
        assert resp.status_code in (200, 204)
        assert client.get(f"/api/v1/constraints/{cid}", headers=hdrs).status_code == 404
