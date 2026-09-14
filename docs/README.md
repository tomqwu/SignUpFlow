# SignUpFlow Documentation Index

> This is a historical catalog with unavailable links, not the current index.
> Start with [the maintained index](INDEX.md), [production roadmap](ROADMAP.md),
> [local testing](TESTING.md), and [local code review](ai-pr-review.md).
> No CI checks: all review and validation run locally. Older instructions below
> do not override that policy or establish production readiness.

**Last Updated:** 2025-10-22

This directory contains all project documentation organized by category.

## 📚 Quick Navigation

### Getting Started
- [Quick Start Guide](QUICK_START.md) - Setup and installation (if exists)
- [API Quickstart](API_QUICKSTART.md) - API usage examples
- [API Documentation](API.md) - Complete API reference
- [Local Email Capture](LOCAL_EMAIL_CAPTURE.md) - Test transactional flows without a provider
- [External Email Smoke Testing](saas/SMOKE_TESTING_EMAIL.md) - Authorized provider checks

### Architecture & Design
- [Admin Console Structure](ADMIN_TABS_STRUCTURE.md) - Admin UI architecture
- [DateTime Architecture](DATETIME_ARCHITECTURE.md) - Timezone handling design
- [Event Roles Feature](EVENT_ROLES_FEATURE.md) - Role-based scheduling

### Testing
- [E2E Testing Guide](E2E_TESTING.md) - End-to-end browser testing
- [E2E Testing Checklist](E2E_TESTING_CHECKLIST.md) - Test coverage checklist
- [E2E Test Coverage Analysis](E2E_TEST_COVERAGE_ANALYSIS.md) - Coverage breakdown
- [E2E GUI Test Coverage Report](E2E_GUI_TEST_COVERAGE_REPORT.md) - GUI test status
- [Comprehensive Test Suite](COMPREHENSIVE_TEST_SUITE.md) - Overall test strategy

### Internationalization (i18n)
- [i18n Quick Start](I18N_QUICK_START.md) - Adding translations
- [i18n Implementation Status](I18N_IMPLEMENTATION_STATUS.md) - Translation coverage
- [i18n Analysis](I18N_ANALYSIS.md) - Architecture and patterns

### Product & Business
- [Launch Roadmap](LAUNCH_ROADMAP.md) - 6-week launch plan
- [Feature Roadmap Analysis](FEATURE_ROADMAP_ANALYSIS.md) - Feature priorities
- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Production deployment
- [Gap Analysis Summary](GAP_ANALYSIS_SUMMARY_2025-10-17.md) - Feature gaps

### Development Guides
- [Backend Debug Guide](BACKEND_DEBUG.md) - Debugging backend issues
- [Debug Refactoring](DEBUG_REFACTORING.md) - Refactoring patterns

### Reports & Status (/docs/status/)
- [Implementation Status - Email Notifications](status/IMPLEMENTATION_STATUS_EMAIL_NOTIFICATIONS.md)
- [Implementation Status Report 2025-10-21](status/IMPLEMENTATION_STATUS_REPORT_2025-10-21.md)
- [MVP Implementation Summary](status/MVP_IMPLEMENTATION_SUMMARY.md)
- [Notification System MVP Complete](status/NOTIFICATION_SYSTEM_MVP_COMPLETE.md)
- [Test Execution Report 2025-10-21](status/TEST_EXECUTION_REPORT_2025-10-21.md)

### Session Notes (/docs/sessions/)
- [Session Summary](sessions/SESSION_SUMMARY.md) - Recent work summary

### Archived (/docs/archived/)
- [Codebase Feature Alignment Analysis](archived/CODEBASE_FEATURE_ALIGNMENT_ANALYSIS.md)

## 📖 Important Root Documentation

These critical documents remain in the project root:
- [CLAUDE.md](../CLAUDE.md) - AI assistant context (comprehensive)
- [CRITICAL_BUGS_FOUND.md](../CRITICAL_BUGS_FOUND.md) - Known critical bugs
- [NEXT_STEPS.md](../NEXT_STEPS.md) - Immediate priorities
- [README.md](../README.md) - Project overview
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines

## 🗂️ Directory Structure

```
docs/
├── README.md                    # This file (documentation index)
├── status/                      # Implementation status reports
│   ├── IMPLEMENTATION_STATUS_EMAIL_NOTIFICATIONS.md
│   ├── IMPLEMENTATION_STATUS_REPORT_2025-10-21.md
│   ├── MVP_IMPLEMENTATION_SUMMARY.md
│   ├── NOTIFICATION_SYSTEM_MVP_COMPLETE.md
│   └── TEST_EXECUTION_REPORT_2025-10-21.md
├── sessions/                    # Session summaries
│   └── SESSION_SUMMARY.md
├── archived/                    # Older/historical documents
│   └── CODEBASE_FEATURE_ALIGNMENT_ANALYSIS.md
├── API.md                       # API documentation
├── ADMIN_TABS_STRUCTURE.md      # Admin console architecture
├── DATETIME_ARCHITECTURE.md     # Timezone handling
├── E2E_TESTING.md              # E2E test guide
├── I18N_QUICK_START.md         # i18n guide
├── LAUNCH_ROADMAP.md           # Launch plan
└── ... (other documentation)
```

## 🔍 Finding Documentation

### By Topic

**Security & Authentication**
- See CLAUDE.md → "Security & Authentication" section

**RBAC (Role-Based Access Control)**
- See docs/ files mentioning "RBAC"

**Testing**
- See E2E_*.md files
- See COMPREHENSIVE_TEST_SUITE.md

**Internationalization**
- See I18N_*.md files

**Deployment**
- See DEPLOYMENT_GUIDE.md
- See LAUNCH_ROADMAP.md

### By Status

**Current Features**
- IMPLEMENTATION_COMPLETE.md (if exists)
- FINAL_STATUS.md

**Planned Features**
- FEATURE_ROADMAP_ANALYSIS.md
- GAPS_ANALYSIS.md

**Known Issues**
- ../CRITICAL_BUGS_FOUND.md (root directory)

## 📝 Documentation Standards

### File Naming
- Use UPPERCASE_WITH_UNDERSCORES.md for documentation
- Date-stamped files: `FILENAME_YYYY-MM-DD.md`
- Version-stamped files: `FILENAME_v1.2.3.md`

### Organization
- **Root docs/** - Current, actively used documentation
- **docs/status/** - Implementation status and progress reports
- **docs/sessions/** - Development session notes
- **docs/archived/** - Historical/outdated documentation

### When to Archive
Move documentation to `archived/` when:
- Information is outdated (>3 months old)
- Feature has been fully implemented and documented elsewhere
- Document replaced by newer version
- No longer referenced by active development

## 🔄 Maintenance

**Weekly:** Review and update status reports
**Monthly:** Archive outdated documentation
**Per Release:** Update IMPLEMENTATION_COMPLETE.md and FINAL_STATUS.md

## 📞 Need Help?

- Check [CLAUDE.md](../CLAUDE.md) first - comprehensive AI assistant context
- See [README.md](../README.md) for project overview
- Check [QUICK_START.md](QUICK_START.md) for setup issues
- Review [CRITICAL_BUGS_FOUND.md](../CRITICAL_BUGS_FOUND.md) for known issues

---

**Last Updated:** 2025-10-22
**Documentation Count:** 76 files
**Project:** SignUpFlow (formerly Rostio)
