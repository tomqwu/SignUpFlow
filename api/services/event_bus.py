"""In-process pub/sub for SSE stream consumers.

Sprint 10 PR 10.4: the admin Solution Review needs live updates when
assignments change. Rather than reach for Redis pub/sub or full
WebSockets, we use a per-topic asyncio.Queue fan-out — light enough
for single-instance deployments, easy to swap for a real broker later.

A "topic" here is a string like ``"solution:{id}"``. Each subscriber
gets its own asyncio.Queue; publish() writes to every queue
registered against that topic at the time of the call. Slow consumers
drop on bounded queues (max 100 items per subscriber) to prevent
back-pressure leaking into the publisher.

Single-process scope: this works inside one uvicorn worker. With
``WORKERS=4`` (the documented default in CLAUDE.md), a publish from
worker A is invisible to a subscriber on worker B. That's an
acceptable trade-off for v1; the operator deploys with ``WORKERS=1``
for the staging smoke or accepts that some workers may miss live
updates. Sprint 11 can revisit with Redis pub/sub if needed.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any

# Per-topic list of subscriber queues. Each subscriber's queue is
# bounded — slow consumers drop, fast consumers don't.
_subscribers: dict[str, list[asyncio.Queue[dict[str, Any]]]] = {}
_lock = asyncio.Lock()

# Default per-subscriber queue depth. Picked to absorb a burst of
# rapid edits during a solution-review session without unbounded
# growth; tune via SUBSCRIBER_QUEUE_DEPTH env if needed.
_QUEUE_DEPTH = 100


async def subscribe(topic: str) -> AsyncIterator[dict[str, Any]]:
    """Async generator yielding events published to `topic` until the
    consumer disconnects. The consumer's queue is registered on entry
    and deregistered on cleanup so a disconnected SSE client doesn't
    accumulate.
    """
    queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=_QUEUE_DEPTH)
    async with _lock:
        _subscribers.setdefault(topic, []).append(queue)
    try:
        while True:
            event = await queue.get()
            yield event
    finally:
        async with _lock:
            queues = _subscribers.get(topic, [])
            if queue in queues:
                queues.remove(queue)
            if not queues:
                _subscribers.pop(topic, None)


async def publish(topic: str, event: dict[str, Any]) -> None:
    """Publish `event` to all current subscribers of `topic`. Drops on
    a full subscriber queue rather than block — `put_nowait` raises
    `asyncio.QueueFull` which we swallow so a single slow consumer
    can't stall the publisher (e.g., an assignment-update endpoint).
    """
    async with _lock:
        queues = list(_subscribers.get(topic, ()))
    for queue in queues:
        try:
            queue.put_nowait(event)
        except asyncio.QueueFull:
            # Slow consumer — silently drop. They'll resync on the
            # next non-stream fetch (the existing pull-to-refresh path).
            continue
