"""Pure guards for the opt-in production artifact validator."""

from __future__ import annotations

import pytest

from scripts.validate_production_artifact import (
    ArtifactTarget,
    parse_loopback_port,
    verify_owned_container,
    verify_owned_network,
)


def test_artifact_target_builds_private_owned_container_commands():
    target = ArtifactTarget(run_id="a1b2c3d4", source_sha="f" * 40, password="secret")

    postgres = target.postgres_command()
    redis = target.redis_command()

    assert "--publish" not in postgres
    assert "--publish" not in redis
    assert f"io.signupflow.artifact-run={target.run_id}" in postgres
    assert f"io.signupflow.artifact-run={target.run_id}" in redis
    assert target.network_name in postgres
    assert target.network_name in redis

    app = target.image_run_command(target.app_names[0], publish=True)
    assert "--read-only" in app
    assert [app[index + 1] for index, value in enumerate(app) if value == "--publish"] == [
        "127.0.0.1::8000"
    ]
    assert "--volume" not in app


def test_artifact_target_rejects_untrusted_identifiers():
    with pytest.raises(ValueError, match="run ID"):
        ArtifactTarget(run_id="../unsafe", source_sha="f" * 40, password="secret")
    with pytest.raises(ValueError, match="source SHA"):
        ArtifactTarget(run_id="a1b2c3d4", source_sha="main", password="secret")


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("127.0.0.1:49152", 49152), ("[::1]:49153", 49153)],
)
def test_parse_loopback_port_accepts_only_loopback(raw, expected):
    assert parse_loopback_port(raw) == expected


@pytest.mark.parametrize("raw", ["0.0.0.0:8000", "192.0.2.1:8000", "8000", ""])
def test_parse_loopback_port_rejects_non_loopback(raw):
    with pytest.raises(ValueError, match="loopback"):
        parse_loopback_port(raw)


def test_owned_container_requires_matching_name_and_label():
    target = ArtifactTarget(run_id="a1b2c3d4", source_sha="f" * 40, password="secret")
    record = {
        "Name": f"/{target.postgres_name}",
        "Config": {"Labels": {"io.signupflow.artifact-run": target.run_id}},
    }

    verify_owned_container(target, target.postgres_name, [record])
    record["Config"]["Labels"]["io.signupflow.artifact-run"] = "someone-else"
    with pytest.raises(RuntimeError, match="ownership"):
        verify_owned_container(target, target.postgres_name, [record])


def test_owned_network_requires_matching_name_and_label():
    target = ArtifactTarget(run_id="a1b2c3d4", source_sha="f" * 40, password="secret")
    record = {
        "Name": target.network_name,
        "Labels": {"io.signupflow.artifact-run": target.run_id},
    }

    verify_owned_network(target, [record])
    record["Name"] = "another-network"
    with pytest.raises(RuntimeError, match="name"):
        verify_owned_network(target, [record])
