#!/bin/bash

echo "======================================================================"
echo "ROSTIO - COMPLETE TEST SUITE"
echo "======================================================================"
echo ""
echo "This will run all automated tests for the Roster scheduling system."
echo ""

# Check if server is running
echo "🔍 Checking if API server is running..."
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ ERROR: API server is not running on port 8000"
    echo ""
    echo "To start the server and run tests:"
    echo "  # Clean environment"
    echo "  pkill -f uvicorn"
    echo "  rm -f roster.db"
    echo ""
    echo "  # Start server"
    echo "  poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 &"
    echo "  sleep 3"
    echo ""
    echo "  # Run tests"
    echo "  ./run_all_tests.sh"
    echo ""
    exit 1
fi

echo "✅ API server is running"
echo ""

# Clean up old test database and restart
echo "🧹 Cleaning test environment..."
echo "   ⚠️  This will:"
echo "   - Kill all uvicorn servers"
echo "   - Delete roster.db"
echo "   - Restart fresh server"
echo ""
read -p "   Continue? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled. Running tests with existing data..."
    echo ""
else
    # Kill servers
    pkill -f uvicorn 2>/dev/null
    sleep 1

    # Delete database
    rm -f roster.db
    echo "   ✅ Database cleaned"

    # Restart server
    poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &
    SERVER_PID=$!
    echo "   ✅ Server restarted (PID: $SERVER_PID)"

    # Wait for server
    echo "   ⏳ Waiting for server to initialize..."
    sleep 5

    # Verify server is up
    if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "   ❌ ERROR: Server failed to start"
        exit 1
    fi
    echo "   ✅ Server ready"
    echo ""
fi

# Run API tests
echo "======================================================================"
echo "1️⃣  API TESTS"
echo "======================================================================"
poetry run python tests/test_api_complete.py
API_RESULT=$?

echo ""
echo ""

# Run GUI tests
echo "======================================================================"
echo "2️⃣  GUI TESTS (Automated)"
echo "======================================================================"
poetry run python tests/test_gui_automated.py
GUI_RESULT=$?

echo ""
echo ""

# Summary
echo "======================================================================"
echo "FINAL SUMMARY"
echo "======================================================================"

if [ $API_RESULT -eq 0 ]; then
    echo "✅ API Tests: PASSED"
else
    echo "❌ API Tests: FAILED"
fi

if [ $GUI_RESULT -eq 0 ]; then
    echo "✅ GUI Tests: PASSED"
else
    echo "❌ GUI Tests: FAILED"
fi

echo ""

if [ $API_RESULT -eq 0 ] && [ $GUI_RESULT -eq 0 ]; then
    echo "🎉 ALL TESTS PASSED!"
    echo ""
    echo "Next steps:"
    echo "  • Manual GUI testing: tests/test_gui_manual.md"
    echo "  • Open application: http://localhost:8000/frontend/index.html"
    echo ""
    exit 0
else
    echo "⚠️  SOME TESTS FAILED"
    echo ""
    echo "Please review the output above for details."
    echo ""
    exit 1
fi
