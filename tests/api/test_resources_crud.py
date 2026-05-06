"""Tests for /api/v1/resources/ — CRUD with admin-only writes."""

from datetime import datetime, timedelta

import pytest

from tests.api.conftest import auth_headers, seed_org, seed_user


def _admin(client, org_id: str, suffix: str):
    seed_user(
        client,
        org_id,
        email=f"admin-{suffix}@r.org",
        name="Admin",
        password="AdminPass1!",
    )
    return auth_headers(client, email=f"admin-{suffix}@r.org", password="AdminPass1!")


def _resource_body(rid: str, org_id: str, *, type_: str = "room", location: str = "Hall A") -> dict:
    return {
        "id": rid,
        "org_id": org_id,
        "type": type_,
        "location": location,
        "capacity": 50,
        "extra_data": {},
    }


@pytest.mark.no_mock_auth
class TestResourceCreate:
    def test_admin_creates_resource(self, client, db):
        org = "res-create"
        seed_org(client, org)
        hdrs = _admin(client, org, "create")

        resp = client.post(
            "/api/v1/resources/",
            json=_resource_body("r-1", org),
            headers=hdrs,
        )
        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["id"] == "r-1"
        assert body["type"] == "room"

    def test_volunteer_cannot_create(self, client, db):
        org = "res-vol"
        seed_org(client, org)
        _admin(client, org, "vol-admin")
        seed_user(
            client,
            org,
            email="vol@r.org",
            name="Vol",
            password="VolPass1!",
            roles=["volunteer"],
        )
        vol_hdrs = auth_headers(client, email="vol@r.org", password="VolPass1!")
        resp = client.post(
            "/api/v1/resources/",
            json=_resource_body("r-vol", org),
            headers=vol_hdrs,
        )
        assert resp.status_code == 403

    def test_admin_cross_org_blocked(self, client, db):
        seed_org(client, "res-a")
        seed_org(client, "res-b")
        a_hdrs = _admin(client, "res-a", "a-admin")

        resp = client.post(
            "/api/v1/resources/",
            json=_resource_body("r-cross", "res-b"),
            headers=a_hdrs,
        )
        assert resp.status_code == 403

    def test_duplicate_id_returns_409(self, client, db):
        org = "res-dup"
        seed_org(client, org)
        hdrs = _admin(client, org, "dup")

        client.post("/api/v1/resources/", json=_resource_body("r-dup", org), headers=hdrs)
        resp = client.post(
            "/api/v1/resources/",
            json=_resource_body("r-dup", org, location="Hall B"),
            headers=hdrs,
        )
        assert resp.status_code == 409


@pytest.mark.no_mock_auth
class TestResourceList:
    def test_list_returns_envelope_filtered_by_org(self, client, db):
        org = "res-list"
        seed_org(client, org)
        hdrs = _admin(client, org, "list")
        for i in range(3):
            client.post(
                "/api/v1/resources/",
                json=_resource_body(f"r-list-{i}", org),
                headers=hdrs,
            )

        resp = client.get(f"/api/v1/resources/?org_id={org}", headers=hdrs)
        assert resp.status_code == 200
        body = resp.json()
        assert {"items", "total", "limit", "offset"} <= set(body.keys())
        assert body["total"] >= 3
        assert all(item["org_id"] == org for item in body["items"])

    def test_list_filters_by_type(self, client, db):
        org = "res-bytype"
        seed_org(client, org)
        hdrs = _admin(client, org, "bytype")
        client.post(
            "/api/v1/resources/",
            json=_resource_body("r-room", org, type_="room"),
            headers=hdrs,
        )
        client.post(
            "/api/v1/resources/",
            json=_resource_body("r-equip", org, type_="equipment"),
            headers=hdrs,
        )

        resp = client.get(f"/api/v1/resources/?org_id={org}&type=equipment", headers=hdrs)
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert all(item["type"] == "equipment" for item in items)

    def test_cross_org_list_blocked(self, client, db):
        seed_org(client, "res-list-a")
        seed_org(client, "res-list-b")
        a_hdrs = _admin(client, "res-list-a", "ll-a")

        resp = client.get("/api/v1/resources/?org_id=res-list-b", headers=a_hdrs)
        assert resp.status_code == 403


@pytest.mark.no_mock_auth
class TestResourceGetUpdateDelete:
    def test_get_by_id(self, client, db):
        org = "res-get"
        seed_org(client, org)
        hdrs = _admin(client, org, "get")
        client.post("/api/v1/resources/", json=_resource_body("r-get", org), headers=hdrs)

        resp = client.get("/api/v1/resources/r-get", headers=hdrs)
        assert resp.status_code == 200
        assert resp.json()["id"] == "r-get"

    def test_get_unknown_404(self, client, db):
        org = "res-getno"
        seed_org(client, org)
        hdrs = _admin(client, org, "getno")

        resp = client.get("/api/v1/resources/nope", headers=hdrs)
        assert resp.status_code == 404

    def test_update_preserves_org_id(self, client, db):
        org = "res-upd"
        seed_org(client, org)
        hdrs = _admin(client, org, "upd")
        client.post("/api/v1/resources/", json=_resource_body("r-upd", org), headers=hdrs)

        resp = client.put(
            "/api/v1/resources/r-upd",
            json={"location": "New Hall"},
            headers=hdrs,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["location"] == "New Hall"
        assert body["org_id"] == org

    def test_delete_blocks_when_referenced_by_event(self, client, db):
        org = "res-del-ref"
        seed_org(client, org)
        hdrs = _admin(client, org, "del-ref")
        client.post("/api/v1/resources/", json=_resource_body("r-ref", org), headers=hdrs)

        # Create an event that references the resource
        event_payload = {
            "id": "evt-ref",
            "org_id": org,
            "type": "service",
            "start_time": (datetime.utcnow() + timedelta(days=2)).isoformat(),
            "end_time": (datetime.utcnow() + timedelta(days=2, hours=1)).isoformat(),
            "resource_id": "r-ref",
            "extra_data": {},
        }
        ev_resp = client.post("/api/v1/events/", json=event_payload, headers=hdrs)
        assert ev_resp.status_code == 201, ev_resp.text

        resp = client.delete("/api/v1/resources/r-ref", headers=hdrs)
        assert resp.status_code == 409

    def test_delete_unreferenced_succeeds(self, client, db):
        org = "res-del-ok"
        seed_org(client, org)
        hdrs = _admin(client, org, "del-ok")
        client.post("/api/v1/resources/", json=_resource_body("r-free", org), headers=hdrs)

        resp = client.delete("/api/v1/resources/r-free", headers=hdrs)
        assert resp.status_code in (200, 204)
        assert client.get("/api/v1/resources/r-free", headers=hdrs).status_code == 404
