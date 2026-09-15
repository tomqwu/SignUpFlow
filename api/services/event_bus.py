"""Tenant-scoped refresh events for solution-review SSE consumers.

Development and tests use bounded in-process queues. Production uses Redis
pub/sub so a mutation handled by one API worker reaches subscribers on another.
Events remain refresh hints; reconnecting clients fetch authoritative state.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
from collections.abc import AsyncIterator
from typing import Any

from redis.asyncio import Redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)
_QUEUE_DEPTH = 100
_subscribers: dict[str, list[asyncio.Queue[dict[str, Any]]]] = {}
_lock = asyncio.Lock()


def solution_topic(org_id: str, solution_id: int | None) -> str:
    """Build a tenant-scoped logical topic without exposing the org in Redis."""
    org_digest = hashlib.sha256(org_id.encode("utf-8")).hexdigest()[:24]
    return f"org:{org_digest}:solution:{solution_id}"


class InProcessEventBus:
    """Bounded event fan-out for a single development/test process."""

    async def subscribe(self, topic: str) -> AsyncIterator[dict[str, Any]]:
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=_QUEUE_DEPTH)
        async with _lock:
            _subscribers.setdefault(topic, []).append(queue)
        try:
            while True:
                yield await queue.get()
        finally:
            async with _lock:
                queues = _subscribers.get(topic, [])
                if queue in queues:
                    queues.remove(queue)
                if not queues:
                    _subscribers.pop(topic, None)

    async def publish(self, topic: str, event: dict[str, Any]) -> bool:
        async with _lock:
            queues = list(_subscribers.get(topic, ()))
        for queue in queues:
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                continue
        return True


class RedisEventBus:
    """Independent Redis pub/sub connections for cross-worker refresh hints."""

    def __init__(self, *, url: str, namespace: str = "signupflow:events") -> None:
        if not url:
            raise ValueError("Redis event bus URL is required")
        self._url = url
        self._namespace = namespace

    def _channel(self, topic: str) -> str:
        digest = hashlib.sha256(topic.encode("utf-8")).hexdigest()
        return f"{self._namespace}:{digest}"

    def _client(self) -> Any:
        return Redis.from_url(
            self._url,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=5,
        )

    async def subscribe(self, topic: str) -> AsyncIterator[dict[str, Any]]:
        client = self._client()
        pubsub = client.pubsub(ignore_subscribe_messages=True)
        channel = self._channel(topic)
        try:
            await pubsub.subscribe(channel)
            async for message in pubsub.listen():
                if message.get("type") != "message":
                    continue
                try:
                    event = json.loads(message["data"])
                except (TypeError, json.JSONDecodeError):
                    logger.warning("Discarded malformed Redis refresh event")
                    continue
                if isinstance(event, dict):
                    yield event
        finally:
            try:
                await pubsub.unsubscribe(channel)
            except (OSError, RedisError):
                pass
            try:
                await pubsub.aclose()
            except (OSError, RedisError):
                pass
            try:
                await client.aclose()
            except (OSError, RedisError):
                pass

    async def publish(self, topic: str, event: dict[str, Any]) -> bool:
        client = self._client()
        try:
            await client.publish(
                self._channel(topic),
                json.dumps(event, separators=(",", ":"), sort_keys=True),
            )
        except (OSError, RedisError):
            logger.exception(
                "Redis refresh event publish failed; clients will refetch on reconnect"
            )
            return False
        finally:
            try:
                await client.aclose()
            except (OSError, RedisError):
                pass
        return True


_in_process_bus = InProcessEventBus()


def _configured_bus() -> InProcessEventBus | RedisEventBus:
    environment = os.getenv("ENVIRONMENT", "development").strip().lower()
    storage = os.getenv("EVENT_BUS_STORAGE", "").strip().lower()
    if storage != "redis" and environment != "production":
        return _in_process_bus
    url = os.getenv("EVENT_BUS_REDIS_URL") or os.getenv("REDIS_URL")
    if not url:
        raise RuntimeError("Redis event delivery requires EVENT_BUS_REDIS_URL or REDIS_URL")
    return RedisEventBus(url=url)


async def subscribe(topic: str) -> AsyncIterator[dict[str, Any]]:
    """Subscribe through the runtime-selected event backend."""
    async for event in _configured_bus().subscribe(topic):
        yield event


async def publish(topic: str, event: dict[str, Any]) -> bool:
    """Publish through the runtime-selected event backend."""
    return await _configured_bus().publish(topic, event)
