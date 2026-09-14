"""Owned local mail capture tests."""

from email import policy
from email.parser import BytesParser
from unittest.mock import Mock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.models import Base, Notification, Organization, Person
from api.services.email_service import EmailService
from api.tasks import notifications as notification_tasks

pytestmark = pytest.mark.unit


def test_local_capture_writes_parseable_message(tmp_path):
    service = EmailService(capture_dir=tmp_path)

    message_id = service.send_email(
        to_email="member@example.test",
        subject="Your schedule changed",
        html_content='<p>Open <a href="http://127.0.0.1:8000/v/schedule">schedule</a>.</p>',
        plain_content="Open http://127.0.0.1:8000/v/schedule",
    )

    assert message_id is not None
    assert service.delivery_mode == "local_capture"
    messages = list(tmp_path.glob("*.eml"))
    assert len(messages) == 1
    parsed = BytesParser(policy=policy.default).parsebytes(messages[0].read_bytes())
    assert parsed["To"] == "member@example.test"
    assert parsed["Subject"] == "Your schedule changed"
    assert "http://127.0.0.1:8000/v/schedule" in parsed.get_body("plain").get_content()
    assert not list(tmp_path.glob("*.tmp"))


def test_disabled_delivery_writes_nothing(tmp_path, monkeypatch):
    monkeypatch.delenv("LOCAL_EMAIL_CAPTURE_DIR", raising=False)
    monkeypatch.setenv("EMAIL_ENABLED", "false")
    service = EmailService()

    result = service.send_email(
        to_email="member@example.test",
        subject="No delivery",
        html_content="<p>Nothing should be written.</p>",
    )

    assert result is None
    assert service.delivery_mode == "disabled"
    assert not list(tmp_path.iterdir())


def test_sent_notification_task_is_idempotent(monkeypatch):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    with session_factory() as session:
        session.add(Organization(id="mail-org", name="Mail Org"))
        session.add(
            Person(
                id="mail-member",
                org_id="mail-org",
                name="Mail Member",
                email="mail-member@example.test",
                roles=["volunteer"],
            )
        )
        session.flush()
        notification = Notification(
            org_id="mail-org",
            recipient_id="mail-member",
            type="reminder",
            status="sent",
            sendgrid_message_id="local-existing",
        )
        session.add(notification)
        session.commit()
        notification_id = notification.id

    task_session = session_factory()
    monkeypatch.setattr(notification_tasks, "get_db", lambda: iter([task_session]))
    send = Mock()
    monkeypatch.setattr(notification_tasks.email_service, "send_email", send)

    result = notification_tasks.send_email_task.run(notification_id)

    assert result == {"status": "already_sent", "message_id": "local-existing"}
    send.assert_not_called()
    engine.dispose()
