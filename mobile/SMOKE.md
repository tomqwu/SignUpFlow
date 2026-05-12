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

1. **Backend health:** `curl -s https://api.signupflow.io/api/config/safe-flags | jq` returns 200 with the expected feature flags (`EMAIL_ENABLED=true` only after #85's smoke runbook is exercised, per `docs/saas/SMOKE_TESTING_EMAIL.md`). For staging, swap the host.
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
   - **iOS:** the Universal Link should route into the app's reset-password screen.
   - **Android:** the `signupflow://reset-password?token=...` link should route into the app.
5. Set a new password. Confirm.
6. Login with the new password succeeds.

### 2. Token refresh interceptor (#79 + #82)

1. Login as the volunteer.
2. Use the app for >24h OR manually expire the access token (set device clock forward, or have an admin force-rotate the user's `refresh_token_version` on the backend).
3. Open the app → tap a screen that makes an API call.
4. Expected: app silently refreshes (no /login prompt). Look in device logs (Xcode console / `adb logcat | grep dio`) for the single `/auth/refresh` round-trip.
5. **Edge case:** tap "Sign out" immediately as a refresh is in flight (this is the #82 P2 race). Expected: app lands on /login. Verify secure storage is empty (re-launch lands on /login, not back into the session).

### 3. Invitation accept JWT pair (#84)

1. As admin, create an invitation for a new email.
2. Open the invitation email on the device.
3. Tap the link → the app launches, accept screen renders.
4. Enter a password, confirm.
5. Expected: lands directly on the volunteer dashboard (no re-login). Secure storage now has both access and refresh tokens.

### 4. Deep-link verification

Already covered for Android in `ANDROID_RELEASE.md`'s "Deep-link smoke"
section. For iOS, manually fire the Universal Link via Safari address
bar:

```
signupflow://invitation?token=fake_test_token
signupflow://reset-password?token=fake_test_token
```

Each should launch the app at the expected screen.

For Android, repeat the `adb shell am start` commands from
`ANDROID_RELEASE.md:130-140`.

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

Deep-links
- [ ] iOS Universal Link routes to in-app screen
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
