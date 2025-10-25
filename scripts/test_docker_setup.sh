#!/bin/bash
# Test script for Docker Compose development environment
# This script validates that all Docker Compose features work correctly

set -e  # Exit on any error

echo "================================================"
echo "SignUpFlow Docker Development Environment Test"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to print test result
test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC}: $2"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}: $2"
        ((TESTS_FAILED++))
    fi
}

# Function to wait for service to be healthy
wait_for_health() {
    local service=$1
    local max_attempts=30
    local attempt=0

    echo "Waiting for $service to be healthy..."
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose -f docker-compose.dev.yml ps | grep "$service" | grep -q "healthy"; then
            return 0
        fi
        sleep 2
        ((attempt++))
    done
    return 1
}

echo "Test 1: Check Docker is running"
if docker info > /dev/null 2>&1; then
    test_result 0 "Docker daemon is running"
else
    test_result 1 "Docker daemon is not running - please start Docker Desktop"
    exit 1
fi
echo ""

echo "Test 2: Validate docker-compose.dev.yml syntax"
if docker-compose -f docker-compose.dev.yml config --quiet 2>&1 | grep -q "variable is not set"; then
    test_result 0 "docker-compose.dev.yml syntax valid (optional env vars not set - OK)"
else
    docker-compose -f docker-compose.dev.yml config --quiet
    if [ $? -eq 0 ]; then
        test_result 0 "docker-compose.dev.yml syntax valid"
    else
        test_result 1 "docker-compose.dev.yml has syntax errors"
        exit 1
    fi
fi
echo ""

echo "Test 3: Build Docker images"
if docker-compose -f docker-compose.dev.yml build; then
    test_result 0 "Docker images built successfully"
else
    test_result 1 "Docker image build failed"
    exit 1
fi
echo ""

echo "Test 4: Start services (PostgreSQL + Redis + API)"
if docker-compose -f docker-compose.dev.yml up -d; then
    test_result 0 "Services started"
else
    test_result 1 "Failed to start services"
    exit 1
fi
echo ""

echo "Test 5: Wait for PostgreSQL to be healthy"
if wait_for_health "db"; then
    test_result 0 "PostgreSQL is healthy"
else
    test_result 1 "PostgreSQL failed to become healthy"
fi
echo ""

echo "Test 6: Wait for Redis to be healthy"
if wait_for_health "redis"; then
    test_result 0 "Redis is healthy"
else
    test_result 1 "Redis failed to become healthy"
fi
echo ""

echo "Test 7: Wait for API to be healthy"
sleep 10  # Give API extra time to start
if wait_for_health "api"; then
    test_result 0 "API is healthy"
else
    test_result 1 "API failed to become healthy"
fi
echo ""

echo "Test 8: Check API health endpoint"
sleep 5
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    test_result 0 "API health endpoint responding"
else
    test_result 1 "API health endpoint not responding"
fi
echo ""

echo "Test 9: Check PostgreSQL connection from API"
HEALTH_JSON=$(curl -s http://localhost:8000/health)
if echo "$HEALTH_JSON" | grep -q '"database":"connected"'; then
    test_result 0 "API connected to PostgreSQL"
else
    test_result 1 "API cannot connect to PostgreSQL"
    echo "Health response: $HEALTH_JSON"
fi
echo ""

echo "Test 10: Test PostgreSQL shell access"
if docker-compose -f docker-compose.dev.yml exec -T db psql -U signupflow -d signupflow_dev -c "SELECT 1;" > /dev/null 2>&1; then
    test_result 0 "PostgreSQL shell access works"
else
    test_result 1 "PostgreSQL shell access failed"
fi
echo ""

echo "Test 11: Test Redis CLI access"
if docker-compose -f docker-compose.dev.yml exec -T redis redis-cli -a dev_redis_password PING 2>/dev/null | grep -q "PONG"; then
    test_result 0 "Redis CLI access works"
else
    test_result 1 "Redis CLI access failed"
fi
echo ""

echo "Test 12: Run database migrations"
if docker-compose -f docker-compose.dev.yml exec -T api alembic upgrade head > /dev/null 2>&1; then
    test_result 0 "Database migrations completed"
else
    test_result 1 "Database migrations failed"
fi
echo ""

echo "Test 13: Verify database tables created"
TABLE_COUNT=$(docker-compose -f docker-compose.dev.yml exec -T db psql -U signupflow -d signupflow_dev -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | xargs)
if [ "$TABLE_COUNT" -gt 5 ]; then
    test_result 0 "Database tables created (found $TABLE_COUNT tables)"
else
    test_result 1 "Database tables not created (found $TABLE_COUNT tables)"
fi
echo ""

echo "Test 14: Test API bash shell access"
if docker-compose -f docker-compose.dev.yml exec -T api bash -c "echo test" | grep -q "test"; then
    test_result 0 "API bash shell access works"
else
    test_result 1 "API bash shell access failed"
fi
echo ""

echo "Test 15: Test running tests in Docker"
if docker-compose -f docker-compose.dev.yml exec -T api pytest tests/unit/test_calendar.py -v --tb=short > /dev/null 2>&1; then
    test_result 0 "Tests run successfully in Docker"
else
    test_result 1 "Tests failed in Docker"
fi
echo ""

echo "Test 16: Check volume mounts (code hot-reload)"
if docker-compose -f docker-compose.dev.yml exec -T api ls /app/api/main.py > /dev/null 2>&1; then
    test_result 0 "Code volumes mounted correctly"
else
    test_result 1 "Code volumes not mounted"
fi
echo ""

echo "Test 17: View API logs"
LOG_OUTPUT=$(docker-compose -f docker-compose.dev.yml logs api --tail=10 2>&1)
if echo "$LOG_OUTPUT" | grep -q "Uvicorn running"; then
    test_result 0 "API logs accessible"
else
    test_result 1 "API logs not accessible or API not started"
fi
echo ""

echo "Test 18: Check service status"
if docker-compose -f docker-compose.dev.yml ps | grep -q "Up"; then
    test_result 0 "Services are running"
else
    test_result 1 "Services are not running"
fi
echo ""

echo "================================================"
echo "Test Summary"
echo "================================================"
echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed! Docker environment is working correctly.${NC}"
    echo ""
    echo "You can now:"
    echo "  - View logs:      make logs"
    echo "  - Open shell:     make shell"
    echo "  - Run tests:      make test-docker"
    echo "  - Stop services:  make down"
    echo ""
    EXIT_CODE=0
else
    echo -e "${RED}❌ Some tests failed. Please review the errors above.${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  - View logs:      docker-compose -f docker-compose.dev.yml logs"
    echo "  - Check services: docker-compose -f docker-compose.dev.yml ps"
    echo "  - Restart:        docker-compose -f docker-compose.dev.yml restart"
    echo ""
    EXIT_CODE=1
fi

# Ask user if they want to keep services running
echo -n "Keep services running? (y/n): "
read -r response
if [[ "$response" != "y" ]] && [[ "$response" != "Y" ]]; then
    echo ""
    echo "Stopping services..."
    docker-compose -f docker-compose.dev.yml down
    echo "Services stopped."
fi

exit $EXIT_CODE
