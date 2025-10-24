# [PROJECT NAME] Development Guidelines

Auto-generated from all feature plans. Last updated: [DATE]

## Constitution Compliance

**All features MUST comply with SignUpFlow Constitution** (`.specify/memory/constitution.md`)

### Core Principles (Non-Negotiable):
1. **E2E Testing First**: Write E2E test before implementation, test user experience not code
2. **Security First**: JWT auth, bcrypt passwords, RBAC enforcement, multi-tenant isolation
3. **Multi-tenant Isolation**: Always filter by org_id, verify org membership
4. **Test Coverage**: ≥99% pass rate, never commit failing tests
5. **i18n by Default**: All text in 6 languages, use i18n.t() not hardcoded strings
6. **Code Quality**: Follow patterns, no TODOs, no mocks/stubs
7. **Clear Documentation**: Update CLAUDE.md, API docs, test docs

### Testing Standards:
- **E2E Tests**: Complete user journeys via Playwright (MANDATORY)
- **Integration Tests**: API workflows with real database
- **Unit Tests**: Business logic, isolated, fast (<10s)
- **Pre-commit Hook**: Must pass before merge

### Security Requirements:
- JWT Bearer tokens (24h expiration)
- Bcrypt password hashing (12 rounds)
- RBAC with admin/volunteer roles
- Organization isolation in every query
- 27+ RBAC E2E tests must remain passing

## Active Technologies
[EXTRACTED FROM ALL PLAN.MD FILES]

## Project Structure
```
[ACTUAL STRUCTURE FROM PLANS]
```

## Commands
[ONLY COMMANDS FOR ACTIVE TECHNOLOGIES]

## Code Style
[LANGUAGE-SPECIFIC, ONLY FOR LANGUAGES IN USE]

## Recent Changes
[LAST 3 FEATURES AND WHAT THEY ADDED]

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
