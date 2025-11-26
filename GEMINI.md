# Project Standards and Guidelines

## Testing Requirements
- **100% Test Coverage**: Every change MUST be accompanied by tests.
- **Test Types**:
  - **Unit Tests**: For individual functions and components.
  - **Integration Tests**: For API endpoints and database interactions.
  - **E2E Tests**: For full user flows using Playwright.
- **Verification**: All tests must pass before marking a task as complete.

## Logging Requirements
- **Clean Logs**: Application logs should be free of errors and unhandled exceptions.
- **Error Handling**: All exceptions must be caught and handled gracefully. 500 Internal Server Errors are unacceptable.

## Development Workflow
- **Reproduction Scripts**: Create reproduction scripts for reported bugs before fixing them.
- **Test Isolation**: Tests must be isolated (separate DB/port) to avoid affecting the development environment.

---

# Project Overview & Architecture (from gemini.md)

## 1. Project Overview

SignUpFlow is designed to help organizations like churches, sports leagues, and non-profits manage volunteer schedules. It leverages AI (OR-Tools) to automate scheduling based on constraints and availability.

### Key Features
-   **AI Scheduling:** Automated schedule generation.
-   **Volunteer Management:** Availability tracking, role assignments.
-   **Event Management:** Recurring events, multi-location support.
-   **Security:** JWT authentication, RBAC (Admin/Volunteer), bcrypt hashing.
-   **Internationalization:** Support for 6 languages.

## 2. Architecture & Tech Stack

### Backend (`api/`)
-   **Language:** Python 3.11+
-   **Framework:** FastAPI
-   **ORM:** SQLAlchemy (Async support planned/implied)
-   **Database:** SQLite (Dev), PostgreSQL (Prod)
-   **Solver:** Google OR-Tools
-   **Auth:** PyJWT, Passlib (bcrypt)
-   **Task Queue:** Celery + Redis (for background tasks)

### Frontend (`frontend/`)
-   **Core:** Vanilla JavaScript, HTML5, CSS3
-   **Routing:** Custom SPA Router (`frontend/js/router.js`)
-   **State Management:** `localStorage` + `sessionStorage`
-   **i18n:** `i18next`
-   **Build Tool:** None (Direct usage), dependencies via `npm`.

### Infrastructure
-   **Containerization:** Docker, Docker Compose
-   **Dependency Management:** Poetry (Python), npm (JS)

## 3. Directory Structure

```
SignUpFlow/
├── api/                  # Backend FastAPI application
│   ├── core/             # Config, security, auth
│   ├── routers/          # API endpoints (auth, people, events, etc.)
│   ├── services/         # Business logic (solver, billing, etc.)
│   ├── models.py         # SQLAlchemy models
│   └── main.py           # App entry point
├── frontend/             # Frontend SPA
│   ├── js/               # Application logic
│   ├── css/              # Styles
│   └── index.html        # Entry HTML
├── tests/                # Test suites
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── e2e/              # Playwright E2E tests
├── docs/                 # Comprehensive documentation
├── locales/              # i18n JSON files
├── migrations/           # Database migrations
├── docker-compose.yml    # Docker services config
├── Makefile              # Automation commands
├── pyproject.toml        # Python config
└── package.json          # JS config
```

## 4. Setup & Usage

### Prerequisites
-   Python 3.11+
-   Node.js & npm
-   Docker (optional but recommended)

### Quick Start (Docker)
```bash
make up           # Start all services
make migrate-docker # Run migrations
# Visit http://localhost:8000
```

### Local Development
```bash
# Backend
poetry install
poetry run uvicorn api.main:app --reload

# Frontend
# Serve `frontend/` directory (e.g., via python http.server or VS Code Live Server)
```

### Default Credentials
-   **Email:** `jane@test.com`
-   **Password:** `password`

## 5. Testing Strategy

The project maintains a high test coverage (99.6%).

### Running Tests
```bash
make test             # Quick tests
make test-all         # Full suite (Unit + E2E)
make test-unit-fast   # Fast unit tests
```

### Test Types
-   **Unit Tests:** `tests/unit/` - Test individual functions and models.
-   **Integration Tests:** `tests/integration/` - Test API endpoints and DB interactions.
-   **E2E Tests:** `tests/e2e/` - Playwright tests for full user journeys. **Critical for UI changes.**

### Key Rules
-   **E2E First:** Write E2E tests before implementing user-facing features.
-   **Test User Journey:** Verify what the user *sees*, not just API status codes.

## 6. Key Documentation Files
-   `README.md`: General overview and quick start.
-   `CLAUDE.md`: Detailed developer guide and context.
-   `docs/INDEX.md`: Index of all documentation.
-   `docs/API.md`: API documentation details.

## 7. Development Rules

> [!IMPORTANT]
> **ALWAYS BDD (Behavior Driven Development)**
> For ANY change (feature, bugfix, refactor), you MUST:
> 1.  **Write the Test First:** Create or update a test case that defines the expected behavior.
> 2.  **Verify Failure:** Run the test to confirm it fails (red).
> 3.  **Implement:** Write the minimum code necessary to make the test pass (green).
> 4.  **Refactor:** Clean up the code while keeping tests passing.
>
> **Every Run Rule:** Consult this `gemini.md` file at the start of every session to ensure compliance.
