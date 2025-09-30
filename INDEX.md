# Roster Project Documentation Index

## 🎯 Quick Navigation

### For New Users
1. **[STATUS.md](STATUS.md)** - Current project status and what works
2. **[API_QUICKSTART.md](API_QUICKSTART.md)** - Get started in 5 minutes
3. **[examples/api_example.py](examples/api_example.py)** - Working code example

### For Developers
1. **[API.md](API.md)** - Complete API reference
2. **[test_api.py](test_api.py)** - Comprehensive test suite
3. **[API_TEST_RESULTS.md](API_TEST_RESULTS.md)** - Test results and validation

### For Project Managers
1. **[SUMMARY.md](SUMMARY.md)** - High-level project summary
2. **[README.md](README.md)** - Full project documentation

---

## 📚 Documentation Files

### Core Documentation

| File | Purpose | Audience |
|------|---------|----------|
| [STATUS.md](STATUS.md) | Current status, what works, what doesn't | Everyone |
| [README.md](README.md) | Complete project documentation | Everyone |
| [API.md](API.md) | Full API reference with examples | Developers |
| [API_QUICKSTART.md](API_QUICKSTART.md) | 5-minute quick start guide | Developers |
| [SUMMARY.md](SUMMARY.md) | Project summary and architecture | Managers |

### Test & Validation

| File | Purpose |
|------|---------|
| [test_api.py](test_api.py) | Comprehensive API test suite |
| [API_TEST_RESULTS.md](API_TEST_RESULTS.md) | Detailed test results |
| [tests/](tests/) | Unit test suite (5 modules) |

### Examples

| File | Purpose |
|------|---------|
| [examples/api_example.py](examples/api_example.py) | Complete working example |

### Configuration

| File | Purpose |
|------|---------|
| [pyproject.toml](pyproject.toml) | Poetry dependencies |
| [Makefile](Makefile) | Development commands |
| [pytest.ini](pytest.ini) | Test configuration |

---

## 🚀 Quick Start Paths

### "I want to schedule events"

1. Read [API_QUICKSTART.md](API_QUICKSTART.md)
2. Run `poetry run python examples/api_example.py`
3. Adapt the example to your needs

### "I want to understand the architecture"

1. Read [SUMMARY.md](SUMMARY.md) - Architecture overview
2. Read [API.md](API.md) - API design
3. Review [roster_cli/core/](roster_cli/core/) - Implementation

### "I want to verify it works"

1. Read [API_TEST_RESULTS.md](API_TEST_RESULTS.md) - Test results
2. Run `poetry run python test_api.py` - Live tests
3. Check output files in `/tmp/test_*/out/`

### "I want to customize constraints"

1. Read [API.md](API.md) § "Advanced Usage → Custom Constraints"
2. Review [roster_cli/templates/](roster_cli/templates/) - Example constraints
3. Review [roster_cli/core/constraints/](roster_cli/core/constraints/) - Engine

### "I want to integrate into my app"

1. Read [API_QUICKSTART.md](API_QUICKSTART.md) § "Complete Minimal Example"
2. Review [API.md](API.md) § "Core Modules"
3. Copy [examples/api_example.py](examples/api_example.py) as starting point

---

## 📦 Project Structure

```
roster/
├── INDEX.md                    ← You are here
├── STATUS.md                   ← Current status
├── README.md                   ← Full documentation
├── API.md                      ← API reference
├── API_QUICKSTART.md           ← Quick start
├── SUMMARY.md                  ← Project summary
├── API_TEST_RESULTS.md         ← Test results
├── test_api.py                 ← Test suite
├── examples/
│   └── api_example.py          ← Working example
├── roster_cli/
│   ├── main.py                 ← CLI entry (Typer issue)
│   ├── commands/               ← 10 CLI commands
│   ├── core/                   ← Core engine
│   │   ├── models.py           ← Data models
│   │   ├── loader.py           ← Data loaders
│   │   ├── constraints/        ← Constraint DSL
│   │   └── solver/             ← Solver architecture
│   └── templates/              ← 3 ready-to-use templates
│       ├── cricket/
│       ├── church/
│       └── oncall/
└── tests/                      ← Unit tests (5 modules)
```

---

## 🎯 Use Cases

### Cricket League Scheduling
- **Template**: `roster_cli/templates/cricket/`
- **Example**: Run `test_api.py` and check `/tmp/test_cricket/`
- **Features**: Round-robin fixtures, long weekend rules, ground allocation

### Church Volunteer Roster
- **Template**: `roster_cli/templates/church/`
- **Example**: Run `examples/api_example.py`
- **Features**: Role coverage, cooldown periods, fairness constraints

### On-Call Rotation
- **Template**: `roster_cli/templates/oncall/`
- **Example**: Run `test_api.py` and check `/tmp/test_oncall/`
- **Features**: L1/L2/L3 tiers, minimum rest gaps, load balancing

---

## 🔧 Development Commands

```bash
# Install
poetry install

# Test API
poetry run python test_api.py

# Run example
poetry run python examples/api_example.py

# Format code
make fmt

# Lint
make lint

# Clean
make clean
```

---

## ⚡ Performance

| Template | Events | People | Solve Time |
|----------|--------|--------|------------|
| Cricket  | 10     | 40     | < 1ms      |
| Church   | 8      | 20     | 1ms        |
| On-Call  | 10     | 12     | 1ms        |

All solves complete in **< 2ms** ✅

---

## 📊 Status Summary

| Component | Status | Notes |
|-----------|--------|-------|
| API | ✅ 100% | Fully functional |
| Solver | ✅ 100% | Greedy heuristic working |
| Templates | ✅ 100% | 3 complete templates |
| Tests | ✅ 100% | API fully tested |
| Docs | ✅ 100% | Comprehensive |
| CLI | ⚠️ 90% | Typer framework issue |

**Overall**: ✅ **Production-ready API MVP**

---

## 🆘 Troubleshooting

### "CLI doesn't work"
- **Cause**: Typer framework compatibility issue
- **Solution**: Use Python API directly (fully functional)
- **Reference**: [STATUS.md](STATUS.md) § "What Doesn't Work"

### "How do I run tests?"
```bash
poetry run python test_api.py
```

### "Where are the examples?"
- Code: [examples/api_example.py](examples/api_example.py)
- Tests: [test_api.py](test_api.py)
- Docs: [API_QUICKSTART.md](API_QUICKSTART.md)

### "How do I customize?"
1. Copy a template from `roster_cli/templates/`
2. Modify YAML files (people, events, constraints)
3. Run solver via API (see [API_QUICKSTART.md](API_QUICKSTART.md))

---

## 📞 Support

- **Bug Reports**: See [STATUS.md](STATUS.md) for known issues
- **API Questions**: See [API.md](API.md)
- **Examples**: See [examples/api_example.py](examples/api_example.py)

---

## 🎓 Learning Path

**Beginner**:
1. [API_QUICKSTART.md](API_QUICKSTART.md) - 5 minutes
2. Run `poetry run python examples/api_example.py`
3. Try modifying the example

**Intermediate**:
1. [API.md](API.md) - Full reference
2. Run `poetry run python test_api.py`
3. Explore templates in `roster_cli/templates/`

**Advanced**:
1. Review [roster_cli/core/solver/](roster_cli/core/solver/)
2. Read [roster_cli/core/constraints/](roster_cli/core/constraints/)
3. Implement custom solver or constraints

---

**Last Updated**: 2025-09-30
**Version**: 0.1.0
**Status**: ✅ API MVP Complete
