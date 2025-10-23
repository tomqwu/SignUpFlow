# Implementation Plan: SMS Notifications

**Branch**: `009-sms-notifications` | **Date**: 2025-10-20 | **Spec**: [spec.md](./spec.md)

## Summary

SMS notification system for volunteer communications with Twilio integration. Volunteers receive SMS alerts for assignment reminders (24h before), schedule changes, and urgent broadcasts. Double opt-in compliance (TCPA), STOP keyword support, phone validation, rate limiting (3 SMS/day, quiet hours 10pm-8am), cost tracking with monthly limits, delivery status monitoring, message templates with dynamic variables, and bilingual support (English/Spanish).

**Key Capabilities**:
- Assignment reminders 24h before with YES/NO reply handling
- Automatic schedule change notifications (time, location, role, cancellation)
- Admin broadcast messages to teams or individuals
- Double opt-in with confirmation code (regulatory compliance)
- STOP/START keyword handling with audit trail
- Cost management (monthly limits, overage alerts, usage dashboard)
- Phone validation (Twilio lookup API, detect landlines)
- Message templates with {{volunteer_name}}, {{event_name}}, {{date}}, {{time}}, {{location}}

**Total Additional Infrastructure Cost**: ~$30-100/month (Twilio usage-based)

## Technical Context

**Language/Version**: Python 3.11+ (backend), Vanilla JavaScript (frontend)
**Primary Dependencies**:
- Twilio SDK (SMS sending, delivery tracking, phone validation)
- Twilio Programmable Messaging API
- PostgreSQL (message history, opt-in audit trail)

**Storage**: PostgreSQL 14+ (SMSMessage, SMSOptIn, SMSTemplate tables)
**Testing**: Pytest (API), Playwright (E2E SMS opt-in workflow), Twilio test credentials
**Performance Goals**: <5s SMS delivery, <200ms opt-in validation, <1s template rendering
**Constraints**:
- Max 3 SMS per volunteer per day (exclude urgent)
- Quiet hours 10pm-8am local time (configurable)
- 160 chars standard SMS, 1600 chars multi-part
- Monthly limit enforcement (500/1000/2000 tiers)

**Cost Model**:
- Twilio SMS: $0.0079/message (US)
- Twilio lookup: $0.005/number validation
- International SMS: $0.05-0.15/message
- Estimated: 500 SMS/month org = $4/month, 2000 SMS/month org = $16/month

## Constitution Check ✅ ALL GATES PASS

E2E tests verify SMS opt-in workflow, delivery tracking, STOP keyword, cost limit enforcement. All other gates pass.

## Project Structure

```
api/
├── routers/sms_notifications.py    # SMS API endpoints
├── services/
│   ├── sms_service.py              # Twilio integration
│   └── sms_templates.py            # Template rendering
├── models.py                       # SMSMessage, SMSOptIn, SMSTemplate

frontend/
├── js/sms-settings.js              # Opt-in UI
└── js/sms-broadcast.js             # Admin broadcast UI

tests/
└── e2e/test_sms_workflow.py        # SMS opt-in E2E tests
```

---

**Status**: Streamlined plan complete
