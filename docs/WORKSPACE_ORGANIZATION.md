# Rostio Workspace Organization

**Last Updated:** 2025-10-06

This document describes the organized workspace structure and repeatable development workflows for Rostio.

---

## 📁 Project Structure

```
rostio/
├── README.md                 # Main project documentation (ONLY .md in root)
├── Makefile                  # Comprehensive development commands
├── pyproject.toml           # Poetry dependencies
├── pytest.ini               # Test configuration
│
├── api/                     # FastAPI backend
│   ├── main.py             # Application entry point
│   ├── database.py         # Database configuration
│   ├── routers/            # API route handlers
│   └── models.py           # SQLAlchemy models
│
├── frontend/               # Web frontend
│   ├── index.html         # Main HTML
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript modules
│   └── images/            # Static assets
│
├── tests/                  # All tests
│   ├── unit/              # Unit tests (147 tests)
│   ├── integration/       # API + GUI tests (25 tests, 2 skipped)
│   ├── conftest.py        # Pytest fixtures
│   └── setup_test_data.py # Test data setup
│
├── docs/                   # All documentation
│   ├── api/               # API documentation
│   ├── testing/           # Test-related docs
│   ├── development/       # Development docs
│   └── archive/           # Old/deprecated docs
│
├── scripts/               # Utility scripts
│   ├── migrate_*.py       # Database migration scripts
│   └── *.sh              # Shell scripts
│
├── backups/               # Database backups
├── logs/                  # Application logs
└── test-reports/          # Test result reports
```

---

## 🔧 Makefile Commands

The `Makefile` provides comprehensive, **repeatable** commands organized by category.

### View All Commands
```bash
make help       # Show all available commands
```

### 📦 Installation
```bash
make install              # Production dependencies only
make install-dev          # All dependencies (dev + test)
make install-playwright   # Playwright browsers for GUI testing
make setup                # Complete setup (recommended for first time)
```

### 🧪 Testing
All test commands are **idempotent** and can be run repeatedly:

```bash
make test                 # Run ALL tests (unit + integration + GUI)
make test-unit            # Unit tests only (147 tests)
make test-integration     # Integration tests (API + Playwright, 25 tests)
make test-gui             # GUI/Playwright tests only
make test-quick           # Fast test suite (unit + integration)
make test-watch           # Run tests in watch mode (auto-rerun on changes)
```

**Test Status:**
- ✅ Unit tests: 147/147 passing (100%)
- ✅ Integration tests: 25 passing, 2 skipped
- ✅ Total: 172 passed, 2 skipped, 0 failed

### 🚀 Server Management
```bash
make server               # Start dev server (auto-reload)
make server-dev           # Start dev server with debug logs
make server-prod          # Start production server (4 workers)
make kill-servers         # Kill all running servers
make check-server         # Check if server is running
```

### 🗄️ Database Management
All database commands are **safe** and **repeatable**:

```bash
make db-init              # Initialize fresh database
make db-reset             # Clean + initialize (complete reset)
make db-backup            # Backup current database (timestamped)
make db-restore           # Restore from latest backup
make db-migrate           # Run Alembic migrations
```

**Database Files:**
- `roster.db` - Main database
- `backups/roster.db.backup.YYYYMMDD_HHMMSS` - Timestamped backups

### 🧹 Cleanup Commands
All cleanup commands are **safe** and can be run anytime:

```bash
make clean                # Clean temp files + cache + logs
make clean-cache          # Remove Python __pycache__, .pyc files
make clean-logs           # Remove all log files
make clean-temp           # Remove temporary test files
make clean-db             # Remove all database files
make clean-docs           # Organize documentation (move .md to docs/)
make clean-all            # Deep clean - reset workspace completely
```

**What gets cleaned:**
- Python cache: `__pycache__/`, `*.pyc`, `.pytest_cache`
- Logs: `logs/*.log`, `/tmp/*.log`
- Temp files: `/tmp/test_*.db`, `/tmp/*.png`
- Test reports: `test-reports/*.html`

### 📝 Documentation
```bash
make docs-consolidate     # Organize docs into docs/ subdirectories
```

**Documentation Structure:**
- `docs/api/` - API documentation
- `docs/testing/` - Test-related documentation
- `docs/development/` - Development guides
- `docs/archive/` - Old/deprecated docs

### 🔍 Code Quality
```bash
make format               # Format code with black
make lint                 # Lint with flake8
make type-check           # Type check with mypy
make quality              # Run all quality checks
```

### 🔧 Git Helpers
```bash
make git-status           # Show enhanced git status with stats
make git-clean            # Interactive untracked file cleanup
```

---

## 🔄 Common Workflows

### First Time Setup
```bash
make setup          # Install everything
make db-init        # Create database
make test           # Verify all tests pass
make server         # Start development server
```

### Daily Development
```bash
make clean          # Clean temp files
make test-quick     # Run quick tests
make server         # Start dev server
```

### Before Committing
```bash
make test           # Run all tests
make quality        # Check code quality
git status          # or: make git-status
```

### Clean Slate / Reset Everything
```bash
make clean-all      # Deep clean workspace
make db-reset       # Fresh database
make test           # Verify all tests pass
```

### Running Tests Continuously
```bash
make test-watch     # Auto-run tests on file changes
```

---

## ✅ Test Organization

### Unit Tests (`tests/unit/`)
- **147 tests** covering all API endpoints
- Test individual components in isolation
- No server required
- Fast execution (~2-3 seconds)

**Categories:**
- `test_availability.py` - Time-off management (10 tests)
- `test_calendar.py` - Calendar export/subscription (18 tests)
- `test_db_helpers.py` - Database helper functions (17 tests)
- `test_dependencies.py` - FastAPI dependencies (16 tests)
- `test_events.py` - Event management (18 tests)
- `test_organizations.py` - Organization CRUD (12 tests)
- `test_people.py` - Person management (16 tests)
- `test_security.py` - Security functions (27 tests)
- `test_teams.py` - Team management (13 tests)

### Integration Tests (`tests/integration/`)
- **25 tests** (2 skipped) covering end-to-end workflows
- Include Playwright GUI tests
- Require API server (managed by pytest fixture)
- Slower execution (~10-15 seconds)

**Categories:**
- `test_auth.py` - Authentication flows (6 tests)
- `test_availability_crud.py` - Time-off CRUD + GUI (3 tests, 1 GUI)
- `test_invitations.py` - Invitation workflows (16 tests)
- `test_multi_org_workflow.py` - Multi-org features (2 skipped - feature incomplete)

**Skipped Tests:**
- Multi-org UI tests (feature not fully implemented)

---

## 🔑 Key Features

### 1. **Idempotent Commands**
All commands can be run multiple times safely:
- `make clean` - Safe to run anytime
- `make test` - Always uses fresh test database
- `make db-reset` - Complete clean slate
- `make server` - Kills old servers first

### 2. **No Manual Server Management**
Tests handle server lifecycle automatically via pytest fixtures:
```python
@pytest.fixture(scope="session")
def api_server():
    # Starts server before tests
    # Stops server after tests
```

### 3. **Organized Documentation**
- Root has ONLY `README.md`
- All other docs in `docs/` directory
- Categorized by purpose (api, testing, development)
- No duplicate documentation

### 4. **Clean Git Workflow**
- Logs and temp files in `.gitignore`
- Documentation organized
- Easy to see what changed: `make git-status`

---

## 📊 Project Statistics

**Code:**
- Python API: ~3,000 lines
- Frontend JS: ~2,000 lines
- Test Code: ~5,000 lines

**Test Coverage:**
- Unit tests: 147 tests (100% passing)
- Integration tests: 25 tests (2 skipped, 100% pass rate)
- Total: 172 active tests

**Dependencies:**
- FastAPI - Web framework
- SQLAlchemy - ORM
- Playwright - GUI testing
- Pytest - Test framework

---

## 🎯 Best Practices

### Testing
1. Always run `make test` before committing
2. Use `make test-watch` during development
3. Keep tests independent and idempotent
4. Use test fixtures for common setup

### Database
1. Backup before major changes: `make db-backup`
2. Use `make db-reset` for clean slate
3. Never commit `roster.db` to git
4. Keep backups in `backups/` directory

### Documentation
1. Update `README.md` for major features
2. Keep detailed docs in `docs/` subdirectories
3. Run `make docs-consolidate` to organize
4. Archive old docs instead of deleting

### Code Quality
1. Run `make format` before committing
2. Fix linting issues: `make lint`
3. Type check: `make type-check`
4. Or run all: `make quality`

---

## 🚨 Troubleshooting

### "Address already in use" error
```bash
make kill-servers    # Kill all servers
make check-server    # Verify port is free
make server          # Start fresh
```

### Tests failing randomly
```bash
make clean-all       # Deep clean
make db-reset        # Fresh database
make test            # Run tests
```

### Database issues
```bash
make db-reset        # Nuclear option - fresh database
# or
make db-restore      # Restore from backup
```

### Documentation messy
```bash
make clean-docs      # Organize all .md files
```

---

## 📚 Related Documentation

- [README.md](../README.md) - Main project documentation
- [docs/api/API.md](api/API.md) - API reference
- [docs/testing/TEST_STATUS.md](testing/TEST_STATUS.md) - Test status details
- [docs/development/REFACTORING_SUMMARY.md](development/REFACTORING_SUMMARY.md) - Refactoring history

---

**Generated:** 2025-10-06
**Status:** ✅ All systems operational - 172/172 tests passing
