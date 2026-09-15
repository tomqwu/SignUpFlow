"""Durable notification outbox state-machine tests."""

from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.models import (
    Assignment,
    Base,
    EmailFrequency,
    EmailPreference,
    Event,
    Notification,
    NotificationStatus,
    NotificationType,
    Organization,
    Person,
)
from api.services import notification_service
from api.services.notification_outbox import (
    claim_notification,
    complete_notification,
    due_notification_refs,
    fail_notification,
    mark_notification_uncertain,
)
from api.services.notification_service import enqueue_notification_ref
from api.tasks import notifications as notification_tasks
from api.timeutils import utcnow


@pytest.fixture
def outbox_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    session = factory()
    session.info["factory"] = factory
    session.add(Organization(id="outbox-org", name="Outbox Org"))
    session.add(
        Person(
            id="outbox-person",
            org_id="outbox-org",
            name="Outbox Person",
            email="outbox@example.test",
            roles=["volunteer"],
        )
    )
    session.commit()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _intent(outbox_db) -> Notification:
    notification = Notification(
        org_id="outbox-org",
        recipient_id="outbox-person",
        type="assignment",
        status=NotificationStatus.PENDING,
        delivery_key="outbox-operation",
    )
    outbox_db.add(notification)
    outbox_db.commit()
    outbox_db.refresh(notification)
    return notification


def _deliverable_intent(outbox_db) -> Notification:
    outbox_db.add(
        Event(
            id="outbox-event",
            org_id="outbox-org",
            type="Practice",
            start_time=datetime(2099, 1, 1, 10),
            end_time=datetime(2099, 1, 1, 11),
        )
    )
    outbox_db.flush()
    outbox_db.add(
        Assignment(
            event_id="outbox-event",
            person_id="outbox-person",
            role="coach",
            status="pending",
        )
    )
    outbox_db.add(
        EmailPreference(
            person_id="outbox-person",
            org_id="outbox-org",
            frequency=EmailFrequency.IMMEDIATE,
            enabled_types=[NotificationType.ASSIGNMENT],
            language="en",
            timezone="UTC",
            unsubscribe_token="local-test-token",
        )
    )
    notification = Notification(
        org_id="outbox-org",
        recipient_id="outbox-person",
        event_id="outbox-event",
        type=NotificationType.ASSIGNMENT,
        status=NotificationStatus.PENDING,
        delivery_key="deliverable-operation",
    )
    outbox_db.add(notification)
    outbox_db.commit()
    outbox_db.refresh(notification)
    return notification


def _task_database(outbox_db, monkeypatch):
    factory = outbox_db.info["factory"]

    def get_db():
        yield factory()

    monkeypatch.setattr(notification_tasks, "get_db", get_db)
    monkeypatch.setattr(notification_tasks.email_service, "enabled", True)
    return factory


def test_only_one_worker_claims_and_stale_lease_recovers(outbox_db) -> None:
    notification = _intent(outbox_db)
    now = utcnow()

    first = claim_notification(
        outbox_db,
        notification_id=notification.id,
        org_id="outbox-org",
        lease_token="worker-a",
        now=now,
        lease_seconds=30,
    )
    blocked = claim_notification(
        outbox_db,
        notification_id=notification.id,
        org_id="outbox-org",
        lease_token="worker-b",
        now=now + timedelta(seconds=10),
        lease_seconds=30,
    )
    recovered = claim_notification(
        outbox_db,
        notification_id=notification.id,
        org_id="outbox-org",
        lease_token="worker-b",
        now=now + timedelta(seconds=31),
        lease_seconds=30,
    )

    assert first is not None
    assert blocked is None
    assert recovered is not None
    assert recovered.delivery_attempts == 2
    assert recovered.delivery_lease_token == "worker-b"


def test_failures_back_off_then_surface_dead_letter(outbox_db) -> None:
    notification = _intent(outbox_db)
    now = utcnow()

    for attempt in range(1, 5):
        claimed = claim_notification(
            outbox_db,
            notification_id=notification.id,
            org_id="outbox-org",
            lease_token=f"worker-{attempt}",
            now=now,
        )
        assert claimed is not None
        failed = fail_notification(
            outbox_db,
            notification_id=notification.id,
            org_id="outbox-org",
            lease_token=f"worker-{attempt}",
            error="synthetic transport failure",
            now=now,
            max_attempts=4,
        )
        if attempt < 4:
            assert failed.status == NotificationStatus.RETRY
            assert failed.next_attempt_at is not None
            now = failed.next_attempt_at
        else:
            assert failed.status == NotificationStatus.DEAD_LETTER
            assert failed.next_attempt_at is None


def test_uncertain_provider_outcome_is_not_reported_as_delivered(outbox_db) -> None:
    notification = _intent(outbox_db)
    claim_notification(
        outbox_db,
        notification_id=notification.id,
        org_id="outbox-org",
        lease_token="worker-a",
    )

    uncertain = mark_notification_uncertain(
        outbox_db,
        notification_id=notification.id,
        org_id="outbox-org",
        lease_token="worker-a",
        error="provider accepted but local commit was not confirmed",
    )

    assert uncertain.status == NotificationStatus.UNCERTAIN
    assert uncertain.sent_at is None
    assert uncertain.delivery_lease_token is None


def test_completion_requires_the_current_lease(outbox_db) -> None:
    notification = _intent(outbox_db)
    claim_notification(
        outbox_db,
        notification_id=notification.id,
        org_id="outbox-org",
        lease_token="worker-a",
    )

    with pytest.raises(ValueError, match="lease"):
        complete_notification(
            outbox_db,
            notification_id=notification.id,
            org_id="outbox-org",
            lease_token="worker-b",
            message_id="message-1",
        )


def test_broker_enqueue_failure_keeps_committed_intent_pending(outbox_db, monkeypatch) -> None:
    notification = _intent(outbox_db)

    def unavailable(*args, **kwargs):
        raise RuntimeError("synthetic broker outage")

    monkeypatch.setattr("api.services.notification_service.send_email_task.delay", unavailable)

    assert not enqueue_notification_ref(notification.id, notification.org_id)
    outbox_db.expire_all()
    persisted = (
        outbox_db.query(Notification)
        .filter(Notification.id == notification.id, Notification.org_id == "outbox-org")
        .one()
    )
    assert persisted.status == NotificationStatus.PENDING
    assert persisted.delivery_attempts == 0


def test_rolled_back_intent_is_neither_persisted_nor_dispatched(outbox_db, monkeypatch) -> None:
    dispatched: list[tuple[int, str]] = []
    monkeypatch.setattr(
        notification_service.send_email_task,
        "delay",
        lambda notification_id, org_id: dispatched.append((notification_id, org_id)),
    )

    notification = notification_service.create_notification(
        recipient_id="outbox-person",
        org_id="outbox-org",
        notification_type=NotificationType.UPDATE,
        delivery_key="rolled-back-operation",
        db=outbox_db,
    )
    assert notification is not None
    notification_id = notification.id

    outbox_db.rollback()

    assert outbox_db.query(Notification).filter(Notification.id == notification_id).count() == 0
    assert dispatched == []


def test_broker_recovery_can_enqueue_the_same_committed_intent(outbox_db, monkeypatch) -> None:
    notification = _intent(outbox_db)
    attempts = iter([RuntimeError("offline"), None])

    def enqueue(*args, **kwargs):
        result = next(attempts)
        if result:
            raise result

    monkeypatch.setattr(notification_service.send_email_task, "delay", enqueue)

    assert not enqueue_notification_ref(notification.id, notification.org_id)
    assert enqueue_notification_ref(notification.id, notification.org_id)


def test_disabled_delivery_does_not_claim_or_dispatch_due_intent(outbox_db, monkeypatch) -> None:
    notification = _intent(outbox_db)
    factory = outbox_db.info["factory"]
    monkeypatch.setattr(notification_tasks, "get_db", lambda: iter([factory()]))
    monkeypatch.setattr(notification_tasks.email_service, "enabled", False)
    monkeypatch.setattr(notification_tasks.email_service, "capture_dir", None)
    monkeypatch.setattr(
        notification_tasks.send_email_task,
        "delay",
        lambda *args: pytest.fail("disabled delivery must not enter the broker"),
    )

    assert notification_tasks.send_email_task.run(notification.id, "outbox-org") == {
        "status": "disabled"
    }
    assert notification_tasks.dispatch_due_notifications.run() == {
        "due": 0,
        "queued": 0,
        "unavailable": 0,
        "delivery": "disabled",
    }
    outbox_db.expire_all()
    persisted = outbox_db.query(Notification).filter(Notification.id == notification.id).one()
    assert persisted.status == NotificationStatus.PENDING
    assert persisted.delivery_attempts == 0


def test_due_scan_excludes_future_retry_and_terminal_rows(outbox_db) -> None:
    due = _intent(outbox_db)
    due.delivery_key = "due"
    legacy_failed = Notification(
        org_id="outbox-org",
        recipient_id="outbox-person",
        type=NotificationType.UPDATE,
        status=NotificationStatus.FAILED,
        delivery_key="legacy-failed",
    )
    stale = Notification(
        org_id="outbox-org",
        recipient_id="outbox-person",
        type=NotificationType.UPDATE,
        status=NotificationStatus.SENDING,
        delivery_key="stale",
        delivery_lease_token="stopped-worker",
        delivery_lease_expires_at=utcnow() - timedelta(seconds=1),
    )
    future = Notification(
        org_id="outbox-org",
        recipient_id="outbox-person",
        type=NotificationType.UPDATE,
        status=NotificationStatus.RETRY,
        delivery_key="future",
        next_attempt_at=utcnow() + timedelta(hours=1),
    )
    terminal = Notification(
        org_id="outbox-org",
        recipient_id="outbox-person",
        type=NotificationType.UPDATE,
        status=NotificationStatus.DEAD_LETTER,
        delivery_key="terminal",
    )
    outbox_db.add_all([legacy_failed, stale, future, terminal])
    outbox_db.commit()

    assert due_notification_refs(outbox_db) == [
        (due.id, "outbox-org"),
        (legacy_failed.id, "outbox-org"),
        (stale.id, "outbox-org"),
    ]


def test_task_revalidates_tenant_and_sends_each_intent_once(outbox_db, monkeypatch) -> None:
    notification = _deliverable_intent(outbox_db)
    factory = _task_database(outbox_db, monkeypatch)
    sends: list[int] = []

    def deliver(notification, *args):
        sends.append(notification.id)
        return "local-message-1"

    monkeypatch.setattr(notification_tasks, "_send_assignment_notification", deliver)

    assert notification_tasks.send_email_task.run(notification.id, "other-org") == {
        "status": "not_due"
    }
    assert notification_tasks.send_email_task.run(notification.id, "outbox-org")["status"] == (
        "success"
    )
    assert notification_tasks.send_email_task.run(notification.id, "outbox-org")["status"] == (
        "already_sent"
    )
    assert sends == [notification.id]
    with factory() as db:
        persisted = (
            db.query(Notification)
            .filter(Notification.id == notification.id, Notification.org_id == "outbox-org")
            .one()
        )
        assert persisted.status == NotificationStatus.SENT
        assert persisted.sendgrid_message_id == "local-message-1"


@pytest.mark.parametrize(
    ("helper_name", "service_method"),
    [
        ("_send_assignment_notification", "send_assignment_email"),
        ("_send_reminder_notification", "send_reminder_email"),
        ("_send_update_notification", "send_update_email"),
        ("_send_cancellation_notification", "send_cancellation_email"),
    ],
)
def test_scheduling_delivery_forwards_notification_tracking_context(
    outbox_db, monkeypatch, helper_name, service_method
) -> None:
    notification = _deliverable_intent(outbox_db)
    captured: dict[str, object] = {}

    def send_assignment_email(**kwargs):
        captured.update(kwargs)
        return "sg-message-1"

    monkeypatch.setattr(
        notification_tasks.email_service,
        service_method,
        send_assignment_email,
    )
    recipient = (
        outbox_db.query(Person)
        .filter(
            Person.id == "outbox-person",
            Person.org_id == "outbox-org",
        )
        .one()
    )
    preference = (
        outbox_db.query(EmailPreference)
        .filter(
            EmailPreference.person_id == "outbox-person",
            EmailPreference.org_id == "outbox-org",
        )
        .one()
    )

    assert (
        getattr(notification_tasks, helper_name)(
            notification,
            recipient,
            preference,
            "en",
            outbox_db,
        )
        == "sg-message-1"
    )
    assert captured["notification"] is notification
    assert captured["db"] is None


def test_task_rechecks_preferences_before_retry(outbox_db, monkeypatch) -> None:
    notification = _deliverable_intent(outbox_db)
    factory = _task_database(outbox_db, monkeypatch)
    with factory() as db:
        preference = (
            db.query(EmailPreference)
            .filter(
                EmailPreference.person_id == "outbox-person",
                EmailPreference.org_id == "outbox-org",
            )
            .one()
        )
        preference.frequency = EmailFrequency.DISABLED
        db.commit()
    monkeypatch.setattr(
        notification_tasks,
        "_send_assignment_notification",
        lambda *args: pytest.fail("disabled preference must prevent delivery"),
    )

    result = notification_tasks.send_email_task.run(notification.id, "outbox-org")

    assert result == {"status": "suppressed"}
    with factory() as db:
        persisted = (
            db.query(Notification)
            .filter(Notification.id == notification.id, Notification.org_id == "outbox-org")
            .one()
        )
        assert persisted.status == NotificationStatus.SUPPRESSED


def test_task_defers_non_immediate_preference_without_sending(outbox_db, monkeypatch) -> None:
    notification = _deliverable_intent(outbox_db)
    factory = _task_database(outbox_db, monkeypatch)
    with factory() as db:
        preference = (
            db.query(EmailPreference)
            .filter(
                EmailPreference.person_id == "outbox-person",
                EmailPreference.org_id == "outbox-org",
            )
            .one()
        )
        preference.frequency = EmailFrequency.DAILY
        db.commit()
    monkeypatch.setattr(
        notification_tasks,
        "_send_assignment_notification",
        lambda *args: pytest.fail("digest preference must prevent immediate delivery"),
    )

    result = notification_tasks.send_email_task.run(notification.id, "outbox-org")

    assert result == {"status": "deferred_to_digest"}
    with factory() as db:
        persisted = (
            db.query(Notification)
            .filter(Notification.id == notification.id, Notification.org_id == "outbox-org")
            .one()
        )
        assert persisted.status == NotificationStatus.PENDING
        assert persisted.delivery_lease_token is None
        assert due_notification_refs(db) == []


def test_task_failure_returns_intent_to_bounded_retry(outbox_db, monkeypatch) -> None:
    notification = _deliverable_intent(outbox_db)
    factory = _task_database(outbox_db, monkeypatch)
    monkeypatch.setattr(notification_tasks, "_send_assignment_notification", lambda *args: None)

    result = notification_tasks.send_email_task.run(notification.id, "outbox-org")

    assert result["status"] == "error"
    with factory() as db:
        persisted = (
            db.query(Notification)
            .filter(Notification.id == notification.id, Notification.org_id == "outbox-org")
            .one()
        )
        assert persisted.status == NotificationStatus.RETRY
        assert persisted.next_attempt_at is not None


def test_task_marks_provider_acceptance_with_failed_local_commit_uncertain(
    outbox_db, monkeypatch
) -> None:
    notification = _deliverable_intent(outbox_db)
    factory = _task_database(outbox_db, monkeypatch)
    monkeypatch.setattr(
        notification_tasks,
        "_send_assignment_notification",
        lambda *args: "provider-message-accepted",
    )
    monkeypatch.setattr(
        notification_tasks,
        "complete_notification",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("synthetic commit failure")),
    )

    result = notification_tasks.send_email_task.run(notification.id, "outbox-org")

    assert result["status"] == "uncertain"
    with factory() as db:
        persisted = (
            db.query(Notification)
            .filter(Notification.id == notification.id, Notification.org_id == "outbox-org")
            .one()
        )
        assert persisted.status == NotificationStatus.UNCERTAIN
        assert persisted.sent_at is None
        assert persisted.next_attempt_at is None
