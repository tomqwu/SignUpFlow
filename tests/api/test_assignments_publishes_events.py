"""Sprint 10 PR 10.4b — publisher wiring for assignment mutations.

Each mutation endpoint that touches an Assignment with a non-null
solution_id must publish to event_bus topic ``"solution:{solution_id}"``
after the DB commit. Manual (admin-created) assignments without a
solution_id are silent — they don't belong to any Solution Review
stream.

Tests pin:
- POST /assignments/{id}/accept publishes (solution_id != None).
- POST /assignments/{id}/decline publishes.
- POST /assignments/{id}/swap-request publishes.
- POST /events/{id}/assignments action=unassign publishes only when the
  deleted row had a solution_id (manual admin assignments are silent).
- POST /events/{id}/assignments action=assign never publishes — it
  always creates an Assignment with solution_id=None.

Auth: tests/api/conftest.py suppresses the root mock_authentication
fixture, so we use real JWTs via ``create_access_token``.
"""

from __future__ import annotations

import asyncio
from datetime import datetime

import pytest
from httpx import AsyncClient

from api.main import app
from api.models import Assignment, Event, Organization, Person, Solution
from api.security import create_access_token
from api.services import event_bus


def _seed(
    db,
    *,
    org_id: str,
    person_id: str,
    event_id: str,
    solution_id: int | None,
    assignment_status: str = "pending",
) -> tuple[Assignment, str]:
    """Seed org/person/event/solution/assignment. Returns (assignment, jwt)."""
    db.add(Organization(id=org_id, name="Test Org", region="Test"))
    db.add(
        Person(
            id=person_id,
            org_id=org_id,
            name="Test Volunteer",
            email=f"{person_id}@example.com",
            password_hash="$2b$12$dummy_hash",
            roles=["admin"],  # admin so unassign tests pass
        )
    )
    db.add(
        Event(
            id=event_id,
            org_id=org_id,
            type="service",
            start_time=datetime(2026, 6, 1, 10, 0),
            end_time=datetime(2026, 6, 1, 11, 0),
        )
    )
    if solution_id is not None:
        db.add(
            Solution(
                id=solution_id,
                org_id=org_id,
                hard_violations=0,
                soft_score=0.0,
                health_score=1.0,
            )
        )
    assignment = Assignment(
        solution_id=solution_id,
        event_id=event_id,
        person_id=person_id,
        role="volunteer",
        status=assignment_status,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment, create_access_token({"sub": person_id})


async def _spawn_listener(topic: str) -> tuple[asyncio.Task, list[dict]]:
    """Subscribe to ``topic`` and return (task, received_list).

    The task completes once one event has been collected.
    """
    received: list[dict] = []
    consumer_started = asyncio.Event()

    async def consumer():
        gen = event_bus.subscribe(topic)
        consumer_started.set()
        async for event in gen:
            received.append(event)
            return

    task = asyncio.create_task(consumer())
    await consumer_started.wait()
    # Yield once so subscribe() registers its queue before any publish.
    await asyncio.sleep(0)
    return task, received


async def _assert_silent(topic: str, *, settle: float = 0.05) -> None:
    """Subscribe to ``topic`` and assert nothing arrives within ``settle``."""
    received: list[dict] = []
    consumer_started = asyncio.Event()

    async def consumer():
        gen = event_bus.subscribe(topic)
        consumer_started.set()
        async for event in gen:
            received.append(event)
            return

    task = asyncio.create_task(consumer())
    await consumer_started.wait()
    await asyncio.sleep(0)
    try:
        await asyncio.wait_for(task, timeout=settle)
    except asyncio.TimeoutError:
        pass
    task.cancel()
    try:
        await task
    except (asyncio.CancelledError, StopAsyncIteration):
        pass
    assert received == [], f"unexpected event on {topic}: {received}"


@pytest.mark.asyncio
async def test_accept_publishes_event(db):
    assignment, jwt = _seed(
        db,
        org_id="pub_accept",
        person_id="pub_accept_user",
        event_id="evt_accept",
        solution_id=501,
    )
    task, received = await _spawn_listener(f"solution:{501}")

    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.post(
            f"/api/v1/assignments/{assignment.id}/accept",
            headers={"Authorization": f"Bearer {jwt}"},
        )
    assert resp.status_code == 200, resp.text

    await asyncio.wait_for(task, timeout=1.0)
    assert received == [
        {
            "type": "assignment.changed",
            "assignment_id": assignment.id,
            "solution_id": 501,
            "status": "confirmed",
        }
    ]


@pytest.mark.asyncio
async def test_decline_publishes_event(db):
    assignment, jwt = _seed(
        db,
        org_id="pub_decline",
        person_id="pub_decline_user",
        event_id="evt_decline",
        solution_id=502,
    )
    task, received = await _spawn_listener(f"solution:{502}")

    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.post(
            f"/api/v1/assignments/{assignment.id}/decline",
            headers={"Authorization": f"Bearer {jwt}"},
            json={"decline_reason": "out of town"},
        )
    assert resp.status_code == 200, resp.text

    await asyncio.wait_for(task, timeout=1.0)
    assert received == [
        {
            "type": "assignment.changed",
            "assignment_id": assignment.id,
            "solution_id": 502,
            "status": "declined",
        }
    ]


@pytest.mark.asyncio
async def test_swap_request_publishes_event(db):
    assignment, jwt = _seed(
        db,
        org_id="pub_swap",
        person_id="pub_swap_user",
        event_id="evt_swap",
        solution_id=503,
    )
    task, received = await _spawn_listener(f"solution:{503}")

    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.post(
            f"/api/v1/assignments/{assignment.id}/swap-request",
            headers={"Authorization": f"Bearer {jwt}"},
            json={"note": "need swap"},
        )
    assert resp.status_code == 200, resp.text

    await asyncio.wait_for(task, timeout=1.0)
    assert received == [
        {
            "type": "assignment.changed",
            "assignment_id": assignment.id,
            "solution_id": 503,
            "status": "swap_requested",
        }
    ]


@pytest.mark.asyncio
async def test_volunteer_self_service_silent_for_manual_assignment(db):
    """Volunteer accept on a manual (solution_id=None) assignment must
    not publish — there's no Solution Review stream to feed."""
    assignment, jwt = _seed(
        db,
        org_id="pub_manual",
        person_id="pub_manual_user",
        event_id="evt_manual",
        solution_id=None,
    )

    # The naive bug would format as "solution:None" — subscribe there to
    # catch any regression.
    async def hit():
        async with AsyncClient(app=app, base_url="http://test") as client:
            resp = await client.post(
                f"/api/v1/assignments/{assignment.id}/accept",
                headers={"Authorization": f"Bearer {jwt}"},
            )
        assert resp.status_code == 200, resp.text

    # Run the HTTP call concurrently with a brief subscriber wait.
    hit_task = asyncio.create_task(hit())
    await _assert_silent("solution:None", settle=0.1)
    await hit_task


@pytest.mark.asyncio
async def test_admin_unassign_publishes_when_from_solution(db):
    """Admin removing a solver-derived assignment must publish so the
    Solution Review stream invalidates."""
    assignment, jwt = _seed(
        db,
        org_id="pub_unassign",
        person_id="pub_unassign_admin",
        event_id="evt_unassign",
        solution_id=504,
    )
    task, received = await _spawn_listener(f"solution:{504}")

    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/events/evt_unassign/assignments",
            headers={"Authorization": f"Bearer {jwt}"},
            json={"action": "unassign", "person_id": "pub_unassign_admin"},
        )
    assert resp.status_code == 200, resp.text

    await asyncio.wait_for(task, timeout=1.0)
    assert received == [
        {
            "type": "assignment.changed",
            "assignment_id": assignment.id,
            "solution_id": 504,
            "status": "deleted",
        }
    ]


@pytest.mark.asyncio
async def test_admin_assign_does_not_publish(db):
    """Admin assign creates with solution_id=None — never publishes."""
    # Seed without an Assignment; we'll create one via the endpoint.
    db.add(Organization(id="pub_assign", name="Test Org", region="Test"))
    db.add(
        Person(
            id="pub_assign_admin",
            org_id="pub_assign",
            name="Admin",
            email="admin@pub_assign.test",
            password_hash="$2b$12$dummy_hash",
            roles=["admin"],
        )
    )
    db.add(
        Event(
            id="evt_admin_assign",
            org_id="pub_assign",
            type="service",
            start_time=datetime(2026, 6, 1, 10, 0),
            end_time=datetime(2026, 6, 1, 11, 0),
        )
    )
    db.commit()
    jwt = create_access_token({"sub": "pub_assign_admin"})

    async def hit():
        async with AsyncClient(app=app, base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/events/evt_admin_assign/assignments",
                headers={"Authorization": f"Bearer {jwt}"},
                json={
                    "action": "assign",
                    "person_id": "pub_assign_admin",
                    "role": "vol",
                },
            )
        assert resp.status_code == 200, resp.text

    hit_task = asyncio.create_task(hit())
    await _assert_silent("solution:None", settle=0.1)
    await hit_task
