# Feature Specification: Sprint 9 — Token refresh, real SendGrid email, Android target

> Status: closing out 2026-05-11.
>
> Mirrors the Sprint 8 closeout structure (`specs/023-sprint-8-completion/spec.md`).

---

## Context

Sprint 8 (`specs/023-sprint-8-completion/spec.md`) shipped the auth flows and every "COMING SOON" closeout, but left three items deferred:

- **Token refresh** — JWT access tokens expire after 24h with no refresh path, so the user is bounced to /login.
- **Real SendGrid sending** — backend has the `EmailService` SendGrid client wired but no public way for an operator to enable it, no smoke verification, and `EMAIL_ENABLED` defaulted to `true` which was unsafe for dev/Docker deployments without credentials.
- **Android target** — Flutter app builds on iOS only; no signing config, no Play Console upload, no deep-link manifest.

Sprint 9 closes all three plus a P2 cleanup bundle covering the deferred follow-ups that surfaced during Sprint 9's Codex review iterations.

---

## Scope (user-confirmed, planning answers 2026-05-07 + 2026-05-08)

- Backend: `POST /auth/refresh` issuing both access + refresh JWTs; `password_reset` flow that actually sends through `EmailService`; `EMAIL_ENABLED` safety default flipped to `false`.
- Mobile: dio interceptor handling 401 → /auth/refresh → replay; `signupflow://` custom-scheme deep links on iOS + Android.
- Android: keystore creation, `flutter build appbundle`, Fastlane lane uploading to Play Console internal track.
- Operator surface: `.env.example` documents `SENDGRID_API_KEY`; one-shot `scripts/email_smoke.py` exercises the live send path; `docs/saas/SMOKE_TESTING_EMAIL.md` documents Mailtrap (dev/staging) + SendGrid (prod) paths.
- Cross-platform smoke runbook (`mobile/SMOKE.md`) so iOS + Android smoke against the same Sprint backend in one document.

## Out of scope

- `POST /webhooks/sendgrid` event handler (delivery / bounce / open tracking) — deferred per `docs/saas/EMAIL_INTEGRATION_PLAN.md:401`.
- Invitation-email dispatch (`api/routers/invitations.py::resend_invitation` still has a TODO) — deferred to Sprint 10.
- Real production `EMAIL_ENABLED=true` flip on `api.signupflow.io` — operator action, not in any PR.
- Dark mode, APNS / FCM push, Solution Review live refresh — Sprint 10.

---

## Phase A — Backend (2 PRs)

### 9.1 — `send_password_reset_email` + wire into `/forgot-password` (PR #78)

`api/routers/password_reset.py` queues a `send_password_reset_email` call via `BackgroundTasks` after issuing the reset token. `api/services/email_service.py` gains `send_password_reset_email(to, name, reset_token, app_url)` rendering an inline-HTML template (HTML-escaped recipient name) with a `signupflow://reset-password?token=...` custom-scheme link plus a web fallback. Reset tokens persisted to DB via `password_reset_tokens` table (Alembic `b4e6f8a2c5d3`) with SHA-256 digest storage + atomic one-time-use claim + prior-token invalidation. `EMAIL_ENABLED=false` by default.

### 9.3 — `POST /auth/refresh` + refresh-token issuance (PR #79)

`/auth/login`, `/auth/signup`, and `/invitations/{token}/accept` now return both `token` (access JWT) and `refresh_token` (long-lived). New endpoint `POST /auth/refresh` consumes the refresh token, rotates it, and returns a fresh access + refresh pair. `Person.refresh_token_version` (Alembic `a3c5d7e9b1f2`) lets the backend invalidate a user's refresh tokens by bumping the counter.

## Phase B — Mobile (3 PRs)

### 9.4 — Mobile dio refresh interceptor (PR #82)

`mobile/lib/api/api_client.dart` adds a dio response interceptor: on 401 for any non-`/auth/refresh` request, fire `/auth/refresh`, persist the new tokens, replay the original request. Concurrent 401s coalesce to a single refresh round-trip. New `signupflow.refresh_jwt` slot in `flutter_secure_storage`; `AuthController.signOut()` calls `clearAll()` so signOut actually clears the long-lived credential.

### 9.4b — Invitation accept returns real JWT pair (PR #84)

`POST /invitations/{token}/accept` now returns the same access+refresh pair as login/signup, so the mobile flow lands the user directly on the dashboard instead of bouncing to /login. `invitation_repository.dart` clears any prior refresh token when the server omits one (pre-9.4b backends).

### 9.7 — Cross-platform smoke runbook (PR #87)

`mobile/SMOKE.md` — single runbook for iOS + Android smoke. Sections: build matrix, pre-flight, volunteer journey, admin journey, Sprint-9-specific backend integration paths (password reset, refresh interceptor, invitation accept, deep-links), pass/fail checklist template. `TESTFLIGHT.md` + `ANDROID_RELEASE.md` carry pointers; platform-specific upload detail stays where it is.

## Phase C — Android target (2 PRs)

### 9.5 — Android release keystore + signing + deep-link (PR #80)

Generates upload keystore, configures `android/app/build.gradle.kts` to sign release builds, registers the `signupflow` custom URL scheme in `AndroidManifest.xml` (intent filters for invitation + reset-password deep links). Monotonic build numbers via `git rev-list --count HEAD`.

### 9.6 — Fastlane Android lane + Play Console upload (PR #83)

`mobile/fastlane/Fastfile` adds `:android internal` lane: `flutter build appbundle --release` → `supply` action uploads to Play Console internal track as draft. `mobile/ANDROID_RELEASE.md` documents the runbook.

## Phase D — Operator surface (1 PR)

### 9.2 — SendGrid wiring docs + smoke runbook + one-shot send (PR #85)

`.env.example` adds `SENDGRID_API_KEY` block with auto-select-rule docs. `docs/saas/SMOKE_TESTING_EMAIL.md` is the new runbook: Path A (Mailtrap sandbox) + Path B (real SendGrid with SPF/DKIM + Activity Feed verification) + failure modes + rollback. `scripts/email_smoke.py` is a thin wrapper around `EmailService.send_email` that dispatches one labeled message and prints the backend + message ID. Refuses to run under `TESTING=true`.

## Phase E — Cleanup + closeout

### 9.x — Sprint 9 P2 cleanup bundle (PR #86)

Six Codex P2 follow-ups deferred during Sprint 9 iteration, resolved in one bundle:

1. `/forgot-password` concurrent-request race — `with_for_update()` Person re-fetch after the audit-log commit, scoped by org_id per tenancy convention.
2. `Settings.EMAIL_ENABLED` default flipped from `True` to `False` to align with `EmailService` env-read gate (no more silently no-op'd Celery email jobs).
3. Mobile refresh-in-flight signOut/login race — `SecureTokenStorage.sessionGeneration` monotonic counter + tri-state `_RefreshOutcome` (success/failure/stale). Stale means storage changed mid-flight; interceptor neither replays nor wipes.
4. `invitation_repository.dart` clears refresh slot when server omits `refresh_token`.
5. `scripts/email_smoke.py` narrow override — `dotenv_values()` only force-clears `SENDGRID_API_KEY`-blank; runbook adds `unset SENDGRID_API_KEY` prelude for Path A.
6. `CLAUDE.md` Codex review invocations use `--base origin/main` + `git fetch` prelude.

### 9.8 — Sprint 9 release + closeout doc (this PR)

Closeout spec doc (this file). Mirrors Sprint 8's structure. The TestFlight + Play Store uploads themselves are operator action — this PR documents what shipped and references the build numbers the operator provides.

---

## Closeout (2026-05-11)

Sprint 9 shipped 10 PRs to main:

| PR | Sprint task | Status |
|----|----|----|
| #77 | (preamble) docs: PR Review Gate section in CLAUDE.md | merged |
| #78 | 9.1 Backend — `send_password_reset_email` + `/forgot-password` queueing | merged |
| #79 | 9.3 Backend — `POST /auth/refresh` + refresh-token issuance | merged |
| #80 | 9.5 Android — release keystore + signing + `signupflow://` deep-link | merged |
| #81 | (mid-sprint) docs: switch PR review to local Codex via plugin | merged |
| #82 | 9.4 Mobile — dio refresh interceptor + secure-storage refresh slot | merged |
| #83 | 9.6 Android — Fastlane lane + Play Console internal upload | merged |
| #84 | 9.4b Backend + mobile — invitation accept returns real JWT pair | merged |
| #85 | 9.2 Email — SendGrid wiring docs + smoke runbook + one-shot send script | merged |
| #86 | 9.x P2 cleanup bundle (6 deferred Codex follow-ups) | merged |
| #87 | 9.7 Mobile — consolidated cross-platform smoke runbook | merged |
| #88 | 9.8 Spec doc (this file) | merged |

### TestFlight build

**Build #_TBD_** uploaded _TBD_ with changelog `"Sprint 9 — token refresh + real password-reset email + Android target"`. Available at App Store Connect → SignUpFlow → TestFlight.

(Operator: fill in build number + date after `bundle exec fastlane beta` completes against the Sprint 9 release SHA. Per `mobile/SMOKE.md`, run the cross-platform smoke against this build before promoting from internal testing.)

### Play Console internal build

**Build #_TBD_** uploaded _TBD_ as draft on the internal testing track. Available at Play Console → SignUpFlow → Internal testing.

(Operator: fill in build number + date after `bundle exec fastlane android internal` completes. The Fastfile lane uploads as draft — finalize manually in Play Console after smoke.)

### What's still deferred (Sprint 10+)

- **SendGrid event webhook** — `POST /webhooks/sendgrid` for delivery/bounce/open tracking (`docs/saas/EMAIL_INTEGRATION_PLAN.md:401`).
- **Invitation email dispatch** — `resend_invitation` TODO; admin UI also discards the `createInvitation` response token (Sprint 10).
- **`ACCESS_TOKEN_EXPIRE_HOURS` env knob** — declared in `api/core/config.py:26` but ignored; `api/security.py:24` uses a hardcoded `ACCESS_TOKEN_EXPIRE_MINUTES`. Documented in `mobile/SMOKE.md` as a source-patch workaround.
- ~~**Inter-write race in `_attemptRefresh`**~~ — closed by Sprint 10 PR 10.3 (`SecureTokenStorage.compareAndWriteTokens` atomic gen-check + dual write). Narrow platform-call-latency window remains in `_RealStorage` between the two awaited platform writes; documented inline.
- **Server-side refresh-token rotation interaction** — discarding a rotated refresh after the stale path could theoretically leave a same-account re-login at a stale version. Depends on backend rotation semantics.
- ~~**Custom-scheme deep-link routing**~~ — closed by Sprint 10 PR 10.3. Added a `_hostRouteRemap` redirect in `mobile/lib/routing/router.dart` that maps `signupflow://<route>` (host form) to `/<route>` defensively, so both URL forms route correctly without changing the backend email URL generation. Verified by `mobile/integration_test/deep_link_test.dart`.
- **Dark mode** — Sprint 10.
- **APNS / FCM push** — Sprint 10 (Inbox is still poll-based).
- **Solution Review live refresh** — Sprint 10 (pull-to-refresh covers v1).
