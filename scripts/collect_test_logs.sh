#!/usr/bin/env bash
set -euo pipefail

LINES=${1:-200}
LOG_FILE=${TEST_SERVER_LOG:-/tmp/test-server.log}

echo "==================== Test Log Collection ===================="

if [[ -f "${LOG_FILE}" ]]; then
	echo "--- Uvicorn Test Server (last ${LINES} lines) ---"
	tail -n "${LINES}" "${LOG_FILE}" || true
	echo "-------------------------------------------------"
else
	echo "ℹ️  No test server log found at ${LOG_FILE}"
fi

# Capture Docker logs if Docker is available
if command -v docker >/dev/null 2>&1; then
	if docker info >/dev/null 2>&1; then
		if docker compose -f docker-compose.dev.yml ps >/dev/null 2>&1; then
			echo "--- Docker API container logs (last ${LINES} lines) ---"
			docker compose -f docker-compose.dev.yml logs api --tail "${LINES}" || true
			echo "---------------------------------------------------------"
		else
			echo "ℹ️  Docker Compose project not running; skipping container logs"
		fi
	else
		echo "ℹ️  Docker daemon unreachable; skipping container logs"
	fi
else
	echo "ℹ️  Docker CLI not installed; skipping container logs"
fi

echo "================ End Test Log Collection ================="
exit 0
