# Research: Billing and Subscription System

**Feature**: 011-billing-subscription-system
**Date**: 2025-10-22
**Status**: Research Complete

## Research Questions

This document consolidates technical research needed to resolve "NEEDS CLARIFICATION" items from the Technical Context and specification requirements.

---

## Q1: Payment Provider Selection (Canada/US Market)

**Question**: Which payment processing provider best supports Canada and US markets for SaaS subscription billing?

**Research Conducted**: Comprehensive evaluation of 5 major providers (Stripe, Paddle, Chargebee, Square, PayPal) across 8 criteria. Full report: `/home/ubuntu/SignUpFlow/claudedocs/research_payment_systems_2025-10-22.md`

**Finding**: **Stripe** (Confidence: 9/10)

**Rationale**:
- **Best Cost**: 3.4-3.7% effective rate vs 5.5% (Paddle) or $599/mo minimum (Chargebee)
- **Tax Compliance**: Stripe Tax automatically handles GST/PST/HST (Canada) and state sales tax (US)
- **Developer Experience**: Best-in-class API, comprehensive documentation, fast integration (3-5 days)
- **SaaS-Native**: Purpose-built for subscription businesses with Smart Retries, Customer Portal, usage-based billing
- **Industry Leadership**: Forrester Wave Leader Q1 2025, Gartner Magic Quadrant Leader 2025
- **Cost Savings**: $10,968/year at $45K MRR vs Paddle (54% less expensive)

**Decision**: Use Stripe for payment processing and subscription management

**Implementation Details**:
- Stripe Python SDK: `pip install stripe` (official SDK, fully typed)
- Test API keys configured in `.env`: `STRIPE_PUBLISHABLE_KEY`, `STRIPE_SECRET_KEY`
- Webhook endpoint required: `POST /api/webhooks/stripe` with signature verification
- Customer Portal URL generation for self-service billing

---

## Q2: Stripe API Integration Architecture

**Question**: How should we structure Stripe API integration for maintainability, testability, and error handling?

**Research Conducted**: Reviewed Stripe official documentation, best practices, and Python SDK patterns

**Finding**: **Service Layer Pattern with SDK Wrapper**

**Architecture**:

```python
# api/utils/stripe_client.py - Singleton wrapper
class StripeClient:
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.api_version = "2024-11-20.acacia"  # Pin API version

    def create_customer(self, email, name, org_id):
        # Thin wrapper around Stripe SDK
        return stripe.Customer.create(
            email=email,
            name=name,
            metadata={"org_id": org_id}  # Critical for multi-tenant isolation
        )

    def create_subscription(self, customer_id, price_id, trial_days=None):
        # Idempotency key for safety
        return stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}],
            trial_period_days=trial_days,
            idempotency_key=f"sub_{customer_id}_{int(time.time())}"
        )

# api/services/stripe_service.py - Business logic
class StripeService:
    def __init__(self, stripe_client: StripeClient, db: Session):
        self.stripe = stripe_client
        self.db = db

    def upgrade_subscription(self, org_id, new_plan):
        org = self.db.query(Organization).filter_by(id=org_id).first()
        subscription = self.stripe.update_subscription(
            org.stripe_subscription_id,
            items=[{"price": PLAN_PRICE_IDS[new_plan]}],
            proration_behavior="always_invoice"
        )
        # Update local database
        self.update_subscription_record(org, subscription)
```

**Benefits**:
- **Testability**: Mock `StripeClient` in tests, keep business logic separate
- **Error Handling**: Centralized retry logic, rate limit handling
- **Multi-tenant Safety**: All Stripe customers tagged with `org_id` in metadata
- **Idempotency**: Prevent duplicate charges with idempotency keys
- **API Versioning**: Pin Stripe API version to prevent breaking changes

**Implementation Notes**:
- Use Stripe test mode clock for time-travel testing (trial expiration, renewals)
- Implement exponential backoff for rate limits (100 req/s limit)
- Log all Stripe API calls with request IDs for debugging

---

## Q3: Webhook Processing Strategy

**Question**: How to reliably process Stripe webhooks with retry logic and fallback mechanisms?

**Research Conducted**: Stripe webhook best practices, idempotency patterns, event handling

**Finding**: **Queue-Based Processing with Fallback Polling**

**Architecture**:

```python
# api/routers/webhooks.py
@router.post("/stripe")
async def stripe_webhook(request: Request):
    # 1. Verify signature (CRITICAL - prevents spoofing)
    sig_header = request.headers.get("stripe-signature")
    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # 2. Queue event for async processing (Celery task)
    process_webhook_event.delay(event.id, event.type, event.data)

    # 3. Return 200 immediately (Stripe expects fast response)
    return {"status": "received"}

# api/tasks/webhook_tasks.py (Celery)
@celery_app.task(bind=True, max_retries=5)
def process_webhook_event(self, event_id, event_type, event_data):
    try:
        # Idempotency check
        if WebhookEvent.query.filter_by(stripe_event_id=event_id).first():
            return {"status": "already_processed"}

        # Process event
        if event_type == "customer.subscription.updated":
            handle_subscription_updated(event_data)
        elif event_type == "invoice.payment_failed":
            handle_payment_failed(event_data)
        # ... other event types

        # Log event
        WebhookEvent.create(stripe_event_id=event_id, processed=True)

    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)

# Fallback: Poll Stripe API every 6 hours
@celery_app.task
def sync_stripe_subscriptions():
    """Fallback mechanism if webhooks fail"""
    for org in Organization.query.filter(Organization.stripe_customer_id.isnot(None)):
        stripe_sub = stripe.Subscription.retrieve(org.stripe_subscription_id)
        if stripe_sub.status != org.subscription_status:
            update_subscription_from_stripe(org, stripe_sub)
```

**Webhook Events to Handle**:
- `customer.subscription.created` - New subscription
- `customer.subscription.updated` - Plan change, status change
- `customer.subscription.deleted` - Cancellation
- `invoice.payment_succeeded` - Successful payment
- `invoice.payment_failed` - Payment failure (trigger retry logic)
- `customer.subscription.trial_will_end` - 3 days before trial ends

**Reliability Strategy**:
1. **Signature Verification**: Prevent unauthorized webhook calls
2. **Idempotency**: Track processed events to prevent duplicates
3. **Async Processing**: Queue events via Celery for background processing
4. **Retry Logic**: Exponential backoff (5 retries: 2s, 4s, 8s, 16s, 32s)
5. **Fallback Polling**: Sync every 6 hours if webhooks fail
6. **Monitoring**: Alert if webhook delay >5 minutes

**Testing**:
- Use Stripe CLI to trigger test webhooks: `stripe trigger customer.subscription.updated`
- Simulate webhook failures to verify retry logic
- Test idempotency by replaying same event multiple times

---

## Q4: Usage Limit Enforcement Implementation

**Question**: How to efficiently enforce volunteer limits based on subscription tier across the application?

**Research Conducted**: Analyzed existing Organization/Person models, performance requirements (SC-003: 100% enforcement, <1s response)

**Finding**: **Middleware + Service Layer Enforcement**

**Architecture**:

```python
# api/services/usage_service.py
class UsageService:
    PLAN_LIMITS = {
        "free": {"volunteers": 10},
        "starter": {"volunteers": 50},
        "pro": {"volunteers": 200},
        "enterprise": {"volunteers": 2000}  # Soft limit
    }

    def check_volunteer_limit(self, org_id: str) -> dict:
        org = db.query(Organization).filter_by(id=org_id).first()
        current_count = db.query(Person).filter_by(org_id=org_id).count()

        limit = self.PLAN_LIMITS[org.subscription_tier]["volunteers"]

        return {
            "current": current_count,
            "limit": limit,
            "can_add": current_count < limit,
            "percentage": (current_count / limit) * 100
        }

    def enforce_volunteer_limit(self, org_id: str):
        """Raises HTTPException if at limit"""
        check = self.check_volunteer_limit(org_id)
        if not check["can_add"]:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "volunteer_limit_reached",
                    "message": i18n.t("billing.errors.limit_reached",
                                     limit=check["limit"],
                                     tier=org.subscription_tier),
                    "upgrade_url": f"/billing/upgrade?from={org.subscription_tier}"
                }
            )

# api/routers/people.py
@router.post("/people")
def create_person(
    request: PersonCreate,
    org_id: str = Query(...),
    admin: Person = Depends(verify_admin_access),
    usage_service: UsageService = Depends(get_usage_service)
):
    # Enforce limit BEFORE creating person
    usage_service.enforce_volunteer_limit(org_id)

    # Create person if limit check passes
    person = Person(**request.dict(), org_id=org_id)
    db.add(person)
    db.commit()
    return person
```

**Frontend Integration**:

```javascript
// frontend/js/app-admin.js - Add person workflow
async function addVolunteer(volunteerData) {
    try {
        const response = await authFetch('/api/people?org_id=' + currentOrg.id, {
            method: 'POST',
            body: JSON.stringify(volunteerData)
        });

        if (!response.ok) {
            const error = await response.json();

            // Handle limit error
            if (error.error === 'volunteer_limit_reached') {
                showUpgradePrompt(error.message, error.upgrade_url);
                return;
            }
        }

        // Success
        showToast(i18n.t('messages.success.volunteer_added'), 'success');

    } catch (error) {
        showToast(i18n.t('messages.error.generic'), 'error');
    }
}

function showUpgradePrompt(message, upgradeUrl) {
    const modal = createUpgradeModal({
        title: i18n.t('billing.upgrade_required'),
        message: message,
        currentPlan: currentOrg.subscription_tier,
        nextPlan: getNextTier(currentOrg.subscription_tier),
        upgradeUrl: upgradeUrl
    });
    modal.show();
}
```

**Performance Optimization**:
- Cache volunteer count in `UsageMetrics` table (updated on create/delete)
- Invalidate cache on subscription tier change
- Query optimization: `COUNT(*)` with index on `org_id`
- Target: <100ms for limit check (well under <1s requirement)

**Edge Case Handling**:
- **Downgrade Over-Limit**: Allow viewing existing volunteers, block adding new ones
- **Trial Expiration**: Maintain volunteer access, prevent new additions until upgraded
- **Enterprise Custom**: Soft limit 2000, contact sales for higher limits

---

## Q5: Database Schema Design

**Question**: What database schema is needed for 5 new billing entities with proper indexing and relationships?

**Research Conducted**: Analyzed spec requirements (FR-001 to FR-045), existing Organization/Person models, multi-tenant isolation needs

**Finding**: **5 Tables with Foreign Key Relationships**

**Schema Design**:

```python
# api/models.py - Add to existing file

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, default=lambda: f"sub_{uuid.uuid4().hex[:12]}")
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False, unique=True, index=True)

    # Stripe references
    stripe_customer_id = Column(String, unique=True, nullable=True, index=True)  # Null for Free plan
    stripe_subscription_id = Column(String, unique=True, nullable=True, index=True)

    # Plan details
    plan_tier = Column(String, nullable=False, default="free")  # free, starter, pro, enterprise
    billing_cycle = Column(String, nullable=False, default="monthly")  # monthly, annual

    # Status tracking
    status = Column(String, nullable=False, default="active")  # active, trialing, past_due, cancelled, incomplete
    trial_end_date = Column(DateTime(timezone=True), nullable=True)
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False)
    cancel_at_period_end = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="subscription")
    billing_history = relationship("BillingHistory", back_populates="subscription")

    __table_args__ = (
        Index("ix_subscriptions_status", "status"),  # Filter by status
        Index("ix_subscriptions_trial_end", "trial_end_date"),  # Find expiring trials
    )

class BillingHistory(Base):
    __tablename__ = "billing_history"

    id = Column(String, primary_key=True, default=lambda: f"bh_{uuid.uuid4().hex[:12]}")
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    subscription_id = Column(String, ForeignKey("subscriptions.id"), nullable=True)

    # Event details
    event_type = Column(String, nullable=False, index=True)  # charge, refund, subscription_change, trial_start, trial_end
    amount_cents = Column(Integer, nullable=False)  # Store as cents to avoid float precision issues
    currency = Column(String, default="usd")
    payment_status = Column(String, nullable=False)  # succeeded, failed, pending

    # Stripe references
    stripe_invoice_id = Column(String, nullable=True, index=True)
    invoice_pdf_url = Column(String, nullable=True)

    # Metadata
    description = Column(String, nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional context

    # Timestamps
    event_timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    organization = relationship("Organization")
    subscription = relationship("Subscription", back_populates="billing_history")

    __table_args__ = (
        Index("ix_billing_history_org_timestamp", "org_id", "event_timestamp"),  # Query by org + date
        Index("ix_billing_history_payment_status", "payment_status"),  # Find failed payments
    )

class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id = Column(String, primary_key=True, default=lambda: f"pm_{uuid.uuid4().hex[:12]}")
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)

    # Stripe reference (actual card details stored in Stripe)
    stripe_payment_method_id = Column(String, unique=True, nullable=False, index=True)

    # Display info only (safe to store)
    card_brand = Column(String, nullable=True)  # visa, mastercard, amex
    card_last4 = Column(String, nullable=True)  # Last 4 digits
    exp_month = Column(Integer, nullable=True)
    exp_year = Column(Integer, nullable=True)

    # Billing address
    billing_address = Column(JSON, nullable=True)  # {line1, city, state, postal_code, country}

    # Status
    is_primary = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)

    # Timestamps
    added_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    organization = relationship("Organization")

class UsageMetrics(Base):
    __tablename__ = "usage_metrics"

    id = Column(String, primary_key=True, default=lambda: f"um_{uuid.uuid4().hex[:12]}")
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)

    # Metric tracking
    metric_type = Column(String, nullable=False, index=True)  # volunteers_count, events_count, storage_mb, api_calls
    current_value = Column(Integer, nullable=False, default=0)
    plan_limit = Column(Integer, nullable=False)

    # Calculated fields
    percentage_used = Column(Float, nullable=False, default=0.0)  # Computed: (current_value / plan_limit) * 100

    # Timestamps
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    organization = relationship("Organization")

    __table_args__ = (
        Index("ix_usage_metrics_org_type", "org_id", "metric_type"),  # Query by org + metric
        UniqueConstraint("org_id", "metric_type", name="uq_org_metric"),  # One row per org per metric
    )

class SubscriptionEvent(Base):
    __tablename__ = "subscription_events"

    id = Column(String, primary_key=True, default=lambda: f"se_{uuid.uuid4().hex[:12]}")
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)

    # Event details
    event_type = Column(String, nullable=False, index=True)  # created, upgraded, downgraded, trial_started, cancelled, reactivated
    previous_plan = Column(String, nullable=True)  # null for first subscription
    new_plan = Column(String, nullable=False)

    # Who initiated
    admin_id = Column(String, ForeignKey("people.id"), nullable=True)  # null for automatic events

    # Metadata
    reason = Column(String, nullable=True)  # "trial_expired", "payment_failed", "user_requested"
    notes = Column(String, nullable=True)

    # Timestamps
    event_timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    organization = relationship("Organization")
    admin = relationship("Person")

    __table_args__ = (
        Index("ix_subscription_events_org_timestamp", "org_id", "event_timestamp"),  # Audit trail query
    )

# Modify existing Organization model
class Organization(Base):
    # ... existing fields ...

    # Add subscription relationship
    subscription = relationship("Subscription", uselist=False, back_populates="organization")

    @property
    def subscription_tier(self) -> str:
        """Convenience property for current tier"""
        return self.subscription.plan_tier if self.subscription else "free"

    @property
    def volunteer_limit(self) -> int:
        """Convenience property for volunteer limit"""
        limits = {"free": 10, "starter": 50, "pro": 200, "enterprise": 2000}
        return limits.get(self.subscription_tier, 10)
```

**Migration Strategy**:
1. Create 5 new tables (Subscription, BillingHistory, PaymentMethod, UsageMetrics, SubscriptionEvent)
2. Backfill Subscription table: Create Free plan record for all existing organizations
3. Backfill UsageMetrics table: Count existing volunteers for each organization
4. Add indexes for query optimization (8 indexes across 5 tables)

**Multi-Tenant Safety**:
- All tables have `org_id` foreign key
- All queries filtered by `org_id`
- Stripe customer metadata includes `org_id` for cross-reference

---

## Q6: Stripe Pricing Model Configuration

**Question**: How to configure Stripe Products and Prices for 4 subscription tiers with monthly/annual billing?

**Research Conducted**: Stripe pricing best practices, product catalog design, tax handling

**Finding**: **Stripe Dashboard Product Configuration**

**Product & Price Setup** (via Stripe Dashboard or API):

```python
# One-time setup script: scripts/setup_stripe_products.py
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

# Product 1: Starter Plan
starter_product = stripe.Product.create(
    name="SignUpFlow Starter",
    description="For small teams managing up to 50 volunteers",
    metadata={"tier": "starter", "volunteer_limit": 50}
)

# Prices for Starter
starter_monthly = stripe.Price.create(
    product=starter_product.id,
    unit_amount=2900,  # $29.00 in cents
    currency="usd",
    recurring={"interval": "month"},
    nickname="Starter Monthly",
    metadata={"tier": "starter", "cycle": "monthly"}
)

starter_annual = stripe.Price.create(
    product=starter_product.id,
    unit_amount=27840,  # $278.40 in cents (20% discount: $348 → $278.40)
    currency="usd",
    recurring={"interval": "year"},
    nickname="Starter Annual",
    metadata={"tier": "starter", "cycle": "annual"}
)

# Product 2: Pro Plan
pro_product = stripe.Product.create(
    name="SignUpFlow Pro",
    description="For growing organizations managing up to 200 volunteers",
    metadata={"tier": "pro", "volunteer_limit": 200}
)

pro_monthly = stripe.Price.create(
    product=pro_product.id,
    unit_amount=7900,  # $79.00
    currency="usd",
    recurring={"interval": "month"},
    nickname="Pro Monthly"
)

pro_annual = stripe.Price.create(
    product=pro_product.id,
    unit_amount=75840,  # $758.40 (20% discount: $948 → $758.40)
    currency="usd",
    recurring={"interval": "year"},
    nickname="Pro Annual"
)

# Product 3: Enterprise Plan
enterprise_product = stripe.Product.create(
    name="SignUpFlow Enterprise",
    description="For large organizations managing up to 2000 volunteers",
    metadata={"tier": "enterprise", "volunteer_limit": 2000}
)

enterprise_monthly = stripe.Price.create(
    product=enterprise_product.id,
    unit_amount=19900,  # $199.00
    currency="usd",
    recurring={"interval": "month"},
    nickname="Enterprise Monthly"
)

enterprise_annual = stripe.Price.create(
    product=enterprise_product.id,
    unit_amount=191040,  # $1,910.40 (20% discount: $2,388 → $1,910.40)
    currency="usd",
    recurring={"interval": "year"},
    nickname="Enterprise Annual"
)

# Store Price IDs in config
STRIPE_PRICE_IDS = {
    "starter_monthly": starter_monthly.id,
    "starter_annual": starter_annual.id,
    "pro_monthly": pro_monthly.id,
    "pro_annual": pro_annual.id,
    "enterprise_monthly": enterprise_monthly.id,
    "enterprise_annual": enterprise_annual.id,
}
```

**Price ID Management**:
- Store price IDs in `api/core/config.py` or environment variables
- Map tier + cycle to price ID: `PRICE_MAP[tier][cycle]`
- Allow easy updating of prices without code changes

**Tax Configuration**:
- Enable Stripe Tax in Dashboard: Settings → Tax → Enable tax calculation
- Configure tax registration: Canada (GST registration), US (state nexus thresholds)
- Stripe Tax automatically calculates correct tax rate based on customer location
- Tax included in invoice total, transparent to customer

**Free Plan**:
- No Stripe subscription created for Free tier
- Track in local database only (`Subscription` table with `stripe_subscription_id = null`)

---

## Q7: Email Notification Strategy

**Question**: What email notifications are needed for billing events, and how to implement with existing `EmailService`?

**Research Conducted**: Reviewed spec requirements (FR-015, FR-017, FR-018), existing email_service.py implementation

**Finding**: **8 Critical Email Types with Template System**

**Email Notifications Required**:

1. **Trial Started** (FR-015)
   - Trigger: User starts Pro/Enterprise trial
   - Template: `api/templates/email/trial_started_{lang}.html`
   - Content: Trial details, end date, upgrade instructions

2. **Trial Ending Soon** (FR-015)
   - Trigger: 7 days before trial end, 3 days before trial end
   - Template: `api/templates/email/trial_ending_{lang}.html`
   - Content: Days remaining, benefits of plan, upgrade CTA

3. **Trial Expired** (FR-015)
   - Trigger: Trial period ends without payment method
   - Template: `api/templates/email/trial_expired_{lang}.html`
   - Content: Downgrade notice, reactivation offer, Free plan features

4. **Payment Failed** (FR-017)
   - Trigger: Subscription renewal payment fails
   - Template: `api/templates/email/payment_failed_{lang}.html`
   - Content: Failure reason, update payment method link, retry schedule

5. **Payment Retry Warning** (FR-018)
   - Trigger: 3 days before downgrade, 1 day before downgrade
   - Template: `api/templates/email/payment_warning_{lang}.html`
   - Content: Retry failures, urgent action needed, downgrade warning

6. **Subscription Upgraded**
   - Trigger: User upgrades to higher tier
   - Template: `api/templates/email/subscription_upgraded_{lang}.html`
   - Content: New plan details, invoice, new limits, thank you

7. **Subscription Cancelled**
   - Trigger: User cancels subscription
   - Template: `api/templates/email/subscription_cancelled_{lang}.html`
   - Content: Cancellation confirmation, service end date, retention offer

8. **Invoice Generated**
   - Trigger: Successful payment processed
   - Template: `api/templates/email/invoice_{lang}.html`
   - Content: Invoice PDF attachment, amount paid, plan details

**Implementation**:

```python
# api/services/email_service.py - Extend existing service

class EmailService:
    # ... existing methods ...

    async def send_trial_started(self, org: Organization, trial_end_date: datetime):
        """Send trial confirmation email"""
        admin = org.admins[0]  # Primary admin

        template_data = {
            "admin_name": admin.name,
            "org_name": org.name,
            "plan_name": org.subscription.plan_tier.title(),
            "trial_end_date": format_date(trial_end_date, admin.language),
            "trial_days": 14,
            "billing_url": f"{settings.APP_URL}/billing"
        }

        await self.send_email(
            to=admin.email,
            subject=i18n.t("billing.email.trial_started.subject", lang=admin.language),
            template=f"trial_started_{admin.language}.html",
            data=template_data
        )

    async def send_payment_failed(self, org: Organization, invoice: stripe.Invoice):
        """Send payment failure notification"""
        admin = org.admins[0]

        template_data = {
            "admin_name": admin.name,
            "org_name": org.name,
            "amount": format_currency(invoice.amount_due / 100),  # Convert cents
            "failure_reason": invoice.last_payment_error.message if invoice.last_payment_error else "Unknown",
            "update_payment_url": f"{settings.APP_URL}/billing/payment-method",
            "retry_schedule": "We'll retry 3 times over 7 days"
        }

        await self.send_email(
            to=admin.email,
            subject=i18n.t("billing.email.payment_failed.subject", lang=admin.language),
            template=f"payment_failed_{admin.language}.html",
            data=template_data,
            priority="high"  # Urgent notification
        )

# api/tasks/billing_tasks.py - Celery scheduled tasks

@celery_app.task
def check_expiring_trials():
    """Run daily: Send reminders for trials ending in 7 or 3 days"""
    from datetime import timedelta

    # Trials ending in 7 days
    seven_days = datetime.utcnow() + timedelta(days=7)
    for sub in Subscription.query.filter(
        Subscription.status == "trialing",
        Subscription.trial_end_date.between(seven_days - timedelta(hours=12), seven_days + timedelta(hours=12))
    ):
        email_service.send_trial_ending_soon(sub.organization, days_remaining=7)

    # Trials ending in 3 days
    three_days = datetime.utcnow() + timedelta(days=3)
    for sub in Subscription.query.filter(
        Subscription.status == "trialing",
        Subscription.trial_end_date.between(three_days - timedelta(hours=12), three_days + timedelta(hours=12))
    ):
        email_service.send_trial_ending_soon(sub.organization, days_remaining=3)
```

**Email Templates** (6 languages × 8 types = 48 template files):
- Location: `api/templates/email/`
- Format: Jinja2 HTML templates with inline CSS (email-safe)
- i18n: Separate template per language (e.g., `trial_started_en.html`, `trial_started_es.html`)
- Testing: Mailtrap for development, SendGrid for production

**Scheduled Tasks**:
- Trial reminders: Daily cron at 10 AM UTC
- Payment retry warnings: Daily cron at 9 AM UTC
- Invoice generation: Triggered by Stripe webhook `invoice.payment_succeeded`

---

## Research Summary

**All Technical Unknowns Resolved**: ✅

| Question | Answer | Confidence | Dependencies |
|----------|--------|------------|--------------|
| Payment Provider | Stripe | 9/10 | Stripe Python SDK, Stripe Dashboard access |
| Stripe API Architecture | Service layer pattern | 10/10 | stripe library, async support |
| Webhook Processing | Queue-based + fallback polling | 9/10 | Celery, Redis, Stripe CLI for testing |
| Usage Limit Enforcement | Middleware + cached metrics | 10/10 | UsageMetrics table, query optimization |
| Database Schema | 5 tables with indexes | 10/10 | SQLAlchemy migration, backfill scripts |
| Stripe Pricing Model | Dashboard product config | 10/10 | One-time setup script, price ID mapping |
| Email Notifications | 8 email types via EmailService | 9/10 | Jinja2 templates, Celery scheduled tasks |

**Blockers Identified**: NONE

**Ready for Phase 1**: ✅ YES - All research complete, proceed to data model and contracts design

**Next Steps**:
1. Phase 1: Generate `data-model.md` from 5 entity schemas
2. Phase 1: Generate API contracts (`contracts/billing-api.md`, `contracts/webhook-api.md`)
3. Phase 1: Generate `quickstart.md` for Stripe integration setup
4. Phase 1: Update agent context via `update-agent-context.sh`
