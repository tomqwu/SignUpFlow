# Repository Guidelines

**Read the constitution:** `.specify/memory/constitution.md`
That file is your single source of truth for this project.

## Project Structure & Module Organization
The FastAPI service lives in `api/`, with `routers/` segmented by domain (events, people, onboarding, etc.) and shared logic in `services/`, `tasks/`, and `utils/`. SQLAlchemy models and Pydantic schemas are split between `models/` and `schemas/`. Static web assets ship from `frontend/`, where `js/` holds feature modules and `css/` the shared theme. Automated checks sit in `tests/` (unit, integration, e2e, frontend, performance), while Alembic migrations reside in `alembic/` and long-form documentation in `docs/`.

## Build, Test, and Development Commands
Prefer the Makefile for reproducible workflows:
```bash
make setup            # install Poetry/npm deps, migrate DB
make run              # start uvicorn on http://localhost:8000
make test             # run Jest + core pytest suite
make test-all         # frontend, backend, integration, e2e
make test-coverage    # Jest coverage + pytest HTML report
make clean            # remove caches, temp DBs, coverage
```
Use `poetry run uvicorn api.main:app --reload` for ad-hoc server runs and `npm test -- --watch` while iterating on frontend logic.

## Coding Style & Naming Conventions
Python code targets 3.11, four-space indentation, and max 100 characters enforced by Black and Ruff (`poetry run black api tests` / `poetry run ruff check`). Keep functions typed to satisfy the strict mypy config (`poetry run mypy api`). Frontend modules follow kebab-case filenames in `frontend/js/` and Jest looks for `*.test.js`. Favor descriptive action-based names (e.g., `send_invitation_email`) and keep i18n text in `locales/`.

## Testing Guidelines
Backend suites use pytest with fixtures in `tests/conftest.py`; group new cases under `tests/unit/` or extend `tests/comprehensive_test_suite.py`. Each user-visible change must ship with a Playwright e2e scenario in `tests/e2e/test_<feature>.py` (see `docs/E2E_TESTING_CHECKLIST.md`). Frontend utilities should include matching Jest specs in `frontend/tests/`. Before opening a PR run `make test-all` or, at minimum, `make test-backend` plus the targeted Jest suite. Keep coverage high by adding negative-path and localization assertions where relevant.

## Commit & Pull Request Guidelines
Follow the Conventional Commit style already in history (`feat:`, `fix:`, `docs:`). Keep messages scoped to a single concern and reference issue IDs when available. PRs should include: a concise summary of the change, screenshots or recordings for UI adjustments, links to any new documentation, and a checklist of tests executed. Flag configuration or migration steps in the PR body so reviewers can verify them locally.
