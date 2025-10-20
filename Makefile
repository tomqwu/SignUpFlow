.PHONY: run dev stop restart setup install migrate test test-frontend test-backend test-integration test-e2e test-e2e-long test-e2e-file test-e2e-quick test-e2e-summary test-email test-email-unit test-all test-coverage test-unit test-unit-fast test-unit-file test-with-timing clean clean-all pre-commit help check-poetry check-npm check-python check-deps install-poetry install-npm install-deps fix-node-libs

# Auto-installation targets
install-poetry:
	@if ! command -v poetry >/dev/null 2>&1; then \
		echo "📦 Installing Poetry..."; \
		echo "   Trying official installer..."; \
		if curl -sSL https://install.python-poetry.org | python3 - 2>/dev/null; then \
			echo "✅ Poetry installed successfully!"; \
			echo "⚠️  Add Poetry to your PATH by running:"; \
			echo "   export PATH=\"\$$HOME/.local/bin:\$$PATH\""; \
			echo "   Or restart your terminal."; \
		else \
			echo "⚠️  Official installer failed. Trying pip installation..."; \
			python3 -m pip install --user poetry && \
			echo "✅ Poetry installed via pip!" && \
			echo "⚠️  You may need to add Poetry to your PATH:"; \
			echo "   export PATH=\"\$$HOME/Library/Python/3.9/bin:\$$PATH\""; \
		fi \
	else \
		echo "✅ Poetry is already installed: $$(poetry --version)"; \
	fi

install-npm:
	@if ! command -v npm >/dev/null 2>&1; then \
		echo "📦 Installing Node.js and npm..."; \
		if command -v brew >/dev/null 2>&1; then \
			brew install node && \
			echo "✅ Node.js and npm installed successfully!"; \
		else \
			echo "❌ Homebrew not found. Please install Node.js manually:"; \
			echo "   Visit: https://nodejs.org/"; \
			echo "   Or install Homebrew: /bin/bash -c \"\$$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""; \
			exit 1; \
		fi \
	else \
		echo "✅ npm is already installed: $$(npm --version)"; \
	fi
	@$(MAKE) fix-node-libs

# Fix Node.js library dependencies (simdjson issue)
fix-node-libs:
	@if command -v brew >/dev/null 2>&1 && command -v node >/dev/null 2>&1; then \
		echo "🔧 Checking Node.js library dependencies..."; \
		if ! node --version >/dev/null 2>&1; then \
			echo "⚠️  Node.js library issue detected. Reinstalling simdjson..."; \
			brew reinstall simdjson && \
			echo "✅ Node.js libraries fixed!"; \
		else \
			echo "✅ Node.js libraries OK"; \
		fi \
	fi

install-deps: install-poetry install-npm
	@echo ""
	@echo "✅ All system dependencies installed!"
	@echo ""

# Dependency checks (for commands that need them)
check-poetry:
	@command -v poetry >/dev/null 2>&1 || { \
		echo "❌ Poetry is not installed or not in PATH"; \
		echo "   Run 'make install-poetry' to install it automatically"; \
		echo "   Or install manually: curl -sSL https://install.python-poetry.org | python3 -"; \
		exit 1; \
	}

check-npm:
	@command -v npm >/dev/null 2>&1 || { \
		echo "❌ npm is not installed or not in PATH"; \
		echo "   Run 'make install-npm' to install it automatically"; \
		echo "   Or install manually: brew install node"; \
		exit 1; \
	}

check-python:
	@PY_VERSION=$$(python3 --version 2>&1 | sed 's/Python //'); \
	PY_MAJOR=$$(echo $$PY_VERSION | cut -d. -f1); \
	PY_MINOR=$$(echo $$PY_VERSION | cut -d. -f2); \
	if [ "$$PY_MAJOR" -lt 3 ] || ([ "$$PY_MAJOR" -eq 3 ] && [ "$$PY_MINOR" -lt 10 ]); then \
		echo "⚠️  Python 3.10+ required (you have: Python $$PY_VERSION)"; \
		echo "   Some features will not work with Python 3.9 or earlier"; \
		echo "   Install with: brew install python@3.11"; \
	else \
		echo "✅ Python version OK: Python $$PY_VERSION"; \
	fi

# Check all dependencies at once
check-deps:
	@echo "🔍 Checking development dependencies..."
	@echo ""
	@echo "Python:"
	@if python3 --version >/dev/null 2>&1; then \
		PY_VERSION=$$(python3 --version 2>&1 | sed 's/Python //'); \
		PY_MAJOR=$$(echo $$PY_VERSION | cut -d. -f1); \
		PY_MINOR=$$(echo $$PY_VERSION | cut -d. -f2); \
		echo "   ✅ Python installed: $$PY_VERSION"; \
		if [ "$$PY_MAJOR" -lt 3 ] || ([ "$$PY_MAJOR" -eq 3 ] && [ "$$PY_MINOR" -lt 10 ]); then \
			echo "   ⚠️  Python 3.10+ required (upgrade recommended)"; \
		else \
			echo "   ✅ Python 3.10+ detected"; \
		fi; \
	else \
		echo "   ❌ Python not found"; \
	fi
	@echo ""
	@echo "Poetry:"
	@command -v poetry >/dev/null 2>&1 && echo "   ✅ Poetry installed: $$(poetry --version)" || echo "   ❌ Poetry not installed"
	@echo ""
	@echo "npm:"
	@command -v npm >/dev/null 2>&1 && echo "   ✅ npm installed: $$(npm --version)" || echo "   ❌ npm not installed"
	@echo ""
	@echo "Node.js:"
	@command -v node >/dev/null 2>&1 && echo "   ✅ Node.js installed: $$(node --version)" || echo "   ❌ Node.js not installed"
	@echo ""
	@if ! command -v poetry >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then \
		echo "⚠️  Missing dependencies detected. Run 'make help' for installation instructions."; \
	else \
		echo "✅ All dependencies installed! You can run 'make setup' to install project packages."; \
	fi

# Run the development server
run: check-poetry
	@echo "🚀 Starting Rostio development server..."
	@poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Alias for run
dev: run

# Stop the development server
stop:
	@echo "🛑 Stopping Rostio server..."
	@-pkill -f "uvicorn api.main:app" 2>/dev/null || true
	@-lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	@echo "✅ Server stopped"

# Restart the development server
restart: stop
	@sleep 1
	@echo "🔄 Restarting server..."
	@$(MAKE) run

# First-time setup (auto-installs everything!)
setup:
	@echo "🚀 Starting Rostio setup..."
	@echo ""
	@$(MAKE) check-python
	@$(MAKE) install-deps
	@$(MAKE) install
	@$(MAKE) migrate
	@echo ""
	@echo "✅ Setup complete! Run 'make run' to start the server."
	@echo "   Visit http://localhost:8000"
	@echo ""
	@echo "   Default admin account:"
	@echo "   Email: jane@test.com"
	@echo "   Password: password"
	@echo ""

# Install project packages (poetry + npm packages)
install: check-poetry check-npm
	@echo "📦 Installing project packages..."
	@poetry install
	@npm install
	@echo "✅ Project packages installed"

# Run database migrations
migrate: check-poetry
	@echo "🔄 Running database migrations..."
	@poetry run alembic upgrade head
	@echo "✅ Migrations complete"

# Run all tests
test: test-frontend test-backend

# Run frontend JavaScript tests
test-frontend: check-npm
	@echo "🧪 Running frontend tests..."
	@npm test

# Run backend Python tests
test-backend: check-poetry
	@echo "🧪 Running backend tests..."
	@poetry run pytest tests/comprehensive_test_suite.py -v --tb=short

# Run integration tests
test-integration: check-poetry
	@echo "🧪 Running integration tests..."
	@poetry run pytest tests/test_i18n_integration.py -v --tb=short

# Run E2E tests (browser automation)
test-e2e: check-poetry
	@echo "🌐 Running E2E browser tests..."
	@echo "🔍 Checking if server is running..."
	@if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then \
		echo "⚠️  Server not running. Starting server..."; \
		poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload > /dev/null 2>&1 & \
		echo "⏳ Waiting for server to be ready..."; \
		for i in 1 2 3 4 5; do \
			sleep 1; \
			if curl -s http://localhost:8000/health > /dev/null 2>&1; then \
				echo "✅ Server ready"; \
				break; \
			fi; \
		done; \
	else \
		echo "✅ Server already running"; \
	fi
	@poetry run pytest tests/e2e/ -v --tb=short

# Run E2E tests with extended timeout (for long-running tests)
test-e2e-long: check-poetry
	@echo "🌐 Running E2E browser tests (extended timeout)..."
	@echo "🔍 Checking if server is running..."
	@if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then \
		echo "⚠️  Server not running. Starting server..."; \
		poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload > /dev/null 2>&1 & \
		echo "⏳ Waiting for server to be ready..."; \
		for i in 1 2 3 4 5; do \
			sleep 1; \
			if curl -s http://localhost:8000/health > /dev/null 2>&1; then \
				echo "✅ Server ready"; \
				break; \
			fi; \
		done; \
	else \
		echo "✅ Server already running"; \
	fi
	@timeout 600 poetry run pytest tests/e2e/ -v --tb=short

# Run specific E2E test file
test-e2e-file: check-poetry
	@echo "🌐 Running specific E2E test file..."
	@if [ -z "$(FILE)" ]; then \
		echo "❌ Usage: make test-e2e-file FILE=tests/e2e/test_name.py"; \
		exit 1; \
	fi
	@timeout 300 poetry run pytest $(FILE) -v --tb=short -s

# Run E2E tests quickly (no traceback, summary only)
test-e2e-quick: check-poetry
	@echo "🌐 Running E2E tests (quick mode - no traceback)..."
	@timeout 600 poetry run pytest tests/e2e/ -v --tb=no

# Run E2E tests and show only summary
test-e2e-summary: check-poetry
	@echo "🌐 Running E2E tests (summary only)..."
	@timeout 600 poetry run pytest tests/e2e/ -v --tb=no | grep -E "(PASSED|FAILED|test session starts|passed|failed|warning)"

# Run email invitation tests (unit tests only - no server required)
test-email-unit: check-poetry
	@echo "📧 Running email invitation unit tests..."
	@poetry run pytest tests/e2e/test_email_invitation_workflow.py::test_invitation_email_contains_correct_content tests/e2e/test_email_invitation_workflow.py::test_invitation_email_service_handles_errors -v --tb=short

# Run all email tests including E2E (requires server and Mailtrap API credentials)
test-email: check-poetry
	@echo "📧 Running all email invitation tests..."
	@echo "🔍 Checking if server is running..."
	@if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then \
		echo "⚠️  Server not running. Starting server..."; \
		poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload > /dev/null 2>&1 & \
		echo "⏳ Waiting for server to be ready..."; \
		for i in 1 2 3 4 5; do \
			sleep 1; \
			if curl -s http://localhost:8000/health > /dev/null 2>&1; then \
				echo "✅ Server ready"; \
				break; \
			fi; \
		done; \
	else \
		echo "✅ Server already running"; \
	fi
	@echo ""
	@echo "Running email tests with rate limit delays..."
	@poetry run pytest tests/e2e/test_email_invitation_workflow.py -v --tb=short

# Run ALL tests (frontend + backend + integration + E2E)
test-all: check-npm check-poetry
	@echo "🚀 Running complete test suite..."
	@echo ""
	@echo "🔍 Checking if server is running..."
	@if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then \
		echo "⚠️  Server not running. Starting server..."; \
		poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload > /dev/null 2>&1 & \
		SERVER_PID=$$!; \
		echo "⏳ Waiting for server to be ready..."; \
		for i in 1 2 3 4 5; do \
			sleep 1; \
			if curl -s http://localhost:8000/health > /dev/null 2>&1; then \
				echo "✅ Server ready (PID: $$SERVER_PID)"; \
				break; \
			fi; \
		done; \
	else \
		echo "✅ Server already running"; \
	fi
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
	@echo ""
	@echo "================================"
	@echo "   E2E BROWSER TESTS"
	@echo "================================"
	@poetry run pytest tests/e2e/ -v --tb=short

# Run tests with coverage
test-coverage: check-npm check-poetry
	@echo "📊 Generating test coverage reports..."
	@npm run test:coverage
	@poetry run pytest tests/ --cov=api --cov-report=html --cov-report=term

# Run unit tests
test-unit: check-poetry
	@echo "🧪 Running unit tests..."
	@poetry run pytest tests/unit/ -v --tb=short

# Run specific unit test file
test-unit-file: check-poetry
	@echo "🧪 Running specific unit test file..."
	@if [ -z "$(FILE)" ]; then \
		echo "❌ Usage: make test-unit-file FILE=tests/unit/test_name.py"; \
		exit 1; \
	fi
	@timeout 60 poetry run pytest $(FILE) -v --tb=short -s

# Clean test artifacts and temporary files
clean:
	@echo "🧹 Cleaning test artifacts and temporary files..."
	@rm -rf node_modules/.cache
	@rm -rf coverage
	@rm -rf htmlcov
	@rm -rf .pytest_cache
	@rm -rf test_roster.db
	@rm -rf __pycache__
	@find . -type d -name "__pycache__" ! -path "*/node_modules/*" ! -path "*/.venv/*" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" ! -path "*/node_modules/*" ! -path "*/.venv/*" -delete 2>/dev/null || true
	@find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@rm -f *.db-shm *.db-wal 2>/dev/null || true
	@echo "✅ Clean complete"

# Weekly maintenance cleanup
clean-weekly:
	@echo "🧹 Running weekly maintenance cleanup..."
	@./scripts/cleanup_maintenance.sh
	@echo "✅ Weekly maintenance complete"

# Clean everything (includes dependencies)
clean-all: stop clean
	@echo "🧹 Deep cleaning (removing dependencies)..."
	@rm -rf node_modules
	@rm -rf .venv
	@echo "✅ Deep clean complete. Run 'make setup' to reinstall."

# Quick pre-commit test (fast tests only)
pre-commit: check-npm check-poetry
	@echo "⚡ Running fast pre-commit tests..."
	@npm test -- --bail
	@poetry run pytest tests/unit/ -x --tb=short
	@echo "✅ Pre-commit tests passed!"

# Run only fast unit tests (skip slow password hashing tests)
test-unit-fast: check-poetry
	@echo "⚡ Running fast unit tests (skipping slow tests)..."
	@poetry run pytest tests/unit/ -v --tb=short -m "not slow"

# Run tests with timing information
test-with-timing: check-poetry
	@echo "⏱️  Running tests with timing information..."
	@poetry run pytest tests/unit/ --durations=20 -v --tb=short

# Help (default target)
.DEFAULT_GOAL := help

help:
	@echo "Rostio Commands:"
	@echo ""
	@echo "🚀 Quick Start (One Command Does Everything!):"
	@echo "  make setup            - Auto-install Poetry, npm, packages, and setup DB"
	@echo ""
	@echo "Getting Started:"
	@echo "  make check-deps       - Check which dependencies are installed"
	@echo "  make install-deps     - Auto-install Poetry and npm (if missing)"
	@echo "  make install-poetry   - Auto-install Poetry only"
	@echo "  make install-npm      - Auto-install npm only"
	@echo "  make install          - Install project packages (requires Poetry/npm)"
	@echo "  make run              - Start development server (localhost:8000)"
	@echo ""
	@echo "Development:"
	@echo "  make dev              - Alias for 'make run'"
	@echo "  make stop             - Stop the development server"
	@echo "  make restart          - Restart the development server"
	@echo "  make migrate          - Run database migrations"
	@echo "  make fix-node-libs    - Fix Node.js library issues (simdjson)"
	@echo ""
	@echo "Testing:"
	@echo "  make test             - Run frontend + backend tests"
	@echo "  make test-frontend    - Run frontend JavaScript tests only"
	@echo "  make test-backend     - Run backend Python tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-e2e         - Run E2E browser tests (auto-starts server)"
	@echo "  make test-e2e-long    - Run E2E tests with 10min timeout (auto-starts server)"
	@echo "  make test-e2e-file    - Run specific E2E file (FILE=path/to/test.py)"
	@echo "  make test-e2e-quick   - Run E2E tests with no traceback"
	@echo "  make test-e2e-summary - Run E2E tests and show only summary"
	@echo "  make test-email-unit  - Run email unit tests (no server required)"
	@echo "  make test-email       - Run all email tests (auto-starts server)"
	@echo "  make test-all         - Run ALL tests (auto-starts server if needed)"
	@echo "  make test-coverage    - Run tests with coverage reports"
	@echo "  make test-unit        - Run unit tests only"
	@echo "  make test-unit-fast   - Run fast unit tests (skip slow password tests)"
	@echo "  make test-unit-file   - Run specific unit file (FILE=path/to/test.py)"
	@echo "  make test-with-timing - Run tests with timing information"
	@echo "  make pre-commit       - Run fast tests for pre-commit hook"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean            - Clean test artifacts and temp files"
	@echo "  make clean-weekly     - Weekly maintenance cleanup (Python cache, logs, WAL files)"
	@echo "  make clean-all        - Deep clean (stop server + remove dependencies)"
	@echo "  make help             - Show this help message"
	@echo ""
	@echo "Manual Dependency Installation (if auto-install fails):"
	@echo "  Poetry:  curl -sSL https://install.python-poetry.org | python3 -"
	@echo "  npm:     brew install node"
	@echo "  Python:  brew install python@3.11"
	@echo ""
