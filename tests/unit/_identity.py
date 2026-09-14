"""Identity setup helpers for endpoint-focused unit tests."""

from fastapi.testclient import TestClient
from httpx import Response


def bootstrap_organization(client: TestClient, *, json: dict) -> Response:
    """Create an organization and its first admin through atomic signup."""
    org_id = json.get("id", "")
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "org_id": org_id,
            "org_name": json.get("name"),
            "region": json.get("region"),
            "name": "Test Owner",
            "email": f"owner-{org_id or 'invalid'}@example.com",
            "password": "OwnerPass1!",
        },
    )
    if response.status_code == 201:
        client.headers["X-Test-Actor-Org"] = org_id
    return response
