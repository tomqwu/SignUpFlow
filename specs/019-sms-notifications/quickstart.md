# Quick Start: SMS Notifications with Twilio (10 Minutes)

**Feature**: SMS Notification System | **Branch**: `009-sms-notifications` | **Date**: 2025-10-23

Get SMS notifications working in 10 minutes using Twilio free trial. Send assignment notifications, receive YES/NO replies, and test TCPA-compliant opt-in workflow.

---

## Prerequisites

- SignUpFlow backend running (`make run`)
- Redis running (`redis-server`)
- Celery worker running (`celery -A api.tasks worker`)
- Admin account in SignUpFlow
- Phone number for testing (mobile, not landline)

**Time Estimate**: 10 minutes

---

## Step 1: Create Twilio Account (2 minutes)

### Sign Up for Free Trial

1. **Visit**: https://www.twilio.com/try-twilio
2. **Sign Up**:
   - Enter email address
   - Create password
   - Verify email (check inbox)
3. **Complete Profile**:
   - Select "I'm evaluating Twilio for work"
   - Select "SMS"
   - Select language: Python
4. **Verify Phone**:
   - Enter your mobile phone number
   - Enter verification code received via SMS

**Trial Limits**:
- $15.50 free credit (~2,000 SMS messages)
- Can only send to verified phone numbers
- Messages include "Sent from your Twilio trial account" prefix
- Upgrade to remove prefix and send to any number

---

## Step 2: Get Twilio Credentials (1 minute)

### Find Account SID and Auth Token

1. **Navigate**: Twilio Console → Dashboard
2. **Locate Credentials** (right sidebar):
   ```
   Account Info
   ├── ACCOUNT SID: ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   └── AUTH TOKEN: [Show] → xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
3. **Copy Credentials**: Click copy icon for each

### Get Twilio Phone Number

1. **Navigate**: Phone Numbers → Manage → Active Numbers
2. **If no number**, click "Buy a number":
   - Select country: United States
   - Capabilities: SMS
   - Click "Search"
   - Select any number (e.g., +1 555-123-4567)
   - Click "Buy" (free with trial)
3. **Copy Phone Number**: `+15551234567` (E.164 format)

---

## Step 3: Configure SignUpFlow Environment (1 minute)

### Add Twilio Credentials to .env

```bash
cd /home/ubuntu/SignUpFlow

# Edit .env file
cat >> .env << 'EOF'

# Twilio SMS Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+15551234567
EOF
```

**Replace**:
- `ACxxxx...` with your Account SID
- `xxxxxx...` with your Auth Token
- `+15551234567` with your Twilio phone number

### Verify Configuration

```bash
# Test environment variables loaded
poetry run python -c "
import os
print('Account SID:', os.getenv('TWILIO_ACCOUNT_SID'))
print('Phone Number:', os.getenv('TWILIO_PHONE_NUMBER'))
print('✅ Configuration loaded successfully!')
"
```

**Expected Output**:
```
Account SID: ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Phone Number: +15551234567
✅ Configuration loaded successfully!
```

---

## Step 4: Configure Twilio Webhooks (2 minutes)

### Set Webhook URLs

1. **Navigate**: Phone Numbers → Manage → Active Numbers → (Select your number)

2. **Messaging Configuration**:
   - **Webhook when message comes in**:
     - URL: `https://your-domain.com/api/webhooks/twilio/incoming`
     - HTTP Method: POST
   - **Status Callback URL** (click "Show more"):
     - URL: `https://your-domain.com/api/webhooks/twilio/status`
     - HTTP Method: POST

3. **Click "Save Configuration"**

**For Local Testing** (ngrok tunnel):

```bash
# Install ngrok
brew install ngrok  # macOS
# OR
sudo snap install ngrok  # Linux

# Start ngrok tunnel to port 8000
ngrok http 8000

# Copy HTTPS URL (e.g., https://abc123.ngrok.io)
# Use this as your domain in webhook URLs:
# - Incoming: https://abc123.ngrok.io/api/webhooks/twilio/incoming
# - Status: https://abc123.ngrok.io/api/webhooks/twilio/status
```

**Note**: Free ngrok URLs change every restart. Paid plan ($8/month) provides persistent URLs.

---

## Step 5: Verify Your Test Phone Number (1 minute)

### Add Phone to Twilio Verified Caller IDs

**Trial accounts can only send to verified numbers.**

1. **Navigate**: Phone Numbers → Manage → Verified Caller IDs
2. **Click**: "Add new Caller ID"
3. **Enter**: Your mobile phone number (E.164 format: +15551234567)
4. **Verify**: Enter 6-digit code received via SMS
5. **Status**: Shows "Verified" ✅

**Upgrade Note**: Upgrade to paid account to send to any phone number (no verification needed).

---

## Step 6: Test SMS Sending (2 minutes)

### Send Test SMS via Python Console

```bash
poetry run python

>>> from api.services.sms_service import SMSService
>>> import os
>>>
>>> # Initialize SMS service
>>> sms = SMSService(
...     account_sid=os.getenv('TWILIO_ACCOUNT_SID'),
...     auth_token=os.getenv('TWILIO_AUTH_TOKEN'),
...     from_number=os.getenv('TWILIO_PHONE_NUMBER')
... )
>>>
>>> # Send test SMS to your phone
>>> result = sms.send_sms(
...     to_number='+15551234567',  # Your verified phone
...     message='SignUpFlow test message! Reply YES to confirm receipt.'
... )
>>>
>>> print(result)
{'sid': 'SM1234567890abcdef', 'status': 'queued', 'cost': None}
>>>
>>> # Should receive SMS within 30 seconds
```

**Expected SMS**:
```
Sent from your Twilio trial account
SignUpFlow test message! Reply YES to confirm receipt.
```

**Verify Delivery**:
1. **Navigate**: Messaging → Logs → SMS Logs
2. **Find Message**: Should show status "delivered"
3. **Check Phone**: Should receive SMS

---

## Step 7: Test Two-Way SMS Replies (1 minute)

### Reply to Test Message

1. **On Your Phone**: Reply "YES" to the test SMS
2. **Check SignUpFlow Logs**:
   ```bash
   # View webhook processing
   tail -f /var/log/signupflow/webhooks.log
   ```

3. **Expected Log Entry**:
   ```
   [2025-01-01 10:00:00] INFO: Incoming SMS from +15551234567
   [2025-01-01 10:00:00] INFO: Body: YES
   [2025-01-01 10:00:00] INFO: Processed: assignment_confirmed
   ```

4. **Check Response SMS**: Should receive confirmation message

**Note**: For full reply processing, you need:
- Pending assignment in database
- SMS preferences configured for volunteer
- Webhook endpoint deployed (not localhost)

---

## Step 8: Complete Phone Verification Flow (2 minutes)

### Test TCPA-Compliant Opt-In

1. **Navigate**: SignUpFlow → Settings → SMS Notifications

2. **Enter Phone Number**:
   - Phone: `+15551234567` (your verified number)
   - Click "Send Verification Code"

3. **Expected SMS**:
   ```
   Sent from your Twilio trial account
   SignUpFlow verification code: 123456. Reply with this code to enable SMS notifications. Code expires in 10 minutes.
   ```

4. **Enter Code**:
   - Verification Code: `123456` (from SMS)
   - Select Notification Types:
     - ☑️ Assignment notifications
     - ☑️ Event reminders
     - ☑️ Broadcast messages
   - Click "Verify & Enable"

5. **Expected Confirmation SMS**:
   ```
   Sent from your Twilio trial account
   SMS notifications enabled for SignUpFlow. Reply STOP to unsubscribe anytime.
   ```

6. **Verify in UI**:
   - Phone number shows verified ✅
   - Notification preferences saved

---

## Step 9: Send Real Assignment Notification (1 minute)

### Create Event and Assign Volunteer

1. **Navigate**: Admin Console → Events → Create Event
   - Title: "Test Event"
   - Date: Tomorrow
   - Time: 10:00 AM
   - Click "Save"

2. **Assign Yourself**:
   - Click "Assign Volunteers"
   - Select your name
   - Role: "Volunteer"
   - Click "Assign & Send SMS"

3. **Expected SMS** (within 30 seconds):
   ```
   Sent from your Twilio trial account
   Test Event - Jan 2 at 10:00AM - Role: Volunteer. Reply YES to confirm, NO to decline
   ```

4. **Test Confirmation**:
   - Reply "YES" to SMS
   - Expected response:
     ```
     Assignment confirmed for Test Event on Jan 2 at 10:00AM. See you there!
     ```
   - Check Admin Console → Assignments → Status shows "Confirmed" ✅

---

## Troubleshooting

### Issue: "Authentication Error" when sending SMS

**Symptom**: `401 Unauthorized` error from Twilio API

**Fix**:
```bash
# Verify credentials are correct
poetry run python -c "
from twilio.rest import Client
import os

client = Client(
    os.getenv('TWILIO_ACCOUNT_SID'),
    os.getenv('TWILIO_AUTH_TOKEN')
)
print('✅ Authentication successful!')
print('Account:', client.api.accounts.get().friendly_name)
"
```

If error persists:
1. Double-check Account SID and Auth Token copied correctly
2. Ensure no extra spaces in `.env` file
3. Regenerate Auth Token in Twilio Console if needed

---

### Issue: "Phone number not verified" error

**Symptom**: `21608: The number +15551234567 is unverified`

**Fix**:
1. **Navigate**: Phone Numbers → Manage → Verified Caller IDs
2. **Verify**: Add your phone number if not listed
3. **Wait**: 5 minutes for verification to propagate
4. **Retry**: Send SMS again

**Upgrade**: To send to any number, upgrade to paid account ($20 minimum).

---

### Issue: SMS not received

**Symptom**: API returns success but no SMS received

**Debug Steps**:

1. **Check Twilio Logs**:
   - Navigate: Messaging → Logs → SMS Logs
   - Find your message
   - Check status: `queued` → `sent` → `delivered` (or `failed`)

2. **If Status "Failed"**:
   - Check Error Code (e.g., 30003, 30005)
   - See error codes: https://www.twilio.com/docs/api/errors

3. **Common Failures**:
   - **30003**: Unreachable (phone off, no signal)
   - **30005**: Unknown destination (invalid number)
   - **30006**: Landline (cannot receive SMS)

4. **Carrier Delays**:
   - US carriers: Usually <10 seconds
   - International: Can take 1-2 minutes

---

### Issue: Webhook not receiving calls

**Symptom**: Reply SMS or status updates not processed

**Debug Steps**:

1. **Check ngrok Status**:
   ```bash
   # Verify ngrok tunnel running
   curl http://localhost:4040/api/tunnels
   ```

2. **Test Webhook Manually**:
   ```bash
   # Simulate Twilio incoming SMS webhook
   curl -X POST https://abc123.ngrok.io/api/webhooks/twilio/incoming \
     -d "From=+15551234567" \
     -d "To=+15559876543" \
     -d "Body=YES" \
     -d "MessageSid=SM1234567890abcdef"
   ```

3. **Check SignUpFlow Logs**:
   ```bash
   tail -f /var/log/signupflow/webhooks.log
   ```

4. **Verify Webhook URLs**:
   - Must be HTTPS (not HTTP)
   - Must be publicly accessible (not localhost)
   - Twilio cannot reach private networks

---

### Issue: "Rate limit exceeded"

**Symptom**: `429 Too Many Requests` error

**Trial Limits**:
- **Sending**: 1 message per second
- **Receiving**: No limit

**Fix**:
```python
# Add delay between messages
import time

for volunteer in volunteers:
    sms.send_sms(volunteer.phone, message)
    time.sleep(1)  # 1-second delay
```

**Upgrade**: Paid accounts have higher rate limits (100 msgs/second).

---

### Issue: "Insufficient funds"

**Symptom**: `21606: Account not authorized`

**Fix**:
1. **Check Balance**: Console → Account → Usage
2. **Add Funds**: Console → Billing → Add Funds
3. **Upgrade**: Remove trial restrictions

**Trial Balance**:
- Initial: $15.50
- Per SMS (US): $0.0079
- Remaining: $15.50 - (messages_sent × $0.0079)

---

## Production Deployment

### Remove Trial Prefix

**Upgrade Account**:
1. **Navigate**: Console → Billing → Upgrade
2. **Add Payment Method**: Credit card or bank account
3. **Add Funds**: Minimum $20
4. **Verify Upgrade**: Messages no longer show "Sent from trial account"

**Cost Estimate**:
- Assignment notifications: ~200/month = $1.58/month
- Event reminders: ~150/month = $1.19/month
- Total: ~$3/month per organization

---

### Use Production Webhook URLs

**Replace ngrok URLs with production domain**:

1. **Deploy SignUpFlow**: Production server (e.g., DigitalOcean, AWS)
2. **Configure DNS**: Point domain to server (e.g., app.signupflow.io)
3. **Enable HTTPS**: Let's Encrypt certificate (Traefik)
4. **Update Webhooks**: Twilio Console → Phone Numbers → (Your number)
   - Incoming: `https://app.signupflow.io/api/webhooks/twilio/incoming`
   - Status: `https://app.signupflow.io/api/webhooks/twilio/status`

---

### Enable Phone Validation

**Twilio Lookup API** (validate phone numbers before sending):

```python
# api/services/sms_service.py
def validate_phone(self, phone_number: str) -> dict:
    """Validate phone via Twilio Lookup API."""
    try:
        lookup = self.client.lookups.v1.phone_numbers(phone_number).fetch(
            type=['carrier']
        )
        return {
            'valid': True,
            'phone_number': lookup.phone_number,
            'carrier_type': lookup.carrier['type'],  # mobile/landline/voip
            'carrier_name': lookup.carrier['name']
        }
    except TwilioRestException as e:
        return {
            'valid': False,
            'error': 'Invalid phone number format'
        }
```

**Cost**: $0.005 per lookup (~200 lookups for $1)

---

## Verification Checklist

Before moving to implementation, verify:

- [ ] Twilio account created and verified
- [ ] Account SID and Auth Token copied to `.env`
- [ ] Twilio phone number purchased and configured
- [ ] Test phone number verified in Twilio Console
- [ ] Webhook URLs configured (incoming + status)
- [ ] SMS sending test successful (received message)
- [ ] SMS reply test successful (YES/NO processing)
- [ ] Phone verification flow complete (6-digit code)
- [ ] Assignment notification test successful
- [ ] ngrok tunnel running for local testing

**Test Summary**:
```bash
# Run SMS integration tests
poetry run pytest tests/integration/test_sms_service.py -v

# Expected: All tests pass
```

---

## Next Steps

After completing this quickstart:

1. **Implement SMS Service**:
   - `api/services/sms_service.py` - Twilio integration
   - `api/routers/sms.py` - SMS API endpoints
   - `api/routers/webhooks.py` - Webhook handlers

2. **Add Database Tables**:
   - `sms_preferences` - Volunteer phone verification
   - `sms_messages` - Message audit trail
   - `sms_templates` - Reusable message templates
   - `sms_usage` - Cost tracking

3. **Build Frontend UI**:
   - `frontend/js/sms-preferences.js` - Phone verification
   - `frontend/js/sms-admin.js` - Admin broadcast messaging

4. **Run Tests**:
   ```bash
   # Unit tests
   poetry run pytest tests/unit/test_sms_service.py -v

   # Integration tests (requires Twilio credentials)
   poetry run pytest tests/integration/test_sms_api.py -v

   # E2E tests
   poetry run pytest tests/e2e/test_sms_workflows.py -v
   ```

---

## Reference Documentation

- **Plan**: `specs/019-sms-notifications/plan.md` - Implementation plan
- **Research**: `specs/019-sms-notifications/research.md` - Technology decisions
- **Data Model**: `specs/019-sms-notifications/data-model.md` - Database schemas
- **API Contracts**: `specs/019-sms-notifications/contracts/` - API specifications
- **Twilio Docs**: https://www.twilio.com/docs/sms
- **Twilio Python SDK**: https://www.twilio.com/docs/libraries/python

---

**Time to Complete**: 10 minutes
**Last Updated**: 2025-10-23
**Feature**: 019 - SMS Notification System
