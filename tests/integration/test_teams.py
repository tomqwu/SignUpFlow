#!/usr/bin/env python3
"""Integration tests: teams router (Sprint 4 PR 4.6b).

Tests the /api/v1/teams endpoints over real HTTP against the
session-scoped uvicorn api_server:
- POST   /teams/                         - Create (admin)
- GET    /teams/                         - List (envelope, q= search, org filter)
- GET    /teams/{team_id}                - Get one
- PUT    /teams/{team_id}                - Update (admin)
- POST   /teams/{team_id}/members        - Add members (admin)
- DELETE /teams/{team_id}/members        - Remove members (admin)
- DELETE /teams/{team_id}                - Delete (admin)
"""

import time

import httpx
import pytest


def _unique(prefix: str) -> str:
    return f"{prefix}_{int(time.time() * 1000)}"


@pytest.fixture
def teams_org(api_server, api_base):
    """Create an org + admin + one volunteer; return authed clients + ids."""
    marker = _unique("teams_org")
    org_id = marker
    admin_email = f"admin_{marker}@test.com"
    vol_email = f"vol_{marker}@test.com"

    bootstrap = httpx.Client()

    org_resp = bootstrap.post(
        f"{api_base}/organizations/",
        json={"id": org_id, "name": f"Teams Setup {marker}", "region": "US", "config": {}},
    )
    assert org_resp.status_code == 201, org_resp.text

    admin_resp = bootstrap.post(
        f"{api_base}/auth/signup",
        json={
            "org_id": org_id,
            "name": "Team Admin",
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
            "name": "Team Volunteer",
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


def _create_team(client: httpx.Client, api_base: str, org_id: str, name_suffix: str = "") -> dict:
    """Helper: POST /teams/ and return the response body."""
    team_id = _unique(f"team_{name_suffix}") if name_suffix else _unique("team")
    resp = client.post(
        f"{api_base}/teams/",
        json={
            "id": team_id,
            "org_id": org_id,
            "name": f"Team {team_id}",
            "description": "Integration test team",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


class TestCreateTeam:
    """POST /teams/ — admin-only creation."""

    def test_create_success(self, teams_org):
        data = teams_org
        team = _create_team(data["admin_client"], data["api_base"], data["org_id"])
        assert team["org_id"] == data["org_id"]
        assert team["member_count"] == 0
        assert team["name"].startswith("Team ")

    def test_create_with_initial_members(self, teams_org):
        data = teams_org
        team_id = _unique("team_with_members")
        resp = data["admin_client"].post(
            f"{data['api_base']}/teams/",
            json={
                "id": team_id,
                "org_id": data["org_id"],
                "name": "Team With Members",
                "member_ids": [data["vol_id"]],
            },
        )
        assert resp.status_code == 201, resp.text
        assert resp.json()["member_count"] == 1

    def test_create_requires_admin(self, teams_org):
        data = teams_org
        team_id = _unique("team_forbidden")
        resp = data["vol_client"].post(
            f"{data['api_base']}/teams/",
            json={
                "id": team_id,
                "org_id": data["org_id"],
                "name": "Nope",
            },
        )
        assert resp.status_code == 403

    def test_create_missing_org_returns_404(self, teams_org):
        data = teams_org
        resp = data["admin_client"].post(
            f"{data['api_base']}/teams/",
            json={
                "id": _unique("orphan_team"),
                "org_id": f"nonexistent_{int(time.time())}",
                "name": "Orphan",
            },
        )
        assert resp.status_code == 404

    def test_create_duplicate_id_rejected(self, teams_org):
        data = teams_org
        team = _create_team(data["admin_client"], data["api_base"], data["org_id"])

        resp = data["admin_client"].post(
            f"{data['api_base']}/teams/",
            json={
                "id": team["id"],
                "org_id": data["org_id"],
                "name": "Duplicate",
            },
        )
        assert resp.status_code == 409


class TestListAndGetTeams:
    """GET /teams/ and GET /teams/{id} — read paths."""

    def test_list_envelope_and_defaults(self, teams_org):
        data = teams_org
        _create_team(data["admin_client"], data["api_base"], data["org_id"])

        resp = data["admin_client"].get(f"{data['api_base']}/teams/")
        assert resp.status_code == 200
        body = resp.json()
        assert set(body.keys()) >= {"items", "total", "limit", "offset"}
        # Default is caller's org
        assert all(t["org_id"] == data["org_id"] for t in body["items"])

    def test_list_q_filter(self, teams_org):
        data = teams_org
        # Team A carries the marker in its name; Team B does not.
        marker = _unique("QSEARCH")
        team_a_id = f"a_{marker}"
        team_b_id = f"b_{marker}"
        data["admin_client"].post(
            f"{data['api_base']}/teams/",
            json={
                "id": team_a_id,
                "org_id": data["org_id"],
                "name": f"Alpha {marker}",
            },
        )
        data["admin_client"].post(
            f"{data['api_base']}/teams/",
            json={
                "id": team_b_id,
                "org_id": data["org_id"],
                "name": "Beta Unmatched",
            },
        )

        resp = data["admin_client"].get(
            f"{data['api_base']}/teams/",
            params={"org_id": data["org_id"], "q": marker},
        )
        assert resp.status_code == 200
        returned = {t["id"] for t in resp.json()["items"]}
        assert team_a_id in returned
        assert team_b_id not in returned

    def test_get_existing(self, teams_org):
        data = teams_org
        team = _create_team(data["admin_client"], data["api_base"], data["org_id"])

        resp = data["admin_client"].get(f"{data['api_base']}/teams/{team['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == team["id"]

    def test_get_missing_returns_404(self, teams_org):
        data = teams_org
        resp = data["admin_client"].get(f"{data['api_base']}/teams/nope_{int(time.time())}")
        assert resp.status_code == 404


class TestUpdateTeam:
    """PUT /teams/{id} — admin-only update."""

    def test_update_name_and_description(self, teams_org):
        data = teams_org
        team = _create_team(data["admin_client"], data["api_base"], data["org_id"])

        resp = data["admin_client"].put(
            f"{data['api_base']}/teams/{team['id']}",
            json={"name": "Renamed", "description": "New desc"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["name"] == "Renamed"
        assert body["description"] == "New desc"

    def test_update_requires_admin(self, teams_org):
        data = teams_org
        team = _create_team(data["admin_client"], data["api_base"], data["org_id"])

        resp = data["vol_client"].put(
            f"{data['api_base']}/teams/{team['id']}",
            json={"name": "wont work"},
        )
        assert resp.status_code == 403


class TestTeamMembership:
    """POST + DELETE /teams/{id}/members — admin membership management."""

    def test_add_member(self, teams_org):
        data = teams_org
        team = _create_team(data["admin_client"], data["api_base"], data["org_id"])

        resp = data["admin_client"].post(
            f"{data['api_base']}/teams/{team['id']}/members",
            json={"person_ids": [data["vol_id"]]},
        )
        assert resp.status_code == 204, resp.text

        # member_count now 1
        get_resp = data["admin_client"].get(f"{data['api_base']}/teams/{team['id']}")
        assert get_resp.status_code == 200
        assert get_resp.json()["member_count"] == 1

    def test_add_member_idempotent(self, teams_org):
        data = teams_org
        team = _create_team(data["admin_client"], data["api_base"], data["org_id"])

        first = data["admin_client"].post(
            f"{data['api_base']}/teams/{team['id']}/members",
            json={"person_ids": [data["vol_id"]]},
        )
        assert first.status_code == 204

        second = data["admin_client"].post(
            f"{data['api_base']}/teams/{team['id']}/members",
            json={"person_ids": [data["vol_id"]]},
        )
        assert second.status_code == 204

        get_resp = data["admin_client"].get(f"{data['api_base']}/teams/{team['id']}")
        assert get_resp.json()["member_count"] == 1

    def test_remove_member(self, teams_org):
        data = teams_org
        team = _create_team(data["admin_client"], data["api_base"], data["org_id"])

        data["admin_client"].post(
            f"{data['api_base']}/teams/{team['id']}/members",
            json={"person_ids": [data["vol_id"]]},
        )

        resp = data["admin_client"].request(
            "DELETE",
            f"{data['api_base']}/teams/{team['id']}/members",
            json={"person_ids": [data["vol_id"]]},
        )
        assert resp.status_code == 204, resp.text

        get_resp = data["admin_client"].get(f"{data['api_base']}/teams/{team['id']}")
        assert get_resp.json()["member_count"] == 0

    def test_add_member_nonexistent_person_404(self, teams_org):
        data = teams_org
        team = _create_team(data["admin_client"], data["api_base"], data["org_id"])

        resp = data["admin_client"].post(
            f"{data['api_base']}/teams/{team['id']}/members",
            json={"person_ids": [f"ghost_{int(time.time())}"]},
        )
        assert resp.status_code == 404

    def test_add_members_requires_admin(self, teams_org):
        data = teams_org
        team = _create_team(data["admin_client"], data["api_base"], data["org_id"])

        resp = data["vol_client"].post(
            f"{data['api_base']}/teams/{team['id']}/members",
            json={"person_ids": [data["vol_id"]]},
        )
        assert resp.status_code == 403


class TestDeleteTeam:
    """DELETE /teams/{id}."""

    def test_delete_removes_team(self, teams_org):
        data = teams_org
        team = _create_team(data["admin_client"], data["api_base"], data["org_id"])

        resp = data["admin_client"].delete(f"{data['api_base']}/teams/{team['id']}")
        assert resp.status_code == 204

        follow = data["admin_client"].get(f"{data['api_base']}/teams/{team['id']}")
        assert follow.status_code == 404

    def test_delete_requires_admin(self, teams_org):
        data = teams_org
        team = _create_team(data["admin_client"], data["api_base"], data["org_id"])

        resp = data["vol_client"].delete(f"{data['api_base']}/teams/{team['id']}")
        assert resp.status_code == 403


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
