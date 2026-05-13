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

echo "==> Resolving Flutter device target"
DEVICES_JSON=$(flutter devices --machine 2>/dev/null || echo "[]")

# Pick an iOS simulator if present; else first Android device; else bail.
TARGET_DEVICE=$(printf '%s' "$DEVICES_JSON" | python3 -c '
import json, sys
devs = json.load(sys.stdin)
ios = [d for d in devs if d.get("platformType") == "ios" and d.get("emulator")]
android = [d for d in devs if d.get("platformType") == "android"]
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
exec flutter test "$TEST_TARGET" -d "$TARGET_DEVICE"
