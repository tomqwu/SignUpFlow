#!/usr/bin/env python3
"""Run a provider-free Basketball workflow against a local SignUpFlow API."""

from __future__ import annotations

import argparse
import os
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, cast
from urllib.parse import urlparse

import httpx

ROLES = (
    "point_guard",
    "shooting_guard",
    "small_forward",
    "power_forward",
    "center",
    "coach",
    "scorekeeper",
)


def _expect(response: Any, status_code: int) -> dict[str, Any]:
    if response.status_code != status_code:
        raise RuntimeError(
            f"{response.request.method} {response.request.url.path} returned "
            f"{response.status_code}: {response.text}"
        )
    return cast(dict[str, Any], response.json())


def run_workflow(client: Any, *, suffix: str | None = None) -> dict[str, Any]:
    """Create and publish one complete Basketball event through canonical routes."""
    suffix = suffix or uuid.uuid4().hex[:8]
    org_id = f"riverside-basketball-{suffix}"
    password = "LocalExample123!"

    health = _expect(client.get("/health"), 200)
    if health.get("status") != "healthy":
        raise RuntimeError(f"API health is not healthy: {health}")

    owner = _expect(
        client.post(
            "/api/v1/auth/signup",
            json={
                "org_id": org_id,
                "org_name": "Riverside Basketball local example",
                "region": "CA-ON",
                "name": "Local team manager",
                "email": f"manager-{suffix}@basketball.example",
                "password": password,
                "timezone": "America/Toronto",
            },
        ),
        201,
    )
    headers = {"Authorization": f"Bearer {owner['token']}"}

    for index, role in enumerate(ROLES, start=1):
        invitation = _expect(
            client.post(
                f"/api/v1/invitations?org_id={org_id}",
                headers=headers,
                json={
                    "name": role.replace("_", " ").title(),
                    "email": f"member-{index}-{suffix}@basketball.example",
                    "roles": ["volunteer", role],
                },
            ),
            201,
        )
        _expect(
            client.post(
                f"/api/v1/invitations/{invitation['token']}/accept",
                json={"password": password, "timezone": "America/Toronto"},
            ),
            201,
        )

    start = datetime.now(UTC).replace(microsecond=0) + timedelta(days=14)
    _expect(
        client.post(
            "/api/v1/events/",
            headers=headers,
            json={
                "id": f"basketball-game-{suffix}",
                "org_id": org_id,
                "type": "Basketball game",
                "start_time": start.isoformat(),
                "end_time": (start + timedelta(hours=2)).isoformat(),
                "extra_data": {"role_counts": {role: 1 for role in ROLES}},
            },
        ),
        201,
    )

    solution = _expect(
        client.post(
            "/api/v1/solver/solve",
            headers=headers,
            json={
                "org_id": org_id,
                "from_date": start.date().isoformat(),
                "to_date": start.date().isoformat(),
                "mode": "strict",
                "change_min": False,
            },
        ),
        200,
    )
    published = _expect(
        client.post(f"/api/v1/solutions/{solution['solution_id']}/publish", headers=headers),
        200,
    )

    return {
        "org_id": org_id,
        "solution_id": solution["solution_id"],
        "assignment_count": solution["assignment_count"],
        "published": published["is_published"],
    }


def _local_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or parsed.hostname not in {
        "localhost",
        "127.0.0.1",
        "::1",
    }:
        raise argparse.ArgumentTypeError("Use an owned loopback SignUpFlow server only")
    return value.rstrip("/")


def main() -> None:
    """Run the example against an explicitly local API endpoint."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url",
        type=_local_url,
        default=_local_url(os.getenv("SIGNUPFLOW_API_URL", "http://127.0.0.1:8000")),
    )
    args = parser.parse_args()

    with httpx.Client(base_url=args.base_url, timeout=30.0) as client:
        result = run_workflow(client)

    print("Published local Basketball example")
    print(f"Organization: {result['org_id']}")
    print(f"Solution: {result['solution_id']}")
    print(f"Event assignments: {result['assignment_count']}")


if __name__ == "__main__":
    main()
