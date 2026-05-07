# TestFlight Upload Runbook

> Sprint 7 PR 7.11 · last step in the Flutter mobile sprint.
>
> The Flutter app is API-complete (Sprint 7 PR 7.0–7.10). This document is
> the human-side runbook for getting a build onto TestFlight. It needs
> sudo, Apple ID 2FA, and an Apple Developer account — all things this
> agent can't do.

---

## One-time setup

### 1. Switch xcode-select to full Xcode

```bash
sudo xcode-select -s /Applications/Xcode.app/Contents/Developer
sudo xcodebuild -license accept    # if prompted
flutter doctor -v
```

`flutter doctor` should now show iOS / Xcode green.

### 2. Install fastlane

```bash
cd mobile
gem install bundler                # if not already
bundle install                     # reads mobile/Gemfile, installs fastlane
```

If you prefer Homebrew: `brew install fastlane` works too. Drop the bundler
prefix from the commands below if you go that route.

### 3. CocoaPods

CocoaPods is required because `flutter_secure_storage` uses native iOS code.

```bash
cd mobile/ios
pod install --repo-update
```

The `Fastfile` runs this for you, but doing it once manually surfaces any
CocoaPods version issues outside the build pipeline.

### 4. Apple credentials

Two paths — pick **A** for production, **B** for first-time exploration:

#### A · App Store Connect API key (recommended)

1. Go to **App Store Connect → Users and Access → Keys**.
2. Create a key with **Developer** role.
3. Download the `.p8` file (you only get this once).
4. Note the **Key ID** and **Issuer ID** shown on the key page.

Add to your shell profile (e.g. `~/.zshrc`):

```bash
export APP_STORE_CONNECT_API_KEY_PATH="$HOME/.signupflow/AuthKey_XXXXXX.p8"
export APP_STORE_CONNECT_KEY_ID="XXXXXX"
export APP_STORE_CONNECT_ISSUER_ID="00000000-0000-0000-0000-000000000000"
```

#### B · Apple ID + app-specific password

1. Go to **appleid.apple.com → Sign-In and Security → App-Specific Passwords**.
2. Generate one labeled "SignUpFlow fastlane".
3. Set:

```bash
export APPLE_ID="you@example.com"
export FASTLANE_APP_SPECIFIC_PASSWORD="abcd-efgh-ijkl-mnop"
```

The `Fastfile` automatically falls back to this path if `APP_STORE_CONNECT_API_KEY_PATH` isn't set.

### 5. Register the app in App Store Connect (first time only)

1. **App Store Connect → My Apps → +**
2. Bundle ID: `app.signupflow.ios` (must match `mobile/ios/Runner.xcodeproj` and `mobile/fastlane/Appfile`).
3. SKU: `signupflow-ios` (any unique string).
4. Note the numeric **Apple ID** that App Store Connect assigns — should match `6767228040` in `Appfile`.

### 6. (Optional) `fastlane match` for cert + provisioning profile

If multiple machines will build, set up `fastlane match` against a private git repo. For a single dev machine, Xcode's automatic signing is fine — open `mobile/ios/Runner.xcworkspace` in Xcode once and let it provision.

---

## Per-release flow

```bash
cd mobile
bundle exec fastlane beta changelog:"Volunteer journey + admin solver flow"
```

What this does:

1. Runs `pod install --repo-update`.
2. Runs `flutter build ipa --release --build-number=<git-rev-count> --export-method=app-store`.
3. Uploads `build/ios/ipa/SignUpFlow.ipa` to TestFlight via `pilot`.
4. Skips waiting for processing (Apple's processing usually takes 5–15 min; you'll get an email).

Build number uses `git rev-list --count HEAD` so it's monotonic and never collides with prior uploads.

---

## Smoke test before upload

If you want to inspect the ipa locally first:

```bash
bundle exec fastlane build_only
```

Outputs `build/ios/ipa/SignUpFlow.ipa` without uploading. Drag it into Xcode → Window → Devices & Simulators → connected iPhone → install.

---

## On-device sanity check

Before tapping "Submit for review" on TestFlight, install the build on a real iPhone (not the developer's daily driver) and walk the volunteer journey:

1. **Login** — paste a real volunteer's credentials. Confirm Keychain saves the JWT.
2. **Schedule** — confirm the date sections render in local timezone.
3. **Assignment detail** — Accept / Decline / Swap, watch the schedule reload.
4. **Availability** — Add a TimeOff range, delete it.
5. **Profile** — Copy ICS URL, paste into Safari, verify it downloads a `.ics` file.
6. **Log out** — confirm Keychain is wiped (re-launch should hit `/login`).

Then admin journey: Dashboard → Run Solver → Solution Review → Publish → Compare → Rollback.

If anything's off, file an issue against `specs/022-flutter-mobile-app/spec.md` and add a fix PR before resubmitting.

---

## Common errors

| Error | Cause | Fix |
|---|---|---|
| `xcode-select: error: tool 'xcodebuild' requires Xcode` | Still pointing at Command Line Tools | Re-run step 1 |
| `Could not find a development team` | Xcode automatic signing not enabled | Open `Runner.xcworkspace` in Xcode → Signing & Capabilities → tick "Automatically manage signing" |
| `Pod install failed` | Stale lockfile | `cd mobile/ios && pod deintegrate && pod install` |
| `2-factor required` during `pilot` | Need app-specific password | Use path B above |
| `ipa not found at build/ios/ipa/SignUpFlow.ipa` | Flutter didn't produce an export | `flutter clean && flutter pub get` then retry |
| Upload succeeds but TestFlight says "Build is invalid" | Missing Info.plist key (push, etc.) | Read the email Apple sent; add the key in `mobile/ios/Runner/Info.plist` |

---

## What this agent did vs. what you'll do

**Already in the repo (this PR):**
- `Gemfile` pinned to fastlane 2.227.
- `fastlane/Appfile` with bundle ID, Team ID, ASC App ID.
- `fastlane/Fastfile` with `beta` (build + upload) and `build_only` (build, no upload) lanes.
- This runbook.

**You do:**
- Steps 1–6 of one-time setup (sudo, App Store Connect access, Xcode workspace open).
- `bundle exec fastlane beta` per release.
- On-device smoke test.
- Submit for App Store review (when ready beyond TestFlight).

The agent can write the changelog string, fix bugs found in smoke testing, and re-trigger CI — it just can't run the actual `xcodebuild` or talk to Apple's servers.
