# Rostio - Roster Scheduling System

Intelligent scheduling system for churches, sports leagues, and volunteer organizations.

## 🚀 Quick Start

```bash
# Install dependencies
make setup

# Start development server
make server

# Run all tests
make test
```

Visit: http://localhost:8000

## 📚 Documentation

- **[Test Summary](TEST_SUMMARY.md)** - Complete test coverage documentation
- **[API Docs](http://localhost:8000/docs)** - Interactive API documentation (when server is running)

## 🎯 Features

- **Smart Scheduling** - AI-powered assignment generation
- **Availability Management** - Track time-off and preferences
- **Multi-Organization** - Support for multiple teams/churches
- **Role-Based Access** - Admin and user roles
- **Calendar Export** - iCal integration
- **Recurring Events** - Daily, weekly, monthly patterns

## 🧪 Testing

### Run Tests

```bash
make test              # All tests
make test-unit         # Unit tests only
make test-integration  # Integration tests
make test-e2e          # End-to-end tests
make test-gui          # GUI tests (Playwright)
make test-quick        # Fast suite (unit + integration)
```

### Test Coverage

- ✅ **Unit Tests:** 87.5% passing (56/64)
- ✅ **GUI Tests:** 66.7% passing (2/3)
- ✅ **100% GUI Event Management Coverage**

See [TEST_SUMMARY.md](TEST_SUMMARY.md) for details.

## 📁 Project Structure

```
rostio/
├── api/                 # FastAPI backend
│   ├── main.py         # API entry point
│   ├── models.py       # Data models
│   └── solver.py       # Scheduling algorithm
├── frontend/           # Web UI
│   ├── index.html      # Main HTML
│   ├── css/           # Styles
│   └── js/            # JavaScript
├── tests/             # Test suite
│   ├── unit/          # Unit tests
│   ├── integration/   # Integration tests
│   ├── e2e/           # End-to-end tests
│   └── gui/           # GUI tests
├── Makefile           # Build commands
└── pyproject.toml     # Dependencies
```

## 🛠️ Development

### Start Server
```bash
make server
```

### View Logs
```bash
tail -f /tmp/rostio_server.log
```

### Clean Up
```bash
make clean             # Remove temporary files
make kill-servers      # Kill all running servers
```

## 🐛 Bug Fixes

### Latest Fix: GUI Event Creation

**Issue:** Events created via GUI didn't appear  
**Root Cause:** Naming conflict with `document.createEvent()`  
**Fix:** Use `window.createEvent()` explicitly  
**Status:** ✅ FIXED - Verified with automated tests

## 📊 Technology Stack

- **Backend:** FastAPI (Python)
- **Frontend:** Vanilla JavaScript
- **Database:** SQLite with SQLAlchemy ORM
- **Testing:** pytest + Playwright
- **Scheduling:** OR-Tools constraint solver

## 🤝 Contributing

1. Make changes
2. Run tests: `make test-quick`
3. Ensure all tests pass
4. Create pull request

## 📝 License

MIT License - See LICENSE file for details

## 🎓 Best Practices

### Before Committing
```bash
make clean
make test-quick
```

### Before Deploying
```bash
make test
```

---

**Last Updated:** 2025-10-03  
**Version:** 0.2.0  
**Status:** Active Development
