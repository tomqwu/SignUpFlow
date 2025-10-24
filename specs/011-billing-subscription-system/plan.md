# Implementation Plan: Billing and Subscription System

**Branch**: `011-billing-subscription-system` | **Date**: 2025-10-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/011-billing-subscription-system/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement Stripe-integrated billing and subscription system with four tiers (Free, Starter, Pro, Enterprise) supporting usage limit enforcement, self-service billing portal, trial management, failed payment handling with retry logic, and webhook-based synchronization. System integrates with existing Organization and Person models to enforce volunteer limits based on subscription tier, supports monthly/annual billing cycles with 20% annual discount, and includes admin analytics dashboard for subscription management.

## Technical Context

**Language/Version**: Python 3.11 (existing SignUpFlow backend)
**Primary Dependencies**: FastAPI 0.109+, Stripe Python SDK (latest), SQLAlchemy 2.0+, Pydantic 2.5+, Celery 5.3.4, Redis 5.0.1
**Storage**: SQLite (development), PostgreSQL (production planned)
**Testing**: pytest 8.2+, pytest-playwright 0.7+ for E2E, comprehensive test coverage (≥99%)
**Target Platform**: Linux server (FastAPI/Uvicorn), modern web browsers (Chrome, Firefox, Safari, Edge)
**Project Type**: Web application (existing backend + frontend integration)
**Performance Goals**:
- Webhook processing: <60 seconds from Stripe event to organization status update
- Billing portal page load: <2 seconds
- Invoice PDF generation: <5 seconds
- Subscription upgrade: <3 minutes from click to confirmation
- Volunteer limit enforcement: <1 second response time

**Constraints**:
- Stripe API rate limits: 100 requests/second (per-account)
- Webhook reliability: 99.9% (with retry logic and fallback polling)
- Multi-tenant isolation: Zero cross-organization data leaks
- Security: PCI DSS compliance via Stripe (no card data stored)
- Backward compatibility: Must not break existing Organization/Person models

**Scale/Scope**:
- Expected organizations: 1,000+ at launch, 10,000+ within 12 months
- Concurrent subscriptions: Support 10,000+ active paid subscriptions
- Webhook volume: 100-500 events/day at launch, 5,000+ at scale
- Database: 5 new tables, 45 functional requirements, 12 success criteria
- Code estimate: ~2,000-3,000 LOC (backend), ~1,500 LOC (frontend), ~1,500 LOC (tests)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Compliance Status**: ✅ PASS - All principles satisfied

### Principle 1: User-First Testing (E2E MANDATORY)
✅ **COMPLIANT** - Spec contains 9 comprehensive user stories with independent test scenarios
- US1: Free plan assignment → E2E test: signup → verify Free plan → test limit enforcement
- US2: Paid upgrade → E2E test: click Upgrade → Stripe checkout → verify new limits
- US3: Trial management → E2E test: start trial → verify access → test expiration
- US4: Failed payment handling → E2E test: simulate failure → verify retries → verify notifications
- All tests will verify UI state (billing portal, dashboard, upgrade prompts) not just API responses

### Principle 2: Security-First Development
✅ **COMPLIANT** - Security requirements explicitly defined
- FR-035: Webhook signature verification to prevent unauthorized requests
- FR-006: Stripe integration (PCI DSS compliant, no card data stored locally)
- Multi-tenant isolation: All billing queries filtered by org_id (FR-004, FR-005)
- Admin-only access: Billing portal requires `verify_admin_access()` dependency
- Sensitive data: Stripe API keys in environment variables, never hardcoded

### Principle 3: Multi-tenant Isolation
✅ **COMPLIANT** - Every requirement respects organization boundaries
- FR-004: Subscription model links to Organization (foreign key)
- FR-005: Volunteer counting filtered by org_id
- All database entities (Subscription, BillingHistory, PaymentMethod, UsageMetrics) have org_id foreign key
- Webhook processing verifies organization ownership before status updates
- No shared resources: Each organization has separate Stripe customer ID

### Principle 4: Test Coverage Excellence
✅ **COMPLIANT** - Comprehensive testing strategy defined
- Unit tests: Stripe API integration, webhook signature validation, volunteer limit calculations
- Integration tests: API endpoints (subscription CRUD, upgrade/downgrade, cancellation)
- E2E tests: 9 user stories × 3-5 scenarios each = ~30-40 E2E tests
- Success criteria SC-010, SC-011, SC-012 explicitly test billing workflows
- Target: Maintain ≥99% test pass rate (current project standard)

### Principle 5: Internationalization by Default
✅ **COMPLIANT** - i18n required for all UI text
- Billing portal text: plan names, pricing, upgrade prompts
- Error messages: payment failed, limit exceeded, trial expiration
- Email notifications: confirmation, invoices, payment failures
- Translation keys required in all 6 languages (en, es, pt, zh-CN, zh-TW, fr)
- Stripe supports 25+ languages (will honor user's browser locale)

### Principle 6: Code Quality Standards
✅ **COMPLIANT** - Follows existing patterns
- Backend: FastAPI routers (`api/routers/billing.py`, `api/routers/webhooks.py`)
- Services: Business logic in `api/services/billing_service.py`, `api/services/stripe_service.py`
- Models: SQLAlchemy ORM for 5 new tables (Subscription, BillingHistory, etc.)
- Frontend: Vanilla JS modules (`frontend/js/billing-portal.js`, `frontend/js/subscription-management.js`)
- No TODO comments: All functionality will be fully implemented
- No mocks: Real Stripe integration with test mode API keys

### Principle 7: Clear Documentation
✅ **COMPLIANT** - Documentation requirements defined
- API documentation: FastAPI Swagger UI will auto-generate billing endpoint docs
- Setup guide: Stripe sandbox setup documented in research report
- Integration guide: Webhook configuration, API key setup
- User guide: Billing portal usage, subscription management
- CLAUDE.md update: Add billing system architecture section
- Update docs/SAAS_READINESS_SUMMARY.md: Mark billing as complete

**Constitution Violations**: NONE

**Complexity Justification**: N/A (no violations to justify)

## Project Structure

### Documentation (this feature)

```
specs/011-billing-subscription-system/
├── spec.md              # Feature specification (COMPLETE)
├── plan.md              # This file (IN PROGRESS)
├── research.md          # Phase 0 output (PENDING)
├── data-model.md        # Phase 1 output (PENDING)
├── quickstart.md        # Phase 1 output (PENDING)
├── contracts/           # Phase 1 output (PENDING)
│   ├── billing-api.md
│   ├── webhook-api.md
│   └── stripe-integration.md
├── progress.md          # Feature progress tracking (CREATED)
└── checklists/          # Validation checklists (CREATED)
    └── requirements.md
```

### Source Code (repository root)

**Structure Decision**: Web application (existing SignUpFlow architecture)

```
api/                                  # Backend (FastAPI)
├── models.py                         # [MODIFY] Add 5 billing tables
│   ├── Subscription
│   ├── BillingHistory
│   ├── PaymentMethod
│   ├── UsageMetrics
│   └── SubscriptionEvent
│
├── routers/                          # API endpoints
│   ├── billing.py                    # [NEW] Subscription management
│   ├── webhooks.py                   # [NEW] Stripe webhook handler
│   └── organizations.py              # [MODIFY] Add subscription tier info
│
├── services/                         # Business logic
│   ├── billing_service.py            # [NEW] Subscription operations
│   ├── stripe_service.py             # [NEW] Stripe API integration
│   ├── webhook_service.py            # [NEW] Webhook processing
│   ├── usage_service.py              # [NEW] Usage tracking
│   └── email_service.py              # [MODIFY] Add billing notifications
│
├── schemas/                          # Pydantic models
│   ├── billing.py                    # [NEW] Billing request/response models
│   └── webhooks.py                   # [NEW] Webhook event schemas
│
└── utils/                            # Utilities
    ├── stripe_client.py              # [NEW] Stripe SDK wrapper
    └── invoice_generator.py          # [NEW] PDF invoice generation

frontend/                             # Frontend (Vanilla JS)
├── index.html                        # [MODIFY] Add billing portal route
│
├── js/
│   ├── billing-portal.js             # [NEW] Self-service billing UI
│   ├── subscription-management.js    # [NEW] Upgrade/downgrade flows
│   ├── usage-dashboard.js            # [NEW] Analytics dashboard
│   ├── app-admin.js                  # [MODIFY] Add billing tab
│   └── router.js                     # [MODIFY] Add /billing route
│
└── css/
    └── billing.css                   # [NEW] Billing portal styles

locales/                              # i18n translations
├── en/billing.json                   # [NEW] English billing text
├── es/billing.json                   # [NEW] Spanish billing text
├── pt/billing.json                   # [NEW] Portuguese billing text
├── zh-CN/billing.json                # [NEW] Simplified Chinese
├── zh-TW/billing.json                # [NEW] Traditional Chinese
└── fr/billing.json                   # [NEW] French billing text

tests/
├── unit/
│   ├── test_billing_service.py       # [NEW] Billing logic tests
│   ├── test_stripe_service.py        # [NEW] Stripe integration tests
│   └── test_webhook_service.py       # [NEW] Webhook processing tests
│
├── integration/
│   ├── test_billing_api.py           # [NEW] Billing API tests
│   └── test_webhook_api.py           # [NEW] Webhook endpoint tests
│
└── e2e/
    ├── test_subscription_upgrade.py  # [NEW] US2: Upgrade flow
    ├── test_trial_management.py      # [NEW] US3: Trial workflow
    ├── test_failed_payment.py        # [NEW] US4: Payment retry
    └── test_billing_portal.py        # [NEW] US8: Portal management
```

**Files Modified**: 4 existing files (models.py, organizations.py, email_service.py, index.html, app-admin.js, router.js)

**Files Created**: ~25 new files (routers, services, schemas, frontend modules, tests, i18n files)

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |

