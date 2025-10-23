# SignUpFlow Constitution

<!--
Sync Impact Report - Version 1.0.0 (Initial Constitution)
═══════════════════════════════════════════════════════════════════════════

Version Change: [NONE] → 1.0.0
Rationale: Initial constitution establishing core development principles for SignUpFlow

Modified Principles:
- NONE (Initial creation)

Added Sections:
- Core Principles (7 principles)
  1. User-First Testing (E2E mandatory)
  2. Security-First Development
  3. Multi-tenant Isolation
  4. Test Coverage Excellence
  5. Internationalization by Default
  6. Code Quality Standards
  7. Clear Documentation

- Quality Requirements
  - Testing standards
  - Security requirements
  - Performance standards

- Development Workflow
  - Feature development process
  - Testing gates
  - Deployment requirements

- Governance
  - Amendment procedures
  - Compliance verification

Removed Sections:
- NONE (Initial creation)

Templates Requiring Updates:
✅ spec-template.md - Aligned (user scenarios match E2E testing principle)
✅ plan-template.md - Aligned (constitution check present)
✅ tasks-template.md - Aligned (testing tasks match principles)
⚠ checklist-template.md - Should reference E2E testing requirement
⚠ agent-file-template.md - Should reference testing and security principles

Follow-up TODOs:
1. Update checklist-template.md to include E2E test verification step
2. Update agent-file-template.md to reference constitution principles
3. Add constitution checks to pre-commit hooks
4. Document constitution compliance verification process

═══════════════════════════════════════════════════════════════════════════
-->

## Core Principles

### 1. User-First Testing (E2E MANDATORY)

**Golden Rule**: If a user can see it, click it, or type in it → it MUST have an E2E test that simulates the EXACT user journey.

**Non-Negotiable Requirements**:
- Write E2E test FIRST before any implementation
- Test what the user EXPERIENCES, not what the code DOES
- Every feature must have: Plan → E2E Test (failing) → Implementation → E2E Test (passing) → Manual Browser Verification
- Test must verify UI state, not just API responses
- All E2E tests must pass before merging to main (no exceptions)
- Disabled tests MUST be re-enabled before feature is considered complete

**Rationale**: User experience is the ultimate measure of success. API tests alone have repeatedly failed to catch UI bugs, state issues, and integration problems. E2E tests are the single source of truth for feature completeness.

**Examples**:
- ❌ Bad: "API returns 201" → ✅ Good: "User sees success message on screen"
- ❌ Bad: "Backend saves to database" → ✅ Good: "User sees saved data displayed in UI"

### 2. Security-First Development

**Non-Negotiable Requirements**:
- JWT Bearer token authentication for ALL protected endpoints
- Bcrypt password hashing (12 rounds minimum) - NEVER plain text or reversible encryption
- Multi-tenant organization isolation in EVERY database query
- RBAC (Role-Based Access Control) enforcement at API layer
- Authentication check via `authFetch()` in frontend (NEVER use plain `fetch()` for protected endpoints)
- No hardcoded secrets (use environment variables)
- Security tests required for authentication, authorization, and data isolation

**Rationale**: SignUpFlow is a SaaS platform managing sensitive volunteer data. Security breaches would destroy user trust and violate multi-tenant guarantees. Security-first approach prevents data leaks between organizations.

**Enforcement**:
- `verify_admin_access()` dependency for admin-only endpoints
- `verify_org_member()` check in every endpoint accessing organization data
- RBAC E2E tests (27+ comprehensive tests) must remain passing

### 3. Multi-tenant Isolation

**Non-Negotiable Requirements**:
- ALWAYS filter database queries by `org_id`
- NEVER allow cross-organization data access
- Verify user belongs to organization in EVERY endpoint
- Organization ID required in all API requests touching org data
- No shared resources between organizations (schedules, people, events)

**Rationale**: Multi-tenant architecture is core to SaaS model. Any data leak between organizations would be catastrophic for business and user trust.

**Pattern Enforcement**:
```python
# CORRECT - Always filter by org_id
people = db.query(Person).filter(Person.org_id == org_id).all()
verify_org_member(current_user, org_id)

# WRONG - Missing org_id filter (data leak!)
people = db.query(Person).all()
```

### 4. Test Coverage Excellence

**Non-Negotiable Requirements**:
- Maintain ≥99% test pass rate (currently 281 passing / 99.6%)
- NEVER commit code with failing tests
- NEVER disable/skip tests to achieve results (find and fix root cause)
- Test types required for all features:
  - Unit tests: Core logic, business rules, utilities
  - Integration tests: API endpoints, database operations
  - E2E tests: Complete user workflows (MANDATORY - see Principle 1)
  - Frontend tests: JavaScript logic, i18n, routing

**Testing Standards**:
- Fast unit tests available: `make test-unit-fast` (~7s)
- Full test suite: `make test-all` (~50s)
- Pre-commit hook runs core tests (frontend + backend unit)
- Test pyramid: Many unit tests, fewer integration tests, critical E2E tests

**Rationale**: High test coverage has caught 100% of critical bugs before production. Tests are the safety net enabling rapid iteration and refactoring. Broken tests indicate broken code—fix the issue, not the test.

### 5. Internationalization by Default

**Non-Negotiable Requirements**:
- All user-facing text MUST use i18n translation keys
- Support for 6 languages: English, Spanish, Portuguese, Simplified Chinese, Traditional Chinese, Korean
- NEVER hardcode English text in UI (use `data-i18n` attributes or `i18n.t()`)
- Translation keys required in all 6 language files before merging
- Comprehensive i18n regression tests (15 tests) must remain passing

**Pattern Enforcement**:
```javascript
// CORRECT - Using i18n
<button data-i18n="common.buttons.save">Save</button>
const message = i18n.t('messages.success.event_created');

// WRONG - Hardcoded English
<button>Save</button>
const message = "Event created successfully";
```

**Rationale**: SignUpFlow targets global organizations (churches, sports leagues, non-profits). Language barriers prevent adoption. i18n from day one prevents costly retrofitting.

### 6. Code Quality Standards

**Non-Negotiable Requirements**:
- Follow existing patterns and conventions (see CLAUDE.md for details)
- Backend: FastAPI routers, SQLAlchemy ORM, Pydantic validation
- Frontend: Vanilla JS (no framework by design), modular structure
- Naming conventions: Python snake_case, JavaScript camelCase, CSS kebab-case
- No TODO comments for core functionality (implement it or create a task)
- No mock/stub implementations (build real functionality)
- Database queries: Use ORM, avoid raw SQL, always include org_id filter

**Code Organization**:
- Backend: `api/routers/` for endpoints, `api/services/` for business logic
- Frontend: `frontend/js/` modular files, no monolithic app.js
- Tests: Organized by type (`unit/`, `integration/`, `e2e/`)
- Documentation: Keep `docs/` and `CLAUDE.md` updated

**Rationale**: Consistent patterns reduce cognitive load, speed up onboarding, and prevent bugs. Vanilla JS choice is intentional for simplicity and learning.

### 7. Clear Documentation

**Non-Negotiable Requirements**:
- Update `CLAUDE.md` for significant architecture changes
- API documentation via FastAPI Swagger UI (`/docs` endpoint)
- i18n changes documented in `docs/I18N_QUICK_START.md`
- RBAC changes documented in `docs/RBAC_IMPLEMENTATION_COMPLETE.md`
- Test performance documented in `docs/TEST_PERFORMANCE.md`
- Every feature branch must have BDD scenarios in feature documentation

**Documentation Types**:
- Architecture docs: System design, tech stack, patterns
- API docs: Auto-generated Swagger, endpoint usage examples
- Testing docs: Coverage reports, E2E test catalog, performance guides
- Process docs: Development workflow, deployment procedures

**Rationale**: SignUpFlow has comprehensive documentation that prevents knowledge silos and enables AI assistants to work effectively. Documentation is a first-class citizen, not an afterthought.

## Quality Requirements

### Testing Standards

**Unit Tests**:
- Fast execution (target: <10s for full unit suite)
- Isolated: No database, network, or external dependencies
- High coverage: All business logic, utilities, validators
- Slow tests marked with `@pytest.mark.slow` for optional skipping

**Integration Tests**:
- Real database connections (SQLite for dev, PostgreSQL for production)
- Test complete API workflows (auth → request → response)
- Multi-tenant isolation verification
- RBAC permission enforcement

**E2E Tests** (See Principle 1):
- Complete user journeys from login to success
- Browser automation via Playwright
- Verify UI state, not just HTTP responses
- Test timezone handling, i18n, role permissions

**Test Performance**:
- `make test` (pre-commit): <15s
- `make test-unit-fast`: <10s
- `make test-all`: <60s
- Individual test timeout: 30s maximum

### Security Requirements

**Authentication**:
- JWT tokens with 24-hour expiration
- Bcrypt password hashing (12 rounds, auto-salting)
- Secure token storage (localStorage with HTTPS only)
- Token validation on every protected endpoint

**Authorization**:
- RBAC with two roles: `admin`, `volunteer`
- Permission checks at API layer (not just UI)
- Organization membership verification
- 27+ RBAC E2E tests covering all permission scenarios

**Data Protection**:
- No passwords in logs or error messages
- No cross-organization data leaks
- Secure session management
- Input validation on frontend AND backend

### Performance Standards

**Response Times**:
- API endpoints: <200ms for simple queries
- Database queries: Indexed columns, no N+1 queries
- Frontend: <2s time to interactive
- Solver: <10s for 200 people, 50 events

**Scalability**:
- Support 200+ volunteers per organization
- Handle 50+ concurrent events
- Multi-tenant: 1000+ organizations
- Database: PostgreSQL for production, proper indexing

## Development Workflow

### Feature Development Process

**1. Planning Phase**:
- Create feature branch: `001-feature-name`
- Document requirements in `spec.md` (BDD scenarios)
- Define technical approach in `plan.md`
- Break down into tasks in `tasks.md`

**2. Test-Driven Development**:
- Write E2E test FIRST (failing)
- Write integration tests for API
- Write unit tests for business logic
- Implement feature to make tests pass
- Verify in browser manually

**3. Quality Gates**:
- All tests passing (unit, integration, E2E)
- i18n translations complete (all 6 languages)
- RBAC permissions verified
- Documentation updated
- Pre-commit hook passes

**4. Review & Merge**:
- Self-review against constitution principles
- Run `make test-all` (must be 100% passing)
- Verify no console errors or warnings
- Update CLAUDE.md if architecture changed
- Commit with descriptive message

### Testing Gates

**Before Implementation**:
- [ ] E2E test written and failing
- [ ] Integration tests written and failing
- [ ] Unit tests written and failing
- [ ] Test plan reviewed and approved

**Before Committing**:
- [ ] E2E tests passing (verified UI state)
- [ ] Integration tests passing
- [ ] Unit tests passing
- [ ] Frontend tests passing
- [ ] Manual browser verification complete
- [ ] No console errors
- [ ] i18n complete for all languages

**Before Deploying**:
- [ ] Full test suite passing (make test-all)
- [ ] Security tests passing
- [ ] Performance tests passing (if applicable)
- [ ] Documentation updated
- [ ] Production checklist complete

### Deployment Requirements

**Pre-Production**:
- SQLite → PostgreSQL migration tested
- Environment variables configured
- HTTPS/SSL certificates installed
- Backup procedures tested
- Monitoring and logging enabled

**Production Monitoring**:
- Error tracking (Sentry or equivalent)
- Performance monitoring (response times)
- Security monitoring (failed auth attempts)
- Database health checks
- Automated backups

## Governance

### Amendment Procedures

**Constitution Changes**:
1. Propose change with rationale (why needed, what problem it solves)
2. Version bump decision:
   - MAJOR: Breaking changes to governance or principle removal
   - MINOR: New principle added or material expansion
   - PATCH: Clarifications, wording improvements
3. Update constitution via `/speckit.constitution` command
4. Update dependent templates (spec, plan, tasks, checklists)
5. Verify no conflicts with existing implementations
6. Document in Sync Impact Report (HTML comment)
7. Commit with version change in message

**Emergency Amendments**:
- Critical security issues may bypass normal procedure
- Document emergency change and rationale
- Follow up with formal amendment review

### Compliance Verification

**Every Feature**:
- Self-review against all 7 core principles
- Verify E2E testing workflow followed (Principle 1)
- Verify security requirements met (Principle 2)
- Verify multi-tenant isolation (Principle 3)
- Verify test coverage maintained (Principle 4)
- Verify i18n complete (Principle 5)
- Verify code quality standards (Principle 6)
- Verify documentation updated (Principle 7)

**Regular Audits**:
- Weekly: Review test pass rate (must be ≥99%)
- Monthly: Security audit (RBAC tests, auth tests)
- Quarterly: Performance audit (test suite speed)
- Annually: Constitution review (principles still relevant?)

**Enforcement**:
- Pre-commit hooks verify test pass rate
- CI/CD pipeline enforces quality gates (future)
- Code reviews verify constitution compliance
- Failed compliance blocks merge to main

**Authority**:
This constitution supersedes all other development practices and conventions. When in doubt, constitution principles take precedence. Exceptions require explicit documentation and approval.

**Guidance Reference**:
For runtime development guidance and detailed patterns, refer to `CLAUDE.md` (AI assistant context) and `docs/` directory.

---

**Version**: 1.0.0 | **Ratified**: 2025-01-20 | **Last Amended**: 2025-01-20
