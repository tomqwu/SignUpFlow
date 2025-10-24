# Billing Portal User Guide

**For:** SignUpFlow Administrators
**Purpose:** Managing your organization's subscription, payments, and billing
**Last Updated:** 2024-10-24

---

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Understanding Your Subscription](#understanding-your-subscription)
3. [Upgrading Your Plan](#upgrading-your-plan)
4. [Managing Payment Methods](#managing-payment-methods)
5. [Viewing Billing History](#viewing-billing-history)
6. [Downgrading Your Plan](#downgrading-your-plan)
7. [Canceling Your Subscription](#canceling-your-subscription)
8. [Reactivating After Cancellation](#reactivating-after-cancellation)
9. [Understanding Usage Limits](#understanding-usage-limits)
10. [Frequently Asked Questions](#frequently-asked-questions)

---

## Getting Started

### Accessing the Billing Portal

1. **Log in** to SignUpFlow at [https://signupflow.io](https://signupflow.io)
2. Click **Admin Console** from the main menu
3. Click the **Billing** tab in the admin console

**Requirements:**
- You must be an **administrator** of your organization
- Regular volunteers cannot access billing features

### What You'll See

The billing portal displays:
- **Current Plan:** Your active subscription tier
- **Usage Summary:** How many volunteers you're using vs. your limit
- **Billing Cycle:** Monthly or annual billing
- **Next Invoice:** When your next payment is due
- **Payment Method:** Your saved card details
- **Billing History:** Past charges and invoices

---

## Understanding Your Subscription

### Plan Tiers

SignUpFlow offers four subscription plans:

#### 🆓 Free Plan
- **Price:** $0/month
- **Volunteers:** Up to 10
- **Features:**
  - Basic volunteer scheduling
  - Event management
  - Calendar export (ICS)
  - Email support (5 emails/month)
- **Best for:** Small churches, starting teams

#### ⭐ Starter Plan
- **Price:** $19.99/month or $191.88/year (save 20%)
- **Volunteers:** Up to 50
- **Features:**
  - Everything in Free
  - AI-powered automatic scheduling
  - SMS notifications (Twilio)
  - Unlimited email notifications
  - Priority email support
- **Best for:** Growing churches, sports teams

#### 💼 Pro Plan
- **Price:** $49.99/month or $479.88/year (save 20%)
- **Volunteers:** Up to 200
- **Features:**
  - Everything in Starter
  - Advanced analytics dashboard
  - API access for integrations
  - Custom branding
  - Recurring events automation
  - Multi-organization support
  - Priority support (24-hour response)
- **Best for:** Large churches, non-profits, enterprises

#### 🏢 Enterprise Plan
- **Price:** Contact sales for custom pricing
- **Volunteers:** Unlimited
- **Features:**
  - Everything in Pro
  - Dedicated account manager
  - White-label option
  - SSO (Single Sign-On)
  - Custom feature development
  - SLA guarantee (99.9% uptime)
  - 24/7 phone support
- **Best for:** Multi-site organizations, large enterprises

### Subscription Status

Your subscription can have one of these statuses:

| Status | Meaning |
|--------|---------|
| **Active** | Subscription is working normally |
| **Trial** | You're on a 14-day free trial of a paid plan |
| **Past Due** | Payment failed - service continues for 7 days |
| **Cancelled** | Service continues until period end, then downgrades to Free |
| **Expired** | Trial ended without payment - downgraded to Free |

---

## Upgrading Your Plan

### Starting a Free Trial

Before paying, try any paid plan free for 14 days:

1. Click **Upgrade Plan** button
2. Select the plan you want to try (Starter or Pro)
3. Click **Start 14-Day Free Trial**
4. No credit card required!
5. Your trial ends on [date shown]

**What happens during trial:**
- Full access to all plan features
- Usage limits increase immediately
- No charges for 14 days
- Cancel anytime before trial ends

**What happens when trial ends:**
- If you've added a payment method → automatically converts to paid subscription
- If you haven't added payment → downgrades to Free plan

### Upgrading from Free to Paid

#### Step 1: Choose Your Plan

1. In the billing portal, review the plan comparison table
2. Decide between **monthly** or **annual** billing
   - Annual saves 20% ($191.88/year vs $239.88/year for Starter)
3. Click **Upgrade to [Plan Name]**

#### Step 2: Enter Payment Information

You'll be redirected to Stripe Checkout (our secure payment processor):

1. **Email:** Pre-filled with your account email
2. **Card Information:**
   - Card number
   - Expiration date (MM/YY)
   - CVC (3-digit security code)
   - ZIP/Postal code
3. **Billing Address:** Required for tax calculation
4. Click **Subscribe**

**Security:**
- SignUpFlow never sees or stores your full card number
- All payment data is handled by Stripe (PCI DSS Level 1 certified)
- Your card is encrypted end-to-end

#### Step 3: Confirm Upgrade

After successful payment:
- You'll be redirected back to the billing portal
- Your plan updates immediately
- Usage limits increase right away
- You'll receive a confirmation email with receipt

**First Charge:**
- For monthly plans: You're charged immediately
- For annual plans: You're charged the full year upfront
- Prorated if upgrading mid-billing cycle

### Upgrading Between Paid Plans

**Example:** Upgrading from Starter ($19.99/month) to Pro ($49.99/month)

1. Click **Change Plan** button
2. Select **Pro Plan**
3. Review the prorated charge
   - Example: If 15 days left in billing cycle, you'll be charged:
   - Pro plan: $49.99 for next 30 days
   - Minus credit: -$9.99 (unused Starter time)
   - **Charge today:** $40.00
4. Click **Confirm Upgrade**
5. New limits apply immediately

---

## Managing Payment Methods

### Adding a Payment Method

1. Click **Payment Methods** in billing portal
2. Click **Add New Card**
3. You'll be redirected to Stripe to securely enter card details
4. Complete the form and click **Save Card**
5. Return to SignUpFlow - new card is now saved

**What we store:**
- Card brand (Visa, Mastercard, etc.)
- Last 4 digits (for identification)
- Expiration date
- Billing ZIP code

**What we don't store:**
- Full card number
- CVC code

### Updating Your Default Card

If you have multiple cards saved:

1. Go to **Payment Methods**
2. Find the card you want to use for subscriptions
3. Click **Set as Primary**
4. Future charges will use this card

### Removing a Card

1. Go to **Payment Methods**
2. Find the card to remove
3. Click **Remove Card**
4. Confirm deletion

**Important:**
- You cannot remove your only card if you have an active paid subscription
- Add a new card first, then remove the old one

### When Payment Fails

If your card is declined or expires:

1. You'll receive an email notification
2. Your subscription status changes to **Past Due**
3. Service continues for 7 days (grace period)
4. Update your payment method immediately:
   - Click **Update Payment Method** in billing portal
   - Enter new card details
   - Click **Retry Payment**

**If payment isn't resolved within 7 days:**
- Subscription is cancelled
- Account downgrades to Free plan
- Data is retained for 30 days

---

## Viewing Billing History

### Accessing Your Invoices

1. Go to billing portal
2. Click **Billing History** tab
3. You'll see a list of all charges and payments

**Each invoice shows:**
- Date of charge
- Plan name (Starter, Pro, etc.)
- Amount charged
- Payment status (Succeeded, Failed, Pending)
- Invoice number

### Downloading Invoices

1. Find the invoice in billing history
2. Click **Download Invoice** (PDF icon)
3. PDF invoice downloads to your computer

**Invoice includes:**
- Organization name and address
- Invoice number (INV-XXXXXXXX)
- Date of charge
- Plan details
- Amount charged
- Payment method (last 4 digits)
- SignUpFlow business information

**Uses for invoices:**
- Expense reimbursement
- Bookkeeping and accounting
- Tax records
- Budget tracking

### Viewing Next Invoice

To see your upcoming charge:

1. Go to billing portal
2. Look for **Next Invoice** section
3. You'll see:
   - Due date
   - Estimated amount
   - Plan being renewed

**Note:** Actual amount may differ if you:
- Change plans before renewal
- Add usage-based features (future)
- Have credits or discounts applied

---

## Downgrading Your Plan

### When to Downgrade

Consider downgrading if:
- You have fewer volunteers than before
- You want to reduce costs
- You're not using premium features

### How Downgrading Works

**Important:** Downgrades are **scheduled** for the end of your billing period:
- Service continues at current level until period ends
- No refunds for unused time
- Credit may be applied to next invoice (if applicable)

### Downgrade Process

#### Step 1: Initiate Downgrade

1. Click **Change Plan** button
2. Select the lower-tier plan (e.g., Pro → Starter)
3. Optionally, provide a reason (helps us improve):
   - Cost reduction
   - Fewer volunteers
   - Missing features
   - Other (free text)

#### Step 2: Review Downgrade Details

You'll see:
- **Current Plan:** Your active subscription
- **New Plan:** Plan you're downgrading to
- **Effective Date:** When downgrade takes effect
- **Credit Amount:** Unused time credit (if applicable)
- **New Usage Limits:** Volunteer limits after downgrade

**Example:**
```
Current Plan: Pro ($49.99/month) - 200 volunteers
New Plan: Starter ($19.99/month) - 50 volunteers
Effective Date: November 23, 2024 (15 days away)
Credit: $24.99 (applied to next invoice)
```

#### Step 3: Confirm Downgrade

1. Review the details carefully
2. Click **Confirm Downgrade**
3. You'll see a confirmation message:
   - "Downgrade scheduled for [date]"
   - Your current plan continues until then

### Canceling a Scheduled Downgrade

Changed your mind? You can cancel the downgrade:

1. Go to billing portal
2. You'll see a notice: **"Downgrade scheduled for [date]"**
3. Click **Cancel Downgrade**
4. Your subscription continues at current tier

**Note:** You can cancel anytime before the effective date.

### After Downgrade Takes Effect

On the downgrade date:
- Plan tier updates automatically
- Usage limits decrease
- Features are restricted to new plan level
- If you exceed new limits:
  - **Volunteers:** Cannot add more until under limit
  - **Events:** Warnings if over limit
  - **Storage:** Read-only access to old data

**What if I'm over the new volunteer limit?**
- Example: 75 volunteers but downgrading to Starter (50 limit)
- You keep all 75 volunteers (read-only)
- You cannot add more volunteers until you're under 50
- Remove or archive volunteers to get under limit

---

## Canceling Your Subscription

### Before You Cancel

Consider these alternatives:
- **Downgrade instead:** Switch to a lower tier to save money
- **Pause trial:** If on trial, no action needed - it expires automatically
- **Contact support:** We might have a solution or discount

### Types of Cancellation

#### 1. Cancel at Period End (Recommended)

**How it works:**
- Service continues until your current billing period ends
- No refund, but you get full value
- Automatically downgrades to Free plan after period ends
- Data retained for 30 days after cancellation

**Example:**
```
Today: October 24, 2024
Period ends: November 23, 2024
- October 24 - November 23: Service continues (Pro plan)
- November 23: Downgrade to Free plan
- December 23: Data deleted if not reactivated
```

#### 2. Cancel Immediately

**How it works:**
- Subscription ends right away
- Account downgrades to Free plan immediately
- Partial refund may be issued (prorated for unused time)
- Data retained for 30 days

### Cancellation Process

1. Go to billing portal
2. Scroll to bottom
3. Click **Cancel Subscription** (red button)
4. Select cancellation type:
   - ⭐ **At period end** (recommended)
   - **Immediately**
5. Optionally, tell us why (helps us improve):
   - Cost too high
   - Missing features
   - Switching to competitor
   - No longer needed
   - Other reason
6. Provide feedback (optional, free text)
7. Click **Confirm Cancellation**

### After Cancellation

**Confirmation:**
- You'll see: "Subscription cancelled. Service ends on [date]"
- Confirmation email sent to your account email
- No more charges after period ends

**What happens to your data:**

| Timeline | Status |
|----------|--------|
| **Days 1-30 (Retention Period)** | Full data access (Free plan limits) |
| **Day 30** | Final warning email sent |
| **Day 31+** | Data permanently deleted (cannot be recovered) |

**During retention period (30 days):**
- All your data is safe
- You can reactivate at any time
- Organization remains in system
- Volunteers cannot access schedules (if over Free limit)

---

## Reactivating After Cancellation

### Eligibility

You can reactivate if:
- Within 30 days of cancellation
- Organization still exists in system
- You're an admin of the organization

### Reactivation Process

1. Log in to SignUpFlow
2. Go to Admin Console → Billing
3. You'll see: **"Subscription cancelled - [X] days until data deletion"**
4. Click **Reactivate Subscription**
5. Select the plan you want (can be different from before)
6. Enter payment information (if not already saved)
7. Click **Confirm Reactivation**

**What happens:**
- Subscription resumes immediately
- Usage limits restore to selected plan
- All data remains intact
- Billing resumes (charged immediately)

**Example:**
```
Original plan: Pro ($49.99/month)
Cancelled: October 20, 2024
Reactivating: October 28, 2024 (8 days later)

You can reactivate as:
- Pro plan again ($49.99/month)
- Different plan like Starter ($19.99/month)
- Start with 14-day free trial first
```

### If Retention Period Expired

After 30 days, you cannot reactivate:
- Data has been permanently deleted
- You must start fresh:
  1. Create new organization
  2. Re-invite volunteers
  3. Recreate events and schedules

**Important:** We cannot recover data after 30 days - this is permanent.

---

## Understanding Usage Limits

### What Counts Toward Limits

#### Volunteer Limit
**Counts:**
- Active volunteer accounts
- Admin accounts
- Invited users (pending acceptance)

**Doesn't count:**
- Deleted/archived volunteers
- Declined invitations
- Test accounts

**Example:**
```
Plan: Starter (50 volunteer limit)
Current usage:
- 35 active volunteers
- 5 admins
- 8 pending invitations
Total: 48/50 (2 remaining)
```

#### Storage Limit (Future Feature)
Not currently enforced, but coming soon:
- Event descriptions
- File attachments
- Profile photos
- Exported schedules

### What Happens When You Hit Limits

#### At 80% of Limit (Warning)
- Email notification sent
- Warning banner in admin console
- Suggested action: Upgrade plan or remove unused volunteers

#### At 100% of Limit (Blocked)
- Cannot add new volunteers
- Cannot send new invitations
- Existing features continue working
- To add more:
  - Upgrade to higher plan (instant)
  - Remove/archive inactive volunteers
  - Wait for invited users to decline

### Checking Your Usage

**In Billing Portal:**
```
Usage Summary
📊 Volunteers: 35/50 (70%)
📅 Events: 150 (unlimited)
💾 Storage: 250 MB / 5 GB
```

**Color Coding:**
- 🟢 Green (0-70%): Healthy usage
- 🟡 Yellow (70-90%): Approaching limit
- 🔴 Red (90-100%): Critical - upgrade soon

---

## Frequently Asked Questions

### Billing & Payments

**Q: When am I charged?**

A:
- **First charge:** Immediately when upgrading to paid plan
- **Recurring charges:** On the same day each month/year
- **Example:** Upgraded on March 15 → charged 15th of each month

**Q: Can I get a refund?**

A:
- **Downgrades:** No refunds, but credit applied to next invoice
- **Cancellations (immediate):** Prorated refund for unused time
- **Cancellations (at period end):** No refund (you get full service)
- **Trial cancellations:** No charges, so no refunds needed

**Q: What payment methods do you accept?**

A: Via Stripe, we accept:
- Visa, Mastercard, American Express, Discover
- Apple Pay, Google Pay
- ACH Direct Debit (US only)
- SEPA Direct Debit (Europe)

**Q: Do you charge sales tax?**

A: Yes, if required by your location:
- US states: Sales tax added based on ZIP code
- EU: VAT added based on country
- Other: Local taxes may apply
- Tax-exempt? Contact support with documentation

**Q: Can I pay by invoice/check?**

A: Only for Enterprise plans. Contact sales@signupflow.io

### Subscription Changes

**Q: Can I change from monthly to annual billing?**

A: Yes!
1. Click **Change Billing Cycle**
2. Select **Annual**
3. You'll be charged prorated amount:
   - Annual price - (remaining monthly value)
4. Saves 20% on annual billing

**Q: Do I lose data when downgrading?**

A: No! All data is retained:
- Volunteers remain (but may exceed new limit)
- Events remain
- Schedules remain
- You just can't add more until under limit

**Q: Can I upgrade mid-cycle?**

A: Yes! Upgrading is instant:
- Charged prorated amount for upgrade
- Credit applied for unused time on old plan
- New limits apply immediately

### Trials & Free Plan

**Q: How long is the free trial?**

A: 14 days for Starter and Pro plans. No credit card required to start.

**Q: What happens when trial ends?**

A:
- **If card added:** Converts to paid subscription
- **If no card:** Downgrades to Free plan
- No surprise charges!

**Q: Can I stay on Free forever?**

A: Yes! The Free plan never expires:
- Up to 10 volunteers forever
- Basic scheduling features
- No hidden fees

**Q: Can I trial multiple plans?**

A: You get one 14-day trial per organization:
- Choose wisely (Starter or Pro)
- Can't trial both
- Can upgrade from trial to higher plan

### Technical Issues

**Q: My payment failed. What do I do?**

A: Common causes and fixes:
1. **Insufficient funds:** Add money to account
2. **Expired card:** Update card expiration date
3. **Wrong ZIP/postal code:** Verify billing address
4. **Card blocked:** Contact your bank
5. **International card:** Ensure international payments enabled

Then: Click **Retry Payment** in billing portal

**Q: I was charged twice!**

A: This shouldn't happen, but if it does:
1. Check billing history for both charges
2. One might be a pending authorization (not a charge)
3. Contact support@signupflow.io with:
   - Organization name
   - Both transaction IDs
   - Screenshots of charges

We'll investigate and refund if duplicate.

**Q: Invoice download isn't working**

A: Try:
1. Disable popup blocker
2. Try different browser (Chrome, Firefox, Safari)
3. Click **View HTML** then print to PDF
4. Contact support if still not working

### Account & Organization

**Q: Can I transfer my subscription to another organization?**

A: No, subscriptions are tied to organizations. But you can:
1. Cancel current subscription
2. Upgrade new organization
3. Contact support for help migrating data

**Q: What if my admin leaves?**

A: Designate another admin before they leave:
1. Admin Console → People
2. Find replacement admin
3. Click **Edit** → Add "admin" role
4. They can now manage billing

**Q: Can multiple people manage billing?**

A: Yes! Anyone with **admin** role can:
- View billing portal
- Upgrade/downgrade plans
- Update payment methods
- View invoices

### Enterprise Plans

**Q: How do I get Enterprise pricing?**

A: Enterprise plans are custom-quoted:
1. Email sales@signupflow.io
2. Tell us:
   - Number of volunteers
   - Number of organizations/sites
   - Features needed
   - Support requirements
3. We'll send custom pricing proposal

**Q: What's included in Enterprise?**

A: In addition to all Pro features:
- Unlimited volunteers
- Dedicated account manager
- 24/7 phone support
- White-label option (custom branding)
- SSO (Single Sign-On)
- Custom feature development
- SLA (99.9% uptime guarantee)
- Annual contract with flexible terms

---

## Need Help?

### Contact Support

**Email:** support@signupflow.io
**Response Time:**
- Free plan: 48 hours
- Starter plan: 24 hours
- Pro plan: 12 hours
- Enterprise plan: 1 hour (24/7 phone support)

### Resources

- **Knowledge Base:** https://docs.signupflow.io
- **Community Forum:** https://community.signupflow.io
- **Video Tutorials:** https://youtube.com/signupflow
- **Technical Documentation:** See `docs/BILLING_SETUP.md`

### Report Billing Issues

For billing emergencies (wrong charge, can't access account):
1. Email billing@signupflow.io
2. Include:
   - Organization name
   - Your email
   - Issue description
   - Screenshots if relevant
3. We'll respond within 4 hours (business days)

---

**Last Updated:** 2024-10-24
**Guide Version:** 1.0.0
**For SignUpFlow Version:** 1.0.0+

---

*This guide is for end users. For technical setup and developer documentation, see [BILLING_SETUP.md](BILLING_SETUP.md).*
