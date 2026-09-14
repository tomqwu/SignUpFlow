"""Safety and startup contracts for the owned PostgreSQL validation runner."""

from unittest.mock import patch

import pytest

import api.database
from scripts.run_postgres_validation import (
    OWNERSHIP_LABEL,
    PostgresTestTarget,
    _junit_counts,
    parse_loopback_port,
    verify_owned_container,
)


def test_postgres_target_is_ephemeral_loopback_and_uniquely_owned() -> None:
    target = PostgresTestTarget(run_id="a1b2c3d4", password="local-only-password")

    assert target.container_name == "signupflow-pgtest-a1b2c3d4"
    assert target.database_name == "signupflow_test_a1b2c3d4"
    command = target.docker_run_command()
    assert command[:3] == ["docker", "run", "--detach"]
    assert "--rm" in command
    assert ["--publish", "127.0.0.1::5432"] == command[
        command.index("--publish") : command.index("--publish") + 2
    ]
    assert "--tmpfs" in command
    assert not any("/Users/" in value or ":/var/lib/postgresql/data" in value for value in command)
    assert f"{OWNERSHIP_LABEL}=a1b2c3d4" in command
    assert command[-1] == "postgres:16-alpine"


@pytest.mark.parametrize(
    "raw",
    [
        "0.0.0.0:5432",
        "192.0.2.10:5432",
        "localhost:not-a-port",
        "5432",
    ],
)
def test_postgres_port_parser_rejects_non_loopback_or_malformed_targets(raw: str) -> None:
    with pytest.raises(ValueError):
        parse_loopback_port(raw)


def test_postgres_port_parser_accepts_ipv4_and_ipv6_loopback() -> None:
    assert parse_loopback_port("127.0.0.1:55432") == 55432
    assert parse_loopback_port("[::1]:55433") == 55433


def test_container_cleanup_requires_matching_name_and_ownership_label() -> None:
    target = PostgresTestTarget(run_id="a1b2c3d4", password="local-only-password")
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


def test_non_sqlite_startup_verifies_migration_head_without_create_all(monkeypatch) -> None:
    monkeypatch.setattr(api.database, "DATABASE_URL", "postgresql://local/owned")

    with (
        patch.object(api.database, "_verify_migration_head") as verify_head,
        patch.object(api.database.Base.metadata, "create_all") as create_all,
    ):
        api.database.init_db()

    verify_head.assert_called_once_with(api.database.engine)
    create_all.assert_not_called()


def test_junit_counts_report_pass_fail_error_and_skip(tmp_path) -> None:
    junit = tmp_path / "junit.xml"
    junit.write_text(
        '<testsuites><testsuite tests="8" failures="1" errors="1" skipped="2" />' "</testsuites>",
        encoding="utf-8",
    )

    assert _junit_counts(junit) == {
        "tests": 8,
        "passed": 4,
        "failures": 1,
        "errors": 1,
        "skipped": 2,
    }
