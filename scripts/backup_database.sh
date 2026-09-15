#!/usr/bin/env bash
set -eu
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR/.."
exec poetry run python "$SCRIPT_DIR/sqlite_recovery.py" backup "$@"
