"""Acceptance checks against the owned Redis test target."""

import asyncio
import os
import secrets

import pytest
from celery import Celery
from kombu.exceptions import OperationalError
from redis import Redis

from api.services.event_bus import RedisEventBus, solution_topic
from api.utils.rate_limiter import RedisRateLimiter


@pytest.fixture
def redis_target():
    url = os.getenv("SIGNUPFLOW_REDIS_TEST_URL")
    if not url:
        pytest.fail("SIGNUPFLOW_REDIS_TEST_URL is required; use scripts/run_redis_validation.py")
    cleanup_client = Redis.from_url(url, decode_responses=True)
    namespace = f"signupflow:rate-limit-test:{secrets.token_hex(8)}"
    yield url, namespace
    keys = list(cleanup_client.scan_iter(match=f"*{namespace}*"))
    if keys:
        cleanup_client.delete(*keys)
    cleanup_client.close()


def test_two_workers_share_one_atomic_quota(redis_target) -> None:
    url, namespace = redis_target
    client_a = Redis.from_url(url, decode_responses=True)
    client_b = Redis.from_url(url, decode_responses=True)
    try:
        worker_a = RedisRateLimiter(client=client_a, namespace=namespace)
        worker_b = RedisRateLimiter(client=client_b, namespace=namespace)

        assert worker_a.is_allowed("login:198.51.100.10", max_requests=2, window_seconds=60)
        assert worker_b.is_allowed("login:198.51.100.10", max_requests=2, window_seconds=60)
        assert not worker_a.is_allowed("login:198.51.100.10", max_requests=2, window_seconds=60)
    finally:
        client_a.close()
        client_b.close()


def test_quota_keys_expire_and_hide_the_client_identifier(redis_target) -> None:
    url, namespace = redis_target
    client = Redis.from_url(url, decode_responses=True)
    try:
        limiter = RedisRateLimiter(client=client, namespace=namespace)

        assert limiter.is_allowed("signup:203.0.113.25", max_requests=1, window_seconds=2)

        keys = list(client.scan_iter(match=f"{namespace}:*"))
        assert len(keys) == 1
        assert "203.0.113.25" not in keys[0]
        ttl = client.ttl(keys[0])
        assert 0 < ttl <= 2
    finally:
        client.close()


@pytest.mark.asyncio
async def test_independent_workers_share_tenant_scoped_events(redis_target) -> None:
    url, namespace = redis_target
    worker_a = RedisEventBus(url=url, namespace=f"{namespace}:events")
    worker_b = RedisEventBus(url=url, namespace=f"{namespace}:events")
    church_topic = solution_topic("church-org", 42)
    basketball_topic = solution_topic("basketball-org", 42)

    church_stream = worker_b.subscribe(church_topic)
    basketball_stream = worker_b.subscribe(basketball_topic)
    church_next = asyncio.create_task(anext(church_stream))
    basketball_next = asyncio.create_task(anext(basketball_stream))
    await asyncio.sleep(0.1)

    assert await worker_a.publish(church_topic, {"type": "assignment.changed", "id": 7})
    assert await asyncio.wait_for(church_next, timeout=2) == {
        "type": "assignment.changed",
        "id": 7,
    }
    with pytest.raises(TimeoutError):
        await asyncio.wait_for(basketball_next, timeout=0.2)
    await church_stream.aclose()
    await basketball_stream.aclose()


def _broker_app(url: str, queue: str) -> Celery:
    app = Celery(f"signupflow-redis-acceptance-{secrets.token_hex(4)}", broker=url)
    app.conf.update(
        task_default_queue=queue,
        broker_connection_retry=False,
        broker_connection_retry_on_startup=False,
        broker_transport_options={
            "max_retries": 0,
            "socket_connect_timeout": 0.2,
            "socket_timeout": 0.2,
        },
    )
    return app


def test_celery_broker_outage_preserves_recoverability(redis_target) -> None:
    url, namespace = redis_target
    queue = f"{namespace}:notifications"
    unavailable_url = url.rsplit(":", 1)[0] + ":1/0"

    with pytest.raises(OperationalError):
        _broker_app(unavailable_url, queue).send_task(
            "signupflow.synthetic.notification",
            args=[41, "church-org"],
            queue=queue,
        )

    live_app = _broker_app(url, queue)
    result = live_app.send_task(
        "signupflow.synthetic.notification",
        args=[41, "church-org"],
        queue=queue,
    )
    client = Redis.from_url(url, decode_responses=True)
    try:
        assert result.id
        assert client.llen(queue) == 1
    finally:
        client.close()
