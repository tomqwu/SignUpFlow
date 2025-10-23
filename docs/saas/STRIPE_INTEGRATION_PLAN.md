# Stripe Integration Plan - SignUpFlow

**Created:** 2025-10-20
**Status:** Planning Phase
**Target:** Week 1-2 of SaaS MVP Launch

---

## 🎯 Objectives

1. Implement subscription billing with Stripe
2. Enforce usage limits based on pricing tiers
3. Self-service billing portal for customers
4. Webhook handling for subscription events

---

## 💰 Pricing Tiers (Final)

### FREE TIER
```yaml
price: $0/month
limits:
  max_volunteers: 10
  max_organizations: 1
  ai_scheduling: false  # Manual only
  email_notifications: 5/month
  calendar_export: true
  support: community
target: Small groups, trial users
```

### STARTER - $29/month
```yaml
price: $29/month
limits:
  max_volunteers: 50
  max_organizations: 1
  ai_scheduling: true  # ⭐ KEY FEATURE
  email_notifications: unlimited
  calendar_export: true
  sms_notifications: false
  support: email (48hr response)
target: Small churches, community groups
conversion_goal: 80% of paid customers
```

### PROFESSIONAL - $99/month
```yaml
price: $99/month
limits:
  max_volunteers: 200
  max_organizations: 3
  ai_scheduling: true
  email_notifications: unlimited
  calendar_export: true
  sms_notifications: 500/month
  api_access: true
  advanced_analytics: true
  support: priority email (24hr response)
target: Multi-site churches, larger non-profits
conversion_goal: 15% of paid customers
```

### ENTERPRISE - Custom Pricing
```yaml
price: contact_sales
limits:
  max_volunteers: unlimited
  max_organizations: unlimited
  ai_scheduling: true
  email_notifications: unlimited
  sms_notifications: unlimited
  api_access: true
  white_label: true
  sso_saml: true
  dedicated_support: true
  sla: 99.9%
target: Large churches, denominations, enterprise non-profits
conversion_goal: 5% of paid customers
```

---

## 🏗️ Technical Implementation

### Phase 1: Stripe Setup (Day 1-2)

```python
# Install Stripe SDK
poetry add stripe

# Environment variables needed
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### Phase 2: Product & Price Creation (Day 2)

```python
# api/services/stripe_service.py

import stripe
from api.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create Products
PRODUCTS = {
    'free': {
        'name': 'SignUpFlow Free',
        'description': 'Perfect for small teams getting started',
    },
    'starter': {
        'name': 'SignUpFlow Starter',
        'description': 'AI-powered scheduling for small churches',
    },
    'professional': {
        'name': 'SignUpFlow Professional',
        'description': 'Advanced features for multi-site organizations',
    }
}

# Create Prices
PRICES = {
    'starter_monthly': {
        'product': 'starter',
        'unit_amount': 2900,  # $29.00
        'currency': 'usd',
        'recurring': {'interval': 'month'}
    },
    'professional_monthly': {
        'product': 'professional',
        'unit_amount': 9900,  # $99.00
        'currency': 'usd',
        'recurring': {'interval': 'month'}
    }
}
```

### Phase 3: Subscription Endpoints (Day 3-4)

```python
# api/routers/billing.py

from fastapi import APIRouter, Depends
from api.core.security import get_current_user
from api.services import stripe_service

router = APIRouter(prefix="/api/billing", tags=["billing"])

@router.post("/create-checkout-session")
async def create_checkout_session(
    price_id: str,
    current_user: Person = Depends(get_current_user)
):
    """Create Stripe Checkout session for subscription."""
    session = stripe.checkout.Session.create(
        customer_email=current_user.email,
        payment_method_types=['card'],
        line_items=[{
            'price': price_id,
            'quantity': 1,
        }],
        mode='subscription',
        success_url='https://signupflow.io/billing/success?session_id={CHECKOUT_SESSION_ID}',
        cancel_url='https://signupflow.io/billing/cancel',
        metadata={
            'org_id': current_user.org_id,
            'user_id': current_user.id
        }
    )
    return {'checkout_url': session.url}

@router.post("/create-portal-session")
async def create_portal_session(
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create Stripe Customer Portal session for self-service."""
    org = db.query(Organization).filter_by(id=current_user.org_id).first()

    if not org.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No subscription found")

    session = stripe.billing_portal.Session.create(
        customer=org.stripe_customer_id,
        return_url='https://signupflow.io/settings/billing'
    )
    return {'portal_url': session.url}

@router.get("/subscription")
async def get_subscription(
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current subscription details."""
    org = db.query(Organization).filter_by(id=current_user.org_id).first()

    if not org.stripe_subscription_id:
        return {'tier': 'free', 'status': 'active'}

    subscription = stripe.Subscription.retrieve(org.stripe_subscription_id)
    return {
        'tier': subscription.metadata.get('tier', 'unknown'),
        'status': subscription.status,
        'current_period_end': subscription.current_period_end,
        'cancel_at_period_end': subscription.cancel_at_period_end
    }
```

### Phase 4: Webhook Handling (Day 5-6)

```python
# api/routers/webhooks.py

@router.post("/stripe-webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle events
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        await handle_checkout_completed(session, db)

    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        await handle_subscription_updated(subscription, db)

    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        await handle_subscription_deleted(subscription, db)

    elif event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']
        await handle_payment_failed(invoice, db)

    return {'status': 'success'}

async def handle_checkout_completed(session, db):
    """Update org with subscription details after checkout."""
    org_id = session.metadata.get('org_id')
    org = db.query(Organization).filter_by(id=org_id).first()

    org.stripe_customer_id = session.customer
    org.stripe_subscription_id = session.subscription
    org.subscription_tier = session.metadata.get('tier')
    org.subscription_status = 'active'

    db.commit()
```

### Phase 5: Usage Enforcement (Day 7-8)

```python
# api/middleware/usage_limits.py

TIER_LIMITS = {
    'free': {'max_volunteers': 10, 'ai_scheduling': False},
    'starter': {'max_volunteers': 50, 'ai_scheduling': True},
    'professional': {'max_volunteers': 200, 'ai_scheduling': True},
    'enterprise': {'max_volunteers': None, 'ai_scheduling': True}
}

def check_usage_limit(org: Organization, limit_type: str):
    """Check if organization has exceeded usage limits."""
    tier = org.subscription_tier or 'free'
    limits = TIER_LIMITS[tier]

    if limit_type == 'volunteers':
        current_count = len(org.people)
        max_allowed = limits['max_volunteers']

        if max_allowed and current_count >= max_allowed:
            raise HTTPException(
                status_code=403,
                detail=f"Volunteer limit reached ({max_allowed}). Please upgrade your plan."
            )

    elif limit_type == 'ai_scheduling':
        if not limits['ai_scheduling']:
            raise HTTPException(
                status_code=403,
                detail="AI scheduling not available on Free tier. Upgrade to Starter plan."
            )

# Usage in endpoints
@router.post("/people")
async def create_person(
    request: PersonCreate,
    org_id: str,
    admin: Person = Depends(verify_admin_access),
    db: Session = Depends(get_db)
):
    org = db.query(Organization).filter_by(id=org_id).first()
    check_usage_limit(org, 'volunteers')  # Check limit before creating

    # ... rest of creation logic
```

---

## 📊 Database Schema Changes

```sql
-- Add to organizations table
ALTER TABLE organizations ADD COLUMN stripe_customer_id VARCHAR(255);
ALTER TABLE organizations ADD COLUMN stripe_subscription_id VARCHAR(255);
ALTER TABLE organizations ADD COLUMN subscription_tier VARCHAR(50) DEFAULT 'free';
ALTER TABLE organizations ADD COLUMN subscription_status VARCHAR(50) DEFAULT 'active';
ALTER TABLE organizations ADD COLUMN subscription_period_end TIMESTAMP;

-- Create subscription_events table for audit trail
CREATE TABLE subscription_events (
    id VARCHAR(255) PRIMARY KEY,
    org_id VARCHAR(255) REFERENCES organizations(id),
    event_type VARCHAR(100),
    stripe_event_id VARCHAR(255),
    data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🎨 Frontend Integration

### Billing Page Component

```javascript
// frontend/js/billing.js

async function loadSubscriptionStatus() {
    const response = await authFetch(`${API_BASE_URL}/billing/subscription`);
    const subscription = await response.json();

    renderCurrentPlan(subscription);
}

async function upgradePlan(priceId) {
    const response = await authFetch(
        `${API_BASE_URL}/billing/create-checkout-session`,
        {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({price_id: priceId})
        }
    );

    const {checkout_url} = await response.json();
    window.location.href = checkout_url;  // Redirect to Stripe Checkout
}

async function manageBilling() {
    const response = await authFetch(
        `${API_BASE_URL}/billing/create-portal-session`,
        {method: 'POST'}
    );

    const {portal_url} = await response.json();
    window.location.href = portal_url;  // Redirect to Stripe Portal
}
```

---

## ✅ Testing Checklist

- [ ] Test checkout flow (Starter plan)
- [ ] Test checkout flow (Professional plan)
- [ ] Test usage limit enforcement (volunteers)
- [ ] Test usage limit enforcement (AI scheduling)
- [ ] Test webhook: checkout.session.completed
- [ ] Test webhook: subscription.updated
- [ ] Test webhook: subscription.deleted
- [ ] Test webhook: payment_failed
- [ ] Test customer portal (cancel subscription)
- [ ] Test customer portal (update payment method)
- [ ] Test downgrade handling (Professional → Starter)
- [ ] Test upgrade handling (Starter → Professional)

---

## 📈 Success Metrics

**Week 1-2 Goals:**
- ✅ Stripe integration complete
- ✅ All 3 pricing tiers live
- ✅ Usage limits enforced
- ✅ Self-service billing portal working
- ✅ Webhook handling tested
- 🎯 First paid customer acquired

**Revenue Projections:**
- Month 1: 5 paid customers × $29 = $145 MRR
- Month 2: 10 paid customers × $29 = $290 MRR
- Month 3: 20 paid customers (16 Starter + 3 Pro + 1 Enterprise) = $1,064 MRR

---

## 🚨 Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Payment failures | Revenue loss | Email notifications, retry logic, grace period |
| Usage limit bugs | Customer frustration | Comprehensive testing, soft limits first |
| Webhook failures | Data inconsistency | Idempotency keys, retry mechanism, audit log |
| Stripe API changes | Integration breaks | Use stable API version, monitor changelog |

---

## 📚 Resources

- [Stripe Checkout Docs](https://stripe.com/docs/payments/checkout)
- [Stripe Subscriptions](https://stripe.com/docs/billing/subscriptions/overview)
- [Stripe Customer Portal](https://stripe.com/docs/billing/subscriptions/integrating-customer-portal)
- [Stripe Webhooks](https://stripe.com/docs/webhooks)
- [Stripe Testing](https://stripe.com/docs/testing)

---

## 🔄 Next Steps

1. Create Stripe account (test mode)
2. Implement Phase 1-2 (setup + products)
3. Create database migration for subscription fields
4. Implement Phase 3 (checkout endpoints)
5. Implement Phase 4 (webhooks)
6. Implement Phase 5 (usage limits)
7. Build frontend billing page
8. Test complete flow end-to-end
9. Launch to production with first beta customers
