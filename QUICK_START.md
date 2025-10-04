# Rostio Quick Start Guide

## 🚀 Running the Application

```bash
# Start the server
make server

# Or manually
poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Access the app at: http://localhost:8000

## 🧪 Running Tests

```bash
# Run comprehensive test suite
poetry run pytest tests/comprehensive_test_suite.py -v

# Run with cleanup (kills zombie processes first)
./scripts/cleanup_and_test.sh

# Run specific test class
poetry run pytest tests/comprehensive_test_suite.py::TestAvailabilityAPI -v
```

## 📁 Project Structure

```
rostio/
├── api/                    # FastAPI backend
│   ├── routers/           # API endpoints
│   ├── schemas/           # Pydantic models
│   └── utils/             # PDF export, etc.
├── frontend/              # HTML/JS/CSS
│   ├── index.html         # Main app
│   ├── js/                # JavaScript
│   └── css/               # Styles
├── roster_cli/            # Core scheduling logic
│   ├── core/              # Solver, constraints
│   └── db/                # Database models
├── tests/                 # Test suite
└── scripts/               # Utility scripts
```

## 🔑 Key Features

### Blocked Dates (Time Off)
- **Add**: Availability view → Fill dates + reason → "Add Time Off"
- **Edit**: Click blocked date badge → Update → Save
- **Delete**: Click blocked date → Delete button

### Event Management
- **Create Event**: Admin Dashboard → "Create Event"
- **Assign People**: Event card → "Assign People" → Toggle assignments
- **View Warnings**: Blocked people show red warnings

### Schedule Generation
- **Generate**: Admin Dashboard → "Generate Schedule"
- **Export PDF**: Select solution → "Export PDF"
- **View**: Solutions list shows all generated schedules

## 🛠️ Common Commands

```bash
# Database migration
poetry run alembic upgrade head

# Create new migration
poetry run alembic revision --autogenerate -m "description"

# Interactive database viewer
poetry run python tools/db_viewer.py

# Kill zombie processes
pkill -9 -f uvicorn
```

## 🧹 Cleanup & Maintenance

```bash
# Full cleanup and test
./scripts/cleanup_and_test.sh

# Clean temp files
rm -f /tmp/*.log /tmp/*.png

# Reset database (careful!)
rm -f rostio.db
poetry run alembic upgrade head
```

## 📊 Test Coverage

- **API Tests**: 18 tests (Organizations, People, Events, Availability, etc.)
- **GUI Tests**: 5 tests (Login, Event Management, Assignments, etc.)
- **Integration**: 1 test (End-to-end blocked dates)
- **Total**: 32 tests, 100% coverage of critical features

See [TEST_COVERAGE.md](TEST_COVERAGE.md) for details.

## 🌍 Multilingual Support

The app is UTF-8 compatible and ready for:
- Any language (Chinese, Arabic, Spanish, etc.)
- Emojis in user content
- International date/time formats

## 🐛 Troubleshooting

### Server won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Tests failing
```bash
# Check server is running
curl http://localhost:8000/api/organizations/

# View server logs
tail -f /tmp/test_server.log

# Run single test with verbose output
pytest tests/comprehensive_test_suite.py::TestClassName::test_name -vv
```

### GUI not updating
- Hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)
- Clear browser cache
- Check browser console for errors

## 📚 Documentation

- [TEST_COVERAGE.md](TEST_COVERAGE.md) - Complete test documentation
- [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) - Recent improvements
- API Docs: http://localhost:8000/docs (when server is running)

## 🎯 Quick Feature Reference

| Feature | Location | Key Files |
|---------|----------|-----------|
| Blocked Dates | Availability view | `api/routers/availability.py` |
| Event Validation | Event Management | `api/routers/events.py` |
| Assignment Modal | Admin Dashboard | `frontend/js/app-user.js` |
| PDF Export | Solutions list | `api/utils/pdf_export.py` |
| Schedule Solver | Admin Dashboard | `api/routers/solver.py` |

## 🚨 Important Notes

1. **Blocked dates are checked everywhere**: Event validation, assignments, PDFs
2. **PDF uses `[BLOCKED]` markers**: Not emojis (for UTF-8 compatibility)
3. **Event validation fails if**: Missing config, insufficient people, OR blocked assignments
4. **Always run tests before deployment**: `./scripts/cleanup_and_test.sh`

## 💡 Tips

- Use `make server` for quick start
- Run `./scripts/cleanup_and_test.sh` before committing
- Check `TEST_COVERAGE.md` for test examples
- Server logs go to `/tmp/test_server.log`
- Screenshots saved to `/tmp/*.png` during GUI tests

---

**Need help?** Check the full documentation in TEST_COVERAGE.md and REFACTORING_SUMMARY.md
