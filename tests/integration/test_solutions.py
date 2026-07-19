#!/usr/bin/env python3
"""Integration tests: solutions router (Sprint 4 PR 4.6b).

Tests /api/v1/solutions endpoints over real HTTP against the
session-scoped uvicorn api_server. Focuses on the manual-create /
list / get / publish-unpublish / rollback / delete lifecycle. The
solver end-to-end is exercised elsewhere (unit + core tests); here we
drive the routes directly with manually-created solution rows.

Endpoints exercised:
- POST   /solutions/                       - Create a manual solution row
- GET    /solutions/                       - List (envelope, org filter)
- GET    /solutions/{id}                   - Get one
- POST   /solutions/{id}/publish           - Publish (admin)
- POST   /solutions/{id}/unpublish         - Unpublish (admin)
- POST   /solutions/{id}/rollback          - Rollback (admin)
- DELETE /solutions/{id}                   - Delete
- GET    /solutions/{id}/stats             - Stats (admin)
"""

import time

import httpx
import pytest


def _unique(prefix: str) -> str:
    return f"{prefix}_{int(time.time() * 1000)}"


@pytest.fixture
def solutions_org(api_server, api_base):
    """Create org + admin + a same-org volunteer + a stranger admin in another org."""
    marker = _unique("sol_org")
    org_id = marker
    stranger_org_id = _unique("sol_stranger_org")

    bootstrap = httpx.Client()

    for oid in (org_id, stranger_org_id):
        resp = bootstrap.post(
            f"{api_base}/organizations/",
            json={"id": oid, "name": f"Sol {oid}", "region": "US", "config": {}},
        )
        assert resp.status_code == 201, resp.text

    def _signup(oid: str, name: str, roles=None) -> dict:
        body = {
            "org_id": oid,
            "name": name,
            "email": f"{name.lower().replace(' ', '_')}_{_unique('u')}@test.com",
            "password": "Password123!",
        }
        if roles is not None:
            body["roles"] = roles
        r = bootstrap.post(f"{api_base}/auth/signup", json=body)
        assert r.status_code == 201, r.text
        return r.json()

    admin = _signup(org_id, "Solutions Admin")
    assert "admin" in admin["roles"]
    volunteer = _signup(org_id, "Solutions Volunteer", roles=["volunteer"])
    assert "admin" not in volunteer["roles"]
    stranger = _signup(stranger_org_id, "Stranger Admin")
    assert "admin" in stranger["roles"]

    bootstrap.close()

    admin_client = httpx.Client()
    admin_client.headers["Authorization"] = f"Bearer {admin['token']}"

    vol_client = httpx.Client()
    vol_client.headers["Authorization"] = f"Bearer {volunteer['token']}"

    stranger_client = httpx.Client()
    stranger_client.headers["Authorization"] = f"Bearer {stranger['token']}"

    yield {
        "marker": marker,
        "org_id": org_id,
        "stranger_org_id": stranger_org_id,
        "admin_id": admin["person_id"],
        "admin_client": admin_client,
        "vol_id": volunteer["person_id"],
        "vol_client": vol_client,
        "stranger_id": stranger["person_id"],
        "stranger_client": stranger_client,
        "api_base": api_base,
    }

    admin_client.close()
    vol_client.close()
    stranger_client.close()


def _create_solution(client: httpx.Client, api_base: str, org_id: str) -> dict:
    resp = client.post(
        f"{api_base}/solutions/",
        json={
            "org_id": org_id,
            "solve_ms": 42.0,
            "hard_violations": 0,
            "soft_score": 1.0,
            "health_score": 0.99,
            "metrics": {},
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


class TestCreateAndRead:
    """POST /solutions/, GET /solutions/, GET /solutions/{id}."""

    def test_create_success(self, solutions_org):
        data = solutions_org
        sol = _create_solution(data["admin_client"], data["api_base"], data["org_id"])
        assert sol["org_id"] == data["org_id"]
        assert sol["assignment_count"] == 0
        assert sol["is_published"] is False

    def test_create_missing_org_id_400(self, solutions_org):
        data = solutions_org
        resp = data["admin_client"].post(
            f"{data['api_base']}/solutions/",
            json={"solve_ms": 1.0},
        )
        assert resp.status_code == 400

    def test_create_unknown_org_404(self, solutions_org):
        data = solutions_org
        resp = data["admin_client"].post(
            f"{data['api_base']}/solutions/",
            json={"org_id": f"ghost_{int(time.time())}"},
        )
        assert resp.status_code == 404

    def test_list_envelope_and_org_filter(self, solutions_org):
        data = solutions_org
        created = _create_solution(data["admin_client"], data["api_base"], data["org_id"])

        resp = data["admin_client"].get(
            f"{data['api_base']}/solutions/",
            params={"org_id": data["org_id"]},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert set(body.keys()) >= {"items", "total", "limit", "offset"}
        assert created["id"] in {s["id"] for s in body["items"]}
        assert all(s["org_id"] == data["org_id"] for s in body["items"])

    def test_get_existing_returns_body(self, solutions_org):
        data = solutions_org
        created = _create_solution(data["admin_client"], data["api_base"], data["org_id"])

        resp = data["admin_client"].get(f"{data['api_base']}/solutions/{created['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == created["id"]

    def test_get_missing_returns_404(self, solutions_org):
        data = solutions_org
        resp = data["admin_client"].get(f"{data['api_base']}/solutions/999999999")
        assert resp.status_code == 404


class TestPublishUnpublish:
    """POST /solutions/{id}/publish and /unpublish — admin-gated lifecycle."""

    def test_publish_flow_sets_is_published(self, solutions_org):
        data = solutions_org
        sol = _create_solution(data["admin_client"], data["api_base"], data["org_id"])

        resp = data["admin_client"].post(f"{data['api_base']}/solutions/{sol['id']}/publish")
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["is_published"] is True
        assert body["published_at"] is not None

    def test_publish_replaces_prior_in_same_org(self, solutions_org):
        data = solutions_org
        first = _create_solution(data["admin_client"], data["api_base"], data["org_id"])
        second = _create_solution(data["admin_client"], data["api_base"], data["org_id"])

        p1 = data["admin_client"].post(f"{data['api_base']}/solutions/{first['id']}/publish")
        assert p1.status_code == 200
        p2 = data["admin_client"].post(f"{data['api_base']}/solutions/{second['id']}/publish")
        assert p2.status_code == 200

        first_after = data["admin_client"].get(f"{data['api_base']}/solutions/{first['id']}")
        assert first_after.status_code == 200
        assert first_after.json()["is_published"] is False
        assert first_after.json()["published_at"] is None

    def test_publish_requires_admin(self, solutions_org):
        data = solutions_org
        sol = _create_solution(data["admin_client"], data["api_base"], data["org_id"])

        resp = data["vol_client"].post(f"{data['api_base']}/solutions/{sol['id']}/publish")
        assert resp.status_code == 403

    def test_publish_cross_org_forbidden(self, solutions_org):
        data = solutions_org
        sol = _create_solution(data["admin_client"], data["api_base"], data["org_id"])

        resp = data["stranger_client"].post(f"{data['api_base']}/solutions/{sol['id']}/publish")
        assert resp.status_code == 403

    def test_publish_missing_solution_404(self, solutions_org):
        data = solutions_org
        resp = data["admin_client"].post(f"{data['api_base']}/solutions/999999999/publish")
        assert resp.status_code == 404

    def test_unpublish_clears_flags(self, solutions_org):
        data = solutions_org
        sol = _create_solution(data["admin_client"], data["api_base"], data["org_id"])

        pub = data["admin_client"].post(f"{data['api_base']}/solutions/{sol['id']}/publish")
        assert pub.status_code == 200
        unp = data["admin_client"].post(f"{data['api_base']}/solutions/{sol['id']}/unpublish")
        assert unp.status_code == 200
        body = unp.json()
        assert body["is_published"] is False
        assert body["published_at"] is None


class TestRollback:
    """POST /solutions/{id}/rollback — republish a previously-published solution."""

    def test_rollback_requires_prior_publish(self, solutions_org):
        data = solutions_org
        sol = _create_solution(data["admin_client"], data["api_base"], data["org_id"])

        resp = data["admin_client"].post(f"{data['api_base']}/solutions/{sol['id']}/rollback")
        assert resp.status_code == 400

    def test_rollback_republishes_prior(self, solutions_org):
        data = solutions_org
        first = _create_solution(data["admin_client"], data["api_base"], data["org_id"])
        second = _create_solution(data["admin_client"], data["api_base"], data["org_id"])

        assert (
            data["admin_client"]
            .post(f"{data['api_base']}/solutions/{first['id']}/publish")
            .status_code
            == 200
        )
        assert (
            data["admin_client"]
            .post(f"{data['api_base']}/solutions/{second['id']}/publish")
            .status_code
            == 200
        )

        resp = data["admin_client"].post(f"{data['api_base']}/solutions/{first['id']}/rollback")
        assert resp.status_code == 200, resp.text
        assert resp.json()["is_published"] is True

        second_after = data["admin_client"].get(f"{data['api_base']}/solutions/{second['id']}")
        assert second_after.status_code == 200
        assert second_after.json()["is_published"] is False

    def test_rollback_requires_admin(self, solutions_org):
        data = solutions_org
        sol = _create_solution(data["admin_client"], data["api_base"], data["org_id"])

        resp = data["vol_client"].post(f"{data['api_base']}/solutions/{sol['id']}/rollback")
        assert resp.status_code == 403


class TestStats:
    """GET /solutions/{id}/stats — admin-only aggregate."""

    def test_stats_returns_zero_when_empty(self, solutions_org):
        data = solutions_org
        sol = _create_solution(data["admin_client"], data["api_base"], data["org_id"])

        resp = data["admin_client"].get(f"{data['api_base']}/solutions/{sol['id']}/stats")
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["solution_id"] == sol["id"]
        # No assignments => zero histogram entries and zero workload.
        assert body["workload"]["total_events_assigned"] == 0

    def test_stats_requires_admin(self, solutions_org):
        data = solutions_org
        sol = _create_solution(data["admin_client"], data["api_base"], data["org_id"])

        resp = data["vol_client"].get(f"{data['api_base']}/solutions/{sol['id']}/stats")
        assert resp.status_code == 403


class TestDelete:
    """DELETE /solutions/{id}."""

    def test_delete_removes_solution(self, solutions_org):
        data = solutions_org
        sol = _create_solution(data["admin_client"], data["api_base"], data["org_id"])

        resp = data["admin_client"].delete(f"{data['api_base']}/solutions/{sol['id']}")
        assert resp.status_code == 204

        follow = data["admin_client"].get(f"{data['api_base']}/solutions/{sol['id']}")
        assert follow.status_code == 404

    def test_delete_missing_404(self, solutions_org):
        data = solutions_org
        resp = data["admin_client"].delete(f"{data['api_base']}/solutions/999999999")
        assert resp.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
