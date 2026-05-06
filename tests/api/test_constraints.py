"""Tests for /api/v1/constraints/ — covers CRUD on the previously zero-test router."""

import pytest

from tests.api.conftest import auth_headers, seed_org, seed_user


@pytest.fixture
def admin_setup(client):
    """Create an org and an admin, return (org_id, headers)."""
    org_id = "constraint-test-org"
    seed_org(client, org_id)
    seed_user(client, org_id, email="admin@c.org", name="Admin", password="AdminPass1!")
    return org_id, auth_headers(client, email="admin@c.org", password="AdminPass1!")


@pytest.mark.no_mock_auth
class TestConstraintCrud:
    def test_create_hard_constraint(self, client, db, admin_setup):
        org_id, _ = admin_setup
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
        )
        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["key"] == "no_double_book"
        assert body["type"] == "hard"

    def test_create_rejects_invalid_type(self, client, db, admin_setup):
        org_id, _ = admin_setup
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
        )
        assert resp.status_code == 400

    def test_create_rejects_unknown_org(self, client, db):
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
        )
        assert resp.status_code == 404

    def test_list_filter_by_org(self, client, db, admin_setup):
        org_id, _ = admin_setup
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
            )

        resp = client.get(f"/api/v1/constraints/?org_id={org_id}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] >= 2
        assert all(item["org_id"] == org_id for item in body["items"])

    def test_list_filter_by_type(self, client, db, admin_setup):
        org_id, _ = admin_setup
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
        )
        resp = client.get(f"/api/v1/constraints/?org_id={org_id}&constraint_type=hard")
        assert resp.status_code == 200
        body = resp.json()
        assert all(item["type"] == "hard" for item in body["items"])

    def test_get_by_id(self, client, db, admin_setup):
        org_id, _ = admin_setup
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
        ).json()
        cid = created["id"]
        resp = client.get(f"/api/v1/constraints/{cid}")
        assert resp.status_code == 200
        assert resp.json()["id"] == cid

    def test_get_returns_404_for_unknown(self, client, db):
        resp = client.get("/api/v1/constraints/999999")
        assert resp.status_code == 404

    def test_delete_constraint(self, client, db, admin_setup):
        org_id, _ = admin_setup
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
        ).json()
        cid = created["id"]
        resp = client.delete(f"/api/v1/constraints/{cid}")
        assert resp.status_code in (200, 204)
        assert client.get(f"/api/v1/constraints/{cid}").status_code == 404
