# Android Release Runbook

> Sprint 9 PR 9.5+ — first Android internal release.
>
> Counterpart to `mobile/TESTFLIGHT.md` (iOS). The Flutter codebase ships
> the same Dart UI on both platforms; only the build / signing /
> distribution pipeline differs.

---

## One-time setup

### 1. Java 17 + Android SDK

Flutter Android builds need JDK 17 and the Android SDK / NDK. Install via
Homebrew or Android Studio. `flutter doctor` should show Android green.

### 2. Generate the release keystore

```bash
keytool -genkey -v \
  -keystore $HOME/keystores/signupflow-android.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias upload
```

The keystore lives **outside** the repo (gitignored). Back it up — the Play
Console will reject builds signed with a different key once you've published
to a track. **Losing this file = re-publishing the app under a new package
ID.**

### 3. Configure `mobile/android/key.properties`

Copy `mobile/android/key.properties.example` to `mobile/android/key.properties`
(gitignored) and fill in the values from step 2:

```
storeFile=/Users/you/keystores/signupflow-android.jks
storePassword=your-store-password
keyAlias=upload
keyPassword=your-key-password
```

If `key.properties` is absent, release builds **fall back to debug signing**
so dev `flutter run --release` keeps working — the gradle build doesn't fail.

### 4. Application id

Already set in `mobile/android/app/build.gradle.kts`:
- `applicationId = "app.signupflow.android"`
- `namespace = "app.signupflow.android"`

This pairs with iOS's `app.signupflow.ios` under the shared `app.signupflow.*`
prefix. Reserve the package on Google Play Console under that name.

---

## Per-release flow

### Build a signed `.aab`

```bash
cd mobile
flutter build appbundle --release
```

Output: `mobile/build/app/outputs/bundle/release/app-release.aab` (signed
with the release keystore when `key.properties` exists).

### Smoke-install on a device / emulator

```bash
flutter build apk --release
adb install -r mobile/build/app/outputs/flutter-apk/app-release.apk
```

Then walk the volunteer + admin journeys (mirror the iOS smoke checklist
in `mobile/TESTFLIGHT.md`).

### Upload to Play Console internal testing

(Sprint 9 PR 9.6 will add a Fastlane lane for this. Until then, manual:)

1. Play Console → SignUpFlow → Internal testing → Create new release.
2. Upload `app-release.aab`.
3. Add release notes.
4. Roll out → Internal testing.

### Deep-link smoke

Verify the `signupflow://` URL scheme registers correctly on a real device:

```bash
adb shell am start -a android.intent.action.VIEW \
  -d "signupflow://invitation?token=fake_test_token"
```

Should open the app at the invitation screen. Same for password reset:

```bash
adb shell am start -a android.intent.action.VIEW \
  -d "signupflow://reset-password?token=fake_test_token"
```

---

## Build history

(populated as releases ship)

| Version code | Sprint | Track | Changelog |
|--------------|--------|-------|-----------|
| _none yet_   | 9      | internal | first internal release after Sprint 9 |

---

## Common gotchas

| Symptom | Fix |
|---------|-----|
| Gradle: "key.properties not found" but builds fall back to debug | Expected when keystore isn't configured. Add `mobile/android/key.properties` to enable release signing. |
| Play Console: "Upload failed because you uploaded an APK that is signed with a different signing key" | You used a different keystore than the prior release. Restore the original `signupflow-android.jks` from backup. |
| Deep link doesn't open the app | Verify `<intent-filter>` with `android:scheme="signupflow"` is present in `mobile/android/app/src/main/AndroidManifest.xml`. |
| `applicationId` mismatch with Play Console listing | Both must be `app.signupflow.android`. The Play Console listing is created once and immutable. |

---

## Where the agent stops, where you start

**The agent can:**
- Edit `build.gradle.kts`, `AndroidManifest.xml`, `key.properties.example`.
- Run `flutter build appbundle --release` (no human input needed).
- Run `bundle exec fastlane android internal` (Sprint 9 PR 9.6+).

**You do:**
- Generate + back up the keystore (step 2).
- Fill in `key.properties` with the keystore secrets (step 3).
- Create the Play Console listing + add testers (Sprint 9 PR 9.6).
- Generate the Google Cloud service-account JSON key for the Fastlane upload (PR 9.6).
- Copy the `app-release.aab` to a real device for smoke testing.
