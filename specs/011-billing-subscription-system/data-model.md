# Data Model: Billing and Subscription System

**Feature**: 011-billing-subscription-system
**Date**: 2025-10-22
**Status**: Design Complete

## Overview

The billing system introduces 5 new database tables to support subscription management, payment processing, usage tracking, and audit logging. All tables integrate with existing `Organization` and `Person` models while maintaining multi-tenant isolation.

---

## Entity Relationship Diagram

```
┌─────────────────┐
│  Organization   │◄──────┐
│  (existing)     │       │
└────────┬────────┘       │
         │1               │1
         │                │
         │*               │
┌────────▼────────┐  ┌───┴──────────────┐
│  Subscription   │  │ PaymentMethod    │
│                 │  │                  │
│  • plan_tier    │  │  • stripe_pm_id  │
│  • status       │  │  • card_last4    │
│  • stripe_ids   │  │  • is_primary    │
└────────┬────────┘  └──────────────────┘
         │1
         │
         │*
┌────────▼────────────────────────────────┐
│                                         │
│  ┌────────────────┐  ┌────────────────┐│
│  │BillingHistory  │  │ UsageMetrics   ││
│  │                │  │                ││
│  │ • event_type   │  │ • metric_type  ││
│  │ • amount       │  │ • current_val  ││
│  │ • invoice_url  │  │ • plan_limit   ││
│  └────────────────┘  └────────────────┘│
│                                         │
│  ┌────────────────┐                    │
│  │SubscriptionEvt │                    │
│  │                │                    │
│  │ • event_type   │                    │
│  │ • old_plan     │                    │
│  │ • new_plan     │                    │
│  └────────────────┘                    │
│                                         │
└─────────────────────────────────────────┘
```

**Relationships**:
- `Organization` 1:1 `Subscription` (one active subscription per organization)
- `Organization` 1:* `PaymentMethod` (multiple cards, one primary)
- `Subscription` 1:* `BillingHistory` (historical billing events)
- `Organization` 1:* `UsageMetrics` (one row per metric type)
- `Organization` 1:* `SubscriptionEvent` (audit trail)

---

## Table 1: Subscription

**Purpose**: Tracks organization's current subscription tier, billing cycle, and Stripe subscription details.

**Schema**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | String(PK) | Primary Key | Format: `sub_{12char}` |
| `org_id` | String(FK) | Foreign Key, Unique, Indexed, NOT NULL | Links to `organizations.id` |
| `stripe_customer_id` | String | Unique, Indexed, Nullable | Stripe Customer ID (null for Free plan) |
| `stripe_subscription_id` | String | Unique, Indexed, Nullable | Stripe Subscription ID (null for Free plan) |
| `plan_tier` | String | NOT NULL, Default: `"free"` | Values: `free`, `starter`, `pro`, `enterprise` |
| `billing_cycle` | String | NOT NULL, Default: `"monthly"` | Values: `monthly`, `annual` |
| `status` | String | NOT NULL, Default: `"active"` | Values: `active`, `trialing`, `past_due`, `cancelled`, `incomplete` |
| `trial_end_date` | DateTime(TZ) | Nullable | When trial expires (null if not on trial) |
| `current_period_start` | DateTime(TZ) | NOT NULL | Current billing period start date |
| `current_period_end` | DateTime(TZ) | NOT NULL | Current billing period end date |
| `cancel_at_period_end` | Boolean | Default: `false` | Flag if cancellation scheduled |
| `created_at` | DateTime(TZ) | Server Default: `now()` | Creation timestamp |
| `updated_at` | DateTime(TZ) | Server Default: `now()`, On Update | Last update timestamp |

**Indexes**:
- `PRIMARY KEY`: `id`
- `UNIQUE KEY`: `org_id` (1:1 relationship)
- `INDEX`: `stripe_customer_id` (lookup by Stripe customer)
- `INDEX`: `stripe_subscription_id` (lookup by Stripe subscription)
- `INDEX`: `status` (filter by subscription status)
- `INDEX`: `trial_end_date` (find expiring trials)

**Relationships**:
- `org_id` → `organizations.id` (FK, CASCADE DELETE)
- Back reference: `organization.subscription` (1:1)

**Business Rules**:
- Free plan: `stripe_customer_id` and `stripe_subscription_id` are null
- Paid plan: Both Stripe IDs must be present
- Status transitions: `trialing` → `active` (payment added), `trialing` → `cancelled` (trial expired)
- Trial period: Only for `pro` and `enterprise` plans (14 days)
- Status `past_due`: Payment failed but still in retry grace period

**Example Row**:
```json
{
  "id": "sub_a8f3e2c4d1b9",
  "org_id": "org_church_xyz",
  "stripe_customer_id": "cus_NQz8xY2I4rXVqP",
  "stripe_subscription_id": "sub_1OQz8xJ2eZvKYlo2",
  "plan_tier": "pro",
  "billing_cycle": "annual",
  "status": "active",
  "trial_end_date": null,
  "current_period_start": "2025-01-01T00:00:00Z",
  "current_period_end": "2026-01-01T00:00:00Z",
  "cancel_at_period_end": false,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

---

## Table 2: BillingHistory

**Purpose**: Historical record of all billing events (charges, refunds, subscription changes) for audit and invoice retrieval.

**Schema**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | String(PK) | Primary Key | Format: `bh_{12char}` |
| `org_id` | String(FK) | Foreign Key, Indexed, NOT NULL | Links to `organizations.id` |
| `subscription_id` | String(FK) | Foreign Key, Nullable | Links to `subscriptions.id` |
| `event_type` | String | Indexed, NOT NULL | Values: `charge`, `refund`, `subscription_change`, `trial_start`, `trial_end` |
| `amount_cents` | Integer | NOT NULL | Amount in cents (USD) to avoid float precision issues |
| `currency` | String | Default: `"usd"` | ISO 4217 currency code |
| `payment_status` | String | NOT NULL | Values: `succeeded`, `failed`, `pending` |
| `stripe_invoice_id` | String | Indexed, Nullable | Stripe Invoice ID for reference |
| `invoice_pdf_url` | String | Nullable | URL to download invoice PDF from Stripe |
| `description` | String | Nullable | Human-readable event description |
| `metadata` | JSON | Nullable | Additional context (e.g., `{"old_plan": "starter", "new_plan": "pro"}`) |
| `event_timestamp` | DateTime(TZ) | Server Default: `now()` | When event occurred |

**Indexes**:
- `PRIMARY KEY`: `id`
- `INDEX`: `org_id` (query by organization)
- `COMPOSITE INDEX`: `(org_id, event_timestamp)` (query org billing history by date)
- `INDEX`: `payment_status` (find failed payments)
- `INDEX`: `stripe_invoice_id` (lookup by Stripe invoice)
- `INDEX`: `event_type` (filter by event type)

**Relationships**:
- `org_id` → `organizations.id` (FK, CASCADE DELETE)
- `subscription_id` → `subscriptions.id` (FK, SET NULL) - Nullable for events like refunds after cancellation

**Business Rules**:
- Amounts stored in cents: `$29.00` = `2900` (avoids float rounding errors)
- Event types map to user-facing billing history:
  - `charge`: Successful payment
  - `refund`: Refund issued (partial or full)
  - `subscription_change`: Upgrade/downgrade
  - `trial_start`: Trial period started
  - `trial_end`: Trial period ended
- Failed payments recorded with `payment_status: "failed"` for retry tracking

**Example Row**:
```json
{
  "id": "bh_9f2e1d3c4b5a",
  "org_id": "org_church_xyz",
  "subscription_id": "sub_a8f3e2c4d1b9",
  "event_type": "subscription_change",
  "amount_cents": 5000,
  "currency": "usd",
  "payment_status": "succeeded",
  "stripe_invoice_id": "in_1OQz8xJ2eZvKYlo2",
  "invoice_pdf_url": "https://pay.stripe.com/invoice/acct_1032D82eZvKYlo2/test_YWNjdF8xMDMyRDgyZVp2S1lsbzIsX1BzVXhUckZvZ0RsdVBLaW9CNThRZlB4eUxpaUp6LDkwNTY5ODM1/pdf",
  "description": "Upgraded from Starter ($29/mo) to Pro ($79/mo)",
  "metadata": {
    "old_plan": "starter",
    "new_plan": "pro",
    "prorated_amount_cents": 5000
  },
  "event_timestamp": "2025-01-15T10:30:00Z"
}
```

---

## Table 3: PaymentMethod

**Purpose**: Stores organization's payment method metadata (NOT card details - those stay in Stripe for PCI compliance).

**Schema**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | String(PK) | Primary Key | Format: `pm_{12char}` |
| `org_id` | String(FK) | Foreign Key, Indexed, NOT NULL | Links to `organizations.id` |
| `stripe_payment_method_id` | String | Unique, Indexed, NOT NULL | Stripe PaymentMethod ID |
| `card_brand` | String | Nullable | Values: `visa`, `mastercard`, `amex`, `discover`, `diners`, `jcb`, `unionpay` |
| `card_last4` | String | Nullable | Last 4 digits (display only, safe to store) |
| `exp_month` | Integer | Nullable | Expiration month (1-12) |
| `exp_year` | Integer | Nullable | Expiration year (YYYY) |
| `billing_address` | JSON | Nullable | Address object: `{"line1": "...", "city": "...", "state": "...", "postal_code": "...", "country": "US"}` |
| `is_primary` | Boolean | Default: `true` | Primary payment method flag |
| `is_active` | Boolean | Default: `true` | Active/deleted flag (soft delete) |
| `added_at` | DateTime(TZ) | Server Default: `now()` | When payment method was added |

**Indexes**:
- `PRIMARY KEY`: `id`
- `UNIQUE KEY`: `stripe_payment_method_id` (prevent duplicates)
- `INDEX`: `org_id` (query by organization)

**Relationships**:
- `org_id` → `organizations.id` (FK, CASCADE DELETE)

**Business Rules**:
- **Security**: Full card details (PAN, CVV) NEVER stored locally - only in Stripe
- **Display Info**: Only safe-to-display info stored (brand, last4, expiration)
- **Primary Method**: Only one payment method can have `is_primary = true` per organization
- **Soft Delete**: `is_active = false` instead of hard delete (maintain billing history integrity)
- **Address**: Used for tax calculation and fraud prevention

**Example Row**:
```json
{
  "id": "pm_7e1f2d3c4b5a",
  "org_id": "org_church_xyz",
  "stripe_payment_method_id": "pm_1OQz8xJ2eZvKYlo2CiU7C9Vn",
  "card_brand": "visa",
  "card_last4": "4242",
  "exp_month": 12,
  "exp_year": 2027,
  "billing_address": {
    "line1": "123 Church St",
    "city": "Toronto",
    "state": "ON",
    "postal_code": "M5H 2N2",
    "country": "CA"
  },
  "is_primary": true,
  "is_active": true,
  "added_at": "2025-01-01T00:00:00Z"
}
```

---

## Table 4: UsageMetrics

**Purpose**: Tracks organization's resource consumption for limit enforcement and analytics dashboard. Cached for performance.

**Schema**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | String(PK) | Primary Key | Format: `um_{12char}` |
| `org_id` | String(FK) | Foreign Key, Indexed, NOT NULL | Links to `organizations.id` |
| `metric_type` | String | Indexed, NOT NULL | Values: `volunteers_count`, `events_count`, `storage_mb`, `api_calls` (extensible) |
| `current_value` | Integer | Default: `0`, NOT NULL | Current metric value |
| `plan_limit` | Integer | NOT NULL | Limit for current plan tier |
| `percentage_used` | Float | Default: `0.0`, NOT NULL | Computed: `(current_value / plan_limit) * 100` |
| `last_updated` | DateTime(TZ) | Server Default: `now()`, On Update | Last metric update |

**Indexes**:
- `PRIMARY KEY`: `id`
- `COMPOSITE INDEX`: `(org_id, metric_type)` (query org metrics)
- `UNIQUE CONSTRAINT`: `(org_id, metric_type)` (one row per org per metric)

**Relationships**:
- `org_id` → `organizations.id` (FK, CASCADE DELETE)

**Business Rules**:
- **Cache Strategy**: Updated on volunteer create/delete, not real-time count query
- **Limit Enforcement**: Check `current_value < plan_limit` before allowing action
- **Percentage**: Pre-computed for dashboard display (avoid repeated calculations)
- **Plan Limits**:
  - `volunteers_count`: Free (10), Starter (50), Pro (200), Enterprise (2000)
  - Other metrics: TBD for future features (events, storage, API calls)
- **Alert Threshold**: Dashboard warns when `percentage_used >= 90%`

**Example Row**:
```json
{
  "id": "um_6d1e2f3c4b5a",
  "org_id": "org_church_xyz",
  "metric_type": "volunteers_count",
  "current_value": 35,
  "plan_limit": 50,
  "percentage_used": 70.0,
  "last_updated": "2025-01-22T15:30:00Z"
}
```

**Cache Invalidation**:
```python
# When volunteer added
def create_volunteer(org_id, volunteer_data):
    volunteer = Volunteer.create(org_id=org_id, **volunteer_data)
    # Invalidate cache
    update_usage_metric(org_id, "volunteers_count", increment=1)

# When volunteer deleted
def delete_volunteer(volunteer_id):
    volunteer = Volunteer.get(volunteer_id)
    org_id = volunteer.org_id
    volunteer.delete()
    # Invalidate cache
    update_usage_metric(org_id, "volunteers_count", increment=-1)
```

---

## Table 5: SubscriptionEvent

**Purpose**: Audit log of all subscription lifecycle events for compliance, analytics, and customer support investigation.

**Schema**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | String(PK) | Primary Key | Format: `se_{12char}` |
| `org_id` | String(FK) | Foreign Key, Indexed, NOT NULL | Links to `organizations.id` |
| `event_type` | String | Indexed, NOT NULL | Values: `created`, `upgraded`, `downgraded`, `trial_started`, `cancelled`, `reactivated`, `payment_failed` |
| `previous_plan` | String | Nullable | Plan before change (null for first subscription) |
| `new_plan` | String | NOT NULL | Plan after change |
| `admin_id` | String(FK) | Foreign Key, Nullable | Admin who initiated (null for automatic events) |
| `reason` | String | Nullable | Event reason: `"trial_expired"`, `"payment_failed"`, `"user_requested"`, `"automatic_retry"` |
| `notes` | String | Nullable | Additional context or admin notes |
| `event_timestamp` | DateTime(TZ) | Server Default: `now()` | When event occurred |

**Indexes**:
- `PRIMARY KEY`: `id`
- `INDEX`: `org_id` (query by organization)
- `COMPOSITE INDEX`: `(org_id, event_timestamp)` (chronological audit trail)
- `INDEX`: `event_type` (filter by event type)

**Relationships**:
- `org_id` → `organizations.id` (FK, CASCADE DELETE)
- `admin_id` → `people.id` (FK, SET NULL) - Nullable for system-triggered events

**Business Rules**:
- **User-Initiated**: `admin_id` present, reason: `"user_requested"`
- **System-Initiated**: `admin_id` null, reason: `"trial_expired"`, `"payment_failed"`, `"automatic_retry"`
- **Audit Trail**: Immutable records (INSERT only, never UPDATE/DELETE)
- **Analytics**: Track conversion rates (trial → paid), churn reasons, upgrade paths

**Example Rows**:
```json
// User upgrade
{
  "id": "se_5c1d2e3f4b5a",
  "org_id": "org_church_xyz",
  "event_type": "upgraded",
  "previous_plan": "starter",
  "new_plan": "pro",
  "admin_id": "person_admin_123",
  "reason": "user_requested",
  "notes": "Organization growing, needed more volunteer capacity",
  "event_timestamp": "2025-01-15T10:30:00Z"
}

// System downgrade
{
  "id": "se_4b1c2d3e4f5a",
  "org_id": "org_church_abc",
  "event_type": "downgraded",
  "previous_plan": "pro",
  "new_plan": "free",
  "admin_id": null,
  "reason": "payment_failed",
  "notes": "All payment retries exhausted (3 attempts over 7 days)",
  "event_timestamp": "2025-01-22T08:00:00Z"
}
```

---

## Modified Existing Tables

### Organization (Modification)

**Changes**:
- Add `subscription` relationship (1:1 back reference)
- Add convenience properties for subscription tier and limits

**New Properties**:
```python
class Organization(Base):
    # ... existing fields ...

    # Relationships
    subscription = relationship("Subscription", uselist=False, back_populates="organization")

    @property
    def subscription_tier(self) -> str:
        """Get current subscription tier (free/starter/pro/enterprise)"""
        return self.subscription.plan_tier if self.subscription else "free"

    @property
    def volunteer_limit(self) -> int:
        """Get volunteer limit for current tier"""
        limits = {"free": 10, "starter": 50, "pro": 200, "enterprise": 2000}
        return limits.get(self.subscription_tier, 10)

    @property
    def is_over_limit(self) -> bool:
        """Check if organization has exceeded volunteer limit"""
        current_count = len(self.people)  # or query count
        return current_count >= self.volunteer_limit
```

**No Database Migration**: Properties are computed, no new columns added to `organizations` table

---

## Migration Plan

### Phase 1: Create New Tables
```bash
# Alembic migration: migrations/versions/add_billing_tables.py
alembic revision --autogenerate -m "Add billing and subscription tables"
alembic upgrade head
```

**Tables Created**:
1. `subscriptions` (with 8 indexes)
2. `billing_history` (with 5 indexes)
3. `payment_methods` (with 3 indexes)
4. `usage_metrics` (with 3 indexes)
5. `subscription_events` (with 4 indexes)

### Phase 2: Backfill Data
```python
# scripts/backfill_billing_data.py
from api.models import Organization, Subscription, UsageMetrics

# 1. Create Free subscriptions for all existing organizations
for org in Organization.query.all():
    if not org.subscription:
        Subscription.create(
            org_id=org.id,
            plan_tier="free",
            billing_cycle="monthly",
            status="active",
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=365)  # Never expires for Free
        )

# 2. Initialize usage metrics
for org in Organization.query.all():
    volunteer_count = Person.query.filter_by(org_id=org.id).count()
    UsageMetrics.create(
        org_id=org.id,
        metric_type="volunteers_count",
        current_value=volunteer_count,
        plan_limit=org.volunteer_limit,
        percentage_used=(volunteer_count / org.volunteer_limit) * 100
    )

db.session.commit()
```

### Phase 3: Verify Data Integrity
```sql
-- Check all organizations have subscriptions
SELECT COUNT(*) FROM organizations o
LEFT JOIN subscriptions s ON o.id = s.org_id
WHERE s.id IS NULL;
-- Expected: 0

-- Check usage metrics exist
SELECT COUNT(*) FROM organizations o
LEFT JOIN usage_metrics um ON o.id = um.org_id
WHERE um.id IS NULL;
-- Expected: 0
```

---

## Performance Considerations

### Query Optimization

**Fast Queries** (< 100ms target):
```python
# Get organization with subscription info (1 query with join)
org = db.query(Organization).options(joinedload(Organization.subscription)).filter_by(id=org_id).first()

# Check volunteer limit (cached in usage_metrics)
metric = db.query(UsageMetrics).filter_by(org_id=org_id, metric_type="volunteers_count").first()
can_add = metric.current_value < metric.plan_limit

# Get billing history for org (indexed by org_id + timestamp)
history = db.query(BillingHistory).filter_by(org_id=org_id).order_by(BillingHistory.event_timestamp.desc()).limit(10).all()
```

**Index Usage**:
- `subscriptions.org_id` (UNIQUE): O(1) lookup
- `usage_metrics.(org_id, metric_type)` (COMPOSITE UNIQUE): O(1) lookup
- `billing_history.(org_id, event_timestamp)` (COMPOSITE): Efficient range scans

### Caching Strategy

**Cache Forever** (rarely changes):
- Stripe Price IDs (in-memory constant)
- Plan limits (in-memory constant)

**Cache 5 Minutes** (changes infrequently):
- Organization subscription tier
- Usage metrics (unless volunteer added/deleted)

**No Cache** (must be real-time):
- Stripe webhook events
- Billing history (already fast with indexes)
- Payment method list (sensitive data)

---

## Security & Multi-Tenant Isolation

### Data Isolation Rules

**Every Query Must**:
1. Filter by `org_id` (prevent cross-organization access)
2. Verify current user belongs to organization
3. Validate admin permissions for sensitive operations

**Example - Secure Billing Query**:
```python
@router.get("/billing/history")
def get_billing_history(
    admin: Person = Depends(verify_admin_access),
    db: Session = Depends(get_db)
):
    # 1. Filter by user's organization
    org_id = admin.org_id

    # 2. Query filtered by org_id
    history = db.query(BillingHistory).filter_by(org_id=org_id).all()

    return {"billing_history": history}
```

### Sensitive Data Protection

**PCI DSS Compliance**:
- ✅ Card details stored in Stripe (Level 1 PCI certified)
- ✅ Only display-safe data stored locally (last4, brand, expiration)
- ✅ No full PANs, CVVs, or magnetic stripe data
- ✅ Payment form uses Stripe Elements (no card data touches our servers)

**Stripe API Keys**:
- Test keys for development: `pk_test_...`, `sk_test_...`
- Live keys for production: `pk_live_...`, `sk_live_...` (NEVER commit to git)
- Environment variables: `STRIPE_PUBLISHABLE_KEY`, `STRIPE_SECRET_KEY`
- Webhook secret: `STRIPE_WEBHOOK_SECRET` (verify signature)

---

## Testing Strategy

### Database Tests

**Unit Tests** (`tests/unit/test_billing_models.py`):
- Test model creation, validation, relationships
- Test computed properties (`organization.volunteer_limit`)
- Test business rules (e.g., only one primary payment method)

**Integration Tests** (`tests/integration/test_billing_data.py`):
- Test subscription lifecycle (create → upgrade → cancel → reactivate)
- Test usage metric updates on volunteer add/delete
- Test billing history recording for all event types
- Test multi-tenant isolation (org A cannot access org B data)

**Migration Tests**:
- Test backfill script creates subscriptions for all orgs
- Test usage metrics calculated correctly
- Test no orphaned records after migration

---

## Data Model Summary

**Tables Created**: 5
**Indexes Created**: 23 (8 + 5 + 3 + 3 + 4)
**Foreign Keys**: 7
**Computed Properties**: 3 (on Organization)
**Total Estimated Rows at Scale**: ~50,000 (10,000 orgs × 5 tables avg)

**Compliance**: ✅ All 7 Constitution Principles
- Multi-tenant isolation: All tables filtered by `org_id`
- Security: PCI compliant (card data in Stripe only)
- Performance: Comprehensive indexing for <100ms queries
- Audit trail: Immutable `subscription_events` table

**Ready for Implementation**: ✅ YES - Proceed to API contract generation
