# Implementation Plan: Security Hardening and Compliance

**Branch**: `014-security-hardening` | **Date**: 2025-10-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/014-security-hardening/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

---

## Summary

Implement comprehensive security hardening across authentication, authorization, and data protection layers including rate limiting to prevent brute force attacks, audit logging for compliance (SOC 2, HIPAA, GDPR), CSRF protection for state-changing operations, session invalidation on security events, two-factor authentication (2FA) via TOTP, security headers (HSTS, CSP, X-Frame-Options), input validation and sanitization, and secure password reset with time-limited tokens. System targets industry-standard security posture with <5% false positive rate on rate limiting and 100% audit trail completeness.

---

## Technical Context

**Language/Version**: Python 3.11 (existing SignUpFlow backend), JavaScript ES6+ (frontend)

**Primary Dependencies**:
- **Rate Limiting**: Redis 7.0+ (fast in-memory storage for rate limit counters), `redis-py` library
- **Audit Logging**: SQLAlchemy (database ORM), dedicated `audit_logs` table
- **CSRF Protection**: `itsdangerous` library (token generation and validation)
- **Session Management**: Redis session store, JWT token blacklist
- **2FA (TOTP)**: `pyotp` 2.9.0 library (TOTP generation/validation), `qrcode` 7.4.2 (QR code generation)
- **Security Headers**: FastAPI middleware (built-in header control)
- **Input Validation**: Pydantic 2.0+ (data validation), `bleach` 6.1.0 (HTML sanitization)
- **Password Reset**: `itsdangerous` (secure token generation)

**Storage**:
- PostgreSQL 15+ (audit logs, user security settings, session metadata)
- Redis 7.0+ (rate limit counters, session store, token blacklist)

**Testing**:
- pytest 8.2+ (unit/integration tests)
- pytest-playwright 0.7+ (E2E security tests)
- `faker` 22.0+ (test data generation)

**Target Platform**: Linux server (Ubuntu 22.04 LTS), containerized deployment (Docker)

**Project Type**: Security enhancement (existing architecture) + new security infrastructure

**Performance Goals**:
- Rate limit check: <5ms overhead per request
- Audit log write: <10ms overhead per admin action
- CSRF token validation: <3ms overhead per request
- Session invalidation: <100ms for all sessions
- 2FA verification: <50ms per TOTP validation
- Input sanitization: <5ms per field

**Constraints**:
- Zero breaking changes to existing authentication flow
- Backward compatibility with existing JWT tokens during rollout
- Audit logs must be append-only (immutable)
- Rate limiting must not block legitimate users (false positive rate <5%)
- 2FA optional (not mandatory for all users initially)
- Redis required for production (adds infrastructure dependency)

**Scale/Scope**:
- Rate limit tracking: ~1000 IP addresses × 10 endpoints = 10K active limits
- Audit log volume: ~1000 actions/day × 90 days retention = 90K records
- Session storage: ~500 active sessions × 2 devices = 1K session keys
- 2FA users: ~20% of user base (~200 users with 2FA enabled)
- Security headers: All HTTP responses (zero overhead with middleware)
- Input validation: All API endpoints (~40 endpoints)
- Password reset: ~10 requests/day

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Compliance Status**: ✅ PASS - All principles satisfied with security-specific emphasis

### Principle 1: User-First Testing (E2E MANDATORY)

✅ **COMPLIANT** - Comprehensive E2E security testing approach

**Security Testing Approach**:
- **US1 (Rate Limiting)**: E2E test simulates 10 failed login attempts → verifies account lockout message → verifies 15-minute wait period → verifies successful login after expiry
- **US2 (Audit Logging)**: E2E test creates event as admin → modifies user roles → deletes team → verifies all actions logged with timestamp, actor, resource IDs
- **US3 (CSRF Protection)**: E2E test submits form without token → verifies 403 Forbidden → submits with valid token → verifies 200 OK
- **US4 (Session Invalidation)**: E2E test logs in on two "devices" (separate browser contexts) → changes password on first → verifies second session logged out
- **US5 (2FA)**: E2E test enables 2FA → scans QR code → logs out → attempts login with password only (fails) → enters TOTP code (succeeds)
- **US6 (Security Headers)**: E2E test verifies HTTP response headers contain HSTS, CSP, X-Frame-Options, X-Content-Type-Options
- **US7 (Input Validation)**: E2E test submits SQL injection payload in form → verifies sanitized output → verifies database integrity
- **US8 (Password Reset)**: E2E test requests reset → receives email with token → uses token to set new password → verifies old password invalid

**User Experience**: Security must be transparent to legitimate users. E2E tests verify security controls don't interfere with normal workflows.

**Test Coverage**: 8 user stories × 4 scenarios each = ~32 E2E security tests

**Rationale**: Security features must be tested from attacker's perspective (E2E tests simulate attacks) AND user's perspective (E2E tests verify UX not degraded).

### Principle 2: Security-First Development

✅ **COMPLIANT** - Security is the core focus of this feature

**Security Requirements Explicitly Addressed**:
- **FR-001 to FR-004**: Rate limiting on auth endpoints (brute force prevention)
- **FR-005 to FR-009**: Comprehensive audit logging (security events + admin actions)
- **FR-010 to FR-013**: CSRF protection for all state-changing operations
- **FR-014 to FR-018**: Session management with automatic invalidation on security events
- **FR-019 to FR-024**: Two-factor authentication (TOTP-based, industry standard)
- **FR-025 to FR-028**: Security headers (HSTS, CSP, X-Frame-Options, X-Content-Type-Options)
- **FR-029 to FR-034**: Input validation and sanitization (SQL injection, XSS prevention)
- **FR-035 to FR-040**: Secure password reset (time-limited tokens, single-use)

**Security-First Implementation**:
- Rate limiting applied BEFORE authentication logic (fail fast)
- Audit logging uses append-only storage (tamper-evident)
- CSRF tokens cryptographically secure (`itsdangerous` library with secret key)
- Session invalidation atomic (Redis transaction ensures no stale sessions)
- 2FA secrets encrypted at rest (never stored plain text)
- Security headers applied to ALL responses via middleware
- Input validation at API boundary (Pydantic models) + sanitization before storage (bleach library)
- Password reset tokens single-use and time-limited (1 hour expiry)

### Principle 3: Multi-tenant Isolation

✅ **COMPLIANT** - Security features preserve organization isolation

**Organization Isolation Maintained**:
- Audit logs include `org_id` (filtered queries maintain isolation)
- Rate limiting per-organization (prevent cross-org attack surface)
- Session management preserves `org_id` in session metadata
- 2FA settings per-user (scoped to organization via user.org_id)
- CSRF tokens session-scoped (cannot cross organizations)
- Password reset tokens user-scoped (email must match org member)

**No Cross-Organization Security Bypass**:
- Admin from Org A cannot view audit logs from Org B
- Rate limits for Org A do not affect Org B
- Session invalidation in Org A does not affect Org B users
- 2FA enrollment for user in Org A independent of Org B

### Principle 4: Test Coverage Excellence

✅ **COMPLIANT** - Comprehensive security testing strategy

**Test Types**:
- **Unit tests**: Rate limit logic, CSRF token generation, TOTP validation, input sanitization
- **Integration tests**: Rate limit Redis integration, audit log database writes, session invalidation flow
- **E2E tests**: Complete security workflows (8 user stories covering rate limiting, audit logging, CSRF, session mgmt, 2FA, headers, input validation, password reset)
- **Security tests**: Penetration testing for injection attacks, XSS, CSRF bypass attempts
- **Success Criteria**: SC-001 to SC-012 define measurable security outcomes (99% attack prevention, 100% audit coverage, <5% false positives)

**Target**: Maintain ≥99% test pass rate (current project standard)

### Principle 5: Internationalization by Default

✅ **COMPLIANT** - Security messages fully internationalized

**i18n for Security UX**:
- Rate limit error messages translated (6 languages: en, es, pt, zh-CN, zh-TW, fr)
- CSRF error messages translated
- Session expiry notifications translated
- 2FA setup instructions translated
- Input validation error messages translated
- Password reset email templates translated

**Security UI Text**:
- All security-related UI text uses i18n keys (`security.rate_limit_exceeded`, `security.csrf_token_invalid`, `security.2fa_required`)
- Error messages user-friendly and translated (avoid technical jargon)
- Security notifications preserve i18n context (email templates support 6 languages)

### Principle 6: Code Quality Standards

✅ **COMPLIANT** - Security code follows project standards

**Quality Standards**:
- **Backend**: FastAPI routers (`api/routers/security.py`), service layer (`api/services/security_service.py`), SQLAlchemy ORM
- **Frontend**: Vanilla JS security helpers (`frontend/js/security.js`), CSRF token management
- **Redis integration**: Connection pooling, error handling, failover logic
- **Testing**: Comprehensive test suite (unit, integration, E2E, security-specific tests)
- **No hardcoded values**: All configuration via environment variables (Redis URL, secret keys, rate limit thresholds)

**Security Code Patterns**:
- Use proven libraries (`pyotp`, `itsdangerous`, `bleach`) not custom crypto
- Fail securely (deny by default, explicit allow)
- Log security events but not sensitive data (no passwords in logs)
- Graceful degradation (if Redis unavailable, fail closed not open)

### Principle 7: Clear Documentation

✅ **COMPLIANT** - Comprehensive security documentation

**Required Documentation** (from spec):
1. **Security Hardening Guide** - Complete security feature overview
2. **Rate Limiting Configuration** - Threshold tuning and bypass procedures
3. **Audit Logging Guide** - Log format, retention, export procedures
4. **CSRF Protection Guide** - Token management and troubleshooting
5. **Session Management Guide** - Invalidation triggers and session monitoring
6. **2FA Setup Guide** - User enrollment and recovery procedures
7. **Security Headers Guide** - Header configuration and browser compatibility
8. **Input Validation Guide** - Validation rules and sanitization patterns
9. **Password Reset Security** - Token generation and security measures
10. **Security Incident Response** - Procedures for handling security events

**CLAUDE.md Update**: Add security architecture section describing rate limiting, audit logging, CSRF protection, session management, 2FA, security headers, input validation, password reset security.

**Constitution Violations**: NONE

**Complexity Justification**: N/A (no violations to justify)

---

## Project Structure

### Documentation (this feature)

```
specs/014-security-hardening/
├── spec.md              # Feature specification (COMPLETE - 432 lines)
├── plan.md              # This file (IN PROGRESS)
├── research.md          # Phase 0 output (PENDING)
├── quickstart.md        # Phase 1 output (PENDING)
├── contracts/           # Phase 1 output (PENDING)
│   ├── rate-limiting.md     # Rate limiting API specification
│   ├── audit-logging.md     # Audit log format and export API
│   ├── csrf-protection.md   # CSRF token generation and validation
│   ├── session-management.md # Session invalidation API
│   ├── 2fa-api.md          # 2FA enrollment and validation API
│   └── password-reset.md   # Password reset token API
└── checklists/          # Validation checklists (CREATED)
    └── requirements.md
```

**Note**: Security feature has no traditional `data-model.md` (security infrastructure spans multiple entities). Security schema documented in contracts.

### Backend Files (existing + new)

```
SignUpFlow/
├── api/
│   ├── routers/
│   │   ├── security.py              # [NEW] Security endpoints (rate limit check, audit logs)
│   │   ├── auth.py                  # [MODIFY] Add rate limiting, 2FA check
│   │   └── people.py                # [MODIFY] Add audit logging for role changes
│   │
│   ├── services/
│   │   ├── rate_limiter.py          # [NEW] Rate limiting logic (Redis-backed)
│   │   ├── audit_logger.py          # [NEW] Audit logging service
│   │   ├── csrf_service.py          # [NEW] CSRF token generation and validation
│   │   ├── session_manager.py       # [NEW] Session invalidation logic
│   │   ├── totp_service.py          # [NEW] 2FA TOTP generation and validation
│   │   ├── input_validator.py       # [NEW] Input validation and sanitization
│   │   └── password_reset_service.py # [MODIFY] Add secure token generation
│   │
│   ├── middleware/
│   │   ├── rate_limit_middleware.py # [NEW] Rate limiting FastAPI middleware
│   │   ├── csrf_middleware.py       # [NEW] CSRF validation middleware
│   │   └── security_headers_middleware.py # [NEW] Security headers middleware
│   │
│   ├── models.py                    # [MODIFY] Add AuditLog, UserSecuritySettings models
│   ├── database.py                  # [MODIFY] Add Redis connection
│   └── core/
│       ├── config.py                # [MODIFY] Add security configuration
│       └── security.py              # [MODIFY] Add 2FA verification
│
├── frontend/
│   └── js/
│       ├── security.js              # [NEW] CSRF token management, 2FA UI
│       └── app-user.js              # [MODIFY] Add CSRF tokens to forms
│
├── locales/                         # i18n translations
│   ├── en/
│   │   └── security.json            # [NEW] Security message translations
│   ├── es/, pt/, zh-CN/, zh-TW/, fr/ # [NEW] Security translations (all languages)
│
├── tests/
│   ├── unit/
│   │   ├── test_rate_limiter.py     # [NEW] Rate limiting unit tests
│   │   ├── test_audit_logger.py     # [NEW] Audit logging unit tests
│   │   ├── test_csrf_service.py     # [NEW] CSRF token unit tests
│   │   ├── test_totp_service.py     # [NEW] 2FA TOTP unit tests
│   │   └── test_input_validator.py  # [NEW] Input validation unit tests
│   │
│   ├── integration/
│   │   ├── test_rate_limiting_redis.py    # [NEW] Rate limit Redis integration
│   │   ├── test_audit_logging_db.py       # [NEW] Audit log database integration
│   │   ├── test_session_invalidation.py   # [NEW] Session invalidation flow
│   │   └── test_security_headers.py       # [NEW] Security headers integration
│   │
│   └── e2e/
│       ├── test_rate_limiting.py          # [NEW] US1: Rate limiting E2E
│       ├── test_audit_logging.py          # [NEW] US2: Audit logging E2E
│       ├── test_csrf_protection.py        # [NEW] US3: CSRF protection E2E
│       ├── test_session_invalidation.py   # [NEW] US4: Session invalidation E2E
│       ├── test_2fa_flow.py              # [NEW] US5: 2FA enrollment and login E2E
│       ├── test_security_headers.py       # [NEW] US6: Security headers verification E2E
│       ├── test_input_validation.py       # [NEW] US7: Input validation E2E
│       └── test_password_reset_security.py # [NEW] US8: Secure password reset E2E
│
└── docs/
    └── security/                     # [NEW] Security documentation
        ├── SECURITY_HARDENING_GUIDE.md
        ├── RATE_LIMITING_CONFIG.md
        ├── AUDIT_LOGGING_GUIDE.md
        ├── CSRF_PROTECTION_GUIDE.md
        ├── SESSION_MANAGEMENT_GUIDE.md
        ├── 2FA_SETUP_GUIDE.md
        ├── SECURITY_HEADERS_GUIDE.md
        ├── INPUT_VALIDATION_GUIDE.md
        ├── PASSWORD_RESET_SECURITY.md
        └── SECURITY_INCIDENT_RESPONSE.md
```

**Files Modified**: ~10 existing files (auth.py, people.py, models.py, database.py, config.py, security.py, app-user.js)

**Files Created**: ~40 new files (8 service files, 3 middleware files, 1 frontend security.js, 6 i18n files, 14 test files, 10 documentation files, 6 contract files)

---

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|----------------------------------------|
| NONE | N/A | N/A |

**Constitution Compliance**: 100% - All principles satisfied with security-appropriate implementations

---

**Next Steps**:
1. Phase 0: Generate research.md (security library selections, Redis vs in-memory, TOTP vs SMS, audit log storage decisions)
2. Phase 1: Generate security contracts (rate-limiting.md, audit-logging.md, csrf-protection.md, session-management.md, 2fa-api.md, password-reset.md)
3. Phase 1: Generate quickstart.md (quick security hardening deployment guide)
4. Phase 1: Update agent context (CLAUDE.md security section)
5. Re-validate constitution compliance post-design
6. Phase 2: Run /speckit.tasks for implementation task breakdown
