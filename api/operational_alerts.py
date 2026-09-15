"""Bounded operational signal state with injectable alert delivery."""

from __future__ import annotations

import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from threading import Lock

from api.logging_config import logger


@dataclass(frozen=True)
class AlertRule:
    """Declare when one fixed operational signal becomes actionable."""

    failure_threshold: int
    runbook: str

    def __post_init__(self) -> None:
        if self.failure_threshold < 1:
            raise ValueError("failure_threshold must be at least one")
        if not self.runbook.strip():
            raise ValueError("runbook must not be empty")


@dataclass(frozen=True)
class AlertEvent:
    """One triggered or recovered bounded operational signal."""

    signal: str
    state: str
    failure_count: int
    environment: str
    release_sha: str
    runbook: str


AlertSink = Callable[[AlertEvent], None]


class LoggingAlertSink:
    """Emit local alert state without claiming external delivery."""

    def __call__(self, event: AlertEvent) -> None:
        logger.warning(
            "operational.signal",
            extra={
                "event": "operational.signal",
                "signal": event.signal,
                "alert_state": event.state,
                "failure_count": event.failure_count,
                "runbook": event.runbook,
            },
        )


class OperationalMonitor:
    """Track consecutive failures and emit one trigger plus one recovery."""

    def __init__(
        self,
        *,
        rules: Mapping[str, AlertRule],
        sink: AlertSink,
        environment: str,
        release_sha: str,
    ) -> None:
        self._rules = dict(rules)
        self._sink = sink
        self._environment = environment or "unknown"
        self._release_sha = release_sha or "unknown"
        self._failure_counts = {name: 0 for name in rules}
        self._active = {name: False for name in rules}
        self._lock = Lock()

    def record(self, signal: str, *, healthy: bool) -> None:
        """Record one fixed signal without accepting unbounded labels or details."""
        if signal not in self._rules:
            raise ValueError(f"Unknown operational signal: {signal}")

        event: AlertEvent | None = None
        with self._lock:
            rule = self._rules[signal]
            if healthy:
                if self._active[signal]:
                    event = self._event(signal, "recovered", 0, rule)
                self._failure_counts[signal] = 0
                self._active[signal] = False
            else:
                self._failure_counts[signal] += 1
                count = self._failure_counts[signal]
                if count >= rule.failure_threshold and not self._active[signal]:
                    self._active[signal] = True
                    event = self._event(signal, "triggered", count, rule)

        if event is not None:
            self._sink(event)

    def _event(self, signal: str, state: str, failure_count: int, rule: AlertRule) -> AlertEvent:
        return AlertEvent(
            signal=signal,
            state=state,
            failure_count=failure_count,
            environment=self._environment,
            release_sha=self._release_sha,
            runbook=rule.runbook,
        )


def _positive_int(name: str, values: Mapping[str, str], default: int) -> int:
    raw = values.get(name, str(default))
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if value < 1:
        raise ValueError(f"{name} must be at least one")
    return value


def build_default_monitor(
    environ: Mapping[str, str] | None = None, *, sink: AlertSink | None = None
) -> OperationalMonitor:
    """Build local signal rules from bounded production settings."""
    values = os.environ if environ is None else environ
    threshold = _positive_int("READINESS_FAILURE_ALERT_THRESHOLD", values, 3)
    return OperationalMonitor(
        rules={
            "database.readiness": AlertRule(
                failure_threshold=threshold,
                runbook="docs/RUNBOOK.md#database-readiness",
            ),
            "notification.queue": AlertRule(
                failure_threshold=3,
                runbook="docs/RUNBOOK.md#notification-queue",
            ),
            "backup.freshness": AlertRule(
                failure_threshold=1,
                runbook="docs/RUNBOOK.md#backup-freshness",
            ),
        },
        sink=sink or LoggingAlertSink(),
        environment=values.get("ENVIRONMENT", "development"),
        release_sha=values.get("RELEASE_SHA", "unknown"),
    )


monitor = build_default_monitor()


def record_operational_signal(signal: str, *, healthy: bool) -> None:
    """Record a signal against the process-local monitor."""
    monitor.record(signal, healthy=healthy)
