.PHONY: install fmt lint test run clean build

install:
	poetry install

fmt:
	poetry run black roster_cli tests
	poetry run ruff check --fix roster_cli tests

lint:
	poetry run ruff check roster_cli tests
	poetry run mypy roster_cli tests
	poetry run black --check roster_cli tests

test:
	poetry run pytest tests/ -v

run:
	poetry run roster

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf dist/ build/

build:
	poetry build

help:
	@echo "Available targets:"
	@echo "  install - Install dependencies with Poetry"
	@echo "  fmt     - Format code with black and ruff"
	@echo "  lint    - Lint code with ruff, mypy, and black"
	@echo "  test    - Run pytest test suite"
	@echo "  run     - Run roster CLI"
	@echo "  clean   - Clean up cache and build files"
	@echo "  build   - Build distribution packages"
