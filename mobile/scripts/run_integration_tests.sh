#!/bin/bash
# run_integration_tests.sh — invoke Flutter integration_test/ on whichever
# device target is available. Tries iOS simulator first (faster startup on
# macOS), falls back to Android emulator if `flutter devices` reports one.
#
# This is operator-invoked. CI does NOT run integration tests (device-
# dependent + slow). Local smoke only.
#
# Usage:
#   ./mobile/scripts/run_integration_tests.sh                 # default test glob
#   ./mobile/scripts/run_integration_tests.sh integration_test/foo_test.dart

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
MOBILE_DIR=$(cd "$SCRIPT_DIR/.." && pwd)
cd "$MOBILE_DIR"

TEST_TARGET="${1:-integration_test/}"
FLUTTER="${FLUTTER:-flutter}"

echo "==> Resolving Flutter device target"
DEVICES_JSON=$("$FLUTTER" devices --machine 2>/dev/null || echo "[]")

# Pick an iOS simulator if present; else first Android device; else bail.
# `flutter devices --machine` emits `targetPlatform` (e.g. "ios",
# "android-arm64", "android-x64") + `emulator` (bool). platformType is
# NOT in the device listing's JSON shape.
TARGET_DEVICE=$(printf '%s' "$DEVICES_JSON" | python3 -c '
import json, sys
devs = json.load(sys.stdin)
def is_ios_sim(d):
    return d.get("targetPlatform") == "ios" and d.get("emulator")
def is_android(d):
    tp = d.get("targetPlatform") or ""
    return tp.startswith("android")
ios = [d for d in devs if is_ios_sim(d)]
android = [d for d in devs if is_android(d)]
pick = (ios + android)[:1]
print(pick[0]["id"] if pick else "")
')

if [ -z "$TARGET_DEVICE" ]; then
  echo "ERROR: no iOS simulator or Android emulator/device available." >&2
  echo "Start one first:" >&2
  echo "  - iOS:     open -a Simulator" >&2
  echo "  - Android: emulator -avd <name>  (list with: emulator -list-avds)" >&2
  exit 1
fi

echo "==> Running integration tests on device: $TARGET_DEVICE"
echo "    Target: $TEST_TARGET"

TEST_FILES=()
if [ -d "$TEST_TARGET" ]; then
  while IFS= read -r test_file; do
    TEST_FILES+=("$test_file")
  done < <(find "$TEST_TARGET" -type f -name '*_test.dart' -print | sort)
else
  TEST_FILES+=("$TEST_TARGET")
fi

if [ "${#TEST_FILES[@]}" -eq 0 ]; then
  echo "ERROR: no integration test files found under $TEST_TARGET." >&2
  exit 1
fi

for test_file in "${TEST_FILES[@]}"; do
  echo "==> Running: $test_file"
  "$FLUTTER" test "$test_file" -d "$TARGET_DEVICE"
done
