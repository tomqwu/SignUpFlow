#!/usr/bin/env bash
set -euo pipefail

# Helper to start a FastAPI uvicorn server for test runs, wait for readiness,
# execute the provided command, and ensure the server is cleaned up.

TEST_SERVER_HOST=${TEST_SERVER_HOST:-0.0.0.0}
TEST_SERVER_PORT=${TEST_SERVER_PORT:-8000}
TEST_SERVER_HEALTH_PATH=${TEST_SERVER_HEALTH_PATH:-/health}
TEST_SERVER_READY_TIMEOUT=${TEST_SERVER_READY_TIMEOUT:-30}
TEST_SERVER_READY_INTERVAL=${TEST_SERVER_READY_INTERVAL:-1}
TEST_SERVER_CMD=${TEST_SERVER_CMD:-"poetry run uvicorn api.main:app --host ${TEST_SERVER_HOST} --port ${TEST_SERVER_PORT} --reload"}
TEST_COMMAND_TIMEOUT=${TEST_COMMAND_TIMEOUT:-0}
TEST_SERVER_KEEP_ALIVE=${TEST_SERVER_KEEP_ALIVE:-0}
TEST_SERVER_LOG=${TEST_SERVER_LOG:-/tmp/test-server.log}

cleanup() {
	if [[ -n "${SPAWNED_SERVER_PID:-}" ]]; then
		if ps -p "${SPAWNED_SERVER_PID}" >/dev/null 2>&1; then
			# Kill child processes first (uvicorn --reload spawns workers)
			pkill -P "${SPAWNED_SERVER_PID}" >/dev/null 2>&1 || true
			kill "${SPAWNED_SERVER_PID}" >/dev/null 2>&1 || true
			wait "${SPAWNED_SERVER_PID}" >/dev/null 2>&1 || true
		fi
	fi
}

trap cleanup EXIT INT TERM

require_cmd() {
	if ! command -v "$1" >/dev/null 2>&1; then
		echo "❌ Missing required command: $1" >&2
		exit 127
	fi
}

require_cmd curl

if [[ $# -eq 0 ]]; then
	echo "Usage: $0 <command...>" >&2
	exit 64
fi

SERVER_ALREADY_RUNNING=0
if curl -s "http://${TEST_SERVER_HOST}:${TEST_SERVER_PORT}${TEST_SERVER_HEALTH_PATH}" >/dev/null 2>&1; then
	SERVER_ALREADY_RUNNING=1
else
	echo "⚠️  Test server not running. Launching..."
	rm -f "${TEST_SERVER_LOG}"
	nohup bash -lc "${TEST_SERVER_CMD}" >"${TEST_SERVER_LOG}" 2>&1 &
	SPAWNED_SERVER_PID=$!

	elapsed=0
	while ! curl -s "http://${TEST_SERVER_HOST}:${TEST_SERVER_PORT}${TEST_SERVER_HEALTH_PATH}" >/dev/null 2>&1; do
		if (( elapsed >= TEST_SERVER_READY_TIMEOUT )); then
			echo "❌ Server failed to become ready within ${TEST_SERVER_READY_TIMEOUT}s" >&2
			if [[ -f "${TEST_SERVER_LOG}" ]]; then
				echo "---- Server Log ----"
				cat "${TEST_SERVER_LOG}" >&2 || true
				echo "---------------------"
			fi
			exit 1
		fi
		sleep "${TEST_SERVER_READY_INTERVAL}"
		elapsed=$((elapsed + TEST_SERVER_READY_INTERVAL))
	done

	echo "✅ Test server ready (PID ${SPAWNED_SERVER_PID})"
fi

# Run the requested command (optional timeout)
if (( TEST_COMMAND_TIMEOUT > 0 )); then
	require_cmd timeout
	timeout --preserve-status "${TEST_COMMAND_TIMEOUT}" "$@"
	EXIT_CODE=$?
else
	"$@"
	EXIT_CODE=$?
fi

if (( EXIT_CODE != 0 )); then
	echo "❌ Test command failed with status ${EXIT_CODE}"
	if command -v bash >/dev/null 2>&1 && [ -f "./scripts/collect_test_logs.sh" ]; then
		./scripts/collect_test_logs.sh || true
	else
		if [[ -f "${TEST_SERVER_LOG}" ]]; then
			echo "---- Test Server Log (tail) ----"
			tail -n 200 "${TEST_SERVER_LOG}" || true
			echo "--------------------------------"
		fi
	fi
fi

# Only tear down the server if we started it and KEEP_ALIVE is disabled.
if (( SERVER_ALREADY_RUNNING == 1 || TEST_SERVER_KEEP_ALIVE == 1 )); then
	SPAWNED_SERVER_PID=""
fi

exit "${EXIT_CODE}"
