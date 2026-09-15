# Local Email Capture

Use the owned local capture backend to exercise invitation, recovery, assignment,
schedule-change, and reminder messages without an SMTP account or external network.
It writes one RFC 822 `.eml` file per successful send.

## Run The Acceptance Workflow

```bash
poetry run pytest tests/e2e/test_local_mail_playbooks.py -v
```

The Playwright fixture creates a disposable database, temporary capture directory,
and loopback Uvicorn server. It sets `APP_URL` and `FRONTEND_URL` to that server so
captured web links are usable. `EMAIL_ENABLED`, billing, paid SMS, SendGrid, Mailtrap,
and inherited provider credentials remain disabled or absent.

Each discovered playbook runs at 360px and 1440px. The test follows the actual
invitation and single-use reset links, proves the old password and replay fail,
publishes and changes one domain-critical assignment, sends a reminder, reconciles
the member inbox, and opens every notification HTTP link.

## Run A Development Sink

Set a directory owned by the current developer process before starting the app:

```bash
export LOCAL_EMAIL_CAPTURE_DIR="$PWD/.local/email-capture"
export APP_URL="http://127.0.0.1:8000"
export FRONTEND_URL="http://127.0.0.1:8000"
make run
```

Do not commit captured messages. They can contain single-use invitation or reset
tokens. Delete the directory when the drill is complete. Do not set this variable in
a production environment; configure an approved provider under the separate external
delivery runbook instead.

## Delivery Contract

- `LOCAL_EMAIL_CAPTURE_DIR` takes precedence over SMTP and SendGrid and reports the
  `local_capture` mode.
- `EMAIL_ENABLED=false` with no capture directory reports `disabled`; user-facing
  copy says delivery is disabled and never says a message was sent.
- Captured notification records move from `pending` to `sent` only after the `.eml`
  file is atomically renamed into place.
- Every notification operation has a unique delivery key. Replaying a publish,
  reminder, or event-update operation does not deliver the same intent twice.
- Invitation and reset endpoints keep transport failures out of the response path.
  Password-recovery confirmation remains neutral for known and unknown addresses.
- Local capture alone does not establish external provider acceptance, inbox placement,
  bounce/webhook processing, or production retry operations.
- Separate PostgreSQL and Redis acceptance proves scheduling-notification transaction
  rollback, one-worker lease ownership, stale-lease recovery, broker outage/re-enqueue,
  and cross-worker refresh hints. It does not make invitation/reset transport durable or
  validate a deployed broker/provider.

The provider smoke process remains documented in
[the external email runbook](saas/SMOKE_TESTING_EMAIL.md). Run it only with explicit
authorization and approved credentials.
