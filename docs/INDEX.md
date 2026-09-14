# SignUpFlow Documentation Index

## Current Entry Points

- [Production roadmap](ROADMAP.md): no CI checks; all validation runs locally.

Reconciled 2026-09-13 for testing, CI, and merge policy:

- [Repository README](../README.md): application entry point and commands.
- [Testing and merge policy](TESTING.md): current local test tiers, prerequisites,
  local checks, and commit-bound evidence. Use this instead of old test reports.
- [Contributor workflow](../CONTRIBUTING.md) and [agent rules](../AGENTS.md).
- [Local code review policy](ai-pr-review.md): local review evidence and merge rules.
- [API authorization matrix](API_AUTHORIZATION.md): executable route classes,
  tenant response semantics, and scheduling regression evidence.
- [Operational playbooks](playbooks/README.md): church and basketball workflows.
- [Mobile guide](../mobile/README.md) and [device smoke checks](../mobile/SMOKE.md).
- [Documentation reconciliation record](DOCUMENTATION_STATUS.md): audit scope,
  historical classification, and verification limits.

## Historical Catalog (2025-10-27)

The catalog below is retained as a historical inventory. Its "Current", "Complete",
and similar labels describe the old snapshot, not current verification. Some old
targets no longer exist, including TEST_STATUS.md and TESTING_STRATEGY.md; use the
current entry points above rather than treating those legacy links as runbooks.
This reconciliation does not certify the old security, deployment, or launch claims.

**Last Updated**: 2025-10-27
**Project**: SignUpFlow - AI-Powered Volunteer Scheduling System

This index provides a comprehensive guide to all SignUpFlow documentation organized by category.

---

## 📋 Table of Contents

1. [Getting Started](#-getting-started)
2. [Development](#-development)
3. [Testing](#-testing)
4. [Deployment & Infrastructure](#-deployment--infrastructure)
5. [Features & Implementation](#-features--implementation)
6. [Security](#-security)
7. [Billing & SaaS](#-billing--saas)
8. [Internationalization](#-internationalization)
9. [Technical Debt & Refactoring](#-technical-debt--refactoring)
10. [Project Status & Roadmaps](#-project-status--roadmaps)
11. [Archive](#-archive)

---

## 🚀 Getting Started

Essential docs for new developers and contributors.

| Document | Description | Audience |
|----------|-------------|----------|
| [README.md](../README.md) | Project overview and quick start | Everyone |
| [QUICK_START.md](QUICK_START.md) | Detailed setup instructions | Developers |
| [CLAUDE.md](../CLAUDE.md) | Comprehensive AI assistant context | AI assistants, developers |
| [USER_STORIES.md](USER_STORIES.md) | Product requirements and user stories | Product, developers |

---

## 💻 Development

Documentation for active development work.

### Core Development
| Document | Description | Last Updated |
|----------|-------------|--------------|
| [DOCKER_DEVELOPMENT.md](DOCKER_DEVELOPMENT.md) | Docker-based development environment | 2025-10 |
| [API.md](API.md) | REST API reference and patterns | 2025-10 |
| [API_QUICKSTART.md](API_QUICKSTART.md) | Quick API usage examples | 2025-10 |
| [BACKEND_DEBUG.md](BACKEND_DEBUG.md) | Backend debugging guide | 2025-10 |

### Architecture
| Document | Description | Notes |
|----------|-------------|-------|
| [DATETIME_ARCHITECTURE.md](DATETIME_ARCHITECTURE.md) | Timezone handling architecture | Critical for scheduling |
| [MULTI_ORG_LIMITATIONS.md](MULTI_ORG_LIMITATIONS.md) | Multi-tenancy constraints | Important for SaaS |
| [WORKSPACE_ORGANIZATION.md](WORKSPACE_ORGANIZATION.md) | Code organization patterns | Best practices |

---

## 🧪 Testing

Comprehensive testing documentation.

### E2E Testing (Primary)
| Document | Description | Status |
|----------|-------------|--------|
| E2E_TEST_COVERAGE_ANALYSIS.md (historical file unavailable) | Coverage analysis and gaps | Historical/unavailable |
| E2E_GUI_TEST_COVERAGE_REPORT.md (historical file unavailable) | GUI-specific coverage | Historical/unavailable |
| E2E_TEST_GAP_ANALYSIS.md (historical file unavailable) | Identified testing gaps | Historical/unavailable |
| E2E_TESTING.md (historical file unavailable) | E2E testing guide | Historical/unavailable |
| E2E_TESTING_CHECKLIST.md (historical file unavailable) | Testing checklist | Historical/unavailable |

### Test Strategy & Results
| Document | Description | Notes |
|----------|-------------|-------|
| [TEST_SUMMARY.md](TEST_SUMMARY.md) | Latest test results summary | ⚠️ See also TEST_STATUS.md |
| TEST_STATUS.md (historical file unavailable) | Current test suite status | Historical/unavailable |
| [TEST_STRATEGY.md](TEST_STRATEGY.md) | Overall testing strategy | Canonical reference |
| TESTING_STRATEGY.md (historical file unavailable) | Testing best practices | Historical/unavailable |
| [TEST_PERFORMANCE.md](TEST_PERFORMANCE.md) | Test performance optimization | Historical snapshot |
| [COMPREHENSIVE_TEST_SUITE.md](COMPREHENSIVE_TEST_SUITE.md) | Complete test suite overview | Historical snapshot |

**Note**: TEST_SUMMARY.md and TEST_STATUS.md should be consolidated.

---

## 🚀 Deployment & Infrastructure

Production deployment and infrastructure documentation.

| Document | Description | Status |
|----------|-------------|--------|
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) | Complete deployment guide | Historical snapshot |
| DEPLOYMENT.md (historical file unavailable) | Alternative deployment guide | Historical/unavailable |
| [DOCKER_DEVELOPMENT.md](DOCKER_DEVELOPMENT.md) | Docker setup (dev & prod) | Historical snapshot |
| [RATE_LIMITING.md](RATE_LIMITING.md) | Rate limiting implementation | ✅ Security feature |

**Recommendation**: Consolidate DEPLOYMENT.md into DEPLOYMENT_GUIDE.md

---

## ⚙️ Features & Implementation

Feature-specific implementation documentation.

### Core Features
| Document | Description | Status |
|----------|-------------|--------|
| ADMIN_CONSOLE_IMPLEMENTATION_REPORT.md (historical file unavailable) | Admin console implementation | Historical/unavailable |
| ADMIN_TABS_STRUCTURE.md (historical file unavailable) | Admin panel structure | Historical/unavailable |
| [EVENT_ROLES_FEATURE.md](EVENT_ROLES_FEATURE.md) | Event roles implementation | Historical snapshot |
| ONBOARDING_SYSTEM_COMPLETE.md (historical file unavailable) | User onboarding flow | Historical/unavailable |

### Advanced Features
| Document | Description | Status |
|----------|-------------|--------|
| FEATURE_019_SMS_IMPLEMENTATION_PROGRESS.md (historical file unavailable) | SMS notifications feature | Historical/unavailable |
| RECAPTCHA.md (historical file unavailable) | reCAPTCHA integration | Historical/unavailable |
| RECAPTCHA_TEST_RESULTS.md (historical file unavailable) | reCAPTCHA testing | Historical/unavailable |
| MAILTRAP_API_TESTING.md (historical file unavailable) | Email testing with Mailtrap | Historical/unavailable |
| LOCAL_EMAIL_SETUP.md (historical file unavailable) | Local email development | Historical/unavailable |

---

## 🔒 Security

Security implementation and audits.

| Document | Description | Status |
|----------|-------------|--------|
| [SECURITY.md](SECURITY.md) | Complete security documentation | Historical snapshot |
| SECURITY_ANALYSIS.md (historical file unavailable) | Security audit results | Historical/unavailable |
| [SECURITY_MIGRATION.md](SECURITY_MIGRATION.md) | JWT migration guide | Historical snapshot |
| [RBAC_IMPLEMENTATION_COMPLETE.md](RBAC_IMPLEMENTATION_COMPLETE.md) | Role-based access control | Historical snapshot |
| [RBAC_AUDIT.md](RBAC_AUDIT.md) | RBAC security audit | Historical snapshot |

---

## 💳 Billing & SaaS

SaaS readiness and billing implementation.

| Document | Description | Status |
|----------|-------------|--------|
| BILLING_SETUP.md (historical file unavailable) | Stripe billing setup | Historical/unavailable |
| BILLING_USER_GUIDE.md (historical file unavailable) | User-facing billing docs | Historical/unavailable |
| [SAAS_DESIGN.md](SAAS_DESIGN.md) | SaaS architecture | ✅ Design doc |
| SAAS_READINESS_SUMMARY.md (historical file unavailable) | SaaS readiness status | Historical/unavailable |
| SAAS_READINESS_GAP_ANALYSIS.md (historical file unavailable) | Detailed gap analysis | Historical/unavailable |

---

## 🌍 Internationalization

i18n implementation and status.

| Document | Description | Status |
|----------|-------------|--------|
| I18N_QUICK_START.md (historical file unavailable) | Quick i18n guide | Historical/unavailable |
| I18N_ANALYSIS.md (historical file unavailable) | i18n implementation analysis | Historical/unavailable |
| I18N_IMPLEMENTATION_STATUS.md (historical file unavailable) | Current i18n status | Historical/unavailable |

---

## 🛠️ Technical Debt & Refactoring

Code quality and refactoring documentation.

| Document | Description | Status |
|----------|-------------|--------|
| [TECHNICAL_DEBT.md](archive/TECHNICAL_DEBT.md) | Technical debt tracking | 📦 Archived 2026-05-14 (snapshot from 2025-10-15; recreate when needed) |
| [REFACTORING.md](REFACTORING.md) | Refactoring plans | ✅ Reference |
| REFACTORING_SUMMARY.md (historical file unavailable) | Completed refactorings | Historical/unavailable |
| [DEBUG_REFACTORING.md](DEBUG_REFACTORING.md) | Debug-related refactoring | Historical snapshot |
| SELF_HEALING_REPORT.md (historical file unavailable) | Self-healing system report | Historical/unavailable |

---

## 📊 Project Status & Roadmaps

Current status and future planning.

### Current Status
| Document | Description | Last Updated |
|----------|-------------|--------------|
| [FINAL_STATUS.md](FINAL_STATUS.md) | Overall project status | 2025-10 |
| [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md) | Feature completion status | 2025-10 |
| IMPLEMENTATION_SUMMARY.md (historical file unavailable) | Implementation summary | Historical/unavailable |
| [NEXT_STEPS.md](NEXT_STEPS.md) | Immediate next steps | 2025-10 |

### Roadmaps & Planning
| Document | Description | Status |
|----------|-------------|--------|
| [LAUNCH_ROADMAP.md](LAUNCH_ROADMAP.md) | Product launch roadmap | Historical snapshot |
| FEATURE_ROADMAP_ANALYSIS.md (historical file unavailable) | Feature prioritization | Historical/unavailable |
| [TESTING_ACTION_PLAN.md](TESTING_ACTION_PLAN.md) | Testing improvement plan | Historical snapshot |

### Gap Analysis
| Document | Description | Status |
|----------|-------------|--------|
| GAPS_ANALYSIS.md (historical file unavailable) | Feature gaps identified | Historical/unavailable |
| GAP_ANALYSIS_SUMMARY_2025-10-17.md (historical file unavailable) | Detailed gap analysis | Historical/unavailable |
| E2E_TEST_GAP_ANALYSIS.md (historical file unavailable) | E2E testing gaps | Historical/unavailable |

---

## 🗄️ Archive

Outdated or superseded documentation (kept for historical reference).

### Session Summaries
| Document | Date | Status |
|----------|------|--------|
| SESSION_2025-10-02_SUMMARY.md (historical file unavailable) | 2025-10-02 | Historical/unavailable |
| SESSION_SUMMARY_2025-10-20.md (historical file unavailable) | 2025-10-20 | Historical/unavailable |

### Outdated Test Docs
| Document | Note | Status |
|----------|------|--------|
| TEST_SUMMARY_OLD_2025-10-05.md (historical file unavailable) | Old version | Historical/unavailable |

### SpecKit (Future Enhancement)
| Document | Description | Status |
|----------|-------------|--------|
| [SPEC_KIT_SETUP.md](SPEC_KIT_SETUP.md) | SpecKit setup guide | 🔮 Future feature |
| [SPEC_KIT_PROGRESS.md](archive/SPEC_KIT_PROGRESS.md) | SpecKit progress tracking | 📦 Archived 2026-05-14 (superseded by per-sprint `specs/0XX-sprint-N-completion/`) |

### Archive Folder
Additional archived docs in [docs/archive/](archive/)

---

## 🔍 How to Find What You Need

### By Role

**New Developer**:
1. Start with [README.md](../README.md)
2. Read [QUICK_START.md](QUICK_START.md)
3. Review [CLAUDE.md](../CLAUDE.md) for project context
4. Check [DOCKER_DEVELOPMENT.md](DOCKER_DEVELOPMENT.md) for environment setup

**Frontend Developer**:
1. ADMIN_TABS_STRUCTURE.md (historical file unavailable) - UI structure
2. I18N_QUICK_START.md (historical file unavailable) - Internationalization
3. E2E_TESTING.md (historical file unavailable) - Testing guidelines

**Backend Developer**:
1. [API.md](API.md) - API reference
2. [SECURITY.md](SECURITY.md) - Security patterns
3. BILLING_SETUP.md (historical file unavailable) - Billing implementation

**DevOps Engineer**:
1. [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Deployment process
2. [DOCKER_DEVELOPMENT.md](DOCKER_DEVELOPMENT.md) - Docker setup
3. [RATE_LIMITING.md](RATE_LIMITING.md) - Infrastructure security

**QA Engineer**:
1. [TEST_STRATEGY.md](TEST_STRATEGY.md) - Testing approach
2. E2E_TEST_COVERAGE_ANALYSIS.md (historical file unavailable) - Coverage status
3. [TESTING_ACTION_PLAN.md](TESTING_ACTION_PLAN.md) - Testing priorities

**Product Manager**:
1. [USER_STORIES.md](USER_STORIES.md) - Product requirements
2. SAAS_READINESS_SUMMARY.md (historical file unavailable) - Launch readiness
3. [LAUNCH_ROADMAP.md](LAUNCH_ROADMAP.md) - Product roadmap
4. FEATURE_ROADMAP_ANALYSIS.md (historical file unavailable) - Feature priorities

### By Task

**Setting up development environment**: [QUICK_START.md](QUICK_START.md) → [DOCKER_DEVELOPMENT.md](DOCKER_DEVELOPMENT.md)

**Writing tests**: [TEST_STRATEGY.md](TEST_STRATEGY.md) → E2E_TESTING.md (historical file unavailable)

**Adding i18n translations**: I18N_QUICK_START.md (historical file unavailable)

**Implementing security features**: [SECURITY.md](SECURITY.md) → [RBAC_IMPLEMENTATION_COMPLETE.md](RBAC_IMPLEMENTATION_COMPLETE.md)

**Deploying to production**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

**Setting up billing**: BILLING_SETUP.md (historical file unavailable) → BILLING_USER_GUIDE.md (historical file unavailable)

---

## 📝 Documentation Standards

### Naming Convention
- Use SCREAMING_SNAKE_CASE for all doc filenames
- Include date in session summaries: `SESSION_YYYY-MM-DD_SUMMARY.md`
- Mark outdated docs with `_OLD` suffix before archiving

### File Organization
- Keep primary docs in `/docs`
- Move historical/outdated docs to `/docs/archive`
- Update this index when adding/removing docs

### Best Practices
- Always include "Last Updated" date in doc headers
- Link to related docs for cross-referencing
- Keep docs focused on single topics
- Consolidate duplicates rather than creating new versions

---

## 🔄 Maintenance

### Regular Updates Needed
- TEST_STATUS.md (historical file unavailable) - After each test run
- [NEXT_STEPS.md](NEXT_STEPS.md) - Weekly or after major milestones
- SAAS_READINESS_SUMMARY.md (historical file unavailable) - Monthly
- This INDEX.md - Whenever docs are added/removed

### Consolidation Candidates
1. ⚠️ TEST_SUMMARY.md + TEST_STATUS.md → Consolidate into single TEST_STATUS.md
2. ⚠️ DEPLOYMENT.md + DEPLOYMENT_GUIDE.md → Keep DEPLOYMENT_GUIDE.md only
3. ⚠️ TEST_STRATEGY.md + TESTING_STRATEGY.md → Consolidate into TEST_STRATEGY.md
4. ⚠️ API.md + API_README.md + API_QUICKSTART.md → Organize as API/ subdirectory

### Archive Candidates
- Session summaries older than 30 days
- Old test summaries with _OLD suffix
- Superseded implementation reports

---

**Maintained by**: Claude Code
**Last Review**: 2025-10-27
**Next Review Due**: 2025-11-27
