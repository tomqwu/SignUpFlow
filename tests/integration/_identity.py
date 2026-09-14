"""Real-HTTP identity builders that follow production onboarding contracts."""

from __future__ import annotations

import httpx


def bootstrap_admin(
    client: httpx.Client,
    api_base: str,
    *,
    org_id: str,
    org_name: str,
    name: str,
    email: str,
    password: str,
    region: str | None = None,
) -> dict:
    response = client.post(
        f"{api_base}/auth/signup",
        json={
            "org_id": org_id,
            "org_name": org_name,
            "region": region,
            "name": name,
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def invite_member(
    client: httpx.Client,
    api_base: str,
    *,
    org_id: str,
    admin_token: str,
    name: str,
    email: str,
    password: str,
    roles: list[str] | None = None,
) -> dict:
    invitation = client.post(
        f"{api_base}/invitations",
        params={"org_id": org_id},
        json={"name": name, "email": email, "roles": roles or ["volunteer"]},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert invitation.status_code == 201, invitation.text
    accepted = client.post(
        f"{api_base}/invitations/{invitation.json()['token']}/accept",
        json={"password": password, "timezone": "UTC"},
    )
    assert accepted.status_code == 201, accepted.text
    return accepted.json()
