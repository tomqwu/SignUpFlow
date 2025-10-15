#!/bin/bash
# Check test status - shows summary of passed/failed/skipped tests

set +e  # Don't exit on error

echo "================================"
echo "   CHECKING TEST STATUS"
echo "================================"
echo ""

# Run E2E tests with short timeout and capture results
echo "Running E2E tests (30s timeout per test)..."
timeout 120 poetry run pytest tests/e2e/ -v --tb=line -x 2>&1 > /tmp/e2e_test_results.txt
E2E_EXIT=$?

# Extract summary
echo ""
echo "E2E Test Results:"
echo "================================"
grep -E "(PASSED|FAILED|SKIPPED|ERROR)" /tmp/e2e_test_results.txt | tail -20
echo ""
grep -E "passed|failed|skipped|error" /tmp/e2e_test_results.txt | tail -3

echo ""
echo "================================"
echo ""

exit $E2E_EXIT
