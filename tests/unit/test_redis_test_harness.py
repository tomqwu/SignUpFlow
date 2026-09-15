"""Safety contracts for the owned Redis validation runner."""

import pytest

from scripts.run_redis_validation import (
    OWNERSHIP_LABEL,
    RedisTestTarget,
    parse_loopback_port,
    verify_owned_container,
)


def test_redis_target_is_ephemeral_loopback_and_uniquely_owned() -> None:
    target = RedisTestTarget(run_id="a1b2c3d4", password="local-only-password")

    assert target.container_name == "signupflow-redistest-a1b2c3d4"
    command = target.docker_run_command()
    assert command[:3] == ["docker", "run", "--detach"]
    assert "--rm" in command
    assert ["--publish", "127.0.0.1::6379"] == command[
        command.index("--publish") : command.index("--publish") + 2
    ]
    assert "--tmpfs" in command
    assert not any("/Users/" in value or ":/data" in value for value in command)
    assert f"{OWNERSHIP_LABEL}=a1b2c3d4" in command
    assert "--requirepass" in command


@pytest.mark.parametrize("raw", ["0.0.0.0:6379", "192.0.2.10:6379", "6379", "localhost:x"])
def test_redis_port_parser_rejects_non_loopback_or_malformed_targets(raw: str) -> None:
    with pytest.raises(ValueError):
        parse_loopback_port(raw)


def test_redis_port_parser_accepts_ipv4_and_ipv6_loopback() -> None:
    assert parse_loopback_port("127.0.0.1:56379") == 56379
    assert parse_loopback_port("[::1]:56380") == 56380


def test_redis_cleanup_requires_matching_name_and_ownership_label() -> None:
    target = RedisTestTarget(run_id="a1b2c3d4", password="local-only-password")
    inspect = [
        {
            "Name": f"/{target.container_name}",
            "Config": {"Labels": {OWNERSHIP_LABEL: target.run_id}},
        }
    ]
    verify_owned_container(target, inspect)

    inspect[0]["Config"]["Labels"][OWNERSHIP_LABEL] = "someone-else"
    with pytest.raises(RuntimeError, match="ownership"):
        verify_owned_container(target, inspect)
