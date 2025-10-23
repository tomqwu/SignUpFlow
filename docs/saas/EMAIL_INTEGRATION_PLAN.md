# Email Integration Plan - SignUpFlow

**Created:** 2025-10-20
**Status:** Planning Phase
**Target:** Week 3 of SaaS MVP Launch

---

## 🎯 Objectives

1. Send transactional emails (invitations, password resets, notifications)
2. Email template system with branding
3. Multi-language email support
4. Email delivery tracking and analytics
5. Bounce/complaint handling

---

## 📧 Email Provider Selection

### Recommended: SendGrid

**Why SendGrid:**
- ✅ 100 emails/day free tier (for testing)
- ✅ Easy SMTP + HTTP API
- ✅ Template engine with HTML/CSS
- ✅ Webhook support for delivery tracking
- ✅ Good deliverability rates
- ✅ Familiar for most developers

**Pricing:**
- Free: 100 emails/day
- Essentials ($15/mo): 40,000 emails/mo
- Pro ($90/mo): 100,000 emails/mo

**Alternative: AWS SES**
- ✅ Cheaper ($0.10 per 1,000 emails)
- ❌ More complex setup
- ❌ Need to verify domain
- 💡 Good for scale (>100k emails/mo)

**Decision: SendGrid for MVP, migrate to SES at scale**

---

## 📨 Email Types & Templates

### 1. Welcome Email
**Trigger:** New user signup
**Subject:** "Welcome to SignUpFlow! 🎉"
**Content:**
```
Hi {name},

Welcome to SignUpFlow! We're excited to have you on board.

Your organization "{org_name}" is ready to go. Here's what you can do next:

✅ Invite your volunteers: {invite_url}
✅ Create your first event: {events_url}
✅ Set up your schedule: {schedule_url}

Need help? Check out our Quick Start Guide: {quickstart_url}

Happy scheduling!
The SignUpFlow Team
```

### 2. Invitation Email
**Trigger:** Admin invites new volunteer
**Subject:** "You're invited to join {org_name} on SignUpFlow"
**Content:**
```
Hi,

{admin_name} has invited you to join {org_name} on SignUpFlow!

SignUpFlow makes volunteer scheduling simple with AI-powered schedule generation.

Accept your invitation: {invitation_url}

This invitation expires in 7 days.

Questions? Reply to this email and we'll help you get started.

Best,
The SignUpFlow Team
```

### 3. Password Reset
**Trigger:** User requests password reset
**Subject:** "Reset your SignUpFlow password"
**Content:**
```
Hi {name},

We received a request to reset your password for SignUpFlow.

Reset your password: {reset_url}

This link expires in 1 hour.

If you didn't request this, you can safely ignore this email.

Best,
The SignUpFlow Team
```

### 4. Event Assignment Notification
**Trigger:** Volunteer assigned to event
**Subject:** "You're scheduled for {event_name} on {date}"
**Content:**
```
Hi {name},

You've been assigned to:

📅 Event: {event_name}
🕐 Date/Time: {datetime}
📍 Location: {location}
👤 Role: {role}

View your full schedule: {schedule_url}

Can't make it? Update your availability: {availability_url}

See you there!
{org_name} Team
```

### 5. Event Reminder
**Trigger:** 24 hours before event
**Subject:** "Reminder: {event_name} tomorrow at {time}"
**Content:**
```
Hi {name},

Just a friendly reminder about your upcoming assignment:

📅 Tomorrow: {event_name}
🕐 Time: {time}
📍 Location: {location}
👤 Your Role: {role}

View details: {event_url}

Thanks for volunteering!
{org_name} Team
```

### 6. Subscription Confirmation
**Trigger:** Successful Stripe checkout
**Subject:** "Welcome to SignUpFlow {tier} Plan!"
**Content:**
```
Hi {name},

Thanks for upgrading to SignUpFlow {tier}! 🎉

Your subscription details:
• Plan: {tier} Plan
• Price: ${price}/month
• Next billing date: {next_billing_date}

New features unlocked:
{feature_list}

Manage your subscription: {billing_url}

Happy scheduling!
The SignUpFlow Team
```

### 7. Payment Failed
**Trigger:** Stripe invoice payment failed
**Subject:** "Action Required: Payment Failed"
**Content:**
```
Hi {name},

We couldn't process your payment for SignUpFlow {tier} Plan.

Amount due: ${amount}
Payment method: •••• {last4}

Update your payment method: {billing_url}

Your account will remain active for 7 days. After that, you'll be downgraded to the Free plan.

Need help? Contact us: support@signupflow.io

Best,
The SignUpFlow Team
```

---

## 🏗️ Technical Implementation

### Phase 1: SendGrid Setup (Day 1)

```bash
# Install SendGrid SDK
poetry add sendgrid

# Environment variables
SENDGRID_API_KEY=SG.xxxxxxxxxxxx
FROM_EMAIL=noreply@signupflow.io
FROM_NAME=SignUpFlow
```

### Phase 2: Email Service (Day 2-3)

```python
# api/services/email_service.py

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from api.core.config import settings

class EmailService:
    def __init__(self):
        self.sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        self.from_email = Email(settings.FROM_EMAIL, settings.FROM_NAME)

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_content: str = None
    ):
        """Send email via SendGrid."""
        message = Mail(
            from_email=self.from_email,
            to_emails=To(to_email),
            subject=subject,
            html_content=Content("text/html", html_content)
        )

        if plain_content:
            message.add_content(Content("text/plain", plain_content))

        try:
            response = self.sg.send(message)
            return {
                'success': True,
                'status_code': response.status_code,
                'message_id': response.headers.get('X-Message-Id')
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def send_welcome_email(self, user: Person, org: Organization):
        """Send welcome email to new user."""
        html = await render_template('welcome.html', {
            'name': user.name,
            'org_name': org.name,
            'invite_url': f'{settings.APP_URL}/admin/invitations',
            'events_url': f'{settings.APP_URL}/app/events',
            'schedule_url': f'{settings.APP_URL}/app/schedule',
            'quickstart_url': 'https://docs.signupflow.io/quickstart'
        })

        await self.send_email(
            to_email=user.email,
            subject=f"Welcome to SignUpFlow! 🎉",
            html_content=html
        )

    async def send_invitation_email(
        self,
        email: str,
        admin_name: str,
        org_name: str,
        invitation_token: str
    ):
        """Send invitation email."""
        invitation_url = f'{settings.APP_URL}/accept-invitation?token={invitation_token}'

        html = await render_template('invitation.html', {
            'admin_name': admin_name,
            'org_name': org_name,
            'invitation_url': invitation_url
        })

        await self.send_email(
            to_email=email,
            subject=f"You're invited to join {org_name} on SignUpFlow",
            html_content=html
        )

    async def send_password_reset_email(self, user: Person, reset_token: str):
        """Send password reset email."""
        reset_url = f'{settings.APP_URL}/reset-password?token={reset_token}'

        html = await render_template('password_reset.html', {
            'name': user.name,
            'reset_url': reset_url
        })

        await self.send_email(
            to_email=user.email,
            subject="Reset your SignUpFlow password",
            html_content=html
        )
```

### Phase 3: Email Templates (Day 4)

```html
<!-- api/templates/emails/welcome.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 10px 10px 0 0;
        }
        .content {
            background: white;
            padding: 30px;
            border: 1px solid #e0e0e0;
            border-top: none;
        }
        .button {
            display: inline-block;
            padding: 12px 30px;
            background: #667eea;
            color: white !important;
            text-decoration: none;
            border-radius: 5px;
            margin: 10px 5px;
        }
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Welcome to SignUpFlow!</h1>
    </div>
    <div class="content">
        <p>Hi {{name}},</p>

        <p>Welcome to SignUpFlow! We're excited to have you on board.</p>

        <p>Your organization <strong>{{org_name}}</strong> is ready to go. Here's what you can do next:</p>

        <ul>
            <li>✅ Invite your volunteers</li>
            <li>✅ Create your first event</li>
            <li>✅ Set up your schedule</li>
        </ul>

        <div style="text-align: center; margin: 30px 0;">
            <a href="{{invite_url}}" class="button">Invite Volunteers</a>
            <a href="{{events_url}}" class="button">Create Event</a>
        </div>

        <p>Need help? Check out our <a href="{{quickstart_url}}">Quick Start Guide</a>.</p>

        <p>Happy scheduling!<br>
        The SignUpFlow Team</p>
    </div>
    <div class="footer">
        <p>SignUpFlow - Volunteer Scheduling Made Simple</p>
        <p>
            <a href="https://signupflow.io">Website</a> |
            <a href="https://docs.signupflow.io">Help Center</a> |
            <a href="mailto:support@signupflow.io">Contact Support</a>
        </p>
    </div>
</body>
</html>
```

### Phase 4: Email Webhooks (Day 5)

```python
# api/routers/webhooks.py

@router.post("/sendgrid-webhook")
async def sendgrid_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle SendGrid event webhooks."""
    events = await request.json()

    for event in events:
        event_type = event['event']
        email = event['email']
        timestamp = event['timestamp']

        # Log event to database
        email_log = EmailLog(
            email=email,
            event_type=event_type,
            timestamp=datetime.fromtimestamp(timestamp),
            metadata=event
        )
        db.add(email_log)

        # Handle specific events
        if event_type == 'bounce':
            await handle_bounce(email, event, db)
        elif event_type == 'spam_report':
            await handle_spam_report(email, event, db)
        elif event_type == 'unsubscribe':
            await handle_unsubscribe(email, event, db)

    db.commit()
    return {'status': 'success'}
```

---

## 🌍 Multi-Language Support

```python
# api/services/email_i18n.py

EMAIL_SUBJECTS = {
    'en': {
        'welcome': 'Welcome to SignUpFlow! 🎉',
        'invitation': 'You\'re invited to join {org_name} on SignUpFlow',
        'password_reset': 'Reset your SignUpFlow password'
    },
    'es': {
        'welcome': '¡Bienvenido a SignUpFlow! 🎉',
        'invitation': 'Estás invitado a unirte a {org_name} en SignUpFlow',
        'password_reset': 'Restablece tu contraseña de SignUpFlow'
    },
    'zh-CN': {
        'welcome': '欢迎来到 SignUpFlow！🎉',
        'invitation': '您已被邀请加入 {org_name} 在 SignUpFlow',
        'password_reset': '重置您的 SignUpFlow 密码'
    }
}

async def render_template(template_name: str, context: dict, language='en'):
    """Render email template with i18n support."""
    template_path = f'api/templates/emails/{language}/{template_name}'
    # ... render logic
```

---

## ✅ Testing Checklist

- [ ] Test welcome email (signup flow)
- [ ] Test invitation email (admin invite)
- [ ] Test password reset email
- [ ] Test event assignment notification
- [ ] Test event reminder (24hr before)
- [ ] Test subscription confirmation
- [ ] Test payment failed email
- [ ] Test multi-language emails (EN, ES, ZH)
- [ ] Test email delivery tracking
- [ ] Test bounce handling
- [ ] Test spam complaint handling
- [ ] Test unsubscribe handling

---

## 📊 Database Schema

```sql
-- Email logs for tracking and debugging
CREATE TABLE email_logs (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255),
    template VARCHAR(100),
    event_type VARCHAR(50),  -- sent, delivered, opened, clicked, bounce, etc.
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Unsubscribe management
CREATE TABLE email_unsubscribes (
    email VARCHAR(255) PRIMARY KEY,
    reason VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🚨 Best Practices

1. **Always use templates** - Don't hardcode HTML in code
2. **Test with real emails** - Use mailtrap.io for development
3. **Handle bounces** - Mark email addresses as invalid
4. **Respect unsubscribes** - Don't send to unsubscribed users
5. **Monitor deliverability** - Check SendGrid analytics weekly
6. **Use plain text fallback** - For email clients that block HTML
7. **Personalize content** - Use recipient's name and context
8. **Include unsubscribe link** - Legal requirement (CAN-SPAM Act)

---

## 💰 Cost Projections

**Month 1-3 (MVP):**
- Free tier: 100 emails/day = 3,000/month
- Cost: $0

**Month 4-6 (Growth):**
- Essentials plan: 40,000 emails/month
- Cost: $15/month

**Month 7-12 (Scale):**
- Pro plan: 100,000 emails/month
- Cost: $90/month

**Break-even:** ~15 paid customers

---

## 📚 Resources

- [SendGrid API Docs](https://docs.sendgrid.com/api-reference)
- [SendGrid Python Library](https://github.com/sendgrid/sendgrid-python)
- [Email Template Best Practices](https://sendgrid.com/blog/email-template-best-practices/)
- [CAN-SPAM Compliance](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business)

---

## 🔄 Next Steps

1. Create SendGrid account
2. Verify sender email (noreply@signupflow.io)
3. Set up SPF/DKIM records for domain
4. Implement email service class
5. Create HTML email templates
6. Implement webhook handling
7. Test with mailtrap.io
8. Launch to production
