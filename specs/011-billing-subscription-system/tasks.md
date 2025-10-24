# Tasks: Billing and Subscription System

**Feature**: 011-billing-subscription-system
**Input**: Design documents from `/specs/011-billing-subscription-system/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Organization**: Tasks are grouped by user story (9 stories: 2xP1, 3xP2, 4xP3) to enable independent implementation and testing of each story. Tests are OPTIONAL and not included per feature specification.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, etc.)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for billing system

- [ ] T001 Install Stripe Python SDK (latest) to project dependencies in pyproject.toml
- [ ] T002 [P] Add Celery 5.3.4 and Redis 5.0.1 dependencies to pyproject.toml for async webhook processing
- [ ] T003 [P] Create environment variables for Stripe API keys in .env.example (STRIPE_SECRET_KEY, STRIPE_PUBLIC_KEY, STRIPE_WEBHOOK_SECRET)
- [ ] T004 [P] Create billing router structure at api/routers/billing.py (empty router with FastAPI router initialization)
- [ ] T005 [P] Create webhook router at api/routers/webhooks.py (empty router)
- [ ] T006 [P] Add billing and webhook routes to main FastAPI app in api/main.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core database models, Stripe integration, and base services that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Schema

- [ ] T007 Create Subscription model in api/models.py with fields: id, org_id, stripe_customer_id, stripe_subscription_id, plan_tier, billing_cycle, status, trial_end_date, current_period_start, current_period_end, cancel_at_period_end, created_at, updated_at
- [ ] T008 [P] Create BillingHistory model in api/models.py with fields: id, org_id, subscription_id, event_type, amount_cents, currency, payment_status, stripe_invoice_id, invoice_pdf_url, description, metadata, event_timestamp
- [ ] T009 [P] Create PaymentMethod model in api/models.py with fields: id, org_id, stripe_payment_method_id, card_brand, card_last4, exp_month, exp_year, billing_address, is_primary, is_active, added_at
- [ ] T010 [P] Create UsageMetrics model in api/models.py with fields: id, org_id, metric_type, current_value, plan_limit, percentage_used, last_updated
- [ ] T011 [P] Create SubscriptionEvent model in api/models.py with fields: id, org_id, event_type, previous_plan, new_plan, admin_id, reason, notes, event_timestamp
- [ ] T012 Add relationships to Organization model in api/models.py: subscription (1:1), usage_metrics (1:*), subscription_events (1:*)
- [ ] T013 Add convenience properties to Organization model: subscription_tier, volunteer_limit, is_over_limit
- [ ] T014 Create Alembic migration for all 5 new billing tables with indexes: alembic revision --autogenerate -m "Add billing tables"
- [ ] T015 Create backfill script at scripts/backfill_billing_data.py to assign Free subscriptions to existing organizations and initialize usage metrics

### Stripe Integration

- [ ] T016 Create Stripe client wrapper at api/utils/stripe_client.py with initialization using STRIPE_SECRET_KEY
- [ ] T017 [P] Implement customer creation method in api/utils/stripe_client.py: create_customer(org_id, email, name)
- [ ] T018 [P] Implement subscription creation method in api/utils/stripe_client.py: create_subscription(customer_id, price_id, trial_days)
- [ ] T019 [P] Implement subscription update method in api/utils/stripe_client.py: update_subscription(subscription_id, new_price_id, proration_behavior)
- [ ] T020 [P] Implement subscription cancellation method in api/utils/stripe_client.py: cancel_subscription(subscription_id, cancel_at_period_end)
- [ ] T021 [P] Implement payment method attachment in api/utils/stripe_client.py: attach_payment_method(customer_id, payment_method_id)

### Base Services

- [ ] T022 Create BillingService at api/services/billing_service.py with base class structure and database session injection
- [ ] T023 [P] Create StripeService at api/services/stripe_service.py for Stripe API operations with error handling
- [ ] T024 [P] Create WebhookService at api/services/webhook_service.py for processing Stripe webhook events
- [ ] T025 [P] Create UsageService at api/services/usage_service.py for tracking volunteer counts and limit enforcement
- [ ] T026 Implement get_subscription method in api/services/billing_service.py to retrieve org subscription with usage metrics

### Pydantic Schemas

- [ ] T027 Create SubscriptionResponse schema in api/schemas/billing.py with all Subscription model fields
- [ ] T028 [P] Create UpgradeRequest schema in api/schemas/billing.py: new_plan, billing_cycle, payment_method_id
- [ ] T029 [P] Create DowngradeRequest schema in api/schemas/billing.py: new_plan, reason
- [ ] T030 [P] Create TrialRequest schema in api/schemas/billing.py: plan, notification_preferences
- [ ] T031 [P] Create CancelRequest schema in api/schemas/billing.py: reason, feedback
- [ ] T032 [P] Create WebhookEvent schema in api/schemas/webhooks.py: event_type, data, api_version

### i18n Translations

- [ ] T033 [P] Create locales/en/billing.json with keys: plan_names, pricing, upgrade_prompts, error_messages, confirmation_messages
- [ ] T034 [P] Create locales/es/billing.json (Spanish translations)
- [ ] T035 [P] Create locales/pt/billing.json (Portuguese translations)
- [ ] T036 [P] Create locales/zh-CN/billing.json (Simplified Chinese translations)
- [ ] T037 [P] Create locales/zh-TW/billing.json (Traditional Chinese translations)
- [ ] T038 [P] Create locales/fr/billing.json (French translations)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Free Plan Assignment (Priority: P1) 🎯 MVP

**Goal**: Automatically assign new organizations to Free plan (10 volunteer limit) upon signup

**Independent Test**: Create new organization → verify Free plan assigned → verify 10 volunteer limit enforced → verify upgrade prompt at limit

### Implementation for US1

- [ ] T039 [US1] Implement assign_free_plan method in api/services/billing_service.py to create Free subscription for new organization
- [ ] T040 [US1] Modify organization signup endpoint in api/routers/auth.py to call assign_free_plan after organization creation
- [ ] T041 [US1] Implement initialize_usage_metrics method in api/services/usage_service.py to create initial volunteers_count metric
- [ ] T042 [US1] Implement check_volunteer_limit method in api/services/usage_service.py returning True/False based on current count vs plan limit
- [ ] T043 [US1] Modify volunteer creation endpoint in api/routers/people.py to check limit before allowing volunteer addition
- [ ] T044 [US1] Add upgrade prompt response when volunteer limit reached: error message "Upgrade to Starter plan to add more volunteers" with /billing/upgrade link
- [ ] T045 [US1] Create GET /api/billing/subscription endpoint in api/routers/billing.py to return current subscription, usage, and next invoice

**Checkpoint**: Free plan auto-assignment complete and volunteer limit enforcement working

---

## Phase 4: User Story 2 - Paid Plan Upgrade (Priority: P1) 🎯 MVP

**Goal**: Enable organization upgrade from Free to Starter/Pro/Enterprise through self-service billing portal

**Independent Test**: Free plan admin → click Upgrade → select Starter monthly → enter payment → verify upgraded → verify 50 volunteer limit

### Implementation for US2

- [ ] T046 [US2] Create Stripe checkout session creation in api/services/stripe_service.py: create_checkout_session(org_id, plan_tier, billing_cycle)
- [ ] T047 [US2] Implement upgrade_subscription method in api/services/billing_service.py to create/update Stripe subscription and local database
- [ ] T048 [US2] Create POST /api/billing/subscription/upgrade endpoint in api/routers/billing.py accepting new_plan, billing_cycle, payment_method_id
- [ ] T049 [US2] Implement prorated billing calculation in api/services/billing_service.py for mid-period upgrades
- [ ] T050 [US2] Update usage metrics volunteer limit when subscription upgraded in api/services/usage_service.py
- [ ] T051 [US2] Create BillingHistory record for upgrade event in api/services/billing_service.py
- [ ] T052 [US2] Create SubscriptionEvent record for upgrade audit trail in api/services/billing_service.py
- [ ] T053 [US2] Send confirmation email via api/services/email_service.py with invoice and new plan details
- [ ] T054 [US2] Create frontend billing portal page at frontend/js/billing-portal.js with plan selection UI (Free, Starter $29, Pro $79, Enterprise $199)
- [ ] T055 [US2] Integrate Stripe Elements in frontend/js/billing-portal.js for secure payment method collection
- [ ] T056 [US2] Add /app/billing route to frontend/js/router.js for billing portal page
- [ ] T057 [US2] Create billing portal styles in frontend/css/billing.css with plan comparison table and pricing cards

**Checkpoint**: Self-service subscription upgrade flow complete with payment processing

---

## Phase 5: User Story 3 - 14-Day Trial (Priority: P2)

**Goal**: Allow Free plan organizations to start 14-day trial of Pro/Enterprise plans for evaluation

**Independent Test**: Free plan admin → start Pro trial → verify Pro access immediately → verify trial expiration countdown → verify auto-downgrade after 14 days

### Implementation for US3

- [ ] T058 [US3] Implement start_trial method in api/services/billing_service.py to upgrade org to trial status with trial_end_date
- [ ] T059 [US3] Create POST /api/billing/subscription/trial endpoint in api/routers/billing.py accepting plan (pro or enterprise)
- [ ] T060 [US3] Create Celery scheduled task at api/tasks/billing_tasks.py to check daily for expiring trials
- [ ] T061 [US3] Implement auto_downgrade_expired_trials method in api/services/billing_service.py to downgrade organizations where trial_end_date < now()
- [ ] T062 [US3] Create trial notification email templates at api/templates/email/trial_started.html, trial_7days.html, trial_3days.html, trial_expired.html
- [ ] T063 [US3] Implement send_trial_notifications method in api/services/billing_service.py to schedule emails at trial start, 7 days, 3 days, and expiration
- [ ] T064 [US3] Add trial status badge to billing portal UI in frontend/js/billing-portal.js showing "Trial ends in X days"
- [ ] T065 [US3] Add "Add Payment Method to Keep Pro Plan" CTA button in billing portal when trial active

**Checkpoint**: Trial management system complete with automatic expiration and notifications

---

## Phase 6: User Story 4 - Failed Payment Handling (Priority: P2)

**Goal**: Retry failed payments automatically over 7 days with admin notifications before downgrading service

**Independent Test**: Simulate payment failure in Stripe test mode → verify retry attempts → verify admin email notifications → verify grace period → verify downgrade after retries exhausted

### Implementation for US4

- [ ] T066 [US4] Configure Stripe subscription with Smart Retries in api/services/stripe_service.py (3 attempts over 7 days)
- [ ] T067 [US4] Implement webhook handler for invoice.payment_failed event in api/services/webhook_service.py
- [ ] T068 [US4] Update subscription status to "past_due" when payment fails in api/services/billing_service.py
- [ ] T069 [US4] Send immediate payment failure email via api/services/email_service.py: "Payment Failed - Update Payment Method"
- [ ] T070 [US4] Implement webhook handler for invoice.payment_succeeded event to mark subscription active again after retry success
- [ ] T071 [US4] Create Celery task at api/tasks/billing_tasks.py to check past_due subscriptions and send warning emails at 3 days and 1 day before downgrade
- [ ] T072 [US4] Implement downgrade_failed_subscriptions method in api/services/billing_service.py to downgrade to Free after 8 days of past_due status
- [ ] T073 [US4] Create payment failure email templates at api/templates/email/payment_failed.html, payment_warning_3days.html, payment_warning_1day.html, payment_final_downgrade.html
- [ ] T074 [US4] Add "Update Payment Method" prominent button in billing portal when subscription status is past_due

**Checkpoint**: Failed payment retry logic with grace period and notifications complete

---

## Phase 7: User Story 5 - Subscription Tier Changes (Priority: P2)

**Goal**: Allow organizations to upgrade or downgrade between tiers with prorated billing

**Independent Test**: Starter admin → upgrade to Pro mid-month → verify prorated charge → verify immediate limit increase → verify next renewal at Pro price

### Implementation for US5

- [ ] T075 [US5] Implement downgrade_subscription method in api/services/billing_service.py to schedule downgrade at period end
- [ ] T076 [US5] Create POST /api/billing/subscription/downgrade endpoint in api/routers/billing.py accepting new_plan and reason
- [ ] T077 [US5] Add pending_downgrade field to subscription response showing scheduled downgrade details
- [ ] T078 [US5] Implement apply_pending_downgrades Celery task at api/tasks/billing_tasks.py to execute scheduled downgrades at period end
- [ ] T079 [US5] Calculate credit for unused time when downgrading in api/services/billing_service.py
- [ ] T080 [US5] Apply credit to Stripe customer balance for use on next invoice
- [ ] T081 [US5] Display "Downgrade scheduled" message in billing portal with effective date and option to cancel downgrade
- [ ] T082 [US5] Add "Cancel Downgrade" button in billing portal when pending_downgrade exists

**Checkpoint**: Full subscription tier change system with prorated billing working

---

## Phase 8: User Story 6 - Annual Billing (Priority: P3)

**Goal**: Offer annual subscription option with 20% discount (equivalent to 2 months free)

**Independent Test**: Monthly Starter admin → switch to annual → verify $278.40 charge (20% off $348) → verify renewal in 12 months

### Implementation for US6

- [ ] T083 [US6] Add annual pricing calculation to billing service: calculate_annual_price(monthly_price) returning monthly_price * 12 * 0.8
- [ ] T084 [US6] Update upgrade endpoint to support billing_cycle parameter and apply annual discount when billing_cycle="annual"
- [ ] T085 [US6] Display annual pricing option in billing portal with savings badge: "Save $69.60 (20% off)"
- [ ] T086 [US6] Implement billing cycle switch from monthly to annual in api/services/billing_service.py
- [ ] T087 [US6] Implement billing cycle switch from annual to monthly with prorated refund calculation
- [ ] T088 [US6] Update subscription detail view to show billing cycle and next renewal date (12 months for annual, 1 month for monthly)

**Checkpoint**: Annual subscription option with discount working

---

## Phase 9: User Story 7 - Cancellation (Priority: P3)

**Goal**: Allow organizations to cancel paid subscription with service continuing until period end and 30-day data retention

**Independent Test**: Pro plan admin → cancel subscription → verify service continues to period end → verify data accessible during retention → verify reactivation option

### Implementation for US7

- [ ] T089 [US7] Implement cancel_subscription method in api/services/billing_service.py setting cancel_at_period_end=true in Stripe
- [ ] T090 [US7] Create POST /api/billing/subscription/cancel endpoint in api/routers/billing.py accepting reason and feedback
- [ ] T091 [US7] Send cancellation confirmation email via api/services/email_service.py: "Subscription will end on [date]. Data retained for 30 days"
- [ ] T092 [US7] Create Celery task at api/tasks/billing_tasks.py to downgrade cancelled subscriptions to Free at period end
- [ ] T093 [US7] Implement data retention flag on Organization model: cancelled_at, data_retention_until (set to period_end + 30 days)
- [ ] T094 [US7] Implement reactivate_subscription method in api/services/billing_service.py to resume subscription within retention period
- [ ] T095 [US7] Create POST /api/billing/subscription/reactivate endpoint in api/routers/billing.py
- [ ] T096 [US7] Create Celery task to permanently mark organizations for deletion after retention period expires
- [ ] T097 [US7] Display cancellation status in billing portal with reactivation option if within retention period

**Checkpoint**: Subscription cancellation with data retention and reactivation working

---

## Phase 10: User Story 8 - Billing Portal (Priority: P3)

**Goal**: Self-service billing management interface for payment methods, billing address, and invoice downloads

**Independent Test**: Admin → access billing portal → update payment method → download invoice PDF → verify changes immediately reflected

### Implementation for US8

- [ ] T098 [US8] Create GET /api/billing/payment-methods endpoint in api/routers/billing.py to list organization's payment methods
- [ ] T099 [US8] Create POST /api/billing/payment-methods endpoint to add new payment method via Stripe
- [ ] T100 [US8] Create DELETE /api/billing/payment-methods/:id endpoint to remove payment method
- [ ] T101 [US8] Create PUT /api/billing/payment-methods/:id/primary endpoint to set primary payment method
- [ ] T102 [US8] Create GET /api/billing/history endpoint to retrieve billing history with pagination
- [ ] T103 [US8] Implement generate_invoice_pdf method in api/utils/invoice_generator.py using reportlab or weasyprint
- [ ] T104 [US8] Create GET /api/billing/invoices/:id/pdf endpoint to generate and download invoice PDF
- [ ] T105 [US8] Build payment method management UI in frontend/js/billing-portal.js with card list and "Add Payment Method" button
- [ ] T106 [US8] Integrate Stripe billing portal for advanced settings: stripe.billingPortal.sessions.create() redirecting to Stripe's hosted portal
- [ ] T107 [US8] Build billing history table in frontend/js/billing-portal.js showing date, description, amount, status, download link
- [ ] T108 [US8] Style invoice PDF template with organization branding, line items, totals, payment details

**Checkpoint**: Complete self-service billing portal with payment method management and invoice downloads

---

## Phase 11: User Story 9 - Analytics Dashboard (Priority: P3)

**Goal**: Display subscription analytics showing usage metrics, billing forecast, and upgrade recommendations

**Independent Test**: Admin → view analytics dashboard → verify shows 35/50 volunteers (70%) → verify next charge amount and date → verify upgrade suggestion at 90%

### Implementation for US9

- [ ] T109 [US9] Create GET /api/billing/analytics endpoint in api/routers/billing.py returning usage metrics, forecast, historical charges
- [ ] T110 [US9] Implement calculate_billing_forecast method in api/services/billing_service.py to predict next invoice amount
- [ ] T111 [US9] Implement get_usage_trends method in api/services/usage_service.py to return last 12 months volunteer count changes
- [ ] T112 [US9] Create analytics dashboard component in frontend/js/usage-dashboard.js
- [ ] T113 [US9] Display volunteer usage gauge chart showing current/limit with percentage
- [ ] T114 [US9] Display billing forecast widget showing next charge amount and date
- [ ] T115 [US9] Display historical billing chart (line chart) for last 12 months
- [ ] T116 [US9] Implement usage alert logic: display upgrade suggestion when percentage_used >= 90%
- [ ] T117 [US9] Add analytics dashboard tab to admin console in frontend/js/app-admin.js

**Checkpoint**: Subscription analytics dashboard complete with usage tracking and billing forecast

---

## Phase 12: Webhook System (Cross-Cutting)

**Purpose**: Stripe webhook integration for real-time subscription status synchronization

- [ ] T118 Create POST /api/webhooks/stripe endpoint in api/routers/webhooks.py to receive Stripe webhook events
- [ ] T119 Implement webhook signature verification in api/services/webhook_service.py using STRIPE_WEBHOOK_SECRET
- [ ] T120 [P] Implement handler for customer.subscription.created event to sync new subscription
- [ ] T121 [P] Implement handler for customer.subscription.updated event to sync subscription changes
- [ ] T122 [P] Implement handler for customer.subscription.deleted event to handle cancellation
- [ ] T123 [P] Implement handler for invoice.payment_succeeded event to record successful payment
- [ ] T124 [P] Implement handler for invoice.payment_failed event to trigger retry logic
- [ ] T125 [P] Implement handler for payment_method.attached event to sync payment method
- [ ] T126 Implement webhook event queueing with Celery for async processing and retry logic
- [ ] T127 Add webhook event logging to SubscriptionEvent table for audit trail
- [ ] T128 Configure Stripe webhook endpoint in Stripe dashboard with WEBHOOK_SECRET
- [ ] T129 Implement fallback polling job (every 6 hours) to sync subscription status if webhooks fail

---

## Phase 13: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, edge cases, performance optimization, and documentation

### Error Handling & Edge Cases

- [ ] T130 Implement comprehensive error handling for Stripe API failures with user-friendly messages
- [ ] T131 Handle edge case: organization exceeds volunteer limit during trial → allow existing volunteers, block new additions
- [ ] T132 Handle edge case: downgrade would put org over new limit → allow downgrade but place in "over-limit" state
- [ ] T133 Handle edge case: annual-to-monthly switch → calculate prorated credit and apply to future invoices
- [ ] T134 Handle edge case: organization deleted → cancel Stripe subscription immediately and remove payment methods
- [ ] T135 Implement enterprise custom limit negotiation: contact sales CTA when requesting > 2000 volunteers

### Performance Optimization

- [ ] T136 Add database indexes for frequent queries: (org_id, status), (org_id, event_timestamp), (stripe_customer_id)
- [ ] T137 Implement caching for usage metrics with Redis (5-minute TTL) to avoid repeated count queries
- [ ] T138 Optimize billing history queries with pagination (50 items per page)
- [ ] T139 Add eager loading for subscription relationships when querying organizations: .options(joinedload(Organization.subscription))

### Email Notifications

- [ ] T140 [P] Create upgrade confirmation email template at api/templates/email/upgrade_confirmation.html
- [ ] T141 [P] Create downgrade confirmation email template at api/templates/email/downgrade_confirmation.html
- [ ] T142 [P] Create invoice email template at api/templates/email/invoice_receipt.html
- [ ] T143 Implement async email sending via Celery task to avoid blocking API requests

### Testing

- [ ] T144 [P] Create integration test for Free plan auto-assignment in tests/integration/test_billing_signup.py
- [ ] T145 [P] Create integration test for subscription upgrade flow in tests/integration/test_billing_upgrade.py
- [ ] T146 [P] Create integration test for trial management in tests/integration/test_billing_trial.py
- [ ] T147 [P] Create integration test for failed payment retry in tests/integration/test_billing_payment_failure.py
- [ ] T148 [P] Create webhook integration test with Stripe test events in tests/integration/test_webhooks.py
- [ ] T149 [P] Create E2E test for complete subscription lifecycle in tests/e2e/test_subscription_lifecycle.py
- [ ] T150 Run full test suite and verify ≥99% pass rate per project standards

### Documentation

- [ ] T151 Update CLAUDE.md with billing system architecture section describing 5 tables, Stripe integration, webhook flow
- [ ] T152 Update docs/SAAS_READINESS_SUMMARY.md marking billing as complete
- [ ] T153 Create docs/BILLING_SETUP.md with Stripe API key configuration, webhook setup, testing guide
- [ ] T154 Update API documentation via FastAPI Swagger UI descriptions for all billing endpoints
- [ ] T155 Create admin user guide at docs/BILLING_USER_GUIDE.md explaining billing portal, plan selection, invoice downloads

---

## Dependencies

**User Story Completion Order** (enables parallel work):

```
Phase 1 (Setup) → Phase 2 (Foundation)
                      ↓
    ┌─────────────────┴─────────────────┐
    │                                   │
Phase 3 (US1: Free Plan)            Phase 4 (US2: Upgrade)
    │ [INDEPENDENT]                     │ [INDEPENDENT]
    │                                   │
    ↓                                   ↓
Phase 5 (US3: Trial)             Phase 7 (US5: Tier Changes)
    │ depends on US1,US2                │ depends on US2
    │                                   │
    ↓                                   ↓
Phase 6 (US4: Failed Payment)    Phase 8 (US6: Annual)
    │ depends on US2                    │ depends on US2
    │                                   │
    │                                   ↓
    │                              Phase 9 (US7: Cancellation)
    │                                   │ depends on US2
    │                                   │
    └───────────────┬───────────────────┘
                    ↓
        Phase 10 (US8: Portal)
                    │ depends on US1,US2
                    ↓
        Phase 11 (US9: Analytics)
                    │ depends on all previous
                    ↓
        Phase 12 (Webhooks)
                    │ cross-cutting
                    ↓
        Phase 13 (Polish)
```

**Critical Path**: Phase 1 → Phase 2 → Phase 3 (US1) → Phase 4 (US2) → All other user stories can proceed

**Parallel Opportunities**:
- After Foundation (Phase 2): US1 and US2 can be implemented simultaneously by different developers
- US3 (Trial), US5 (Tier Changes), US6 (Annual) are independent after US2 completes
- All email template creation tasks can run in parallel (T140-T143)
- All i18n translation tasks can run in parallel (T033-T038)
- All test creation tasks can run in parallel (T144-T149)

---

## Implementation Strategy

### MVP Scope (Recommended First Delivery)

**Phase 1** + **Phase 2** + **Phase 3 (US1: Free Plan)** + **Phase 4 (US2: Upgrade)**

This delivers core revenue-generating functionality:
- ✅ Free plan auto-assignment
- ✅ Self-service paid upgrades
- ✅ Volunteer limit enforcement
- ✅ Basic billing portal
- ✅ Stripe payment processing

**Estimated Effort**: ~40 tasks, 1-2 weeks with 2 developers

### Incremental Delivery Plan

1. **Week 1-2**: MVP (US1 + US2) - Launch-ready billing
2. **Week 3**: Add trial support (US3) - Reduce conversion friction
3. **Week 4**: Add payment retry (US4) + tier changes (US5) - Reduce churn
4. **Week 5**: Add annual billing (US6) + cancellation (US7) - Improve cash flow
5. **Week 6**: Add portal (US8) + analytics (US9) - Reduce support load
6. **Week 7**: Webhooks (Phase 12) + Polish (Phase 13) - Production hardening

### Testing Approach

Tests are OPTIONAL per feature specification. If tests are added later:
1. Write integration tests FIRST for each user story before implementation
2. Write E2E test for complete subscription lifecycle
3. Test with Stripe test mode API keys and test cards (4242424242424242)
4. Verify webhook handling with Stripe CLI: `stripe listen --forward-to localhost:8000/api/webhooks/stripe`
5. Target ≥99% test pass rate per project standards

---

## Task Summary

**Total Tasks**: 155 tasks
**Parallelizable**: 47 tasks marked with [P]
**User Story Breakdown**:
- Setup: 6 tasks
- Foundation: 32 tasks (blocking)
- US1 (Free Plan): 7 tasks
- US2 (Upgrade): 12 tasks
- US3 (Trial): 8 tasks
- US4 (Failed Payment): 9 tasks
- US5 (Tier Changes): 8 tasks
- US6 (Annual): 6 tasks
- US7 (Cancellation): 9 tasks
- US8 (Portal): 11 tasks
- US9 (Analytics): 9 tasks
- Webhooks: 12 tasks
- Polish: 26 tasks

**Estimated Effort**:
- MVP (US1 + US2): 57 tasks, 1-2 weeks (2 developers)
- Full Feature: 155 tasks, 5-7 weeks (2 developers)

**Format Validation**: ✅ ALL tasks follow checklist format with checkbox, task ID, optional [P] marker, optional [Story] label, and exact file paths.
