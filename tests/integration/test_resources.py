#!/usr/bin/env python3
"""Integration tests: resources router (Sprint 4 PR 4.6b).

Tests the /api/v1/resources endpoints over real HTTP against the
session-scoped uvicorn api_server:
- POST   /resources/               - Create (admin)
- GET    /resources/               - List (envelope, org + type filter)
- GET    /resources/{resource_id}  - Get one
- PUT    /resources/{resource_id}  - Update (admin)
- DELETE /resources/{resource_id}  - Delete (admin), 409 when Event refs it
"""

import random
import time
from datetime import UTC, datetime, timedelta

import httpx
import pytest


def _unique(prefix: str) -> str:
    return f"{prefix}_{int(time.time() * 1000)}_{random.randint(10000, 99999)}"


@pytest.fixture
def resources_org(api_server, api_base):
    marker = _unique("resources_org")
    org_id = marker
    admin_email = f"admin_{marker}@test.com"
    vol_email = f"vol_{marker}@test.com"

    bootstrap = httpx.Client()
    org_resp = bootstrap.post(
        f"{api_base}/organizations/",
        json={"id": org_id, "name": f"Resources Setup {marker}", "region": "US", "config": {}},
    )
    assert org_resp.status_code == 201, org_resp.text

    admin_resp = bootstrap.post(
        f"{api_base}/auth/signup",
        json={
            "org_id": org_id,
            "name": "Resource Admin",
            "email": admin_email,
            "password": "AdminPass123!",
        },
    )
    assert admin_resp.status_code == 201, admin_resp.text
    admin_data = admin_resp.json()

    vol_resp = bootstrap.post(
        f"{api_base}/auth/signup",
        json={
            "org_id": org_id,
            "name": "Resource Volunteer",
            "email": vol_email,
            "password": "VolPass123!",
            "roles": ["volunteer"],
        },
    )
    assert vol_resp.status_code == 201, vol_resp.text
    vol_data = vol_resp.json()
    bootstrap.close()

    admin_client = httpx.Client()
    admin_client.headers["Authorization"] = f"Bearer {admin_data['token']}"

    vol_client = httpx.Client()
    vol_client.headers["Authorization"] = f"Bearer {vol_data['token']}"

    yield {
        "marker": marker,
        "org_id": org_id,
        "admin_client": admin_client,
        "vol_client": vol_client,
        "api_base": api_base,
    }

    admin_client.close()
    vol_client.close()


def _create_resource(client, api_base, org_id, *, rtype: str = "room", capacity: int = 20) -> dict:
    rid = _unique("res")
    resp = client.post(
        f"{api_base}/resources/",
        json={
            "id": rid,
            "org_id": org_id,
            "type": rtype,
            "location": f"Main Hall {rid}",
            "capacity": capacity,
            "extra_data": {},
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


class TestCreateResource:
    """POST /resources/ — admin-only creation."""

    def test_create_success(self, resources_org):
        data = resources_org
        r = _create_resource(data["admin_client"], data["api_base"], data["org_id"])
        assert r["org_id"] == data["org_id"]
        assert r["type"] == "room"
        assert r["capacity"] == 20

    def test_create_requires_admin(self, resources_org):
        data = resources_org
        resp = data["vol_client"].post(
            f"{data['api_base']}/resources/",
            json={
                "id": _unique("res"),
                "org_id": data["org_id"],
                "type": "room",
                "location": "hall",
                "capacity": 10,
            },
        )
        assert resp.status_code == 403

    def test_create_duplicate_id_rejected(self, resources_org):
        data = resources_org
        r = _create_resource(data["admin_client"], data["api_base"], data["org_id"])
        resp = data["admin_client"].post(
            f"{data['api_base']}/resources/",
            json={
                "id": r["id"],
                "org_id": data["org_id"],
                "type": "room",
                "location": "Overlap",
                "capacity": 5,
            },
        )
        assert resp.status_code == 409

    def test_create_cross_org_rejected(self, resources_org):
        data = resources_org
        resp = data["admin_client"].post(
            f"{data['api_base']}/resources/",
            json={
                "id": _unique("res"),
                "org_id": f"other_{int(time.time())}",
                "type": "room",
                "location": "elsewhere",
                "capacity": 1,
            },
        )
        assert resp.status_code in (403, 404)


class TestListAndGetResources:
    """GET /resources/ and GET /resources/{id}."""

    def test_list_envelope_and_scoping(self, resources_org):
        data = resources_org
        _create_resource(data["admin_client"], data["api_base"], data["org_id"])
        resp = data["admin_client"].get(
            f"{data['api_base']}/resources/",
            params={"org_id": data["org_id"]},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert set(body.keys()) >= {"items", "total", "limit", "offset"}
        assert all(r["org_id"] == data["org_id"] for r in body["items"])

    def test_list_type_filter(self, resources_org):
        data = resources_org
        _create_resource(data["admin_client"], data["api_base"], data["org_id"], rtype="room")
        _create_resource(data["admin_client"], data["api_base"], data["org_id"], rtype="equipment")
        resp = data["admin_client"].get(
            f"{data['api_base']}/resources/",
            params={"org_id": data["org_id"], "type": "equipment"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] >= 1
        assert all(r["type"] == "equipment" for r in body["items"])

    def test_list_volunteer_can_read(self, resources_org):
        data = resources_org
        _create_resource(data["admin_client"], data["api_base"], data["org_id"])
        resp = data["vol_client"].get(
            f"{data['api_base']}/resources/",
            params={"org_id": data["org_id"]},
        )
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

    def test_list_cross_org_rejected(self, resources_org):
        data = resources_org
        resp = data["admin_client"].get(
            f"{data['api_base']}/resources/",
            params={"org_id": f"other_{int(time.time())}"},
        )
        assert resp.status_code == 403

    def test_get_existing(self, resources_org):
        data = resources_org
        r = _create_resource(data["admin_client"], data["api_base"], data["org_id"])
        resp = data["admin_client"].get(f"{data['api_base']}/resources/{r['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == r["id"]

    def test_get_missing_returns_404(self, resources_org):
        data = resources_org
        resp = data["admin_client"].get(f"{data['api_base']}/resources/nope_{int(time.time())}")
        assert resp.status_code == 404


class TestUpdateResource:
    """PUT /resources/{id} — admin-only update."""

    def test_update_capacity_and_location(self, resources_org):
        data = resources_org
        r = _create_resource(data["admin_client"], data["api_base"], data["org_id"])
        resp = data["admin_client"].put(
            f"{data['api_base']}/resources/{r['id']}",
            json={"capacity": 99, "location": "Renamed hall"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["capacity"] == 99
        assert body["location"] == "Renamed hall"

    def test_update_requires_admin(self, resources_org):
        data = resources_org
        r = _create_resource(data["admin_client"], data["api_base"], data["org_id"])
        resp = data["vol_client"].put(
            f"{data['api_base']}/resources/{r['id']}",
            json={"capacity": 5},
        )
        assert resp.status_code == 403

    def test_update_missing_returns_404(self, resources_org):
        data = resources_org
        resp = data["admin_client"].put(
            f"{data['api_base']}/resources/nope_{int(time.time())}",
            json={"capacity": 1},
        )
        assert resp.status_code == 404


class TestDeleteResource:
    """DELETE /resources/{id}."""

    def test_delete_removes_resource(self, resources_org):
        data = resources_org
        r = _create_resource(data["admin_client"], data["api_base"], data["org_id"])
        resp = data["admin_client"].delete(f"{data['api_base']}/resources/{r['id']}")
        assert resp.status_code == 204
        follow = data["admin_client"].get(f"{data['api_base']}/resources/{r['id']}")
        assert follow.status_code == 404

    def test_delete_requires_admin(self, resources_org):
        data = resources_org
        r = _create_resource(data["admin_client"], data["api_base"], data["org_id"])
        resp = data["vol_client"].delete(f"{data['api_base']}/resources/{r['id']}")
        assert resp.status_code == 403

    def test_delete_missing_returns_404(self, resources_org):
        data = resources_org
        resp = data["admin_client"].delete(f"{data['api_base']}/resources/nope_{int(time.time())}")
        assert resp.status_code == 404

    def test_delete_referenced_by_event_409(self, resources_org):
        data = resources_org
        r = _create_resource(data["admin_client"], data["api_base"], data["org_id"])
        # Create an event that references this resource
        start = (datetime.now(UTC) + timedelta(days=25)).replace(
            hour=10, minute=0, second=0, microsecond=0
        )
        end = start + timedelta(hours=2)
        event_id = _unique("evt")
        event_resp = data["admin_client"].post(
            f"{data['api_base']}/events/",
            json={
                "id": event_id,
                "org_id": data["org_id"],
                "type": "worship",
                "start_time": start.isoformat(),
                "end_time": end.isoformat(),
                "resource_id": r["id"],
                "extra_data": {},
            },
        )
        assert event_resp.status_code == 201, event_resp.text

        resp = data["admin_client"].delete(f"{data['api_base']}/resources/{r['id']}")
        assert resp.status_code == 409, resp.text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
