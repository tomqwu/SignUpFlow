.PHONY: run dev setup install migrate test test-frontend test-backend test-integration test-all test-coverage clean help

# Run the development server
run:
	@echo "🚀 Starting Rostio development server..."
	@poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Alias for run
dev: run

# First-time setup (install + migrate)
setup: install migrate
	@echo ""
	@echo "✅ Setup complete! Run 'make run' to start the server."
	@echo "   Visit http://localhost:8000"
	@echo ""
	@echo "   Default admin account:"
	@echo "   Email: jane@test.com"
	@echo "   Password: password"
	@echo ""

# Install all dependencies
install:
	@echo "📦 Installing dependencies..."
	@poetry install
	@npm install
	@echo "✅ Dependencies installed"

# Run database migrations
migrate:
	@echo "🔄 Running database migrations..."
	@poetry run python migrate_timezone.py
	@poetry run python migrate_invitations.py
	@echo "✅ Migrations complete"

# Run all tests
test: test-frontend test-backend

# Run frontend JavaScript tests
test-frontend:
	@echo "🧪 Running frontend tests..."
	@npm test

# Run backend Python tests
test-backend:
	@echo "🧪 Running backend tests..."
	@poetry run pytest tests/comprehensive_test_suite.py -v --tb=short

# Run integration tests
test-integration:
	@echo "🧪 Running integration tests..."
	@poetry run pytest tests/test_i18n_integration.py -v --tb=short

# Run ALL tests (frontend + backend + integration)
test-all:
	@echo "🚀 Running complete test suite..."
	@echo ""
	@echo "================================"
	@echo "   FRONTEND TESTS"
	@echo "================================"
	@npm test
	@echo ""
	@echo "================================"
	@echo "   BACKEND TESTS"
	@echo "================================"
	@poetry run pytest tests/comprehensive_test_suite.py -v --tb=short
	@echo ""
	@echo "================================"
	@echo "   INTEGRATION TESTS"
	@echo "================================"
	@poetry run pytest tests/test_i18n_integration.py -v --tb=short

# Run tests with coverage
test-coverage:
	@echo "📊 Generating test coverage reports..."
	@npm run test:coverage
	@poetry run pytest tests/ --cov=api --cov-report=html --cov-report=term

# Clean test artifacts
clean:
	@echo "🧹 Cleaning test artifacts..."
	@rm -rf node_modules/.cache
	@rm -rf coverage
	@rm -rf htmlcov
	@rm -rf .pytest_cache
	@rm -rf test_roster.db
	@echo "✅ Clean complete"

# Quick pre-commit test (fast tests only)
pre-commit:
	@echo "⚡ Running fast pre-commit tests..."
	@npm test -- --bail
	@poetry run pytest tests/ -x --tb=short -m "not slow"
	@echo "✅ Pre-commit tests passed!"

# Help (default target)
.DEFAULT_GOAL := help

help:
	@echo "Rostio Commands:"
	@echo ""
	@echo "Getting Started:"
	@echo "  make setup            - First-time setup (install + migrate)"
	@echo "  make run              - Start development server (localhost:8000)"
	@echo ""
	@echo "Development:"
	@echo "  make dev              - Alias for 'make run'"
	@echo "  make install          - Install all dependencies (poetry + npm)"
	@echo "  make migrate          - Run database migrations"
	@echo ""
	@echo "Testing:"
	@echo "  make test             - Run frontend + backend tests"
	@echo "  make test-frontend    - Run frontend JavaScript tests only"
	@echo "  make test-backend     - Run backend Python tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-all         - Run ALL tests (complete suite)"
	@echo "  make test-coverage    - Run tests with coverage reports"
	@echo "  make pre-commit       - Run fast tests for pre-commit hook"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean            - Clean test artifacts"
	@echo "  make help             - Show this help message"
	@echo ""
