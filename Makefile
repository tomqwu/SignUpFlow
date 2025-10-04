.PHONY: help test test-unit test-integration test-e2e test-gui test-all clean server kill-servers setup

# Default target
help:
	@echo "Rostio - Makefile Commands"
	@echo "=========================="
	@echo "make setup          - Install dependencies"
	@echo "make server         - Start development server"
	@echo "make kill-servers   - Kill all running servers"
	@echo "make test           - Run all tests"
	@echo "make test-unit      - Run unit tests only"
	@echo "make test-integration - Run integration tests only"
	@echo "make test-e2e       - Run end-to-end tests only"
	@echo "make test-gui       - Run GUI tests only"
	@echo "make test-quick     - Run quick test suite (unit + integration)"
	@echo "make clean          - Clean up temporary files"

# Install dependencies
setup:
	@echo "📦 Installing dependencies..."
	poetry install
	@echo "✅ Setup complete!"

# Kill all servers
kill-servers:
	@echo "🔪 Killing all uvicorn servers..."
	-pkill -9 -f uvicorn
	@sleep 1
	@echo "✅ Servers killed"

# Start development server
server: kill-servers
	@echo "🚀 Starting Rostio server..."
	poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Clean temporary files
clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".pytest_cache" -delete
	rm -rf .pytest_cache
	rm -f /tmp/rostio*.log /tmp/test*.log /tmp/server*.log
	@echo "✅ Cleanup complete"

# Run unit tests
test-unit:
	@echo "🧪 Running Unit Tests..."
	@echo "======================="
	@rm -f roster.db
	@poetry run python -c "from api.database import engine, Base; Base.metadata.create_all(bind=engine)"
	poetry run pytest tests/unit/ -v --tb=short

# Run integration tests  
test-integration: kill-servers
	@echo "🔗 Running Integration Tests..."
	@echo "=============================="
	@poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 > /tmp/test_server.log 2>&1 & echo $$! > /tmp/test_server.pid
	@sleep 3
	@poetry run python tests/setup_test_data.py
	@poetry run pytest tests/integration/ -v --tb=short || (kill `cat /tmp/test_server.pid` 2>/dev/null; exit 1)
	@kill `cat /tmp/test_server.pid` 2>/dev/null || true
	@rm -f /tmp/test_server.pid

# Run E2E tests
test-e2e: kill-servers
	@echo "🎯 Running End-to-End Tests..."
	@echo "============================="
	@poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 > /tmp/test_server.log 2>&1 & echo $$! > /tmp/test_server.pid
	@sleep 3
	@poetry run python tests/setup_test_data.py
	@poetry run pytest tests/e2e/ -v --tb=short || (kill `cat /tmp/test_server.pid` 2>/dev/null; exit 1)
	@kill `cat /tmp/test_server.pid` 2>/dev/null || true
	@rm -f /tmp/test_server.pid

# Run GUI tests
test-gui: kill-servers
	@echo "🖥️  Running GUI Tests..."
	@echo "======================"
	@poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 > /tmp/test_server.log 2>&1 & echo $$! > /tmp/test_server.pid
	@sleep 3
	@poetry run python tests/setup_test_data.py
	@poetry run python tests/gui/test_gui_complete_coverage.py || (kill `cat /tmp/test_server.pid` 2>/dev/null; exit 1)
	@kill `cat /tmp/test_server.pid` 2>/dev/null || true
	@rm -f /tmp/test_server.pid

# Run quick tests (unit + integration)
test-quick: test-unit test-integration
	@echo "✅ Quick test suite complete!"

# Run all tests
test-all: kill-servers
	@echo ""
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║  ROSTIO - COMPLETE TEST SUITE                              ║"
	@echo "╚════════════════════════════════════════════════════════════╝"
	@echo ""
	@# Start server
	@poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 > /tmp/test_server.log 2>&1 & echo $$! > /tmp/test_server.pid
	@sleep 3
	@poetry run python tests/setup_test_data.py
	@# Run all test suites
	@$(MAKE) test-unit || (kill `cat /tmp/test_server.pid` 2>/dev/null; exit 1)
	@$(MAKE) test-integration || (kill `cat /tmp/test_server.pid` 2>/dev/null; exit 1)
	@$(MAKE) test-e2e || (kill `cat /tmp/test_server.pid` 2>/dev/null; exit 1)
	@$(MAKE) test-gui || (kill `cat /tmp/test_server.pid` 2>/dev/null; exit 1)
	@# Cleanup
	@kill `cat /tmp/test_server.pid` 2>/dev/null || true
	@rm -f /tmp/test_server.pid
	@echo ""
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║  ✅ ALL TESTS PASSED!                                      ║"
	@echo "╚════════════════════════════════════════════════════════════╝"
	@echo ""

# Alias: 'make test' runs all tests
test: test-all
