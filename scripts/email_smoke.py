"""One-shot live email send for smoke testing the EmailService pipeline.

Usage:
    poetry run python scripts/email_smoke.py --to recipient@example.com

Reads credentials from .env (loaded automatically by api.main / dotenv).
Picks SendGrid if SENDGRID_API_KEY is set, otherwise falls back to SMTP
(Mailtrap sandbox in dev/staging). Refuses to run under TESTING=true so
it can't be invoked from CI by accident.

See docs/saas/SMOKE_TESTING_EMAIL.md for the full runbook (credential
setup, verification, failure modes, rollback).
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone

from dotenv import load_dotenv


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--to",
        required=True,
        help="Recipient email address. For Mailtrap sandbox, this is captured "
        "regardless of the address — anything goes to your sandbox inbox.",
    )
    args = parser.parse_args()

    # override=True so a blank SENDGRID_API_KEY in .env actually wins over a
    # stale `export SENDGRID_API_KEY=...` from the operator's shell — without
    # it, dotenv silently keeps the shell value and the Mailtrap smoke would
    # accidentally hit live SendGrid.
    load_dotenv(override=True)

    sendgrid_set = bool(os.getenv("SENDGRID_API_KEY"))
    mailtrap_set = bool(os.getenv("MAILTRAP_SMTP_USER"))
    if sendgrid_set and mailtrap_set:
        print(
            "warning: both SENDGRID_API_KEY and MAILTRAP_SMTP_USER are set. "
            "EmailService will pick SendGrid (real send). If you intended "
            "the Mailtrap smoke, blank SENDGRID_API_KEY in .env or "
            "`unset SENDGRID_API_KEY` in your shell.",
            file=sys.stderr,
        )

    if os.getenv("TESTING", "").lower() == "true":
        print(
            "won't run under TESTING=true — this script issues real sends. "
            "Unset TESTING in your shell / .env first.",
            file=sys.stderr,
        )
        return 1

    # Import after load_dotenv so EmailService picks up the configured env.
    from api.services.email_service import EmailService

    service = EmailService()

    backend = "sendgrid" if (service.use_sendgrid and service.sendgrid_client) else "smtp"
    print(f"backend: {backend}")
    print(f"enabled: {service.enabled}")

    if not service.enabled:
        print(
            "email service disabled — set EMAIL_ENABLED=true in .env "
            "to dispatch a real send. No message was queued."
        )
        return 0

    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    subject = f"[smoke] SignUpFlow email pipeline test — {timestamp}"
    html = (
        "<p>This is a smoke-test message from "
        "<code>scripts/email_smoke.py</code>.</p>"
        f"<p>Timestamp: {timestamp}<br>Backend: {backend}</p>"
        "<p>If you're reading this, the email pipeline is wired correctly "
        "for the current environment. Safe to delete.</p>"
    )

    try:
        message_id = service.send_email(
            to_email=args.to,
            subject=subject,
            html_content=html,
        )
    except Exception as exc:  # surface the backend exception verbatim
        print(f"send failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    if not message_id:
        # send_email returns None when the service is disabled mid-flight,
        # or when the backend swallowed an error. The retry loop logs detail.
        print(
            "send returned no message ID. Check the EmailService log for "
            "the backend's error (api/services/email_service.py).",
            file=sys.stderr,
        )
        return 1

    print(f"message_id: {message_id}")
    print(f"sent to: {args.to}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
