#!/bin/sh
# Keep the declared process as PID 1 so signals and exit codes are preserved.
set -e
exec "$@"
