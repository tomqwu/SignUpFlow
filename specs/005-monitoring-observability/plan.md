# Implementation Plan: Monitoring & Observability Platform

**Branch**: `005-monitoring-observability` | **Date**: 2025-10-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-monitoring-observability/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Comprehensive monitoring and observability platform integrating Sentry error tracking, uptime monitoring via Feature 003 health endpoints, performance metrics dashboard with PostgreSQL timeseries storage, Papertrail log aggregation, automated alerting via Slack/email, public status page, and performance bottleneck identification. Provides operational visibility into production system health with real-time error tracking, centralized logging, and proactive incident response.

**Key Capabilities**:
- Real-time error tracking with Sentry SDK integration ($26/month for 10K events)
- Uptime monitoring leveraging Feature 003's `/api/health` endpoint (already implemented)
- Performance metrics dashboard (response times, database query performance, memory usage)
- Centralized log aggregation via Papertrail (free tier: 50MB/day)
- Automated alerting via Slack webhooks and email notifications
- Public status page showing service health and incident history
- Performance bottleneck identification with automated detection

**Total Additional Infrastructure Cost**: ~$26/month (Sentry only; Papertrail free tier, Slack webhooks free)

## Technical Context

**Language/Version**: Python 3.11+ (backend), Vanilla JavaScript (frontend)
**Primary Dependencies**:
- `sentry-sdk` (Python error tracking SDK)
- `python-json-logger` (structured logging)
- Papertrail (SaaS log aggregation, free tier)
- Slack Incoming Webhooks API (alerting)
- Feature 003 health check endpoint (`/api/health` - already implemented)

**Storage**:
- PostgreSQL 14+ (performance metrics timeseries - leverage Feature 003 database)
- Sentry cloud storage (error events, stack traces)
- Papertrail cloud storage (log archives, 7-day retention on free tier)

**Testing**:
- Pytest (backend unit, integration, E2E tests)
- Jest (frontend tests for metrics dashboard)
- Playwright (E2E tests for status page UI)

**Target Platform**: Linux server (DigitalOcean Droplet from Feature 003)

**Project Type**: Web application (FastAPI backend + Vanilla JS frontend)

**Performance Goals**:
- Error tracking: <100ms overhead per request (Sentry SDK async)
- Metrics dashboard: <2s page load, <500ms API response
- Log aggregation: <5s ingestion latency (Papertrail SLA)
- Alert delivery: <30s notification latency (Slack webhook SLA)
- Status page: <1s page load (static HTML on CDN)

**Constraints**:
- Cost: <5% of total infrastructure budget (~$60/month from Feature 003)
- Sentry free tier: 5K events/month (upgrade to $26/month for 10K events at launch)
- Papertrail free tier: 50MB/day, 7-day retention (sufficient for launch)
- Alert rate limiting: Max 10 alerts/hour to prevent notification spam
- Uptime SLA: 99.9% uptime target (43 minutes downtime/month acceptable)

**Scale/Scope**:
- Initial launch: 100 organizations, 1,000 users
- Error volume: ~2K errors/month (well under 10K Sentry limit)
- Log volume: ~30MB/day (within 50MB Papertrail free tier)
- Metrics retention: 90 days (PostgreSQL timeseries)
- Alert rules: ~10 rules (error rate, response time, uptime)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ GATE 1: User-First Testing (E2E MANDATORY)
**Status**: PASS
**Validation**:
- E2E test: Trigger error → verify Sentry capture → check dashboard displays error
- E2E test: Status page shows "Operational" → simulate downtime → verify "Degraded" status
- E2E test: Configure alert rule → trigger threshold → verify Slack notification received
- E2E test: Performance metrics dashboard loads → verify response times chart renders
- Integration test: Papertrail log ingestion → query logs via API → verify search results
- User journey: Admin configures alert → error threshold exceeded → receives notification

### ✅ GATE 2: Security-First Development
**Status**: PASS
**Validation**:
- Sentry DSN (Data Source Name) stored as environment variable, never hardcoded
- Status page API requires JWT authentication for write operations (create/update incidents)
- Alert rules API requires admin role (`verify_admin_access()` middleware)
- Papertrail API token encrypted at rest in PostgreSQL (pgcrypto)
- Metrics dashboard filters by `org_id` for multi-tenant isolation
- All sensitive configuration (Sentry DSN, Papertrail token, Slack webhook URL) in environment variables

### ✅ GATE 3: Multi-Tenant Isolation
**Status**: PASS
**Validation**:
- PerformanceMetric table includes `org_id` for per-organization metrics
- Alert rules scoped by `org_id` (each organization configures own thresholds)
- Status page incidents optionally filtered by `org_id` for private status pages
- Sentry tags include `org_id` for error grouping and filtering
- Papertrail logs tagged with `org_id` for log search and analysis
- All API endpoints validate `verify_org_member(current_user, org_id)` before data access

### ✅ GATE 4: Test Coverage Excellence
**Status**: PASS
**Validation**:
- Unit tests: Sentry error capture (mock SDK calls), alert rule threshold evaluation, log parsing
- Integration tests: Metrics API CRUD, alert rule execution, status page incident creation
- E2E tests: Full monitoring workflows (error tracking, alerting, status updates)
- Security tests: Admin-only endpoints, JWT authentication, org isolation
- Performance tests: Metrics dashboard load time, API response times
- Target: Maintain ≥99% test pass rate across 300+ total tests

### ✅ GATE 5: Internationalization by Default
**Status**: PASS
**Validation**:
- Status page incident messages translated (6 languages: EN, ES, PT, ZH-CN, ZH-TW, KO)
- Metrics dashboard labels and tooltips use i18n keys (`locales/en/monitoring.json`)
- Alert notification messages support i18n (Slack message templates with language parameter)
- Error messages from backend validation translated (`locales/*/messages.json`)
- All user-facing monitoring UI text has i18n keys (no hardcoded English)

### ✅ GATE 6: Code Quality Standards
**Status**: PASS
**Validation**:
- FastAPI router: `api/routers/monitoring.py` for metrics, alerts, status endpoints
- Pydantic schemas: `api/schemas/monitoring.py` (MetricCreate, AlertRuleCreate, IncidentUpdate)
- SQLAlchemy models: `PerformanceMetric`, `AlertRule`, `Incident` (data-model.md)
- Service layer: `api/services/sentry_service.py`, `api/services/alerting_service.py`
- Middleware pattern: Sentry error capture middleware integrated into FastAPI app
- Frontend: Vanilla JS modules (`frontend/js/monitoring-dashboard.js`, `frontend/js/status-page.js`)

### ✅ GATE 7: Clear Documentation
**Status**: PASS
**Validation**:
- `quickstart.md`: Local Sentry testing, Papertrail setup, alert configuration guide
- `contracts/`: Complete API specifications for metrics, alerts, status page
- `data-model.md`: PostgreSQL schemas, Sentry event structure, alert rule definitions
- API documentation: Auto-generated Swagger UI at `/docs` for all monitoring endpoints
- Status page documentation: Public status page setup, incident management workflow
- Alert rule examples: Sample configurations for common scenarios (error rate, response time)

**RESULT**: ✅ ALL GATES PASS - Feature 005 approved for implementation.

## Project Structure

### Documentation (this feature)

```
specs/005-monitoring-observability/
├── plan.md              # This file (/speckit.plan command output)
├── data-model.md        # Phase 1 output - entities: ErrorEvent, PerformanceMetric, AlertRule, Incident
├── quickstart.md        # Phase 1 output - local monitoring testing guide
├── contracts/           # Phase 1 output - API specifications
│   ├── metrics_endpoints.md         # Performance metrics CRUD API
│   ├── alert_rules_endpoints.md     # Alert rule configuration API
│   └── status_page_endpoints.md     # Public status page API
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

**Note**: No `research.md` needed - straightforward SaaS integrations (Sentry, Papertrail) with well-documented APIs and SDKs.

### Source Code (repository root)

```
# Web application structure (backend + frontend)
api/
├── routers/
│   └── monitoring.py                    # Metrics, alerts, status page endpoints
├── schemas/
│   └── monitoring.py                    # Pydantic models: MetricCreate, AlertRuleCreate, IncidentUpdate
├── services/
│   ├── sentry_service.py                # Sentry SDK initialization and error capture
│   ├── alerting_service.py              # Alert rule evaluation and notification delivery
│   └── papertrail_service.py            # Papertrail log query integration (optional)
├── models.py                            # SQLAlchemy models: PerformanceMetric, AlertRule, Incident
└── main.py                              # Sentry middleware integration

frontend/
├── js/
│   ├── monitoring-dashboard.js          # Metrics dashboard UI (response times chart, DB query stats)
│   └── status-page.js                   # Public status page UI (service health, incident history)
└── index.html                           # Updated with monitoring dashboard link

locales/
├── en/
│   └── monitoring.json                  # EN translations: dashboard labels, status messages
├── es/
│   └── monitoring.json                  # ES translations
└── [other languages...]

tests/
├── unit/
│   ├── test_sentry_service.py           # Sentry error capture (mocked SDK)
│   ├── test_alerting_service.py         # Alert rule evaluation logic
│   └── test_monitoring_models.py        # SQLAlchemy model validation
├── integration/
│   ├── test_metrics_api.py              # Metrics CRUD endpoints
│   ├── test_alert_rules_api.py          # Alert rule configuration
│   └── test_status_page_api.py          # Status page incident management
└── e2e/
    ├── test_sentry_integration.py       # Trigger error → verify Sentry dashboard
    ├── test_alerting_workflow.py        # Configure alert → trigger → verify Slack notification
    └── test_status_page_ui.py           # Status page displays correct service health

scripts/
└── setup_monitoring.sh                  # One-command Sentry + Papertrail configuration
```

**Structure Decision**: Web application structure selected. Backend monitoring services integrated into existing `api/` directory with new `routers/monitoring.py` for API endpoints. Frontend monitoring dashboard added as new JS module (`monitoring-dashboard.js`) integrated into existing SPA router. Status page optionally implemented as separate static HTML page for public access (no authentication required). Sentry middleware integrated into `api/main.py` FastAPI app initialization.

## Recommended Technology Stack

| Component | Technology | Justification | Cost |
|-----------|------------|---------------|------|
| **Error Tracking** | Sentry (SaaS) | Industry standard, automatic exception capture, rich context (stack traces, breadcrumbs, user info), integrates with Slack/email | $26/month (10K events) |
| **Uptime Monitoring** | Feature 003 Health Endpoint | Already implemented (`/api/health`), returns DB + Redis status, <50ms response time | $0/month |
| **Log Aggregation** | Papertrail (SaaS) | Centralized logging, 7-day retention, powerful search, syslog protocol support, free tier sufficient for launch | $0/month (free tier) |
| **Alerting** | Slack Incoming Webhooks + Email | Team already uses Slack, webhook delivery <1s, email fallback for critical alerts | $0/month |
| **Status Page** | Custom Static HTML OR StatusPage.io | Custom: Full control, DigitalOcean Spaces hosting (free within storage quota). StatusPage.io: $29/month (if budget allows) | $0/month (custom) OR $29/month (StatusPage.io) |
| **Metrics Storage** | PostgreSQL 14+ | Leverage Feature 003 database, timeseries extension (`timescaledb` optional), 90-day retention, SQL query flexibility | $0/month (shared) |
| **Performance Metrics** | Custom Middleware + PostgreSQL | FastAPI middleware captures response times, DB query count, memory usage. Store in PostgreSQL timeseries table. | $0/month |
| **Alert Delivery** | Python `smtplib` + Slack SDK | Email via SMTP (SendGrid integration from future feature), Slack via webhook POST request | $0/month |

**Total Monthly Cost**: $26/month (Sentry only) - well under 5% of $60/month infrastructure budget

**Future Enhancements** (not in initial scope):
- Upgrade Papertrail to paid tier ($7/month) for 1GB/day, 1-year retention
- Add StatusPage.io ($29/month) for professional public status page
- Add Datadog APM ($15/month) for advanced performance profiling
- Add PagerDuty ($21/month/user) for on-call rotation and escalation

## Implementation Notes

### Sentry Integration
- **Initialization**: `sentry_sdk.init()` in `api/main.py` startup event handler
- **DSN Configuration**: Environment variable `SENTRY_DSN` (never commit to git)
- **Error Context**: Automatically captures request headers, user info, org_id tag
- **Performance Monitoring**: Optional Sentry Performance (additional cost, defer to Phase 2)
- **Release Tracking**: Tag errors with git commit SHA for deployment correlation

### Health Check Endpoint (Already Implemented in Feature 003)
- **Endpoint**: `GET /api/health`
- **Response**: `{"status": "healthy", "database": "connected", "redis": "connected", "timestamp": "..."}`
- **Monitoring**: External uptime service (e.g., UptimeRobot free tier) pings every 5 minutes
- **Alerting**: UptimeRobot sends Slack webhook notification on downtime detection

### Papertrail Log Aggregation
- **Integration**: Configure rsyslog or Python logging handler to forward logs to Papertrail
- **Log Format**: JSON structured logs (`python-json-logger` library)
- **Tagging**: Include `org_id`, `user_id`, `request_id` in log context
- **Search**: Papertrail web UI for log search and analysis
- **Retention**: 7 days on free tier (sufficient for debugging recent issues)

### Alert Rule System
- **Rule Types**: Error rate threshold, response time P95 threshold, uptime percentage
- **Evaluation**: Cron job (every 5 minutes) queries metrics and evaluates rules
- **Notification**: Slack webhook POST for immediate alerts, email for critical alerts
- **Rate Limiting**: Max 10 alerts/hour per rule to prevent spam
- **Snooze**: Admin can snooze alerts for 1 hour via API

### Status Page Options
**Option A: Custom Static HTML (Recommended for Launch)**
- Static HTML page hosted on DigitalOcean Spaces (CDN)
- Updates via API POST to `/api/status-page/incidents`
- Client-side JavaScript fetches incident history from API
- Cost: $0/month (within existing storage quota)

**Option B: StatusPage.io (Future Enhancement)**
- Professional status page with automatic updates
- Subscriber notifications (email, SMS)
- Cost: $29/month

**Decision**: Start with Option A (custom static page), upgrade to Option B if customer demand justifies cost.

### Performance Metrics Collection
- **Middleware**: FastAPI middleware captures request start/end time, calculates duration
- **Metrics Stored**: Response time (ms), HTTP status code, endpoint path, org_id
- **Database Schema**: `performance_metrics` table with timestamp, metric_type, value, metadata (JSONB)
- **Dashboard**: Chart.js line chart showing P50/P95/P99 response times over time
- **Retention**: 90 days (delete older metrics via scheduled job)

## Complexity Tracking

*No constitutional violations - no complexity tracking needed.*

