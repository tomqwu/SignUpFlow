#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

if [[ "${1:-}" == "--dry-run" ]]; then
    echo "make test-all"
    exit 0
fi
if [[ $# -ne 0 ]]; then
    echo "Usage: scripts/cleanup_and_test.sh [--dry-run]" >&2
    exit 2
fi

cd "$REPO_ROOT"
exec make test-all
