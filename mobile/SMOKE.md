# Cross-platform mobile smoke

End-to-end manual verification that a Sprint-release Flutter build
behaves correctly on both iOS (TestFlight) and Android (Play internal
track) against the deployed backend. Run before opening a sprint
closeout PR — surfaced regressions become `<sprint>-fix-<what>` PRs.

This document is the **single runbook** for cross-platform smoke. The
platform-specific upload + signing details remain in
`mobile/TESTFLIGHT.md` (iOS) and `mobile/ANDROID_RELEASE.md` (Android).
This file assumes both builds already exist and are installable on
your devices.

> **Why a consolidated runbook?** Before Sprint 9, the iOS smoke
> checklist lived in `TESTFLIGHT.md:127-137` and the Android version
> was "mirror the iOS checklist" with a few platform extras
> (`ANDROID_RELEASE.md:114-138`). One source of truth means the two
> platforms can't drift, and a future "iOS works, Android doesn't"
> regression has somewhere obvious to be filed against.

---

## Build matrix

Each sprint cuts both platforms at the same git commit. Build numbers
are monotonic (`git rev-list --count HEAD`), so iOS build #N and Play
internal build #N reference the same source.

| Platform | Build artifact         | Upload lane                                | Detail doc                |
|----------|------------------------|--------------------------------------------|---------------------------|
| iOS      | `.ipa` (TestFlight)    | `bundle exec fastlane beta`                | `mobile/TESTFLIGHT.md`    |
| Android  | `.aab` (Play internal) | `bundle exec fastlane android internal`    | `mobile/ANDROID_RELEASE.md` |

Before walking the runbook below: confirm with `flutter --version`,
`bundle exec fastlane --version`, that both lanes have run cleanly
for the SHA you're smoking, and that the deployed backend
(`api.signupflow.io` or staging) is on the same Sprint's main.

---

## Pre-flight

1. **Backend health:** `curl -s -o /dev/null -w '%{http_code}\n' https://api.signupflow.io/health` returns `200`. (The repo currently only exposes `/health` and `/api/v1/*`; there is no `/api/config/safe-flags` endpoint despite older docs referencing one. For email-enabled checks see `docs/saas/SMOKE_TESTING_EMAIL.md`.)
2. **Test users:** keep one volunteer account and one admin account seeded in the backend (not the developer's daily driver — these will get reset password emails, logged-out states, etc.). Note their credentials.
3. **Devices:** one iPhone with TestFlight build #N installed; one Android phone with Play internal build #N installed via the testers-track invitation link. **Don't smoke on an emulator** — keychain/secure-storage behavior differs and a passing emulator run won't catch real-device issues.

---

## Volunteer journey (run on both platforms)

For each platform, run the steps below in order. Mark each line ✅ / ❌
in the closeout doc; ❌ becomes a fix PR before tagging the sprint.

1. **Login.** Paste the volunteer's credentials.
   - iOS: confirm Keychain saves the JWT (close + relaunch → should land on schedule, not /login).
   - Android: confirm `flutter_secure_storage` saves the JWT (same close + relaunch test).
2. **Schedule renders.** Date sections in local timezone. Assignments display name + role.
3. **Assignment detail.** Tap an assignment → Accept / Decline / Swap. Schedule reloads with the new state.
4. **Availability.** Add a TimeOff range. Delete it. Confirm both round-trip to backend.
5. **Profile / ICS export.** Copy ICS URL → paste into Safari (iOS) / Chrome (Android) → verify `.ics` file downloads and opens in default calendar.
6. **Log out.** Confirm secure storage is wiped (close + relaunch → /login).

---

## Admin journey (run on both platforms)

1. Login as admin.
2. **Dashboard** loads org metrics.
3. **Run Solver** → solution generates within ~10s for a typical org.
4. **Solution Review** → assignment grid renders, can edit assignments.
5. **Publish** the solution.
6. **Compare** vs previous published — diff view loads.
7. **Rollback** → previous solution becomes active.

---

## Backend-Sprint-9-specific paths

Sprint 9 introduced backend features that mobile must exercise
end-to-end. Run these IN ADDITION to the journeys above; any
regression here is a release blocker.

### 1. Password reset email (#78)

Requires `EMAIL_ENABLED=true` on the deployed backend. If the backend
is dev/staging-only, this can be skipped — note it in the closeout.

1. On the login screen, tap **Forgot password**.
2. Enter the volunteer's email. Submit.
3. Email lands within ~30s (real inbox for prod / Mailtrap for staging — see `docs/saas/SMOKE_TESTING_EMAIL.md`).
4. Open the reset link on the same device.
   - **iOS:** the `signupflow://reset-password?token=...` custom-scheme link should route into the app's reset-password screen. (The iOS app currently only registers the `signupflow` custom URL scheme in `Info.plist` — no Universal Link / Associated Domains setup. Tap the link from the email body in Mail.app; Safari paste also works.)
   - **Android:** the `signupflow://reset-password?token=...` link should route into the app (verified via the manifest's `<intent-filter>` for the `signupflow` scheme).
5. Set a new password. Confirm.
6. Login with the new password succeeds.

### 2. Token refresh interceptor (#79 + #82)

To exercise the refresh path the **server** must reject the access token while the refresh token remains valid. Device clock forwarding doesn't work (the JWT `exp` claim is checked server-side against server time), and rotating the user's `refresh_token_version` invalidates the *refresh* token (the opposite of what we want).

There is currently **no env-driven knob** for the access-token TTL — `api/core/config.py:26` declares `ACCESS_TOKEN_EXPIRE_HOURS` but `api/security.py:24` uses a hard-coded `ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24`. Until that's wired up (separate ticket), use one of:

- **Source patch + redeploy (preferred):** temporarily change `ACCESS_TOKEN_EXPIRE_MINUTES = 3` in `api/security.py` on the staging deploy, restart the API, run the smoke, revert. The refresh interceptor exercises the same code path the prod 24h expiry will hit later.
- **Admin force-expire (future):** if/when an admin endpoint to invalidate a single access token lands (none in `api/routers/auth.py` at time of writing), point this section at it.

Steps:

1. Login as the volunteer.
2. Wait for the access token to expire (≥3 min if you took the short-expiry path).
3. Open the app → tap a screen that makes an API call.
4. Expected: app silently refreshes (no /login prompt). In device logs (Xcode console / `adb logcat | grep dio`) you'll see one `/auth/refresh` round-trip.
5. **Edge case:** tap "Sign out" immediately as a refresh is in flight (this is the #82 P2 race). Expected: app lands on /login. Verify secure storage is empty (re-launch lands on /login, not back into the session).

### 3. Invitation accept JWT pair (#84)

> The backend's `create_invitation` endpoint returns the invitation token in the response body — **it doesn't send an email yet** (`resend_invitation` still has a TODO for SMTP dispatch). Until that lands, the smoke walks the token through manually.

1. As admin, create an invitation via the **API** — the response body carries the raw invitation token. The mobile admin UI currently discards that response and only shows "Invitation sent", so it can't surface the token until invitation-email dispatch lands.

   ```bash
   curl -X POST 'https://api.signupflow.io/api/v1/invitations?org_id=<your-org-id>' \
     -H 'Authorization: Bearer <admin-jwt>' \
     -H 'Content-Type: application/json' \
     -d '{"email":"newvolunteer@example.com","name":"New Volunteer","roles":["volunteer"]}'
   ```

   `org_id` is a required query param; `email` / `name` / `roles` are required body fields per `api/schemas/invitation.py:InvitationCreate`. Pluck `token` out of the JSON response.
2. On the test device, open `signupflow://invitation?token=<captured-token>` (paste into Safari address bar on iOS; use `adb shell am start` on Android — see `ANDROID_RELEASE.md:130-140`).
3. App launches at the accept screen.
4. Enter a password, confirm.
5. Expected: lands directly on the volunteer dashboard (no re-login). Secure storage now has both access and refresh tokens.

(When invitation-email dispatch ships, this section will simplify to "open the invitation email on the device → tap the link" — same as the password-reset section.)

### 4. Deep-link verification

The mobile app registers the `signupflow` custom URL scheme on both
platforms — no Universal Link / App Links setup yet. Verify both
deep-link entrypoints route correctly.

For iOS, paste each URL into Safari's address bar:

```
signupflow://invitation?token=fake_test_token
signupflow://reset-password?token=fake_test_token
```

Each should launch the app at the expected screen (then bail out with
an "invalid token" message — that's fine, we're testing routing, not
acceptance).

For Android, repeat the `adb shell am start` commands from
`ANDROID_RELEASE.md` (the section "Deep-link smoke").

---

## Pass/fail checklist (paste into closeout doc)

Replace `<SHA>` with the smoked commit, `<N>` with the build number.

```
## Sprint <N> cross-platform smoke (commit <SHA>)

iOS  TestFlight build #<N>    Android  Play internal build #<N>

Volunteer journey
- [ ] Login + Keychain persistence
- [ ] Schedule renders
- [ ] Assignment Accept / Decline / Swap
- [ ] Availability add / delete
- [ ] ICS export
- [ ] Logout wipes secure storage

Admin journey
- [ ] Dashboard
- [ ] Solver run
- [ ] Solution review + edit
- [ ] Publish
- [ ] Compare
- [ ] Rollback

Sprint 9 backend integrations
- [ ] Password reset email (or N/A: backend EMAIL_ENABLED=false)
- [ ] Token refresh on expired access
- [ ] Token refresh + signOut race doesn't resurrect session
- [ ] Invitation accept lands directly in app

Deep-links (signupflow:// custom scheme on both platforms — no Universal Links yet)
- [ ] iOS signupflow:// scheme routes to in-app screen
- [ ] Android signupflow:// scheme routes to in-app screen

Issues filed:
- (link to issue or fix PR per ❌ above)
```

---

## Related

- `mobile/TESTFLIGHT.md` — iOS-specific upload + signing details.
- `mobile/ANDROID_RELEASE.md` — Android keystore + Play Console
  internal track upload + deep-link manifest detail.
- `docs/saas/SMOKE_TESTING_EMAIL.md` — backend email pipeline smoke
  (Mailtrap + SendGrid). The mobile reset-link smoke step above depends
  on this having been exercised first for the deployed backend.
