<div align="center">

# 🎯 Rostio

### Modern Volunteer Scheduling & Roster Management

*AI-powered scheduling for churches, non-profits, and organizations*

[![Tests](https://img.shields.io/badge/tests-344%20passing-brightgreen?style=for-the-badge)](TEST_REPORT.md)
[![Coverage](https://img.shields.io/badge/coverage-100%25-success?style=for-the-badge)](TEST_REPORT.md)
[![Security](https://img.shields.io/badge/security-JWT%20%2B%20bcrypt-blue?style=for-the-badge&logo=security)](docs/SECURITY_ANALYSIS.md)
[![Python](https://img.shields.io/badge/python-3.11+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](LICENSE)

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Roadmap](#-product-roadmap) • [Contributing](#-contributing)

<img src="docs/screenshots/01-dashboard-home.png" alt="Rostio Dashboard" width="800">

</div>

---

## 🌟 Features

<table>
<tr>
<td width="50%">

### 🤖 Smart Scheduling
- **AI-Powered Constraint Solver** - Automatically generate optimal schedules
- **Conflict Detection** - Prevent double-booking and overloading
- **Manual Editing** - Fine-tune AI-generated schedules
- **Recurring Events** - Set up repeating services and events

### 📅 Event Management
- **Flexible Event Types** - Worship services, meetings, classes
- **Role Requirements** - Define needed positions per event
- **Multi-location Support** - Manage multiple venues
- **Timezone Aware** - Handle global teams seamlessly

### 👥 Volunteer Management
- **Availability Tracking** - Volunteers set their own schedules
- **Time-off Requests** - Manage blocked dates with reasons
- **Role Assignment** - Assign multiple roles per person
- **Invitation System** - Secure email invitations with tokens

</td>
<td width="50%">

### 🔐 Enterprise Security
- **JWT Authentication** - Industry-standard Bearer token auth
- **Bcrypt Password Hashing** - 12 rounds with auto-salting
- **RBAC Permissions** - Granular admin/volunteer access
- **Audit Logging** - Track all changes (coming soon)

### 📧 Communication
- **Email Notifications** - Assignment alerts (coming soon)
- **Calendar Integration** - ICS export + live webcal sync
- **Multi-language Support** - EN, ES, PT, ZH-CN, ZH-TW
- **SMS Notifications** - Text reminders (coming soon)

### 📊 Analytics & Reports
- **PDF Export** - Print-ready schedules
- **Usage Statistics** - Track volunteer participation
- **Coverage Reports** - Identify gaps in scheduling
- **Custom Dashboards** - Real-time insights

</td>
</tr>
</table>

---

## 🎨 Beautiful, Modern UI

<div align="center">

### Intuitive Dashboard
<img src="docs/screenshots/01-dashboard-home.png" alt="Dashboard" width="700">

### Powerful Admin Console
<img src="docs/screenshots/03-admin-events.png" alt="Admin Console" width="700">

### Mobile Responsive
<img src="docs/screenshots/08-settings-modal.png" alt="Settings Modal" width="350">

</div>

---

## 🚀 Quick Start

### Prerequisites

```bash
Python 3.11+ | Poetry | SQLite
```

### One-Command Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/rostio.git
cd rostio

# Install and setup (using Makefile)
make setup

# Start the server
make run

# Visit http://localhost:8000
```

### Manual Installation

```bash
# Install dependencies
poetry install
npm install

# Run database migrations
poetry run python migrate_timezone.py
poetry run python migrate_invitations.py

# Start the server
poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Default Admin Login

```
Email: jane@test.com
Password: password
```

---

## 🛠️ Tech Stack

<div align="center">

| Category | Technologies |
|----------|-------------|
| **Backend** | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white) ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat&logoColor=white) ![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=flat&logoColor=white) |
| **Frontend** | ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black) ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat&logo=css3&logoColor=white) |
| **Security** | ![JWT](https://img.shields.io/badge/JWT-000000?style=flat&logo=jsonwebtokens&logoColor=white) ![Bcrypt](https://img.shields.io/badge/Bcrypt-005571?style=flat&logoColor=white) |
| **Testing** | ![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=flat&logo=pytest&logoColor=white) ![Jest](https://img.shields.io/badge/Jest-C21325?style=flat&logo=jest&logoColor=white) ![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=flat&logo=playwright&logoColor=white) |
| **Database** | ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white) (production) |

</div>

---

## 🧪 Testing

### Test Coverage: 344 Tests, 100% Pass Rate

```bash
# Quick test (pre-commit)
make test

# Full test suite (backend + frontend + E2E)
make test-all
```

<details>
<summary><b>📊 Test Breakdown</b></summary>

| Type | Count | Coverage | Runtime |
|------|-------|----------|---------|
| 🔧 Unit Tests | 158 | Core logic, models, utilities | ~10s |
| 🔗 Integration Tests | 129 | API endpoints, workflows | ~8s |
| 🔐 Security Tests | 7 | JWT auth, bcrypt hashing | ~2s |
| 💻 Frontend Tests | 50 | JS logic, i18n, router | ~0.4s |
| 🌐 E2E Tests | 15+ | Full user workflows, UI | ~30s |

**Key Test Files:**
- [test_auth_flows.py](tests/e2e/test_auth_flows.py) - Authentication workflows
- [test_authentication.py](tests/security/test_authentication.py) - Security
- [test_invitations.py](tests/integration/test_invitations.py) - User invitations
- [test_calendar.py](tests/unit/test_calendar.py) - Calendar export
- [test_admin_console.py](tests/e2e/test_admin_console.py) - Admin features

See [TEST_REPORT.md](TEST_REPORT.md) for detailed results.

</details>

---

## 📚 Documentation

<div align="center">

| Document | Description |
|----------|-------------|
| 📖 [Product Roadmap](PRODUCT_ROADMAP_INDEX.md) | 6-week launch plan & pricing strategy |
| 🎯 [SaaS Readiness](docs/SAAS_READINESS_SUMMARY.md) | Gap analysis & launch timeline |
| 🏗️ [Launch Roadmap](docs/LAUNCH_ROADMAP.md) | Week-by-week implementation plan |
| 🔒 [Security Guide](docs/SECURITY_MIGRATION.md) | JWT, bcrypt, best practices |
| 🌐 [API Documentation](http://localhost:8000/docs) | Interactive Swagger UI |
| 🧪 [Test Coverage](TEST_REPORT.md) | Comprehensive test results |
| 🌍 [i18n Guide](docs/I18N_QUICK_START.md) | Multi-language setup |

</div>

---

## 🗺️ Product Roadmap

<div align="center">

### 🎯 Current Status: 80% SaaS Ready

```
Core Product:        ████████████████████  100% ✅
Security:            ████████████░░░░░░░░   60% ⚠️
Infrastructure:      ████░░░░░░░░░░░░░░░░   20% ⏳
Pricing/Billing:     ░░░░░░░░░░░░░░░░░░░░    0% 🔜
Email:               ░░░░░░░░░░░░░░░░░░░░    0% 🔜
```

### 📅 6-Week Launch Plan

| Week | Phase | Status |
|------|-------|--------|
| 1-2 | 💰 Billing System (Stripe) | 🔜 Planned |
| 3 | 📧 Email Infrastructure (SendGrid) | 🔜 Planned |
| 4-5 | 🐳 Production Deployment (Docker + PostgreSQL) | 🔜 Planned |
| 6 | 🔒 Security & Monitoring | 🔜 Planned |
| **6** | **🚀 LAUNCH READY** | **🎯 Target** |

### 💰 Pricing Model (Planned)

| Plan | Price | Volunteers | Features |
|------|-------|-----------|----------|
| 🆓 **Free** | $0/mo | 10 | Basic scheduling, 5 emails/month |
| ⭐ **Starter** | $29/mo | 50 | AI scheduling, unlimited emails, calendar export |
| 💼 **Pro** | $99/mo | 200 | Multi-org, SMS, priority support, analytics |
| 🏢 **Enterprise** | Custom | Unlimited | White-label, SSO, dedicated support, SLA |

**Break-even:** 7-10 customers | **Target:** 100 signups, 10 paid customers (90 days)

📖 **Full Details:** See [PRODUCT_ROADMAP_INDEX.md](PRODUCT_ROADMAP_INDEX.md)

</div>

---

## 🎯 Key Endpoints

### Authentication
```http
POST /api/auth/signup      # Create account (returns JWT)
POST /api/auth/login       # Login (returns JWT)
GET  /api/people/me        # Get current user (requires auth)
PUT  /api/people/me        # Update profile (requires auth)
```

### Invitations
```http
POST   /api/invitations              # Create invitation (admin)
GET    /api/invitations              # List invitations (admin)
POST   /api/invitations/{token}/accept # Accept invitation
DELETE /api/invitations/{id}         # Cancel invitation (admin)
```

### Calendar Export
```http
GET  /api/calendar/export           # Download ICS file (auth)
GET  /api/calendar/subscribe        # Get webcal URL (auth)
GET  /api/calendar/feed/{token}     # Public calendar feed
POST /api/calendar/reset-token      # Reset subscription token (auth)
```

**Interactive Docs:** Visit `http://localhost:8000/docs`

---

## 🎨 Screenshots

<details>
<summary><b>📸 View All Screenshots</b></summary>

### Dashboard & User Views

#### Personal Dashboard
<img src="docs/screenshots/01-dashboard-home.png" alt="Dashboard" width="600">

#### My Schedule
<img src="docs/screenshots/02-my-schedule.png" alt="My Schedule" width="600">

### Admin Console

#### Events Management
<img src="docs/screenshots/03-admin-events.png" alt="Admin Events" width="600">

#### Roles Management
<img src="docs/screenshots/04-admin-roles.png" alt="Admin Roles" width="600">

#### Schedule Management
<img src="docs/screenshots/05-admin-schedule.png" alt="Admin Schedule" width="600">

#### People & Invitations
<img src="docs/screenshots/06-admin-people.png" alt="Admin People" width="600">

#### Reports & Analytics
<img src="docs/screenshots/07-admin-reports.png" alt="Admin Reports" width="600">

### Modals & Features

#### Settings Modal
<img src="docs/screenshots/08-settings-modal.png" alt="Settings" width="400">

#### Invite User Modal
<img src="docs/screenshots/09-invite-user-modal.png" alt="Invite User" width="400">

</details>

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. 🍴 **Fork** the repository
2. 🌿 **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. ✅ **Write** tests for your changes
4. 📝 **Commit** your changes: `git commit -m 'Add amazing feature'`
5. 📤 **Push** to the branch: `git push origin feature/amazing-feature`
6. 🎉 **Open** a Pull Request

### Development Guidelines

- ✅ Write tests for all new features (maintain 100% pass rate)
- 📚 Update documentation for user-facing changes
- 🎨 Follow existing code style and patterns
- 🔒 Security-first mindset (no hardcoded secrets)
- 🌍 Support internationalization (add translations)

---

## 🌍 Community & Support

<div align="center">

### Get Help

[![Discord](https://img.shields.io/badge/Discord-Join%20Chat-7289DA?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/rostio)
[![GitHub Issues](https://img.shields.io/badge/GitHub-Issues-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/yourusername/rostio/issues)
[![Documentation](https://img.shields.io/badge/Docs-Read-blue?style=for-the-badge&logo=read-the-docs&logoColor=white)](docs/)

### Stay Updated

[![Twitter](https://img.shields.io/badge/Twitter-Follow-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://twitter.com/rostio_app)
[![Blog](https://img.shields.io/badge/Blog-Latest-orange?style=for-the-badge&logo=rss&logoColor=white)](https://blog.rostio.com)

</div>

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

## ⭐ Star Us!

If Rostio helps your organization, please consider starring the repo to show your support!

[![Star on GitHub](https://img.shields.io/github/stars/yourusername/rostio?style=social)](https://github.com/yourusername/rostio)

---

**Made with ❤️ by the Rostio Team**

*Simplifying volunteer scheduling for organizations worldwide*

[Report Bug](https://github.com/yourusername/rostio/issues) • [Request Feature](https://github.com/yourusername/rostio/issues) • [View Roadmap](PRODUCT_ROADMAP_INDEX.md)

</div>
