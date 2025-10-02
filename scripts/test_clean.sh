#!/bin/bash
# Simple script to run tests with clean database

echo "🧹 Cleaning environment..."
pkill -f uvicorn 2>/dev/null
rm -f roster.db
sleep 1

echo "🚀 Starting server..."
poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 > /tmp/roster_server.log 2>&1 &
SERVER_PID=$!
sleep 5

echo "✅ Server started (PID: $SERVER_PID)"
echo ""

echo "======================================================================"
echo "RUNNING TESTS"
echo "======================================================================"
echo ""

poetry run python tests/test_api_complete.py

echo ""
echo "======================================================================"
echo "Server is still running on http://localhost:8000"
echo "To stop: kill $SERVER_PID"
echo "To view GUI: http://localhost:8000/frontend/index.html"
echo "======================================================================"
