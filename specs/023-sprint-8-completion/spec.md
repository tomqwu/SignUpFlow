# Feature Specification: Sprint 8 — Auth completion + every "COMING SOON" closeout

**Feature Branch**: `023-sprint-8-completion`
**Created**: 2026-05-07
**Status**: Draft
**Type**: Closeout sprint — backend gaps + mobile feature finish

---

## Context

Sprint 7 shipped the Flutter mobile app to TestFlight (build #425, app id `app.signupflow.ios`). The first attempt at signing in failed: there are no accounts in the dev DB, and the app has no signup UI. The login screen has a "Have an invitation? Tap here" link that points at a `StubScreen`.

Beyond auth, several screens still display **"COMING SOON"** callouts because the underlying backend endpoints either don't exist or return untyped `JsonObject`:

| Screen | Callout | Underlying gap |
|---|---|---|
| Volunteer · Availability | Recurring rules + one-off blocked dates | No `/availability/{id}/rrule` or `/availability/{id}/exceptions` endpoints |
| Volunteer · Inbox (4th tab) | Stub, dropped from tab bar in 7.1 v2 | No `/notifications` router |
| Admin · Solution Review | "Per-event breakdown — coming in 7.10" | `getSolutionAssignments` returns `JsonObject` (untyped) |
| Auth · Invitation accept | `StubScreen` | Endpoint exists; mobile UI missing |
| Auth · Forgot/reset password | No screen at all | Endpoint exists; mobile UI missing |
| Auth · Signup (create org) | No screen at all | Endpoint exists; mobile UI missing |

Sprint 8 closes all of the above.

## Scope (user-confirmed, planning answers 2026-05-07)

1. **Sign-in failure** = "no account exists" → fix is implementing signup, not debugging the login flow.
2. Build **both** signup paths: create-organization (admin onboarding) and accept-invitation (volunteer onboarding).
3. **Auth + everything deferred** — close every "COMING SOON" callout in the iOS app and any backend endpoint a callout was waiting on.

## Out of scope

- Token refresh (24h re-login still acceptable for v1; deferred to Sprint 9)
- Dark mode (Sprint 9 — needs `brand-spec.md` dark variant)
- Android target (Flutter codebase makes it cheap when pulled in; not in Sprint 8)
- Push notifications via APNS (Inbox in 8.10 is poll-based; APNS push is Sprint 9)
- SendGrid email actually sending (`EMAIL_ENABLED=false` stays off until the constitution's safety rule is consciously revoked)
- Solution Review per-event refresh on remote mutation (pull-to-refresh covers it)

## Phase A — Backend prerequisites (4 PRs)

Each PR ships a router or response-model change, refreshes `tests/contract/openapi.snapshot.json` via `make update-openapi-snapshot`, and is gated by the existing CI test tiers.

### 8.1 — Enrich `/solutions/{id}/assignments` response

**Branch:** `sprint-8-1-solution-assignments-enriched`

Today: `SolutionsApi.getSolutionAssignments` returns `JsonObject` (untyped — backend has no FastAPI response model). Mobile cannot render it cleanly.

Files:
- `api/routers/solutions.py` — declare typed response model on the `get_solution_assignments` handler.
- `api/schemas/solver.py` — new `SolutionAssignmentsResponse` shape:
  ```python
  class SolutionAssignmentEntry(BaseModel):
      event_id: str
      event_type: str
      event_start: datetime
      event_end: datetime
      assignees: list[AssignmentEntry]   # person_id, name, role, status

  class SolutionAssignmentsResponse(BaseModel):
      solution_id: int
      events: list[SolutionAssignmentEntry]
  ```
- `tests/api/test_solution_assignments_enriched.py` (new).

### 8.2 — `/availability/{person_id}/exceptions` CRUD

**Branch:** `sprint-8-2-availability-exceptions-crud`

Sprint 5 PR 5.4 added `AvailabilityException` rows that the solver consumes, but no API surface exists for managing them.

Files:
- `api/routers/availability.py` — `GET`, `POST`, `DELETE /{exception_id}` for `/availability/{person_id}/exceptions`. POST body: `{exception_date: date, reason: str | None}`.
- `api/schemas/availability.py` — request/response models.
- `tests/api/test_availability_exceptions.py` (new).

### 8.3 — `/availability/{person_id}/rrule` CRUD

**Branch:** `sprint-8-3-availability-rrule-crud`

Decision: **one rrule per person, not a list** — keeps the schema simple and matches the existing `Availability.rrule: str | None` column. The mobile UI can hide multi-rule complexity behind a preset picker (8.9).

Files:
- `api/routers/availability.py` — `GET` / `PUT` / `DELETE` on `/availability/{person_id}/rrule`. PUT body: `{rrule: str}` (single rrule); DELETE clears it.
- `tests/api/test_availability_rrule.py` (new).

### 8.4 — `/notifications` (Inbox feed)

**Branch:** `sprint-8-4-notifications-router`

Files:
- `api/routers/notifications.py` (new) — `GET /notifications` returns paginated audit-log-derived rows for the authenticated person. Sources: `audit_logs` filtered to `actor_id == current_user.id` AND `action IN ('assignment.accepted', 'assignment.declined', 'assignment.swap_requested', 'solution.published', 'invitation.accepted')`. Read state lives in a new `notification_reads` table (`person_id`, `audit_log_id`, `read_at`).
- `api/models.py` — `NotificationRead` model.
- `api/schemas/notifications.py` — response shapes.
- `api/main.py` — register the router.
- `alembic/versions/<new>.py` — migration for `notification_reads`.
- `tests/api/test_notifications.py` (new).
- `CLAUDE.md` — add `/api/v1/notifications` to the active-routers block.

## Phase B — Mobile codegen refresh (1 PR)

### 8.5 — Run `make mobile-codegen`

**Branch:** `sprint-8-5-run-mobile-codegen`

Pure regeneration. After 8.1–8.4 land, the OpenAPI snapshot has new schemas; `mobile/api_client/` is stale. Single PR, large diff, mostly auto-generated.

Verify `flutter analyze` + `flutter test` still pass with the updated client.

## Phase C — Mobile auth screens (3 PRs)

### 8.6 — Create-organization signup flow

**Branch:** `sprint-8-6-create-org-signup`

New:
- `mobile/lib/features/auth/create_org_screen.dart` — form: org name, org id (slug), admin name/email/password. Submit calls `POST /organizations` then `POST /auth/signup` with `org_id` from the org just created. On success, store JWT in Keychain, route to `/a/dashboard` (first user is admin).
- `mobile/lib/auth/signup_repository.dart` — wraps `OrganizationsApi.createOrganization` + `AuthApi.signup`. Handles 409 (org exists) and 422 (validation) with user-facing messages.
- `mobile/lib/features/auth/login_screen.dart` — add "Create new organization" link below the demo shortcut card.

Reuse: `LoginRepository._resolveRole`, `secureTokenStorageProvider`, `BlockButton`, `BlockCard`, `_Field`.

Tests: `mobile/test/create_org_test.dart` — fake repo, asserts form validation + happy-path navigation.

### 8.7 — Invitation accept (real implementation)

**Branch:** `sprint-8-7-invitation-accept`

Replace stub: `mobile/lib/features/auth/invitation_screen.dart` is a `StubScreen` today.

New:
- `invitation_screen.dart` — takes `?token=...` query param via GoRouter. Calls `InvitationsApi.getInvitation(token: ...)` to load invitation card (org name, role, inviter). User sets a password → `InvitationsApi.acceptInvitation(token, body: {password, timezone})`. On success, store JWT + role, route to `/v/schedule` or `/a/dashboard`.
- `mobile/lib/auth/invitation_repository.dart` — typed wrapper.
- `mobile/lib/routing/router.dart` — `/invitation` takes `?token=` query param.
- `mobile/ios/Runner/Info.plist` — register custom URL scheme `signupflow://` so deep-links from invitation emails open the app.
- `login_screen.dart` — wire "Have an invitation? Tap here" to a manual-token-paste field for testing without email delivery.

Tests: `mobile/test/invitation_accept_test.dart` — token-parse, accept-success, accept-failure (token-already-used), invalid-token-404.

### 8.8 — Forgot password + Reset password

**Branch:** `sprint-8-8-password-reset`

New:
- `mobile/lib/features/auth/forgot_password_screen.dart` — email field → `AuthApi.requestPasswordReset({email})` → confirmation message. Even with SendGrid off, the endpoint creates a token row — useful for manual testing by querying the dev DB.
- `mobile/lib/features/auth/reset_password_screen.dart` — takes `?token=...` from deep-link, prompts for new password, calls `AuthApi.resetPassword({token, new_password})`.
- `mobile/lib/auth/password_reset_repository.dart` — wraps both endpoints.
- `mobile/lib/routing/router.dart` — `/forgot-password` and `/reset-password?token=...` routes.
- `login_screen.dart` — "Forgot password?" copy → `context.go('/forgot-password')`.
- `Info.plist` — `signupflow://reset-password?token=...` deep-link (alongside the invitation deep-link from 8.7).

Tests: `mobile/test/password_reset_test.dart`.

## Phase D — Mobile feature closeouts (3 PRs)

### 8.9 — Availability rrule editor + single-date exceptions

**Branch:** `sprint-8-9-availability-recurring`

Replace the COMING SOON card in `mobile/lib/features/volunteer/availability_screen.dart`.

New:
- `availability_provider.dart` — extend with `availabilityRruleProvider` (fetch + put + delete the single rrule string) and `availabilityExceptionsProvider` (fetch list of single-date exceptions). Mutations: `setRrule`, `clearRrule`, `addException(date, reason?)`, `deleteException(id)`.
- `availability_screen.dart` — two new sections:
  - **Recurring rules** — single rrule field with friendly preset picker ("Every Monday", "Every other Friday", "Custom rrule…") that builds the rrule string.
  - **One-off blocked dates** — list with "+ Add date" sheet that adds a single date as an exception.

Tests: widget test confirms both sections render with overridden providers.

### 8.10 — Volunteer Inbox

**Branch:** `sprint-8-10-volunteer-inbox`

Replace stub: `mobile/lib/features/volunteer/inbox_screen.dart` is a stub today (and was dropped from the tab bar in 7.1 v2). Re-add it now that the backend supports it.

New:
- `inbox_provider.dart` — `FutureProvider` over `NotificationsApi.listNotifications()`.
- `inbox_screen.dart` — list rows: title, subject, timestamp, unread dot. Tapping a row navigates to the related entity and marks-read.
- Re-add 4th tab to `mobile/lib/features/volunteer/shell.dart`.
- Update jump-to dropdown in dev controls.

Tests: widget test for empty + populated state.

### 8.11 — Per-event Solution Review assignments

**Branch:** `sprint-8-11-solution-review-assignments`

Replace the "Per-event breakdown — coming in 7.10" callout in `mobile/lib/features/admin/solution_review_screen.dart`.

New:
- `solution_assignments_provider.dart` — `FutureProvider.family<int>(solutionId)` over `SolutionsApi.getSolutionAssignments` (now typed thanks to 8.1).
- Replace the COMING SOON `BlockCard` in the ASSIGNMENTS segment with a real list: grouped by event (date label, event title, time chip), avatars + names of assignees inside each group.

Tests: widget test asserts grouping + avatar rendering.

## Phase E — Closeout

### 8.12 — TestFlight upload + Sprint 8 closeout doc

**Branch:** `sprint-8-12-testflight`

After 8.6–8.11 are merged, run `bundle exec fastlane beta` from `mobile/` to push build #426+ to TestFlight. Update `mobile/TESTFLIGHT.md` with a Sprint 8 changelog template. Append a Sprint 8 closeout section to this spec doc summarizing what shipped and known follow-ups.

## PR sequencing

```
8.0  Spec doc (this file)
─────────────────────── Mobile auth (early user impact) ───────────────────────
8.6  Create-org signup
8.7  Invitation accept
8.8  Forgot + reset password
─────────────────────── Backend ───────────────────────
8.1  Enrich /solutions/{id}/assignments
8.2  /availability/exceptions CRUD
8.3  /availability/rrule CRUD
8.4  /notifications router + NotificationRead model
─────────────────────── Codegen ───────────────────────
8.5  make mobile-codegen
─────────────────────── Mobile features ───────────────
8.9  Availability rrule + exceptions
8.10 Volunteer Inbox (re-add 4th tab)
8.11 Solution Review per-event assignments
─────────────────────── Closeout ──────────────────────
8.12 TestFlight upload + Sprint 8 closeout doc
```

13 PRs total (counting 8.0). Auth screens (8.6–8.8) ship first against the existing generated client (`AuthApi`/`OrganizationsApi`/`InvitationsApi` have been generated since 7.2b). Backend phase blocks codegen blocks Phase D mobile feature work.

## Verification per PR

Backend (8.1–8.4):
1. `poetry run black --check api tests` clean.
2. `poetry run ruff check api tests` clean.
3. `poetry run pytest tests/unit/ tests/api/ tests/cli/ tests/contract/ tests/integration/` — each tier separately.
4. Refresh `tests/contract/openapi.snapshot.json` via `make update-openapi-snapshot`.

Mobile (8.5–8.11):
1. `cd mobile && flutter analyze` — 0 issues.
2. `cd mobile && flutter test` — all passing.
3. Manual smoke: `flutter run -d "iPhone 17"` against `make run` backend — walk the affected flow end-to-end.
4. For 8.7 + 8.8 deep-link routes: `xcrun simctl openurl <device-id> "signupflow://invite?token=fake"` opens the app at the right route.

Sprint close (8.12):
- `bundle exec fastlane beta changelog:"Sprint 8 — auth + feature closeout"` produces a TestFlight build.
- On-device smoke per `mobile/TESTFLIGHT.md` checklist.

## Risks / open questions

- **`org_id` field on the create-org form** — slug the user types (must be unique) or auto-generated from the org name? Defer the decision into 8.6 implementation; either is fine.
- **Invitation deep-link delivery** — SendGrid is off, so the invitation email never goes out. PR 8.7 includes a manual-token-paste affordance on the login screen so the flow is testable end-to-end without email.
- **`notification_reads` migration on prod** — Alembic migration is additive (new table, no existing-row rewrite); safe to roll forward.
