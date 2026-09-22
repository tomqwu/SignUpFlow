.PHONY: run dev stop restart setup install migrate seed-demo test test-backend test-integration test-all test-postgres test-redis test-artifact test-coverage test-unit test-unit-fast test-unit-file test-with-timing clean clean-all pre-commit help check-poetry check-python check-deps install-poetry install-deps up down build logs shell db-shell redis-shell test-docker migrate-docker restart-api ps clean-docker check-docker ensure-test-deps prepare-test-data ensure-test-env

export SKIP_TEST_DB_FIXTURES ?= false

.PHONY: doctor services serve compose-up require-docker test-web test-contract test-e2e test-mobile test-mobile-generated test-performance test-load test-recovery test-security test-staging test-docs mobile-codegen-preflight mobile-codegen mobile-codegen-check capture-screenshots validate-screenshots
FLUTTER ?= flutter
DART ?= dart
JAVA_BIN ?=
NPX ?= npx

TEST_SERVER_HOST ?= 0.0.0.0
TEST_SERVER_PORT ?= 8000
TEST_APP_URL ?= http://localhost:$(TEST_SERVER_PORT)
TEST_API_BASE ?= $(TEST_APP_URL)/api

# Share one disposable database across this invocation's test tiers.
# Independent make/pytest runs must never reset another checkout's database.
TEST_DB_PATH := $(shell mktemp -d /tmp/signupflow-tests.XXXXXX)/signupflow_test.db
TEST_DB_PATH_STRIPPED := $(patsubst /%,%,$(TEST_DB_PATH))
TEST_DB_URL := sqlite:////$(TEST_DB_PATH_STRIPPED)
ifneq ($(filter test% pre-commit prepare-test-data ensure-test-env capture-screenshots validate-screenshots,$(MAKECMDGOALS)),)
export SIGNUPFLOW_TEST_DATABASE_URL := $(TEST_DB_URL)
export DATABASE_URL := $(TEST_DB_URL)
endif

# Detect available Docker Compose command (v1 `docker-compose` or v2 `docker compose`)
DOCKER_COMPOSE := $(shell \
	if command -v docker-compose >/dev/null 2>&1; then \
		echo docker-compose; \
	elif docker compose version >/dev/null 2>&1; then \
		echo docker compose; \
	else \
		echo missing; \
	fi)

# Ensure Docker CLI and daemon are available before running docker-compose targets
check-docker:
	@command -v docker >/dev/null 2>&1 || { \
		echo "❌ Docker CLI not found. Install Docker Desktop or Docker Engine first."; \
		exit 1; \
	}
	@docker info >/dev/null 2>&1 || { \
		echo "❌ Cannot connect to the Docker daemon. Start Docker (Docker Desktop, colima, or 'systemctl start docker') and ensure your user can access /var/run/docker.sock."; \
		exit 1; \
	}

DOCKER_TARGETS := compose-up down build rebuild logs logs-api logs-db logs-redis shell db-shell redis-shell \
	test-docker test-docker-quick test-docker-summary test-docker-file \
	test-docker-unit test-docker-unit-fast test-docker-integration \
	test-docker-coverage \
	migrate-docker restart-api ps

$(DOCKER_TARGETS): check-docker

ensure-test-deps: check-python
	@poetry check --lock
	@poetry install --no-interaction
	@poetry run python -c "import playwright, pytest"

prepare-test-data: ensure-test-deps
	@echo "🧪 Preparing baseline test data..."
	@poetry run python -m tests.setup_test_data

ensure-test-env: prepare-test-data

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

install-deps: install-poetry
	@echo ""
	@echo "✅ All system dependencies installed!"
	@echo ""

check-poetry:
	@command -v poetry >/dev/null 2>&1 || { \
		echo "❌ Poetry is not installed or not in PATH"; \
		echo "   Run 'make install-poetry' to install it automatically"; \
		echo "   Or install manually: curl -sSL https://install.python-poetry.org | python3 -"; \
		exit 1; \
	}

check-python: check-poetry
	@PY_VERSION=$$(poetry run python --version 2>&1 | sed 's/Python //'); \
	PY_MAJOR=$$(echo $$PY_VERSION | cut -d. -f1); \
	PY_MINOR=$$(echo $$PY_VERSION | cut -d. -f2); \
	if [ "$$PY_MAJOR" -ne 3 ] || [ "$$PY_MINOR" -lt 11 ] || [ "$$PY_MINOR" -gt 13 ]; then \
		echo "❌ Python 3.11 through 3.13 required (you have: Python $$PY_VERSION)"; \
		echo "   Install with: brew install python@3.11"; \
		exit 1; \
	else \
		echo "✅ Python version OK: Python $$PY_VERSION"; \
	fi

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
	@if ! command -v poetry >/dev/null 2>&1; then \
		echo "⚠️  Missing dependencies detected. Run 'make help' for installation instructions."; \
	else \
		echo "✅ All dependencies installed! You can run 'make setup' to install project packages."; \
	fi

# Bring the app up. Two commands cover the whole lifecycle: 'make setup'
# prepares the environment, 'make up' serves the app. Which way it is served
# follows DATABASE_URL, so the same command works on either path.
up:
	@set -e; \
	DB_URL="$$($(DB_URL_CMD))"; \
	case "$$DB_URL" in \
		$(COMPOSE_DB_PATTERNS)) \
			echo "🐳 DATABASE_URL names the compose database, so the app runs there."; \
			$(MAKE) compose-up; \
			;; \
		*) \
			$(MAKE) serve; \
			;; \
	esac

# Run the development server on the host.
serve: check-poetry
	@echo "🚀 Starting SignUpFlow development server..."
	@poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

run: up

# Run Celery worker
celery: check-poetry
	@echo "🚀 Starting Celery worker..."
	@poetry run celery -A api.celery_app worker --loglevel=info

dev: run

stop:
	@echo "Retired: stop the development server from the terminal that ran 'make up'."
	@exit 2

restart:
	@echo "Retired: stop the owned 'make up' process, then run 'make up' again."
	@exit 2

# Deliberately does not depend on check-poetry or an installed virtualenv:
# this is what you run when setup itself fails, so it must work before setup.
doctor:
	@python3 scripts/doctor.py

# Resolve DATABASE_URL the way the app does: an exported variable wins, because
# python-dotenv will not override one, and .env is only consulted when it does
# not. Shared by every target that needs to know which database is configured.
DB_URL_CMD = if [ -n "$$DATABASE_URL" ]; then printf '%s' "$$DATABASE_URL"; \
	elif [ -f .env ]; then \
		sed -n 's/^[[:space:]]*\(export[[:space:]][[:space:]]*\)\{0,1\}DATABASE_URL[[:space:]]*=[[:space:]]*//p' .env \
		| tail -n 1 | sed -e 's/^"//' -e 's/"$$//' -e "s/^'//" -e "s/'$$//"; \
	fi

# The shapes a URL takes when its host is the compose service name 'db', which
# resolves only inside the compose network. Kept in one place so every target
# agrees on what "the compose database" means.
COMPOSE_DB_PATTERNS = *@db:*|*@db/*|*@db

# Prepare everything the app needs to run: language dependencies, any backing
# services the configuration asks for, and the schema. It does not serve the
# app; 'make up' does that. Whether the services are containers is decided by
# DATABASE_URL, not by which target you typed, so the configuration and the
# commands cannot disagree.
setup:
	@echo "🚀 Starting SignUpFlow setup..."
	@echo ""
	@$(MAKE) check-python
	@$(MAKE) install-deps
	@$(MAKE) install
	@$(MAKE) services
	@$(MAKE) migrate
	@if [ "$(SEED_DEMO)" != "false" ]; then echo ""; $(MAKE) --no-print-directory seed-demo; fi
	@echo ""
	@echo "✅ Setup complete! Run 'make up' to start the app."
	@echo "   Visit http://localhost:8000/docs"
	@echo ""

# Start the backing services the configuration points at, and nothing else.
#
# A compose hostname is only resolvable inside the compose network, so a
# compose-backed database brings its containers up here; the app itself waits
# for 'make up'. A SQLite or directly reachable database needs nothing, so the
# common case stays free of Docker entirely.
services:
	@set -e; \
	if [ -f /.dockerenv ]; then \
		echo "ℹ️  Inside a container; backing services are managed by compose."; \
	else \
		DB_URL="$$($(DB_URL_CMD))"; \
		case "$$DB_URL" in \
			$(COMPOSE_DB_PATTERNS)) \
				echo "🐳 DATABASE_URL names the compose database, which only resolves"; \
				echo "   inside docker compose, so the database runs there."; \
				$(MAKE) require-docker; \
				$(DOCKER_COMPOSE) -f docker-compose.dev.yml up -d db redis; \
				echo "✅ Backing services are up."; \
				;; \
			*) \
				echo "✅ No backing services needed (using the configured database directly)."; \
				;; \
		esac; \
	fi

# One explanation of an unusable Docker, shared by every target that needs it,
# so the remedy never drifts between them. Callers that know why they wanted
# Docker say so first; this only reports that it is not there.
require-docker:
	@if ! command -v docker >/dev/null 2>&1 || ! docker info >/dev/null 2>&1; then \
		echo "❌ Docker is unavailable, so the compose stack cannot be reached."; \
		echo "   Start Docker and retry, or switch to SQLite for a host-only setup:"; \
		echo "       DATABASE_URL=sqlite:///./roster.db"; \
		echo "   Run 'make doctor' for the full environment report."; \
		exit 1; \
	fi

install: check-poetry
	@echo "📦 Installing project packages..."
	@poetry install
	@echo "✅ Project packages installed"

# Migrations run wherever the configured database actually lives. A compose
# hostname resolves only inside that network, so running alembic on the host
# could never reach it; those migrations go through a one-off api container,
# which works whether or not the app is already serving.
migrate: check-poetry
	@set -e; \
	DB_URL="$$($(DB_URL_CMD))"; \
	case "$$DB_URL" in \
		$(COMPOSE_DB_PATTERNS)) \
			if [ -f /.dockerenv ]; then \
				echo "🔄 Running database migrations..."; \
				poetry run alembic upgrade head; \
			else \
				echo "🐳 DATABASE_URL names the compose database, which only resolves"; \
				echo "   inside docker compose, so migrations run there too."; \
				$(MAKE) require-docker; \
				echo "🔄 Running database migrations inside compose..."; \
				$(DOCKER_COMPOSE) -f docker-compose.dev.yml run --rm api alembic upgrade head; \
			fi; \
			;; \
		*) \
			echo "🔄 Running database migrations..."; \
			poetry run alembic upgrade head; \
			;; \
	esac
	@echo "✅ Migrations complete"

# Load the demo organization and print its sample logins. 'make setup' runs
# this last; set SEED_DEMO=false to skip it, and RESET=1 rebuilds it with
# fresh dates. It is routed like 'migrate',
# because it writes to the same database, and it refuses ENVIRONMENT=production.
SEED_DEMO_FLAGS = $(if $(filter 1 true yes,$(RESET)),--reset,)

seed-demo: check-poetry
	@set -e; \
	DB_URL="$$($(DB_URL_CMD))"; \
	case "$$DB_URL" in \
		$(COMPOSE_DB_PATTERNS)) \
			if [ -f /.dockerenv ]; then \
				poetry run python -m api.cli.main seed-demo $(SEED_DEMO_FLAGS); \
			else \
				$(MAKE) require-docker; \
				$(DOCKER_COMPOSE) -f docker-compose.dev.yml run --rm api python -m api.cli.main seed-demo $(SEED_DEMO_FLAGS); \
			fi; \
			;; \
		*) \
			poetry run python -m api.cli.main seed-demo $(SEED_DEMO_FLAGS); \
			;; \
	esac

# Run all backend tests
test: test-all

test-backend: test-all

test-integration: check-poetry
	@echo "🧪 Running integration tests..."
	@poetry run pytest tests/integration/ -v --tb=short

test-all: ensure-test-env
	@echo "🚀 Running complete test suite..."
	@rm -f $(TEST_DB_PATH) $(TEST_DB_PATH)-shm $(TEST_DB_PATH)-wal
	@echo "🔄 Rebuilding fresh SQLite test database..."
	@poetry run python -m tests.setup_test_data >/dev/null
	@poetry run python scripts/run_local_validation.py

test-postgres: check-poetry check-docker
	@echo "🧪 Running owned PostgreSQL acceptance..."
	@poetry run python scripts/run_postgres_validation.py

test-redis: check-poetry check-docker
	@echo "🧪 Running owned Redis quota, event-bus, and broker acceptance..."
	@poetry run python scripts/run_redis_validation.py

test-artifact: check-poetry check-docker
	@echo "🧪 Building and exercising an owned production artifact through loopback TLS..."
	@poetry run python scripts/validate_production_artifact.py

test-staging: check-poetry
	@test -n "$$STAGING_BASE_URL" || { echo "STAGING_BASE_URL is required"; exit 2; }
	@test -n "$$STAGING_EXPECTED_RELEASE_SHA" || { echo "STAGING_EXPECTED_RELEASE_SHA is required"; exit 2; }
	@test -n "$$STAGING_APPROVAL_REFERENCE" || { echo "STAGING_APPROVAL_REFERENCE is required"; exit 2; }
	@echo "Running explicitly authorized staging acceptance against $$STAGING_BASE_URL..."
	@poetry run python scripts/run_staging_acceptance.py \
		--base-url "$$STAGING_BASE_URL" \
		--expected-release-sha "$$STAGING_EXPECTED_RELEASE_SHA" \
		--approval-reference "$$STAGING_APPROVAL_REFERENCE" \
		--allow-authorized-remote

test-recovery: check-poetry
	@echo "🧪 Running owned SQLite backup and restore acceptance..."
	@poetry run python scripts/run_sqlite_recovery_drill.py

test-security: check-poetry check-docker
	@echo "🧪 Scanning the committed source and exact retained production image..."
	@poetry run python scripts/run_security_validation.py

test-docs: check-poetry
	@echo "🧪 Validating the tracked documentation inventory and current local links..."
	@poetry run python scripts/validate_documentation.py

test-web: check-poetry
	@poetry run pytest tests/web/ -v --tb=short

test-contract: check-poetry
	@poetry run pytest tests/contract/ -v --tb=short

test-e2e: check-poetry
	@poetry run pytest tests/e2e/ -v --tb=short

capture-screenshots: ensure-test-env
	@poetry run python scripts/capture_playbook_screenshots.py --source-ref "$${SCREENSHOT_SOURCE_REF:-$$(git rev-parse HEAD)}"

validate-screenshots: check-poetry
	@poetry run python scripts/capture_playbook_screenshots.py --source-ref "$$(git rev-parse HEAD)" --validate-only

test-mobile:
	@cd mobile && $(FLUTTER) pub get && $(FLUTTER) test

test-mobile-generated:
	@cd mobile/api_client && $(DART) analyze --no-fatal-warnings && $(DART) test

test-performance: ensure-test-env
	@poetry run pytest tests/performance/ -v --tb=short

test-load: check-poetry
	@echo "Running bounded source-identified load validation..."
	@poetry run python scripts/run_load_validation.py \
		--start-local \
		--profile tests/performance/profiles/local-smoke.json

test-coverage: check-poetry
	@echo "📊 Generating test coverage reports..."
	@poetry run pytest tests/ --cov=api --cov-report=html --cov-report=term

test-unit: check-poetry
	@echo "🧪 Running unit tests..."
	@poetry run pytest tests/unit/ -v --tb=short

test-unit-file: check-poetry
	@echo "🧪 Running specific unit test file..."
	@if [ -z "$(FILE)" ]; then \
		echo "❌ Usage: make test-unit-file FILE=tests/unit/test_name.py"; \
		exit 1; \
	fi
	@timeout 60 poetry run pytest $(FILE) -v --tb=short -s

clean:
	@echo "Retired: each command cleans only the unique artifacts it owns."
	@exit 2

clean-weekly:
	@echo "Retired: no repository-wide scheduled deletion is supported."
	@exit 2

clean-all:
	@echo "Retired: remove dependencies or data only with an explicit path-specific action."
	@exit 2

pre-commit: check-poetry
	@echo "⚡ Running fast pre-commit tests..."
	@poetry run pytest tests/unit/ -x --tb=short
	@echo "✅ Pre-commit tests passed!"

test-unit-fast: check-poetry
	@echo "⚡ Running fast unit tests (skipping slow tests)..."
	@poetry run pytest tests/unit/ -v --tb=short -m "not slow"

test-with-timing: check-poetry
	@echo "⏱️  Running tests with timing information..."
	@poetry run pytest tests/unit/ --durations=20 -v --tb=short

update-openapi-snapshot: check-poetry
	@echo "🔄 Refreshing OpenAPI contract snapshot..."
	@poetry run python -m tests.contract.test_openapi_snapshot --update
	@echo "✅ Snapshot updated. Review the diff, run 'make mobile-codegen' to refresh the Flutter client, then commit."

# ============================================================================
# Mobile (Flutter) — see specs/022-flutter-mobile-app/spec.md
# ============================================================================

# Validate the pinned Java/Node/Flutter/Dart toolchain and canonical schema.
# Override tool discovery with JAVA_BIN, NPX, FLUTTER, or DART when needed.
mobile-codegen-preflight: check-poetry
	@JAVA_BIN="$(JAVA_BIN)" NPX="$(NPX)" FLUTTER="$(FLUTTER)" DART="$(DART)" \
		poetry run python scripts/mobile_codegen.py --preflight

# Generate twice in temporary directories, require identical output, then sync
# the complete generated package. The strict canonical snapshot is never modified.
mobile-codegen: check-poetry
	@JAVA_BIN="$(JAVA_BIN)" NPX="$(NPX)" FLUTTER="$(FLUTTER)" DART="$(DART)" \
		poetry run python scripts/mobile_codegen.py --write

# Prove deterministic generation and fail on checked-in client drift without
# modifying mobile/api_client or the maintained Flutter application.
mobile-codegen-check: check-poetry
	@JAVA_BIN="$(JAVA_BIN)" NPX="$(NPX)" FLUTTER="$(FLUTTER)" DART="$(DART)" \
		poetry run python scripts/mobile_codegen.py --check

# ============================================================================
# Docker Compose Commands (Development Environment)
# ============================================================================

# The unconditional compose path. 'make up' routes here when DATABASE_URL names
# the compose database; call it directly to bring the stack up regardless.
compose-up:
	@echo "🐳 Starting SignUpFlow development environment..."
	@$(DOCKER_COMPOSE) -f docker-compose.dev.yml up -d
	@echo ""
	@echo "✅ Services started!"
	@echo "   API:        http://localhost:8000"
	@echo "   PostgreSQL: localhost:5433 (user: signupflow, db: signupflow_dev)"
	@echo "   Redis:      localhost:6380"
	@echo ""
	@echo "View logs:     make logs"
	@echo "Stop services: make down"
	@echo ""

down:
	@echo "🛑 Stopping SignUpFlow development environment..."
	@$(DOCKER_COMPOSE) -f docker-compose.dev.yml down
	@echo "✅ Services stopped"

build:
	@echo "🔨 Building Docker images..."
	@$(DOCKER_COMPOSE) -f docker-compose.dev.yml build --no-cache
	@echo "✅ Build complete"

rebuild: down build compose-up

logs:
	@$(DOCKER_COMPOSE) -f docker-compose.dev.yml logs -f

logs-api:
	@$(DOCKER_COMPOSE) -f docker-compose.dev.yml logs -f api

logs-db:
	@$(DOCKER_COMPOSE) -f docker-compose.dev.yml logs -f db

logs-redis:
	@$(DOCKER_COMPOSE) -f docker-compose.dev.yml logs -f redis

logs-worker:
	@$(DOCKER_COMPOSE) -f docker-compose.dev.yml logs -f worker

shell:
	@echo "🐚 Opening shell in API container..."
	@$(DOCKER_COMPOSE) -f docker-compose.dev.yml exec api bash

db-shell:
	@echo "🐘 Opening PostgreSQL shell..."
	@$(DOCKER_COMPOSE) -f docker-compose.dev.yml exec db psql -U signupflow -d signupflow_dev

redis-shell:
	@echo "🔴 Opening Redis CLI..."
	@$(DOCKER_COMPOSE) -f docker-compose.dev.yml exec redis redis-cli -a dev_redis_password

# ============================================================================
# Docker-Based Testing
# ============================================================================

test-docker:
	@echo "🧪 Running unit tests in Docker container..."
	@$(DOCKER_COMPOSE) -f docker-compose.dev.yml exec -T api pytest tests/unit/ -v --tb=short

test-docker-quick:
	@echo "⚡ Running unit tests in Docker (quick mode)..."
	@$(DOCKER_COMPOSE) -f docker-compose.dev.yml exec -T api pytest tests/unit/ -v --tb=no

test-docker-summary:
	@echo "📊 Running unit tests in Docker (summary only)..."
	@$(DOCKER_COMPOSE) -f docker-compose.dev.yml exec -T api pytest tests/unit/ -v --tb=no 2>&1 | grep -E "(PASSED|FAILED|SKIPPED|ERROR|=====|passed|failed|warning)"

test-docker-file:
	@echo "🎯 Running specific test file in Docker..."
	@if [ -z "$(FILE)" ]; then \
		echo "❌ Usage: make test-docker-file FILE=tests/unit/test_name.py"; \
		exit 1; \
	fi
	@$(DOCKER_COMPOSE) -f docker-compose.dev.yml exec -T api pytest $(FILE) -v --tb=short

test-docker-unit:
	@echo "🧪 Running unit tests in Docker container..."
	@$(DOCKER_COMPOSE) -f docker-compose.dev.yml exec -T api pytest tests/unit/ -v --tb=short

test-docker-unit-fast:
	@echo "⚡ Running fast unit tests in Docker..."
	@$(DOCKER_COMPOSE) -f docker-compose.dev.yml exec -T api pytest tests/unit/ -v --tb=short -m "not slow"

test-docker-integration:
	@echo "🔗 Running integration tests in Docker..."
	@$(DOCKER_COMPOSE) -f docker-compose.dev.yml exec -T api pytest tests/integration/ -v --tb=short

test-docker-comprehensive:
	@echo "Docker comprehensive validation is retired; run 'make test-all' locally."
	@exit 2

test-docker-all:
	@echo "Docker full validation is retired; run 'make test-all' locally."
	@exit 2

test-docker-coverage:
	@echo "📊 Running tests with coverage in Docker..."
	@$(DOCKER_COMPOSE) -f docker-compose.dev.yml exec -T api pytest tests/ --cov=api --cov-report=html --cov-report=term -v --tb=short

migrate-docker:
	@echo "🔄 Running migrations in Docker container..."
	@$(DOCKER_COMPOSE) -f docker-compose.dev.yml exec api alembic upgrade head
	@echo "✅ Migrations complete"

restart-api:
	@echo "🔄 Restarting API service..."
	@$(DOCKER_COMPOSE) -f docker-compose.dev.yml restart api
	@echo "✅ API restarted"

ps:
	@$(DOCKER_COMPOSE) -f docker-compose.dev.yml ps

clean-docker:
	@echo "Retired: use 'make down' for the owned Compose project; volume deletion is separate."
	@exit 2

clean-docker-all:
	@echo "Retired: global image and volume deletion is not a repository helper operation."
	@exit 2

.DEFAULT_GOAL := help

help:
	@echo "SignUpFlow Commands:"
	@echo ""
	@echo "🚀 Quick Start:"
	@echo "  make doctor           - Report what this machine will start the app with"
	@echo "  make setup            - Prepare the environment: deps, services, schema"
	@echo "  make up               - Start the app (follows DATABASE_URL)"
	@echo ""
	@echo "🐳 Docker Development:"
	@echo "  make compose-up       - Start all services (PostgreSQL + Redis + API)"
	@echo "  make down             - Stop all services"
	@echo "  make logs             - View logs from all services"
	@echo "  make logs-api         - View API logs only"
	@echo "  make shell            - Open bash shell in API container"
	@echo "  make db-shell         - Open PostgreSQL shell"
	@echo "  make redis-shell      - Open Redis CLI"
	@echo "  make test-docker      - Run tests in Docker container"
	@echo "  make migrate-docker   - Run migrations in Docker container"
	@echo "  make restart-api      - Restart API service only"
	@echo "  make build            - Build Docker images"
	@echo "  make rebuild          - Rebuild and restart all services"
	@echo "  make ps               - Show running services"
	@echo "  make clean-docker     - Retired; does not delete volumes"
	@echo "  make clean-docker-all - Retired; does not delete images or volumes"
	@echo ""
	@echo "💻 Local Development (Without Docker):"
	@echo "  make check-deps       - Check which dependencies are installed"
	@echo "  make install-deps     - Auto-install Poetry (if missing)"
	@echo "  make install-poetry   - Auto-install Poetry only"
	@echo "  make install          - Install project packages (requires Poetry)"
	@echo "  make serve            - Start development server on the host (localhost:8000)"
	@echo ""
	@echo "Development:"
	@echo "  make run / make dev   - Aliases for 'make up'"
	@echo "  make stop             - Retired; stop the owning 'make up' terminal"
	@echo "  make restart          - Retired; restart from the owning terminal"
	@echo "  make migrate          - Run database migrations"
	@echo "  make seed-demo        - Load the demo organization and print its logins (RESET=1 rebuilds)"
	@echo ""
	@echo "Testing:"
	@echo "  make test             - Run backend tests"
	@echo "  make test-backend     - Run backend Python tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-all         - Run all Python tiers, including web/contract/Playwright"
	@echo "  make test-postgres    - Run owned PostgreSQL migration/business/race acceptance"
	@echo "  make test-redis       - Run owned Redis quota, event-bus, and broker acceptance"
	@echo "  make test-artifact    - Exercise an owned production image and loopback TLS"
	@echo "  make test-staging     - Run approval-gated Church/Basketball staging acceptance"
	@echo "  make test-security    - Scan the exact committed source and retained image locally"
	@echo "  make test-recovery    - Run the owned encrypted SQLite restore drill"
	@echo "  make test-docs        - Validate documentation dispositions and current local links"
	@echo "  make test-performance - Run load tests against an explicit owned loopback server"
	@echo "  make test-load        - Run bounded source-identified load validation locally"
	@echo "  make test-mobile      - Run Flutter tests locally (requires Flutter SDK)"
	@echo "  make test-mobile-generated - Analyze and test the generated Dart client"
	@echo "  make mobile-codegen-preflight - Validate pinned tools and the OpenAPI snapshot"
	@echo "  make mobile-codegen   - Reproducibly update the generated Dart API client"
	@echo "  make mobile-codegen-check - Detect generated-client drift without writing"
	@echo "  make test-e2e         - Run Playwright browser tests locally"
	@echo "  make test-web         - Run in-process web tests locally"
	@echo "  make test-contract    - Run OpenAPI contract tests locally"
	@echo "  make test-coverage    - Run tests with coverage reports"
	@echo "  make test-unit        - Run unit tests only"
	@echo "  make test-unit-fast   - Run fast unit tests (skip slow password tests)"
	@echo "  make test-unit-file   - Run specific unit file (FILE=path/to/test.py)"
	@echo "  make test-with-timing - Run tests with timing information"
	@echo "  make pre-commit       - Run fast tests for pre-commit hook"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean            - Retired; commands clean only owned artifacts"
	@echo "  make clean-weekly     - Retired; no broad scheduled deletion"
	@echo "  make clean-all        - Retired; no broad dependency/data deletion"
	@echo "  make help             - Show this help message"
	@echo ""
	@echo "Manual Dependency Installation (if auto-install fails):"
	@echo "  Poetry:  curl -sSL https://install.python-poetry.org | python3 -"
	@echo "  Python:  brew install python@3.11"
	@echo ""
