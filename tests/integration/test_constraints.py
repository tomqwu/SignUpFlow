#!/usr/bin/env python3
"""Integration tests: constraints router (Sprint 4 PR 4.6b).

Tests the /api/v1/constraints endpoints over real HTTP against the
session-scoped uvicorn api_server:
- POST   /constraints/                 - Create (admin)
- GET    /constraints/                 - List (envelope, org + type filter)
- GET    /constraints/{constraint_id}  - Get one
- PUT    /constraints/{constraint_id}  - Update (admin)
- DELETE /constraints/{constraint_id}  - Delete (admin)
"""

import time

import httpx
import pytest


def _unique(prefix: str) -> str:
    return f"{prefix}_{int(time.time() * 1000)}"


@pytest.fixture
def constraints_org(api_server, api_base):
    """Create an org + admin + one volunteer; return authed clients + ids."""
    marker = _unique("constraints_org")
    org_id = marker
    admin_email = f"admin_{marker}@test.com"
    vol_email = f"vol_{marker}@test.com"

    bootstrap = httpx.Client()

    org_resp = bootstrap.post(
        f"{api_base}/organizations/",
        json={"id": org_id, "name": f"Constraints Setup {marker}", "region": "US", "config": {}},
    )
    assert org_resp.status_code == 201, org_resp.text

    admin_resp = bootstrap.post(
        f"{api_base}/auth/signup",
        json={
            "org_id": org_id,
            "name": "Constraint Admin",
            "email": admin_email,
            "password": "AdminPass123!",
        },
    )
    assert admin_resp.status_code == 201, admin_resp.text
    admin_data = admin_resp.json()
    assert "admin" in admin_data["roles"]

    vol_resp = bootstrap.post(
        f"{api_base}/auth/signup",
        json={
            "org_id": org_id,
            "name": "Constraint Volunteer",
            "email": vol_email,
            "password": "VolPass123!",
            "roles": ["volunteer"],
        },
    )
    assert vol_resp.status_code == 201, vol_resp.text
    vol_data = vol_resp.json()
    assert "admin" not in vol_data["roles"]

    bootstrap.close()

    admin_client = httpx.Client()
    admin_client.headers["Authorization"] = f"Bearer {admin_data['token']}"

    vol_client = httpx.Client()
    vol_client.headers["Authorization"] = f"Bearer {vol_data['token']}"

    yield {
        "marker": marker,
        "org_id": org_id,
        "admin_id": admin_data["person_id"],
        "admin_client": admin_client,
        "vol_id": vol_data["person_id"],
        "vol_client": vol_client,
        "api_base": api_base,
    }

    admin_client.close()
    vol_client.close()


def _create_constraint(
    client: httpx.Client,
    api_base: str,
    org_id: str,
    *,
    key: str | None = None,
    ctype: str = "hard",
    weight: int = 1,
    predicate: str = "no_conflict",
    params: dict | None = None,
) -> dict:
    """Helper: POST /constraints/ and return the response body."""
    resp = client.post(
        f"{api_base}/constraints/",
        json={
            "org_id": org_id,
            "key": key or _unique("k"),
            "type": ctype,
            "weight": weight,
            "predicate": predicate,
            "params": params or {},
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


class TestCreateConstraint:
    """POST /constraints/ — admin-only creation."""

    def test_create_success(self, constraints_org):
        data = constraints_org
        c = _create_constraint(data["admin_client"], data["api_base"], data["org_id"])
        assert c["org_id"] == data["org_id"]
        assert c["type"] == "hard"
        assert c["weight"] == 1
        assert isinstance(c["id"], int)

    def test_create_requires_admin(self, constraints_org):
        data = constraints_org
        resp = data["vol_client"].post(
            f"{data['api_base']}/constraints/",
            json={
                "org_id": data["org_id"],
                "key": _unique("k"),
                "type": "hard",
                "weight": 1,
                "predicate": "no_conflict",
                "params": {},
            },
        )
        assert resp.status_code == 403

    def test_create_unauthenticated_rejected(self, constraints_org):
        data = constraints_org
        anon = httpx.Client()
        try:
            resp = anon.post(
                f"{data['api_base']}/constraints/",
                json={
                    "org_id": data["org_id"],
                    "key": _unique("k"),
                    "type": "hard",
                    "weight": 1,
                    "predicate": "no_conflict",
                    "params": {},
                },
            )
        finally:
            anon.close()
        assert resp.status_code in (401, 403)

    def test_create_invalid_type_rejected(self, constraints_org):
        data = constraints_org
        resp = data["admin_client"].post(
            f"{data['api_base']}/constraints/",
            json={
                "org_id": data["org_id"],
                "key": _unique("k"),
                "type": "bogus",
                "weight": 1,
                "predicate": "no_conflict",
                "params": {},
            },
        )
        assert resp.status_code == 400

    def test_create_missing_org_returns_404_or_403(self, constraints_org):
        data = constraints_org
        # Admin isn't a member of a random org, so verify_org_member fires
        # (403). If tenancy guard is ever bypassed, org lookup would 404.
        resp = data["admin_client"].post(
            f"{data['api_base']}/constraints/",
            json={
                "org_id": f"nonexistent_{int(time.time())}",
                "key": _unique("k"),
                "type": "hard",
                "weight": 1,
                "predicate": "no_conflict",
                "params": {},
            },
        )
        assert resp.status_code in (403, 404)


class TestListAndGetConstraints:
    """GET /constraints/ and GET /constraints/{id} — read paths."""

    def test_list_envelope_and_defaults(self, constraints_org):
        data = constraints_org
        _create_constraint(data["admin_client"], data["api_base"], data["org_id"])

        resp = data["admin_client"].get(f"{data['api_base']}/constraints/")
        assert resp.status_code == 200
        body = resp.json()
        assert set(body.keys()) >= {"items", "total", "limit", "offset"}
        assert all(c["org_id"] == data["org_id"] for c in body["items"])

    def test_list_volunteer_can_read(self, constraints_org):
        data = constraints_org
        _create_constraint(data["admin_client"], data["api_base"], data["org_id"])

        resp = data["vol_client"].get(f"{data['api_base']}/constraints/")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] >= 1

    def test_list_type_filter(self, constraints_org):
        data = constraints_org
        _create_constraint(data["admin_client"], data["api_base"], data["org_id"], ctype="hard")
        _create_constraint(data["admin_client"], data["api_base"], data["org_id"], ctype="soft")

        resp = data["admin_client"].get(
            f"{data['api_base']}/constraints/",
            params={"constraint_type": "soft"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] >= 1
        assert all(c["type"] == "soft" for c in body["items"])

    def test_get_existing(self, constraints_org):
        data = constraints_org
        c = _create_constraint(data["admin_client"], data["api_base"], data["org_id"])

        resp = data["admin_client"].get(f"{data['api_base']}/constraints/{c['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == c["id"]

    def test_get_missing_returns_404(self, constraints_org):
        data = constraints_org
        resp = data["admin_client"].get(f"{data['api_base']}/constraints/999999999")
        assert resp.status_code == 404


class TestUpdateConstraint:
    """PUT /constraints/{id} — admin-only update."""

    def test_update_weight_and_predicate(self, constraints_org):
        data = constraints_org
        c = _create_constraint(data["admin_client"], data["api_base"], data["org_id"])

        resp = data["admin_client"].put(
            f"{data['api_base']}/constraints/{c['id']}",
            json={"weight": 42, "predicate": "no_double_book"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["weight"] == 42
        assert body["predicate"] == "no_double_book"

    def test_update_invalid_type_rejected(self, constraints_org):
        data = constraints_org
        c = _create_constraint(data["admin_client"], data["api_base"], data["org_id"])

        resp = data["admin_client"].put(
            f"{data['api_base']}/constraints/{c['id']}",
            json={"type": "not_a_type"},
        )
        assert resp.status_code == 400

    def test_update_requires_admin(self, constraints_org):
        data = constraints_org
        c = _create_constraint(data["admin_client"], data["api_base"], data["org_id"])

        resp = data["vol_client"].put(
            f"{data['api_base']}/constraints/{c['id']}",
            json={"weight": 99},
        )
        assert resp.status_code == 403

    def test_update_missing_returns_404(self, constraints_org):
        data = constraints_org
        resp = data["admin_client"].put(
            f"{data['api_base']}/constraints/999999999",
            json={"weight": 5},
        )
        assert resp.status_code == 404


class TestDeleteConstraint:
    """DELETE /constraints/{id}."""

    def test_delete_removes_constraint(self, constraints_org):
        data = constraints_org
        c = _create_constraint(data["admin_client"], data["api_base"], data["org_id"])

        resp = data["admin_client"].delete(f"{data['api_base']}/constraints/{c['id']}")
        assert resp.status_code == 204

        follow = data["admin_client"].get(f"{data['api_base']}/constraints/{c['id']}")
        assert follow.status_code == 404

    def test_delete_requires_admin(self, constraints_org):
        data = constraints_org
        c = _create_constraint(data["admin_client"], data["api_base"], data["org_id"])

        resp = data["vol_client"].delete(f"{data['api_base']}/constraints/{c['id']}")
        assert resp.status_code == 403

    def test_delete_missing_returns_404(self, constraints_org):
        data = constraints_org
        resp = data["admin_client"].delete(f"{data['api_base']}/constraints/999999999")
        assert resp.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
