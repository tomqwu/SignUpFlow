# Billing System Setup Guide

Complete guide for configuring Stripe integration and testing the billing system.

**Status:** Production-ready billing system with Stripe integration
**Last Updated:** 2025-10-24
**Prerequisites:** Stripe account, Python 3.11+, Poetry installed

---

## Table of Contents

1. [Stripe Account Setup](#stripe-account-setup)
2. [API Key Configuration](#api-key-configuration)
3. [Webhook Configuration](#webhook-configuration)
4. [Testing Guide](#testing-guide)
5. [Production Deployment](#production-deployment)
6. [Troubleshooting](#troubleshooting)

---

## Stripe Account Setup

### 1. Create Stripe Account

1. Go to [https://stripe.com](https://stripe.com) and sign up
2. Complete identity verification (required for live payments)
3. Navigate to Dashboard → Developers

### 2. Get API Keys

**Test Mode Keys** (for development):
```
Dashboard → Developers → API keys → Test mode
- Publishable key: pk_test_xxxxx
- Secret key: sk_test_xxxxx
```

**Live Mode Keys** (for production):
```
Dashboard → Developers → API keys → Live mode
- Publishable key: pk_live_xxxxx
- Secret key: sk_live_xxxxx
```

⚠️ **NEVER commit secret keys to version control!**

### 3. Create Products and Prices

Navigate to **Products** in Stripe Dashboard:

#### Free Plan
- **Name:** SignUpFlow Free
- **Description:** 10 volunteers, basic scheduling
- **Price:** $0 (no Stripe product needed - handled in app)

#### Starter Plan
- **Name:** SignUpFlow Starter
- **Description:** 50 volunteers, AI scheduling, SMS notifications
- **Monthly Price:** $19.99 USD
- **Annual Price:** $191.88 USD (20% discount)
- Copy price IDs: `price_starter_monthly`, `price_starter_annual`

#### Pro Plan
- **Name:** SignUpFlow Pro
- **Description:** 200 volunteers, analytics, API access
- **Monthly Price:** $49.99 USD
- **Annual Price:** $479.88 USD (20% discount)
- Copy price IDs: `price_pro_monthly`, `price_pro_annual`

#### Enterprise Plan
- **Name:** SignUpFlow Enterprise
- **Description:** Unlimited volunteers, dedicated support, SLA
- **Price:** Custom (contact sales)
- No Stripe product needed (manual invoicing)

---

## API Key Configuration

### 1. Environment Variables

Create `.env` file in project root (already in `.gitignore`):

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxx

# Stripe Price IDs (from Dashboard → Products → Prices)
STRIPE_PRICE_STARTER_MONTHLY=price_xxxxxxxxxxxxx
STRIPE_PRICE_STARTER_ANNUAL=price_xxxxxxxxxxxxx
STRIPE_PRICE_PRO_MONTHLY=price_xxxxxxxxxxxxx
STRIPE_PRICE_PRO_ANNUAL=price_xxxxxxxxxxxxx

# Application Configuration
API_BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:8000
```

### 2. Verify Configuration

```bash
# Test Stripe API key
poetry run python -c "import stripe, os; stripe.api_key = os.getenv('STRIPE_SECRET_KEY'); print('✅ Stripe API key valid')"

# Verify environment variables loaded
poetry run python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(f'Stripe key: {os.getenv(\"STRIPE_SECRET_KEY\")[:12]}...')"
```

Expected output:
```
✅ Stripe API key valid
Stripe key: sk_test_xxxx...
```

### 3. Update Price IDs in Code

If using different Stripe price IDs, update in `api/services/billing_service.py`:

```python
PLAN_PRICES = {
    "starter": {
        "monthly": "price_your_starter_monthly_id",
        "annual": "price_your_starter_annual_id"
    },
    "pro": {
        "monthly": "price_your_pro_monthly_id",
        "annual": "price_your_pro_annual_id"
    }
}
```

---

## Webhook Configuration

Stripe webhooks allow SignUpFlow to receive real-time notifications about billing events.

### 1. Local Development (using Stripe CLI)

**Install Stripe CLI:**

```bash
# macOS
brew install stripe/stripe-cli/stripe

# Linux
wget https://github.com/stripe/stripe-cli/releases/download/vXX.X.X/stripe_XX.X.X_linux_x86_64.tar.gz
tar -xvf stripe_*.tar.gz
sudo mv stripe /usr/local/bin/

# Windows
scoop install stripe
```

**Login to Stripe:**

```bash
stripe login
```

**Forward webhooks to localhost:**

```bash
# Terminal 1: Run SignUpFlow backend
poetry run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Forward Stripe webhooks
stripe listen --forward-to localhost:8000/api/webhooks/stripe
```

Expected output:
```
> Ready! Your webhook signing secret is whsec_xxxxx (^C to quit)
```

Copy the webhook signing secret to `.env`:
```bash
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxx
```

**Test webhook delivery:**

```bash
stripe trigger payment_intent.succeeded
```

Expected output in Terminal 1 (SignUpFlow backend logs):
```
INFO: Received Stripe webhook: payment_intent.succeeded
INFO: Processed webhook successfully
```

### 2. Production Deployment

**Create webhook endpoint in Stripe Dashboard:**

1. Navigate to **Developers → Webhooks**
2. Click **Add endpoint**
3. Enter your production URL:
   ```
   https://yourdomain.com/api/webhooks/stripe
   ```
4. Select events to listen for:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
   - `payment_method.attached`

5. Click **Add endpoint**
6. Copy **Signing secret** (starts with `whsec_`)
7. Add to production environment variables:
   ```bash
   STRIPE_WEBHOOK_SECRET=whsec_live_xxxxxxxxxxxxxxxxxxxxx
   ```

**Test production webhook:**

```bash
curl -X POST https://yourdomain.com/api/webhooks/stripe \
  -H "Content-Type: application/json" \
  -H "Stripe-Signature: test_signature" \
  -d '{"type":"test_event"}'
```

Expected response:
```json
{"status": "webhook_received"}
```

---

## Testing Guide

### 1. Backend API Testing

**Test subscription creation:**

```bash
# Start backend
poetry run uvicorn api.main:app --reload

# Test GET /billing/subscription
curl http://localhost:8000/api/billing/subscription?org_id=test_org \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Expected: Current subscription details
{
  "success": true,
  "subscription": {
    "plan_tier": "free",
    "status": "active",
    "volunteer_limit": 10
  }
}
```

**Test upgrade to paid plan:**

```bash
# POST /billing/upgrade
curl -X POST http://localhost:8000/api/billing/upgrade?org_id=test_org \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_tier": "starter",
    "billing_cycle": "monthly",
    "trial_days": 14
  }'

# Expected: Subscription created with trial
{
  "success": true,
  "stripe_subscription_id": "sub_xxxxx",
  "trial_end_date": "2025-11-07T00:00:00"
}
```

### 2. Stripe Checkout Testing

**Test checkout flow:**

```bash
# Create checkout session
curl -X POST http://localhost:8000/api/billing/checkout-session?org_id=test_org \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_tier": "pro",
    "billing_cycle": "annual"
  }'

# Expected: Checkout session URL
{
  "success": true,
  "checkout_url": "https://checkout.stripe.com/c/pay/cs_test_xxxxx",
  "session_id": "cs_test_xxxxx"
}
```

Open the `checkout_url` in browser and use Stripe test cards:

**Successful Payment:**
```
Card Number: 4242 4242 4242 4242
Expiry: Any future date (e.g., 12/34)
CVC: Any 3 digits (e.g., 123)
ZIP: Any 5 digits (e.g., 12345)
```

**Declined Card:**
```
Card Number: 4000 0000 0000 0002
```

**Insufficient Funds:**
```
Card Number: 4000 0000 0000 9995
```

**Expired Card:**
```
Card Number: 4000 0000 0000 0069
```

Full list: [Stripe Test Cards](https://stripe.com/docs/testing#cards)

### 3. Webhook Testing

**Trigger test webhooks:**

```bash
# Subscription created
stripe trigger customer.subscription.created

# Payment succeeded
stripe trigger invoice.payment_succeeded

# Payment failed
stripe trigger invoice.payment_failed
```

**Verify in logs:**

```bash
# Check SignUpFlow logs for webhook processing
tail -f logs/app.log | grep "webhook"
```

Expected output:
```
INFO: Received Stripe webhook: customer.subscription.created
INFO: Processing webhook for org: org_xxxxx
INFO: Subscription status updated: active
```

### 4. Frontend Testing

**Manual testing steps:**

1. **Navigate to billing portal:**
   ```
   http://localhost:8000/app/admin#billing
   ```

2. **View current plan:**
   - Should display "Free" plan with 10 volunteer limit
   - Should show usage: X/10 volunteers

3. **Test upgrade flow:**
   - Click "Upgrade to Starter" button
   - Should redirect to Stripe Checkout
   - Complete payment with test card (4242...)
   - Should redirect back to billing portal
   - Should now display "Starter" plan with 50 volunteer limit

4. **Test downgrade:**
   - Click "Downgrade to Free" button
   - Confirm downgrade
   - Should schedule downgrade for end of billing period
   - Status should show "Active (scheduled cancellation)"

5. **Test payment method:**
   - Click "Update Payment Method"
   - Enter new test card
   - Should save successfully
   - Should display last 4 digits (e.g., "•••• 4242")

6. **Test invoice download:**
   - Click "View Billing History"
   - Click "Download Invoice" on any billing record
   - Should download PDF invoice

### 5. Integration Testing

**Run test suite:**

```bash
# Run all billing tests
poetry run pytest tests/integration/test_billing*.py -v

# Run specific test
poetry run pytest tests/integration/test_billing.py::test_upgrade_to_paid -v

# Run with coverage
poetry run pytest tests/integration/test_billing*.py --cov=api/services/billing_service
```

Expected output:
```
tests/integration/test_billing.py::test_upgrade_to_paid PASSED
tests/integration/test_billing.py::test_downgrade_plan PASSED
tests/integration/test_billing.py::test_cancel_subscription PASSED
...
========== 15 passed in 3.21s ==========
```

---

## Production Deployment

### 1. Switch to Live Mode

**Update environment variables:**

```bash
# Production .env
STRIPE_SECRET_KEY=sk_live_xxxxxxxxxxxxxxxxxxxxx  # Live secret key
STRIPE_WEBHOOK_SECRET=whsec_live_xxxxxxxxxxxxxxxxxxxxx  # Live webhook secret

# Update price IDs to live prices
STRIPE_PRICE_STARTER_MONTHLY=price_live_xxxxx
STRIPE_PRICE_STARTER_ANNUAL=price_live_xxxxx
STRIPE_PRICE_PRO_MONTHLY=price_live_xxxxx
STRIPE_PRICE_PRO_ANNUAL=price_live_xxxxx
```

### 2. Configure Production Webhooks

Follow steps in [Webhook Configuration → Production Deployment](#2-production-deployment)

### 3. Enable Payment Methods

In Stripe Dashboard → Settings → Payment methods:

- ✅ Cards (Visa, Mastercard, Amex)
- ✅ ACH Direct Debit (US only)
- ✅ SEPA Direct Debit (Europe)
- Optional: Apple Pay, Google Pay, Link

### 4. Configure Tax Collection

If required by your jurisdiction:

1. Navigate to **Settings → Tax**
2. Enable automatic tax calculation
3. Configure tax IDs and rates

### 5. Set Up Billing Email Notifications

1. Navigate to **Settings → Emails**
2. Customize email templates:
   - Payment receipts
   - Failed payment notifications
   - Subscription updates
   - Invoice reminders

### 6. Enable Fraud Prevention

1. Navigate to **Settings → Radar**
2. Review default fraud rules
3. Enable additional protections:
   - 3D Secure (recommended for EU/UK)
   - CVC verification
   - ZIP code verification

---

## Troubleshooting

### Common Issues

#### 1. Webhook Signature Verification Failed

**Error:**
```
HTTPException: 401 Unauthorized - Invalid webhook signature
```

**Cause:** Incorrect webhook secret or signature mismatch

**Solution:**
```bash
# Verify webhook secret is correct
echo $STRIPE_WEBHOOK_SECRET

# Should start with whsec_

# If using Stripe CLI, restart forwarding:
stripe listen --forward-to localhost:8000/api/webhooks/stripe
```

#### 2. Payment Failed - Card Declined

**Error:**
```
{
  "success": false,
  "message": "Your card was declined.",
  "error_code": "card_declined"
}
```

**Cause:** Insufficient funds, expired card, or test card for specific scenario

**Solution:**
- In test mode: Use test card 4242 4242 4242 4242
- In live mode: Ask customer to use different payment method
- Check Stripe Dashboard → Payments → Failed for details

#### 3. Subscription Not Created

**Error:**
```
{
  "success": false,
  "message": "Subscription creation failed"
}
```

**Possible Causes:**
1. Invalid price ID
2. Customer doesn't exist in Stripe
3. API key permissions issue

**Debug:**
```bash
# Check Stripe logs
stripe logs tail

# Verify price IDs
curl https://api.stripe.com/v1/prices/price_xxxxx \
  -u sk_test_xxxxx:

# Expected: Price details
```

#### 4. Duplicate Subscriptions

**Issue:** Organization has multiple active subscriptions

**Solution:**
```python
# Cancel duplicate subscriptions via Python
from api.services.stripe_service import StripeService
from api.database import SessionLocal

db = SessionLocal()
stripe_service = StripeService(db)

# Cancel old subscription
result = stripe_service.cancel_subscription(
    org_id="org_xxxxx",
    subscription_id="sub_old_xxxxx"
)
```

#### 5. Webhook Not Received

**Issue:** Stripe sends webhook but SignUpFlow doesn't process it

**Debug:**
```bash
# Check webhook delivery in Stripe Dashboard
Dashboard → Developers → Webhooks → [Your endpoint] → Attempts

# Verify endpoint is reachable
curl -X POST https://yourdomain.com/api/webhooks/stripe \
  -H "Content-Type: application/json" \
  -d '{"test": true}'

# Expected: 200 OK (even if signature fails)

# Check SignUpFlow logs
tail -f logs/app.log | grep "webhook"
```

---

## Support

### Documentation
- **Stripe API Docs:** https://stripe.com/docs/api
- **Stripe Webhook Guide:** https://stripe.com/docs/webhooks
- **Test Cards:** https://stripe.com/docs/testing#cards

### Get Help
- **Stripe Support:** https://support.stripe.com
- **SignUpFlow Issues:** https://github.com/tomqwu/signupflow/issues
- **Community:** Discord or Slack (if available)

---

**Last Updated:** 2025-10-24
**Billing System Version:** 1.0.0
**Stripe API Version:** 2024-10-28 (latest)
