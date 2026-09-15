# Contributing to SignUpFlow

## Before Making Changes

### The Golden Rule
**Write the test first. Implement to make it pass. Verify against the suite before committing.**

---

## Development Workflow

### 1. Plan the Feature
- [ ] Write down the user journey in plain English
- [ ] Identify the API endpoints, CLI commands, or domain logic involved
- [ ] Note any dependencies (auth, RBAC, multi-tenancy, solver constraints)

### 2. Write the Test FIRST
- [ ] **Unit-level**: add to `tests/unit/test_<module>.py`
- [ ] **HTTP-level**: add to `tests/api/test_<feature>.py` (real JWT, isolated DB)
- [ ] **CLI-level**: add to `tests/cli/test_<feature>.py` (subprocess, YAML in / JSON out)
- [ ] Run the new test — it should FAIL (test-first)

### 3. Implement the Feature
- [ ] Write minimum code to make the test pass
- [ ] Check for dependencies:
  - [ ] Auth + RBAC (admin vs volunteer)
  - [ ] `org_id` filter on every query (multi-tenant isolation)
  - [ ] Pydantic schema validation at the boundary
  - [ ] Error handling with clear API messages

### 4. Verify the Feature
- [ ] Run the new test — it should PASS
- [ ] Run `make test-unit` — no regressions
- [ ] Run `make test-all` before every PR; it includes all seven Python tiers
- [ ] Run `make test-postgres` for database or migration changes
- [ ] Run `make test-redis` for rate-limit changes
- [ ] Run `make test-artifact` and then `make test-security` for release-image or dependency changes
- [ ] Run `make test-mobile` for mobile changes

### 5. Before Submitting
- [ ] All tests pass
- [ ] No TODOs or FIXMEs in code
- [ ] `poetry run black api tests` and `poetry run ruff check`
- [ ] `poetry run mypy api` if you touched typed modules

---

## Test Layout

| Suite | Location | What it covers |
|-------|----------|----------------|
| Unit | `tests/unit/` | Individual functions, mocked auth, fast |
| API | `tests/api/`, `tests/security/` | Full HTTP and authentication workflows with real JWT + isolated DB |
| CLI | `tests/cli/` | Subprocess CLI: YAML in, JSON out, real solver |
| Integration | `tests/integration/` | Real DB + real auth |
| Web | `tests/web/` | Cookie and HTMX routes |
| Contract | `tests/contract/` | OpenAPI snapshot |
| Browser | `tests/e2e/` | Live application with Playwright |
| Mobile | `mobile/test/` | Flutter unit/widget tests, separate command |
| Local manifest | `tests/local_validation_manifest.json` | Complete default and opt-in inventory |

Every public API endpoint or CLI subcommand MUST have:

1. **Happy Path** — caller provides valid input, expected output is returned
2. **Validation Path** — caller provides invalid input, clear error returned
3. **Authorization Path** — wrong role / wrong org / no token returns 401/403

---

## Common Feature Dependencies

### Authentication
- [ ] JWT token issued + verified
- [ ] Role-based access control (`admin` vs `volunteer`)
- [ ] Org membership check via `verify_org_member`

### Multi-tenancy
- [ ] `org_id` filter on every DB query
- [ ] Cross-org request returns 403/404 (never leaks data)

### Solver
- [ ] Constraints honored (hard violations = 0)
- [ ] Fairness reasonable (low stdev)
- [ ] Health score reported in solution metrics

---

## Testing Checklist

### Before Saying "Done"

**Implementation:**
- [ ] Test exists and covers the feature
- [ ] Test passes consistently
- [ ] Manually exercised via `curl` or the CLI

**Code Quality:**
- [ ] No TODOs or FIXMEs
- [ ] Error handling for all async operations
- [ ] Pydantic schemas at boundaries

**Dependencies:**
- [ ] RBAC checks in place
- [ ] `org_id` filter on every query
- [ ] Schema validation (request + response)

**Testing:**
- [ ] Unit tests for business logic
- [ ] API or CLI tests for the user-facing surface
- [ ] All tests pass
- [ ] No flaky tests

---

## Running Tests

```bash
# Fast iteration
make test-unit-fast

# Single file
poetry run pytest tests/unit/test_events.py -v

# Single test
poetry run pytest tests/unit/test_events.py::test_create_event -v

# Whole pyramid
make test-all

# Owned PostgreSQL acceptance for database/migration changes
make test-postgres
make test-redis

# Same-SHA release artifact and local security/SBOM acceptance
make test-artifact
make test-security
```

---

## Commits & PRs

- Use imperative plain-English commit titles; no mandatory Conventional Commit prefix
- Keep each commit scoped to a single concern
- PRs include: a short summary, list of tests run, and any migration / config steps
- Record local results against the pushed head SHA. Require successful local validation,
  current-head/base local code review, and GitHub mergeability before merging.
- No CI checks. Run all analysis, migrations, tests and code review locally.
- Follow [the current testing guide](docs/TESTING.md), including browser prerequisites.
- Reconcile affected code, tests, documentation, and agent instructions before
  declaring done. Label retained historical guidance; report unverified scope.
