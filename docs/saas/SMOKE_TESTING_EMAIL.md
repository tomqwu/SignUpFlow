# Email Smoke Testing — Runbook

End-to-end verification that the email pipeline (`api/services/email_service.py`)
actually delivers a message to a real inbox, after credentials have been
configured in `.env`. Use this when:

- Wiring a new environment for the first time (dev, staging, prod).
- After rotating the SendGrid API key or Mailtrap credentials.
- After any change to `EmailService` itself (sanity check that the send
  path still works against a live backend, not just unit-test mocks).

The pipeline has two backends:

| Backend  | When                | Vars                                    |
|----------|---------------------|-----------------------------------------|
| SMTP     | dev / staging / CI  | `MAILTRAP_SMTP_*` (Mailtrap sandbox)    |
| SendGrid | production          | `SENDGRID_API_KEY` (auto-selects)       |

Selection is automatic in `EmailService.__init__`: if `SENDGRID_API_KEY` is
set, the SendGrid backend is used; otherwise SMTP. `EMAIL_ENABLED=true` is
required either way — without it, every send is a no-op (with a `WARNING`
log line). See `specs/001-email-notifications/spec.md:105` for the design.

---

## Prerequisites

Run the existing prerequisite check first:

```bash
./scripts/validate_email_system.sh
```

It verifies Python 3.10+, Poetry, and Redis (the broker for the Celery
notification worker — not strictly needed for the synchronous smoke send,
but required for the full notification path). Fix anything it flags before
continuing.

---

## Path A — Mailtrap sandbox (dev / staging / CI)

Mailtrap captures every send to a virtual inbox you can view in the
browser. Nothing leaves their network — safe to use without any domain
authentication.

### 1. Get credentials

1. Sign up / log in at <https://mailtrap.io/>.
2. Navigate to **Email Testing → Inboxes → SMTP Settings**.
3. Copy `Username` and `Password`. The host (`sandbox.smtp.mailtrap.io`)
   and port (`2525`) are already set as defaults in `.env.example`.

### 2. Configure `.env`

```bash
cp .env.example .env  # if you haven't already
```

Edit `.env`:

```ini
EMAIL_ENABLED=true
MAILTRAP_SMTP_USER=<paste from step 1>
MAILTRAP_SMTP_PASSWORD=<paste from step 1>
SENDGRID_API_KEY=        # leave blank — forces SMTP backend
```

### 3. Run the smoke send

```bash
poetry run python scripts/email_smoke.py --to your-mailtrap-inbox@example.com
```

(The `--to` address is the envelope recipient. Mailtrap captures it
regardless — anything you put here ends up in your sandbox inbox, not in
that real mailbox.)

### 4. Verify

- Script prints `backend: smtp`, a non-empty message ID, and exits 0.
- Open your Mailtrap inbox in the browser. The message appears within
  ~30s with subject `[smoke] SignUpFlow email pipeline test — <ISO ts>`.
- Click into it; the body should render the smoke payload HTML cleanly.

If you don't see the message:

- Check the script output for an exception. SMTP auth errors mean the
  Mailtrap user/password is wrong.
- Check `MAILTRAP_SMTP_HOST` and `MAILTRAP_SMTP_PORT` weren't overridden
  in `.env` — the sandbox host is required, the bulk host won't work
  without a paid plan.

---

## Path B — SendGrid (production)

This actually sends a real email to a real inbox. Only run against an
environment whose `EMAIL_FROM` belongs to a domain you've authenticated
with SendGrid (SPF + DKIM). Sending from an unverified domain triggers a
403 from SendGrid and the message never leaves the API.

### 1. Generate an API key

1. <https://app.sendgrid.com/settings/api_keys> → **Create API Key**.
2. Choose **Restricted Access**, grant **Mail Send: Full**, deny
   everything else.
3. Copy the key (it's shown once — store it in your password manager).

### 2. Authenticate the sender domain

1. <https://app.sendgrid.com/settings/sender_auth> → **Authenticate Your
   Domain**.
2. Add the SPF and DKIM records SendGrid generates to your DNS. Wait for
   them to propagate (usually < 1 hour, sometimes longer).
3. Confirm `EMAIL_FROM` in `.env` matches a mailbox on the authenticated
   domain (default `noreply@signupflow.io` from `api/core/config.py:38`).

### 3. Configure `.env`

```ini
EMAIL_ENABLED=true
EMAIL_FROM=noreply@yourdomain.com  # must match an authenticated domain
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxx
```

`MAILTRAP_*` vars are ignored once `SENDGRID_API_KEY` is set — the SMTP
client is never constructed.

### 4. Run the smoke send

```bash
poetry run python scripts/email_smoke.py --to your-personal-inbox@example.com
```

### 5. Verify

- Script prints `backend: sendgrid`, a non-empty `X-Message-Id`
  (`sendgrid-msg-<22 hex chars>`), exit 0.
- Watch the SendGrid Activity Feed
  (<https://app.sendgrid.com/email_activity>) — the smoke message
  appears within ~5s with status `Delivered`.
- Check the recipient inbox (give it a minute, especially first send to
  a domain).

---

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| Script prints `email service disabled — set EMAIL_ENABLED=true` and exits 0 | `EMAIL_ENABLED=false` in `.env` (or unset — default is now `false` per #78) | Set `EMAIL_ENABLED=true`. The no-op log lives at `api/services/email_service.py:191-193`. |
| Script refuses with `won't run under TESTING=true` and exits 1 | `TESTING=true` in your shell or `.env` | Unset `TESTING`. The smoke is for live envs only; CI uses mocked email. |
| `backend: sendgrid` + 401 in the exception | API key invalid, expired, or revoked | Regenerate the key (Path B step 1). The 401 surfaces from `sendgrid.SendGridAPIClient.send` and is logged at `email_service.py:295`. |
| `backend: sendgrid` + 403 in the exception | `EMAIL_FROM` is not an authenticated SendGrid sender | Either authenticate the domain (Path B step 2) or change `EMAIL_FROM` to a verified address. |
| `backend: smtp` + auth error | Mailtrap user/password wrong, or you used a non-sandbox host without a paid plan | Re-paste from Mailtrap dashboard; confirm `MAILTRAP_SMTP_HOST=sandbox.smtp.mailtrap.io`. |
| Script succeeds but message never appears in recipient inbox | SendGrid Activity Feed shows `Delivered` → it's at the recipient end (spam folder, deferred, blocked). Activity Feed shows `Bounced` / `Dropped` → recipient address invalid or blocklisted. | Inspect the Activity Feed entry; SendGrid surfaces the SMTP response code there. |

---

## Rollback

If a live send goes wrong (wrong recipients, content issue, etc.) and you
need to immediately stop further sends:

1. `EMAIL_ENABLED=false` in the deployed `.env` and restart the API
   process. Every subsequent send becomes a no-op.
2. If the leak was via the SendGrid key (e.g., committed to git, exposed
   in a screenshot): revoke the key in the SendGrid dashboard
   (<https://app.sendgrid.com/settings/api_keys>) — this invalidates it
   immediately, even before the env var is rotated. Then generate a
   replacement and redeploy.

---

## Related

- `docs/saas/EMAIL_INTEGRATION_PLAN.md` — design doc for the email
  pipeline (templates, notification model, future webhook).
- `specs/001-email-notifications/spec.md` — original spec, including the
  Mailtrap-for-staging / SendGrid-for-prod split.
- `scripts/validate_email_system.sh` — prerequisite checks (Python,
  Poetry, Redis).
- `api/services/email_service.py` — the implementation under test here.
