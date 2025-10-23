# Implementation Plan: Security Hardening & Compliance

**Branch**: `004-security-hardening` | **Date**: 2025-10-20 | **Spec**: [spec.md](./spec.md)

## Summary

Security hardening features including rate limiting (5 attempts/15min lockout), comprehensive audit logging (12-month retention), TOTP-based 2FA, CSRF protection, session invalidation on password changes, security headers (HSTS, CSP, X-Frame-Options), input validation/sanitization, and secure password reset with time-limited tokens.

## Technical Context

**Language/Version**: Python 3.11+ (backend), Vanilla JavaScript (frontend)

**Primary Dependencies**:
- FastAPI 0.115+ (existing backend framework)
- PyJWT (existing JWT authentication)
- bcrypt (existing password hashing)
- **pyotp** (TOTP 2FA implementation - RFC 6238)
- **qrcode** (QR code generation for 2FA setup)
- **slowapi** (rate limiting middleware for FastAPI)
- **python-multipart** (CSRF token handling)
- Pydantic 2.0+ (input validation)
- bleach (HTML sanitization for XSS prevention)
- **NEEDS CLARIFICATION**: CSRF token storage (session-based vs JWT claims vs separate Redis store)
- **NEEDS CLARIFICATION**: Rate limit storage backend (in-memory vs Redis vs database)

**Storage**:
- PostgreSQL 14+ (audit logs, rate limit data, 2FA secrets, CSRF tokens)
- Redis (optional: distributed rate limiting, session blacklist for password changes)

**Testing**:
- pytest (backend security tests)
- Playwright (E2E security workflow tests)
- **NEEDS CLARIFICATION**: Security scanning tools (OWASP ZAP, Bandit, Safety) - which to integrate into CI/CD

**Target Platform**: Linux server containers (Docker-based)

**Project Type**: Web application (FastAPI backend + Vanilla JS frontend)

**Performance Goals**:
- Rate limit check: <10ms overhead per request
- Audit log write: <50ms (async, non-blocking)
- 2FA validation: <100ms (TOTP computation + database lookup)
- CSRF validation: <5ms (token comparison)

**Constraints**:
- Audit logs immutable (append-only, no updates/deletes)
- 2FA secret storage encrypted at rest
- Rate limiting must not affect legitimate users during traffic spikes
- Security headers must not break existing frontend functionality

**Scale/Scope**:
- Audit log retention: 12 months minimum (compliance requirement)
- Rate limiting: Handle 1000+ login attempts/second distributed across accounts
- 2FA adoption: Target 50% of users enabling 2FA within first month
- Audit log storage: Estimate 10MB/month for 100 organizations

---

## Constitution Check

**Overall Status**: ✅ ALL GATES PASS

### Principle 1: User-First Testing (E2E MANDATORY)

**Status**: ✅ PASS

E2E tests will verify:
- **Rate Limiting**: User attempts 6 failed logins → 6th blocked → lockout message displayed
- **Audit Logging**: Admin changes user role → Audit log entry visible in admin dashboard → Export works
- **2FA Setup**: User scans QR code → Enters code → Login requires 2FA → Lost phone recovery works
- **CSRF Protection**: Form submit without token → 403 error shown → With token succeeds
- **Session Invalidation**: User changes password in Browser A → Browser B immediately logged out

Tests verify what user/admin EXPERIENCES, not just API responses.

### Principle 2: Security-First Development

**Status**: ✅ PASS (This IS security-first)

This entire feature enhances security posture:
- Rate limiting prevents brute force attacks
- Audit logging enables breach investigation and compliance
- 2FA protects against password compromise
- CSRF prevents unauthorized state changes
- Security headers provide defense-in-depth

No security regressions - all changes strengthen existing JWT authentication.

### Principle 3: Multi-tenant Isolation

**Status**: ✅ PASS

Security features preserve multi-tenant isolation:
- Audit logs filtered by org_id (admins only see own org's audit trail)
- Rate limiting scoped per-account (not global limits affecting other orgs)
- 2FA secrets per-user (no cross-user access)
- CSRF tokens per-session (isolation maintained)

### Principle 4: Test Coverage Excellence

**Status**: ✅ PASS

Comprehensive security tests required:
- **Unit tests**: Rate limiting logic, TOTP validation, audit log immutability
- **Integration tests**: CSRF middleware, security headers, password reset flow
- **E2E tests**: Complete security workflows (2FA setup, rate limit lockout, audit log export)
- **Security tests**: Penetration testing, OWASP Top 10 coverage

### Principle 5: Internationalization

**Status**: ✅ PASS

All security messages require i18n:
- Rate limit errors: "Too many failed attempts. Try again in {minutes} minutes"
- 2FA setup instructions: "Scan QR code with authenticator app"
- CSRF errors: "Security token invalid. Please refresh page"
- Audit log UI: Action types, export labels

### Principle 6: Code Quality Standards

**Status**: ✅ PASS

Security code follows strict quality standards:
- No hardcoded secrets (2FA seeds, CSRF keys from environment)
- Input validation using Pydantic (type-safe, automatic OpenAPI docs)
- Security middleware (reusable rate limiting, CSRF decorators)
- Security headers configured centrally (FastAPI middleware)

### Principle 7: Clear Documentation

**Status**: ✅ PASS

Security documentation required:
- `docs/SECURITY_GUIDE.md`: Security features overview, 2FA setup, audit logging
- `docs/COMPLIANCE.md`: Audit trail for SOC 2, GDPR compliance evidence
- `docs/RATE_LIMITING.md`: Rate limit configuration, admin override procedures
- API docs: Security endpoints documented in Swagger UI

---

## Project Structure

### Documentation (this feature)

```
specs/004-security-hardening/
├── plan.md              # This file
├── research.md          # Phase 0: Technology choices for rate limiting, 2FA, CSRF
├── data-model.md        # Phase 1: AuditLog, RateLimitEntry, TwoFactorSecret entities
├── quickstart.md        # Phase 1: Local security testing setup
├── contracts/           # Phase 1: API contracts for security endpoints
└── tasks.md             # Phase 2: Implementation tasks (NOT created by /speckit.plan)
```

### Source Code (repository root)

```
SignUpFlow/
├── api/
│   ├── routers/
│   │   ├── security.py           # NEW: 2FA setup, audit log endpoints
│   │   ├── auth.py               # MODIFIED: Add rate limiting, CSRF, session invalidation
│   │   └── ...
│   ├── services/
│   │   ├── rate_limiter.py       # NEW: Rate limiting service
│   │   ├── audit_logger.py       # NEW: Audit logging service
│   │   ├── two_factor.py         # NEW: TOTP 2FA service
│   │   └── csrf_protection.py    # NEW: CSRF token management
│   ├── middleware/
│   │   ├── rate_limit.py         # NEW: Rate limiting middleware
│   │   ├── csrf.py               # NEW: CSRF validation middleware
│   │   └── security_headers.py   # NEW: Security headers middleware
│   ├── models.py                 # MODIFIED: Add AuditLog, RateLimitEntry, TwoFactorSecret
│   └── main.py                   # MODIFIED: Register security middleware
│
├── frontend/
│   ├── js/
│   │   ├── app-user.js           # MODIFIED: 2FA setup UI, password change
│   │   ├── app-admin.js          # MODIFIED: Audit log viewer, rate limit dashboard
│   │   ├── csrf.js               # NEW: CSRF token handling
│   │   └── auth.js               # MODIFIED: 2FA login flow
│   └── index.html                # MODIFIED: Add CSP meta tags
│
├── tests/
│   ├── e2e/
│   │   ├── test_rate_limiting.py     # NEW: Rate limit E2E tests
│   │   ├── test_2fa_workflow.py      # NEW: 2FA setup/login E2E tests
│   │   ├── test_audit_logging.py     # NEW: Audit log E2E tests
│   │   └── test_csrf_protection.py   # NEW: CSRF E2E tests
│   ├── integration/
│   │   ├── test_rate_limiter.py      # NEW: Rate limiting integration
│   │   ├── test_2fa_service.py       # NEW: TOTP validation integration
│   │   └── test_audit_service.py     # NEW: Audit logging integration
│   ├── security/
│   │   ├── test_xss_prevention.py    # NEW: XSS attack prevention
│   │   ├── test_sql_injection.py     # NEW: SQL injection prevention
│   │   └── test_csrf_attacks.py      # NEW: CSRF attack prevention
│   └── unit/
│       ├── test_totp.py              # NEW: TOTP generation/validation
│       ├── test_csrf_tokens.py       # NEW: CSRF token logic
│       └── test_security_headers.py  # NEW: Header configuration
│
├── docs/
│   ├── SECURITY_GUIDE.md         # NEW: Security features guide
│   ├── COMPLIANCE.md             # NEW: Compliance documentation
│   └── RATE_LIMITING.md          # NEW: Rate limiting configuration
│
└── .env.example                  # UPDATED: 2FA secret key, CSRF secret key
```

**Structure Decision**: Security features integrate into existing FastAPI backend structure with new middleware layer for cross-cutting security concerns (rate limiting, CSRF, headers). Audit logging and 2FA are service-layer components called from routers.

---

## Complexity Tracking

**No violations detected** - Complexity tracking table not needed. All constitutional principles satisfied.

---

**Phase 0 Next**: Generate research.md to resolve NEEDS CLARIFICATION items (CSRF storage strategy, rate limit backend, security scanning tools).
