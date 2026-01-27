#!/bin/bash
# Check which user journeys have e2e test coverage
# Dynamically lists all tests in tests/e2e/

echo "======================================"
echo "E2E Test Coverage Report"
echo "======================================"
echo ""

# Run the python docstring checker
python3 scripts/check_test_docstrings.py tests/e2e

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Excellent! Test coverage documentation is complete."
    exit 0
else
    echo ""
    echo "❌ Audit failed. Please add missing docstrings."
    exit 1
fi
