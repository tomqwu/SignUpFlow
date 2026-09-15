"""Provider-free tests for SendGrid tenant tracking metadata."""

from types import SimpleNamespace
from unittest.mock import Mock

from api.services import email_service as email_module


def test_sendgrid_message_carries_notification_tenant_identity(monkeypatch) -> None:
    client = Mock()
    client.send.return_value.headers = {"X-Message-Id": "sg-message-1"}
    monkeypatch.setattr(email_module, "SendGridAPIClient", lambda _key: client)

    service = email_module.EmailService(sendgrid_api_key="local-test-key", use_sendgrid=True)
    service.enabled = True
    notification = SimpleNamespace(id=42, org_id="church-east")

    result = service.send_email(
        to_email="volunteer@example.test",
        subject="Assignment",
        html_content="<p>Assignment</p>",
        notification=notification,
    )

    assert result == "sg-message-1"
    payload = client.send.call_args.args[0].get()
    assert payload["custom_args"] == {
        "signupflow_notification_id": "42",
        "signupflow_org_id": "church-east",
    }


def test_sendgrid_message_omits_tracking_metadata_without_notification(monkeypatch) -> None:
    client = Mock()
    client.send.return_value.headers = {"X-Message-Id": "sg-message-2"}
    monkeypatch.setattr(email_module, "SendGridAPIClient", lambda _key: client)

    service = email_module.EmailService(sendgrid_api_key="local-test-key", use_sendgrid=True)
    service.enabled = True

    assert (
        service.send_email(
            to_email="invitee@example.test",
            subject="Invitation",
            html_content="<p>Invitation</p>",
        )
        == "sg-message-2"
    )
    assert "custom_args" not in client.send.call_args.args[0].get()
