"""Acceptance checks against the owned Redis test target."""

import os
import secrets

import pytest
from redis import Redis

from api.utils.rate_limiter import RedisRateLimiter


@pytest.fixture
def redis_target():
    url = os.getenv("SIGNUPFLOW_REDIS_TEST_URL")
    if not url:
        pytest.fail("SIGNUPFLOW_REDIS_TEST_URL is required; use scripts/run_redis_validation.py")
    client = Redis.from_url(url, decode_responses=True)
    namespace = f"signupflow:rate-limit-test:{secrets.token_hex(8)}"
    yield client, namespace
    keys = list(client.scan_iter(match=f"{namespace}:*"))
    if keys:
        client.delete(*keys)


def test_two_workers_share_one_atomic_quota(redis_target) -> None:
    client, namespace = redis_target
    worker_a = RedisRateLimiter(client=client, namespace=namespace)
    worker_b = RedisRateLimiter(client=client, namespace=namespace)

    assert worker_a.is_allowed("login:198.51.100.10", max_requests=2, window_seconds=60)
    assert worker_b.is_allowed("login:198.51.100.10", max_requests=2, window_seconds=60)
    assert not worker_a.is_allowed("login:198.51.100.10", max_requests=2, window_seconds=60)


def test_quota_keys_expire_and_hide_the_client_identifier(redis_target) -> None:
    client, namespace = redis_target
    limiter = RedisRateLimiter(client=client, namespace=namespace)

    assert limiter.is_allowed("signup:203.0.113.25", max_requests=1, window_seconds=2)

    keys = list(client.scan_iter(match=f"{namespace}:*"))
    assert len(keys) == 1
    assert "203.0.113.25" not in keys[0]
    ttl = client.ttl(keys[0])
    assert 0 < ttl <= 2
