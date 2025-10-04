#!/bin/bash

# Rostio Cleanup and Test Script
# Kills all zombie processes, starts fresh server, runs comprehensive tests

set -e

echo "=================================================="
echo "ROSTIO CLEANUP AND TEST SUITE"
echo "=================================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Kill all zombie processes
echo -e "\n${YELLOW}[1/5] Killing zombie processes...${NC}"
pkill -9 -f "uvicorn" 2>/dev/null || true
pkill -9 -f "python.*api.main" 2>/dev/null || true
sleep 2

zombie_count=$(ps aux | grep -E "uvicorn|python.*api.main" | grep -v grep | wc -l)
if [ $zombie_count -eq 0 ]; then
    echo -e "${GREEN}✓ All zombie processes killed${NC}"
else
    echo -e "${RED}✗ Warning: $zombie_count processes still running${NC}"
fi

# Step 2: Clean up old test artifacts
echo -e "\n${YELLOW}[2/5] Cleaning old test artifacts...${NC}"
rm -f /tmp/blocked_dates_gui_test.png
rm -f /tmp/current_gui_state.png
rm -f /tmp/assignment_modal.png
rm -f /tmp/*.log
echo -e "${GREEN}✓ Artifacts cleaned${NC}"

# Step 3: Start fresh server
echo -e "\n${YELLOW}[3/5] Starting fresh server...${NC}"
cd /home/ubuntu/rostio
poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/test_server.log 2>&1 &
SERVER_PID=$!
echo "Server PID: $SERVER_PID"
sleep 5

# Check if server is running
if ps -p $SERVER_PID > /dev/null; then
    echo -e "${GREEN}✓ Server started successfully${NC}"
else
    echo -e "${RED}✗ Server failed to start${NC}"
    cat /tmp/test_server.log
    exit 1
fi

# Wait for server to be ready
echo "Waiting for server to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/organizations/ > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Server is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}✗ Server did not start in time${NC}"
        cat /tmp/test_server.log
        exit 1
    fi
    sleep 1
done

# Step 4: Run comprehensive tests
echo -e "\n${YELLOW}[4/5] Running comprehensive test suite...${NC}"
poetry run pytest tests/comprehensive_test_suite.py -v --tb=short

TEST_RESULT=$?

# Step 5: Generate coverage report
echo -e "\n${YELLOW}[5/5] Test Results Summary${NC}"

if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}✓ ALL TESTS PASSED${NC}"
    echo -e "${GREEN}================================${NC}"
else
    echo -e "${RED}================================${NC}"
    echo -e "${RED}✗ SOME TESTS FAILED${NC}"
    echo -e "${RED}================================${NC}"
fi

echo ""
echo "Server is still running with PID: $SERVER_PID"
echo "To stop the server, run: kill $SERVER_PID"
echo ""
echo "Server logs: /tmp/test_server.log"
echo ""

exit $TEST_RESULT
