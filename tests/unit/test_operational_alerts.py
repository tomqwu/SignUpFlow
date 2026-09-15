"""Operational signal thresholds must alert once and report recovery."""

import pytest

from api.operational_alerts import AlertRule, OperationalMonitor, build_default_monitor


def test_consecutive_failures_trigger_once_and_recovery_clears_alert():
    events = []
    monitor = OperationalMonitor(
        rules={
            "database.readiness": AlertRule(
                failure_threshold=3,
                runbook="docs/RUNBOOK.md#database-readiness",
            )
        },
        sink=events.append,
        environment="staging",
        release_sha="abc123",
    )

    monitor.record("database.readiness", healthy=False)
    monitor.record("database.readiness", healthy=False)
    assert events == []

    monitor.record("database.readiness", healthy=False)
    monitor.record("database.readiness", healthy=False)
    assert [event.state for event in events] == ["triggered"]
    assert events[0].failure_count == 3
    assert events[0].environment == "staging"
    assert events[0].release_sha == "abc123"
    assert events[0].runbook == "docs/RUNBOOK.md#database-readiness"

    monitor.record("database.readiness", healthy=True)
    monitor.record("database.readiness", healthy=True)
    assert [event.state for event in events] == ["triggered", "recovered"]
    assert events[-1].failure_count == 0


def test_unknown_unbounded_signal_is_rejected():
    monitor = OperationalMonitor(
        rules={
            "database.readiness": AlertRule(
                failure_threshold=1,
                runbook="docs/RUNBOOK.md#database-readiness",
            )
        },
        sink=lambda _event: None,
        environment="test",
        release_sha="test",
    )

    with pytest.raises(ValueError, match="Unknown operational signal"):
        monitor.record("person.private@example.com", healthy=False)


def test_rule_rejects_invalid_threshold_or_runbook():
    with pytest.raises(ValueError, match="failure_threshold"):
        AlertRule(failure_threshold=0, runbook="docs/RUNBOOK.md#database-readiness")
    with pytest.raises(ValueError, match="runbook"):
        AlertRule(failure_threshold=1, runbook="")


@pytest.mark.parametrize(
    ("signal", "failures"),
    [("notification.queue", 3), ("backup.freshness", 1)],
)
def test_default_queue_and_backup_rules_trigger_and_recover(signal, failures):
    events = []
    monitor = build_default_monitor(
        {
            "ENVIRONMENT": "test",
            "RELEASE_SHA": "b" * 40,
            "READINESS_FAILURE_ALERT_THRESHOLD": "3",
        },
        sink=events.append,
    )

    for _ in range(failures):
        monitor.record(signal, healthy=False)
    monitor.record(signal, healthy=True)

    assert [event.state for event in events] == ["triggered", "recovered"]
    assert all(event.signal == signal for event in events)
    assert all(event.runbook.startswith("docs/RUNBOOK.md#") for event in events)
