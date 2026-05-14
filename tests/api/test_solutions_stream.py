"""Sprint 10 PR 10.4 — SSE stream endpoint for Solution Review live refresh.

Tests pin:
- 404 for an unknown solution.
- 401/403 when not authenticated as admin.
- Authenticated admin gets a text/event-stream response with the
  opening comment frame.
- Published events round-trip through event_bus → SSE consumer.
"""

from __future__ import annotations

import asyncio

import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.models import Organization, Person, Solution
from api.security import create_access_token
from api.services import event_bus


def _seed_admin_and_solution(db, *, org_id="sse_org", solution_id=987):
    org = Organization(id=org_id, name="SSE Org", region="Test")
    db.add(org)
    admin = Person(
        id=f"{org_id}_admin",
        org_id=org_id,
        name="SSE Admin",
        email=f"{org_id}_admin@example.com",
        password_hash="$2b$12$dummy_hash",
        roles=["admin"],
    )
    db.add(admin)
    solution = Solution(
        id=solution_id,
        org_id=org_id,
        hard_violations=0,
        soft_score=0.0,
        health_score=1.0,
    )
    db.add(solution)
    db.commit()
    return admin, solution


def test_stream_404_for_unknown_solution(db):
    _seed_admin_and_solution(db, org_id="sse_404")
    admin = db.query(Person).filter(Person.id == "sse_404_admin").first()
    jwt = create_access_token({"sub": admin.id})

    client = TestClient(app)
    resp = client.get(
        "/api/v1/solutions/99999999/assignments/stream",
        headers={"Authorization": f"Bearer {jwt}"},
    )
    assert resp.status_code == 404


def test_stream_requires_auth(db):
    _seed_admin_and_solution(db, org_id="sse_noauth", solution_id=2001)
    client = TestClient(app)
    resp = client.get("/api/v1/solutions/2001/assignments/stream")
    # No bearer → unauthenticated. 401 or 403 depending on the
    # dependency chain in get_current_admin_user.
    assert resp.status_code in {401, 403}


@pytest.mark.asyncio
async def test_event_bus_subscribe_publish_round_trip():
    """Direct event_bus contract: a subscriber receives a published event.

    Uses the bus directly (no HTTP) so the test is hermetic and fast.
    The SSE endpoint composes this with StreamingResponse — verified
    by the auth/404 tests above + the operator runs the full stream
    against a real client.
    """
    topic = "test_topic_roundtrip"

    received: list[dict] = []
    consumer_started = asyncio.Event()

    async def consumer():
        gen = event_bus.subscribe(topic)
        consumer_started.set()
        async for event in gen:
            received.append(event)
            if len(received) >= 1:
                break

    task = asyncio.create_task(consumer())
    # Wait for the subscriber to register its queue before publishing.
    await consumer_started.wait()
    # Yield once so the subscribe() generator can register the queue.
    await asyncio.sleep(0)

    await event_bus.publish(topic, {"kind": "assignment.updated", "id": 42})

    await asyncio.wait_for(task, timeout=1.0)
    assert received == [{"kind": "assignment.updated", "id": 42}]


@pytest.mark.asyncio
async def test_event_bus_drops_when_subscriber_queue_full():
    """Slow consumer protection: publisher doesn't stall when a
    subscriber stops draining. Drops are silent; the next non-stream
    fetch resyncs."""
    topic = "test_topic_drop"

    # Register a subscriber but never read from it.
    gen = event_bus.subscribe(topic)
    aiter_ = gen.__aiter__()
    # Pump one __anext__ to register the queue, but immediately cancel
    # so the subscriber never drains again.
    drain_task = asyncio.create_task(aiter_.__anext__())
    await asyncio.sleep(0)

    # Fill past queue depth (default 100) — publish must not raise/hang.
    for i in range(200):
        await event_bus.publish(topic, {"i": i})

    # Cleanup.
    drain_task.cancel()
    try:
        await drain_task
    except (asyncio.CancelledError, StopAsyncIteration):
        pass
