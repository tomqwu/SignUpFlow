#!/bin/bash
# Run all E2E tests with screenshots and reports

echo "🧪 Running Rostio E2E Test Suite"
echo "=================================="
echo ""

# Create screenshots directory
mkdir -p /tmp/e2e-screenshots

# Run tests with verbose output
echo "📋 Running authentication flow tests..."
poetry run pytest tests/e2e/test_auth_flows.py -v -s --tb=short

echo ""
echo "📋 Running login flow tests..."
poetry run pytest tests/e2e/test_login_flow.py -v -s --tb=short

echo ""
echo "📋 Running invitation flow tests..."
poetry run pytest tests/e2e/test_invitation_flow.py -v -s --tb=short

echo ""
echo "📋 Running calendar feature tests..."
poetry run pytest tests/e2e/test_calendar_features.py -v -s --tb=short

echo ""
echo "📋 Running admin console tests..."
poetry run pytest tests/e2e/test_admin_console.py -v -s --tb=short

echo ""
echo "📋 Running user feature tests..."
poetry run pytest tests/e2e/test_user_features.py -v -s --tb=short

echo ""
echo "=================================="
echo "✅ E2E Test Suite Complete"
echo ""
echo "📸 Screenshots saved to /tmp/"
echo "   View them to see UI state at each test point"
