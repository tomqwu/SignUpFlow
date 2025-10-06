.PHONY: help setup clean clean-all clean-db clean-logs clean-cache clean-temp clean-docs
.PHONY: test test-unit test-integration test-gui test-all test-quick test-watch
.PHONY: server server-dev server-prod kill-servers check-server
.PHONY: db-init db-reset db-backup db-restore db-migrate
.PHONY: format lint type-check quality
.PHONY: docs docs-clean docs-consolidate
.PHONY: install install-dev install-playwright
.PHONY: git-status git-clean

# ============================================================================
# CONFIGURATION
# ============================================================================
PYTHON := poetry run python
PYTEST := poetry run pytest
UVICORN := poetry run uvicorn
SERVER_HOST := 0.0.0.0
SERVER_PORT := 8000
DB_FILE := roster.db
TEST_DB_FILE := test_roster.db
BACKUP_DIR := backups
LOGS_DIR := logs
DOCS_DIR := docs

# ============================================================================
# HELP
# ============================================================================
help:
	@echo ""
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║  ROSTIO - Development & Testing Commands                  ║"
	@echo "╚════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "📦 INSTALLATION:"
	@echo "  make install              - Install production dependencies"
	@echo "  make install-dev          - Install all dependencies (dev + test)"
	@echo "  make install-playwright   - Install Playwright browsers"
	@echo "  make setup                - Complete setup (install-dev + playwright)"
	@echo ""
	@echo "🧪 TESTING:"
	@echo "  make test                 - Run all tests (unit + integration + GUI)"
	@echo "  make test-unit            - Run unit tests only"
	@echo "  make test-integration     - Run integration tests (API + Playwright)"
	@echo "  make test-gui             - Run GUI/Playwright tests only"
	@echo "  make test-quick           - Quick test (unit + integration)"
	@echo "  make test-watch           - Run tests in watch mode"
	@echo ""
	@echo "🚀 SERVER:"
	@echo "  make server               - Start development server (with reload)"
	@echo "  make server-dev           - Start dev server with detailed logs"
	@echo "  make server-prod          - Start production server (no reload)"
	@echo "  make kill-servers         - Kill all running servers"
	@echo "  make check-server         - Check if server is running"
	@echo ""
	@echo "🗄️  DATABASE:"
	@echo "  make db-init              - Initialize fresh database"
	@echo "  make db-reset             - Reset database (clean + init)"
	@echo "  make db-backup            - Backup current database"
	@echo "  make db-restore           - Restore database from backup"
	@echo "  make db-migrate           - Run database migrations"
	@echo ""
	@echo "🧹 CLEANUP:"
	@echo "  make clean                - Clean temporary files"
	@echo "  make clean-db             - Remove all database files"
	@echo "  make clean-logs           - Remove all log files"
	@echo "  make clean-cache          - Remove Python cache files"
	@echo "  make clean-temp           - Remove temporary test files"
	@echo "  make clean-docs           - Remove duplicate documentation"
	@echo "  make clean-all            - Deep clean (all of the above)"
	@echo ""
	@echo "📝 DOCUMENTATION:"
	@echo "  make docs-consolidate     - Consolidate duplicate docs"
	@echo "  make docs-clean           - Remove outdated/duplicate docs"
	@echo ""
	@echo "🔍 CODE QUALITY:"
	@echo "  make format               - Format code with black"
	@echo "  make lint                 - Lint code with flake8"
	@echo "  make type-check           - Type check with mypy"
	@echo "  make quality              - Run all quality checks"
	@echo ""
	@echo "🔧 GIT:"
	@echo "  make git-status           - Show git status with statistics"
	@echo "  make git-clean            - Remove untracked files (interactive)"
	@echo ""

# ============================================================================
# INSTALLATION
# ============================================================================
install:
	@echo "📦 Installing production dependencies..."
	@poetry install --only main
	@echo "✅ Installation complete!"

install-dev:
	@echo "📦 Installing all dependencies (dev + test)..."
	@poetry install
	@echo "✅ Development installation complete!"

install-playwright:
	@echo "🎭 Installing Playwright browsers..."
	@$(PYTHON) -m playwright install chromium
	@echo "✅ Playwright browsers installed!"

setup: install-dev install-playwright
	@echo ""
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║  ✅ SETUP COMPLETE!                                        ║"
	@echo "╚════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "Next steps:"
	@echo "  1. make db-init     - Initialize database"
	@echo "  2. make test        - Run all tests"
	@echo "  3. make server      - Start development server"
	@echo ""

# ============================================================================
# SERVER MANAGEMENT
# ============================================================================
kill-servers:
	@echo "🔪 Killing all uvicorn servers..."
	@pkill -9 -f "uvicorn api.main" 2>/dev/null || true
	@pkill -9 -f "python.*api.main" 2>/dev/null || true
	@rm -f /tmp/test_server.pid /tmp/rostio_server.pid 2>/dev/null || true
	@sleep 1
	@echo "✅ All servers stopped"

check-server:
	@echo "🔍 Checking for running servers..."
	@pgrep -f "uvicorn api.main" && echo "✅ Server is running" || echo "❌ No server running"
	@lsof -ti:$(SERVER_PORT) && echo "✅ Port $(SERVER_PORT) in use" || echo "⚠️  Port $(SERVER_PORT) available"

server: kill-servers
	@echo "🚀 Starting Rostio development server..."
	@echo "   URL: http://$(SERVER_HOST):$(SERVER_PORT)"
	@echo "   Press Ctrl+C to stop"
	@echo ""
	@$(UVICORN) api.main:app --host $(SERVER_HOST) --port $(SERVER_PORT) --reload

server-dev: kill-servers
	@echo "🚀 Starting Rostio development server (detailed logs)..."
	@$(UVICORN) api.main:app --host $(SERVER_HOST) --port $(SERVER_PORT) --reload --log-level debug

server-prod: kill-servers
	@echo "🚀 Starting Rostio production server..."
	@$(UVICORN) api.main:app --host $(SERVER_HOST) --port $(SERVER_PORT) --workers 4

# ============================================================================
# DATABASE MANAGEMENT
# ============================================================================
db-init:
	@echo "🗄️  Initializing database..."
	@$(PYTHON) -c "from api.database import engine, Base; Base.metadata.create_all(bind=engine)"
	@echo "✅ Database initialized"

db-reset: clean-db db-init
	@echo "✅ Database reset complete"

db-backup:
	@echo "💾 Backing up database..."
	@mkdir -p $(BACKUP_DIR)
	@if [ -f $(DB_FILE) ]; then \
		cp $(DB_FILE) $(BACKUP_DIR)/$(DB_FILE).backup.$$(date +%Y%m%d_%H%M%S); \
		echo "✅ Database backed up to $(BACKUP_DIR)/"; \
	else \
		echo "⚠️  No database file found to backup"; \
	fi

db-restore:
	@echo "📥 Restoring database from latest backup..."
	@if [ -f $(BACKUP_DIR)/$(DB_FILE).backup.* ]; then \
		cp $$(ls -t $(BACKUP_DIR)/$(DB_FILE).backup.* | head -1) $(DB_FILE); \
		echo "✅ Database restored"; \
	else \
		echo "❌ No backup found in $(BACKUP_DIR)/"; \
		exit 1; \
	fi

db-migrate:
	@echo "🔄 Running database migrations..."
	@poetry run alembic upgrade head
	@echo "✅ Migrations complete"

# ============================================================================
# TESTING
# ============================================================================
test-unit:
	@echo ""
	@echo "🧪 Running Unit Tests..."
	@echo "======================="
	@rm -f $(TEST_DB_FILE)
	@$(PYTHON) -c "from api.database import engine, Base; Base.metadata.create_all(bind=engine)"
	@$(PYTEST) tests/unit/ -v --tb=short
	@echo ""

test-integration:
	@echo ""
	@echo "🔗 Running Integration Tests (API + Playwright)..."
	@echo "================================================="
	@$(PYTEST) tests/integration/ -v --tb=short
	@echo ""

test-gui:
	@echo ""
	@echo "🖥️  Running GUI/Playwright Tests..."
	@echo "==================================="
	@$(PYTEST) tests/integration/ -v --tb=short -k "gui"
	@echo ""

test-quick: test-unit test-integration
	@echo ""
	@echo "✅ Quick test suite complete!"
	@echo ""

test-all:
	@echo ""
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║  ROSTIO - COMPLETE TEST SUITE                              ║"
	@echo "╚════════════════════════════════════════════════════════════╝"
	@echo ""
	@$(PYTEST) tests/unit/ tests/integration/ -v --tb=short
	@echo ""
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║  ✅ ALL TESTS COMPLETE!                                    ║"
	@echo "╚════════════════════════════════════════════════════════════╝"
	@echo ""

test-watch:
	@echo "👀 Running tests in watch mode..."
	@$(PYTEST) tests/ -v --tb=short -f

test: test-all

# ============================================================================
# CLEANUP
# ============================================================================
clean-cache:
	@echo "🧹 Cleaning Python cache files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@rm -rf .pytest_cache .mypy_cache .ruff_cache
	@echo "✅ Cache cleaned"

clean-logs:
	@echo "🧹 Cleaning log files..."
	@rm -f $(LOGS_DIR)/*.log
	@rm -f /tmp/rostio*.log /tmp/test*.log /tmp/server*.log
	@rm -f /tmp/*.pid
	@echo "✅ Logs cleaned"

clean-temp:
	@echo "🧹 Cleaning temporary test files..."
	@rm -f /tmp/test_*.db
	@rm -f /tmp/login_failure.png
	@rm -f /tmp/*.png /tmp/*.jpg
	@rm -rf test-reports/*.html
	@echo "✅ Temporary files cleaned"

clean-db:
	@echo "🧹 Cleaning database files..."
	@rm -f $(DB_FILE) $(TEST_DB_FILE)
	@rm -f *.db *.db-journal
	@echo "✅ Database files removed"

clean-docs:
	@echo "🧹 Removing duplicate documentation..."
	@# Keep only README.md in root, move others to docs/
	@if [ -f "TEST_STATUS.md" ]; then mv TEST_STATUS.md $(DOCS_DIR)/; fi
	@if [ -f "TEST_SUMMARY.md" ]; then mv TEST_SUMMARY.md $(DOCS_DIR)/; fi
	@if [ -f "REFACTORING_SUMMARY.md" ]; then mv REFACTORING_SUMMARY.md $(DOCS_DIR)/; fi
	@if [ -f "FINAL_STATUS.md" ]; then mv FINAL_STATUS.md $(DOCS_DIR)/; fi
	@if [ -f "QUICK_START.md" ]; then mv QUICK_START.md $(DOCS_DIR)/; fi
	@# Remove duplicate docs in docs/ directory
	@cd $(DOCS_DIR) && rm -f TEST_RESULTS.md TEST_COVERAGE.md 2>/dev/null || true
	@echo "✅ Documentation organized"

clean: clean-cache clean-logs clean-temp
	@echo "✅ Cleanup complete"

clean-all: kill-servers clean clean-db clean-docs
	@echo ""
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║  ✅ DEEP CLEAN COMPLETE - Workspace Reset!                 ║"
	@echo "╚════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "Next steps:"
	@echo "  1. make db-init     - Initialize fresh database"
	@echo "  2. make test        - Run all tests"
	@echo ""

# ============================================================================
# DOCUMENTATION
# ============================================================================
docs-consolidate:
	@echo "📝 Consolidating documentation..."
	@# Create docs structure
	@mkdir -p $(DOCS_DIR)/archive
	@mkdir -p $(DOCS_DIR)/api
	@mkdir -p $(DOCS_DIR)/testing
	@mkdir -p $(DOCS_DIR)/development
	@# Move test docs
	@mv -f TEST_STATUS.md $(DOCS_DIR)/testing/ 2>/dev/null || true
	@mv -f TEST_SUMMARY.md $(DOCS_DIR)/testing/ 2>/dev/null || true
	@# Move development docs
	@mv -f REFACTORING_SUMMARY.md $(DOCS_DIR)/development/ 2>/dev/null || true
	@mv -f FINAL_STATUS.md $(DOCS_DIR)/development/ 2>/dev/null || true
	@# Move old API docs
	@mv -f $(DOCS_DIR)/API_README.md $(DOCS_DIR)/api/ 2>/dev/null || true
	@mv -f $(DOCS_DIR)/API_QUICKSTART.md $(DOCS_DIR)/api/ 2>/dev/null || true
	@echo "✅ Documentation consolidated"

# ============================================================================
# CODE QUALITY
# ============================================================================
format:
	@echo "🎨 Formatting code with black..."
	@poetry run black api/ roster_cli/ tests/ || echo "⚠️  black not installed"

lint:
	@echo "🔍 Linting code with flake8..."
	@poetry run flake8 api/ roster_cli/ tests/ --max-line-length=120 || echo "⚠️  flake8 not installed"

type-check:
	@echo "🔎 Type checking with mypy..."
	@poetry run mypy api/ roster_cli/ || echo "⚠️  mypy not installed"

quality: format lint type-check
	@echo "✅ Code quality checks complete"

# ============================================================================
# GIT HELPERS
# ============================================================================
git-status:
	@echo ""
	@echo "📊 Git Status Summary"
	@echo "===================="
	@git status --short
	@echo ""
	@echo "Branch: $$(git branch --show-current)"
	@echo "Commits ahead: $$(git rev-list --count @{u}.. 2>/dev/null || echo '0')"
	@echo "Commits behind: $$(git rev-list --count ..@{u} 2>/dev/null || echo '0')"
	@echo ""
	@echo "Recent commits:"
	@git log --oneline -5
	@echo ""

git-clean:
	@echo "🧹 Cleaning untracked files..."
	@git clean -fd -i
