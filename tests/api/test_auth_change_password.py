"""Marathon P1.2 — authenticated self-service password change."""

from __future__ import annotations

from tests.api.conftest import auth_headers, seed_org, seed_user


def _setup(client, org, email):
    seed_org(client, org)
    seed_user(client, org, email=email, name="U", password="OldPass1!")
    return auth_headers(client, email, "OldPass1!")


def test_change_password_happy_path(client, db):
    h = _setup(client, "cp_o1", "u1@cp.org")
    r = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "OldPass1!", "new_password": "NewPass2!"},
        headers=h,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["token"] and body["person_id"]

    # Old password rejected, new password accepted.
    old = client.post("/api/v1/auth/login", json={"email": "u1@cp.org", "password": "OldPass1!"})
    assert old.status_code == 401
    new = client.post("/api/v1/auth/login", json={"email": "u1@cp.org", "password": "NewPass2!"})
    assert new.status_code == 200


def test_change_password_wrong_current_rejected(client, db):
    h = _setup(client, "cp_o2", "u2@cp.org")
    r = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "WRONG", "new_password": "NewPass2!"},
        headers=h,
    )
    assert r.status_code == 400
    # Original password still valid.
    assert (
        client.post(
            "/api/v1/auth/login", json={"email": "u2@cp.org", "password": "OldPass1!"}
        ).status_code
        == 200
    )


def test_change_password_requires_auth(client, db):
    r = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "x", "new_password": "yyyyyy"},
    )
    assert r.status_code in (401, 403)


def test_change_password_min_length_enforced(client, db):
    h = _setup(client, "cp_o3", "u3@cp.org")
    r = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "OldPass1!", "new_password": "123"},
        headers=h,
    )
    assert r.status_code == 422  # pydantic min_length=6
