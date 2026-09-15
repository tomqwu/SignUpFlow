# Password Reset Contract

## Supported Routes

| Surface | Route | Purpose |
| --- | --- | --- |
| Web | `GET /auth/forgot` | Render the recovery request form |
| Web | `POST /auth/forgot` | Issue recovery and attach the delivery task to the response |
| Web | `GET /auth/reset/{token}` | Render the reset form from the captured email link |
| Web | `POST /auth/reset/{token}` | Validate and consume the token, then return to login |
| API | `POST /api/v1/auth/forgot-password` | Issue recovery with a generic public response |
| API | `POST /api/v1/auth/reset-password` | Validate and consume a token with a new password |

The web link uses `FRONTEND_URL`, falling back to `APP_URL` and then
`http://localhost:8000`. Messages also retain the
`signupflow:///reset-password?token=...` mobile deep link.

## Request Contract

Submit a valid email address. Known login accounts and unknown or roster-only people
receive the same public message:

```json
{
  "message": "If the email exists, recovery instructions were processed"
}
```

Roster-only people have no `password_hash`; recovery must not turn those rows into login
accounts. A known login account receives one new token and one best-effort background
delivery attempt. A newer request marks every earlier unused token for that person used.

Keep `DEBUG_RETURN_RESET_TOKEN` disabled outside isolated debugging. Committed browser
acceptance follows the actual captured message and never treats debug output or a direct
database token lookup as delivered email.

## Token Contract

- Generate bearer tokens with `secrets.token_urlsafe(32)`.
- Store only the SHA-256 digest in `password_reset_tokens.token_hash`.
- Bind each row to `person_id`; expire it one hour after issuance.
- Accept only a row whose digest matches, `used_at` is null, and `expires_at` is in the
  future.
- Claim the row with one conditional update so replay or concurrent redemption has one
  winner.
- Do not claim an invalid or expired token.
- Do not automatically delete expired rows; expiry is enforced during redemption.

## Password And Session Contract

`new_password` must contain at least six characters on both web and API routes. Validate
that policy before claiming the token, so a rejected password leaves the valid link usable.

A successful reset hashes the new password, stamps `Person.password_changed_at`, and
commits the password and token claim together. The old password then fails. Access tokens
and browser cookies carrying an older `pwd_iat` fail authentication; refresh tokens also
fail the password-version check. A successful self-service password change returns fresh
API tokens or reissues the browser cookie so the active session can continue while copied
pre-change sessions become invalid.

Tokens created before the `pwd_iat` claim existed remain backward-compatible until their
normal JWT expiry. Removing that compatibility is security-hardening work under #261, not
something the current tests silently claim.

## Delivery Modes

Automated acceptance uses `LOCAL_EMAIL_CAPTURE_DIR`, which writes RFC 822 messages to an
owned temporary directory and makes no external connection. The browser test parses the
generated message, follows its HTTP link, and completes recovery on the same local server.

External SMTP/SendGrid delivery, sender reputation, inbox placement, and mailbox latency
require separately authorized provider acceptance. Invitation and password-reset
background tasks remain direct best-effort transport and do not survive process loss;
the durable scheduling-notification outbox does not cover these token messages.

Delivery failure is logged without exposing the token or recipient. The caller still sees
the generic response, and a fresh request can create a new usable link while invalidating
the failed request's token. Do not label disabled delivery as sent.

## Rate-Limit Boundary

The API and browser routes use the same `password_reset` and `password_reset_confirm`
rate-limit operations. Development uses a process-local bucket; production requires an
atomic Redis counter shared by workers and returns retryable `503` when that storage is
unavailable. Forwarded client addresses are honored only from configured trusted proxies.
Owned local tests cover browser wiring, two-worker quota sharing, outage, and recovery;
deployed edge/proxy/TLS behavior remains release acceptance.

## Executable Evidence

Run the focused contract:

```bash
poetry run pytest tests/api/test_password_reset_email.py tests/api/test_password_reset.py -q
poetry run pytest tests/web/test_password_reset.py tests/web/test_account.py -q
poetry run pytest tests/integration/test_password_reset.py -q
poetry run pytest tests/e2e/test_local_mail_playbooks.py --playbook church --playbook basketball -q
```

The pluggable browser journey runs Church and Basketball at 360px and 1440px. For both
administrator and volunteer access it covers logout/login, self-service password change,
continued use of the refreshed session, copied-session rejection, captured reset email,
old-password rejection, replay rejection, and final login. It saves administrator and
member recovery screenshots in pytest's temporary directory.

API regressions separately cover known/unknown response shape, roster-only exclusion,
hashed persistence, new-token invalidation, one-time/concurrent claim behavior, expiration,
short-password rejection before claim, escaped display names, and delivery failure.

## Remaining Acceptance

- Validate an approved external mailbox/provider only in the later release slice.
- Decide whether invitation/reset token messages require their own durable outbox before
  provider activation; current transport remains explicitly best effort.
- Validate mobile deep-link handling on an installed client under #191.
