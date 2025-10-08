# Rostio - Modern Volunteer Scheduling & Roster Management

A comprehensive SaaS platform for managing volunteer schedules, events, and team assignments with advanced features like JWT authentication, RBAC, user invitations, and calendar integration.

[![Tests](https://img.shields.io/badge/tests-344%20passing-brightgreen)](TEST_REPORT.md)
[![Security](https://img.shields.io/badge/security-JWT%20%2B%20bcrypt-blue)](docs/SECURITY_ANALYSIS.md)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

![Dashboard](docs/screenshots/01-dashboard-home.png)

## 🌟 Features

### Core Functionality
- **Smart Schedule Generation** - Automated scheduling with constraint solving
- **Event Management** - Create, manage, and track events with role requirements
- **Availability Tracking** - Manage volunteer availability and time-off/blocked dates
- **Role-Based Access Control (RBAC)** - Secure permissions for admins and volunteers
- **Calendar Integration** - ICS export and live calendar subscriptions
- **PDF Reports** - Professional schedule exports

### New Features (2025)
- ✅ **JWT Authentication** - Industry-standard Bearer token authentication with 24-hour expiration
- ✅ **Bcrypt Password Hashing** - Secure password storage with automatic salting
- ✅ **Protected API Endpoints** - Authentication middleware for sensitive operations
- ✅ **User Invitation System** - Invite volunteers via email with secure tokens
- ✅ **ICS Calendar Export** - Export schedules to Google Calendar, Apple Calendar, Outlook
- ✅ **Live Calendar Subscription** - Auto-updating calendar feeds (webcal://)
- ✅ **Tabbed Admin Console** - Organized management interface with 5 tabs
- ✅ **Timezone Support** - User-specific timezone preferences
- ✅ **Enhanced RBAC** - Granular permissions and invitation workflows
- ✅ **Role Management** - Edit roles, manage people assignments, and edit individual roles
- ✅ **Blocked Dates with Reasons** - Track time-off with optional reasons
- ✅ **Internationalization (i18n)** - Multi-language support (English, Spanish, Chinese)

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - High-performance async Python web framework
- **SQLAlchemy** - SQL ORM with SQLite database
- **Pydantic** - Data validation and settings management
- **python-jose** - JWT token encoding/decoding (HS256)
- **passlib + bcrypt** - Secure password hashing
- **pytest** - Testing framework with async support

### Frontend
- **Vanilla JavaScript** - Zero dependencies, fast loading
- **SPA Router** - Client-side routing with browser history
- **i18n System** - Multi-language support (EN/ES/ZH)
- **LocalStorage** - Session management and JWT token storage
- **Fetch API** - RESTful API communication with Bearer auth
- **Jest** - Frontend testing framework

### Security
- **JWT Authentication** - Bearer token auth (24h expiration)
- **Bcrypt Password Hashing** - 12 rounds with automatic salting
- **HTTPBearer** - FastAPI security dependency injection
- **Token-based Calendar Feeds** - Secure public calendar subscriptions

---

## 📸 Screenshots

### Dashboard & User Views

#### Personal Dashboard
Clean, intuitive dashboard showing your schedule, assignments, and upcoming events.

![Dashboard](docs/screenshots/01-dashboard-home.png)

#### My Schedule
View all your assignments and export them to your calendar app.

![My Schedule](docs/screenshots/02-my-schedule.png)

### Admin Console

The admin console features a modern tabbed interface for efficient management:

#### Events Management
Create, edit, and manage all organizational events with role requirements.

![Admin Events](docs/screenshots/03-admin-events.png)

#### Roles Management
Define and manage organizational roles with statistics and usage tracking.

![Admin Roles](docs/screenshots/04-admin-roles.png)

#### Schedule Management
Generate and manage schedules with AI-powered constraint solving.

![Admin Schedule](docs/screenshots/05-admin-schedule.png)

#### People & Invitations
Manage team members, send invitations, and track invitation status.

![Admin People](docs/screenshots/06-admin-people.png)

#### Reports & Analytics
Export schedules, view statistics, and generate reports.

![Admin Reports](docs/screenshots/07-admin-reports.png)

### Modals & Features

#### User Settings
Manage profile, roles, and timezone preferences.

![Settings Modal](docs/screenshots/08-settings-modal.png)

#### Invite Users
Send secure invitations to new volunteers with pre-assigned roles.

![Invite User Modal](docs/screenshots/09-invite-user-modal.png)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Poetry (Python package manager)
- SQLite (included)

### Installation

#### Quick Start (Using Makefile)

```bash
# Clone the repository
git clone https://github.com/yourusername/rostio.git
cd rostio

# One-command setup (install dependencies + run migrations)
make setup

# Start the server
make run
```

#### Manual Installation

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

Visit `http://localhost:8000` to access the application.

#### Available Make Commands

Run `make` or `make help` to see all available commands:

**Getting Started:**
- `make setup` - First-time setup (install + migrate)
- `make run` - Start development server

**Development:**
- `make stop` - Stop the server
- `make restart` - Restart the server
- `make install` - Install dependencies
- `make migrate` - Run migrations

**Testing:**
- `make test` - Run all tests
- `make test-coverage` - Generate coverage reports
- `make pre-commit` - Fast tests for pre-commit

**Maintenance:**
- `make clean` - Clean temp files
- `make clean-all` - Deep clean (removes dependencies)

### Default Admin Account
- **Email:** jane@test.com
- **Password:** password

### Environment Variables (Optional)

```bash
# Create .env file for production
SECRET_KEY=your-secret-key-here  # REQUIRED for production JWT signing
DATABASE_URL=sqlite:///./roster.db  # Default: SQLite
```

**⚠️ Security Note:** Change `SECRET_KEY` in production! See [SECURITY_MIGRATION.md](docs/SECURITY_MIGRATION.md)

---

## 🧪 Testing

### Run All Tests

```bash
# Run all tests (294 tests)
poetry run pytest tests/ -v

# Run specific test suites
poetry run pytest tests/unit/ -v                    # Unit tests (158)
poetry run pytest tests/integration/ -v             # Integration tests (129)
poetry run pytest tests/security/ -v                # Security tests (7)

# Frontend tests (50)
npm test

# Run feature-specific tests
poetry run pytest tests/security/test_authentication.py -v     # JWT & bcrypt (7)
poetry run pytest tests/integration/test_invitations.py -v     # Invitations (16)
poetry run pytest tests/unit/test_calendar.py -v               # Calendar export (18)
poetry run pytest tests/unit/test_security.py -v               # Password hashing (26)
```

### Test Coverage

- **294 backend tests passing** (100% pass rate)
- **50 frontend tests passing** (100% pass rate)
- **158 unit tests** - Core API functionality
- **129 integration tests** - End-to-end workflows
- **7 security tests** - JWT authentication & bcrypt
- **Runtime:** Backend ~10s, Frontend ~0.4s

#### Key Test Files
- [test_authentication.py](tests/security/test_authentication.py) - JWT token auth, bcrypt hashing
- [test_invitations.py](tests/integration/test_invitations.py) - Invitation workflows
- [test_calendar.py](tests/unit/test_calendar.py) - ICS export & webcal subscriptions
- [test_security.py](tests/unit/test_security.py) - Password hashing & token generation
- [test_api_complete.py](tests/integration/test_api_complete.py) - Full API coverage

See [TEST_REPORT.md](TEST_REPORT.md) for detailed test results.

---

## 📚 API Documentation

### Interactive API Docs
Visit `http://localhost:8000/docs` for Swagger UI documentation.

### Key Endpoints

#### Authentication & Security
- `POST /api/auth/signup` - Create new user account (returns JWT token)
- `POST /api/auth/login` - User login (returns JWT token)
- `GET /api/people/me` - Get current authenticated user (requires Bearer token)
- `PUT /api/people/me` - Update current user profile (requires Bearer token)

**Security Features:**
- All authenticated endpoints require `Authorization: Bearer {token}` header
- JWT tokens expire after 24 hours
- Passwords hashed with bcrypt (12 rounds)
- See [SECURITY_MIGRATION.md](docs/SECURITY_MIGRATION.md) for details

#### Invitations
- `POST /api/invitations` - Create invitation (admin only)
- `GET /api/invitations` - List invitations (admin only)
- `GET /api/invitations/{token}` - Verify invitation token
- `POST /api/invitations/{token}/accept` - Accept invitation
- `DELETE /api/invitations/{id}` - Cancel invitation (admin only)
- `POST /api/invitations/{id}/resend` - Resend invitation (admin only)

#### Calendar Export
- `GET /api/calendar/export` - Download personal schedule as ICS (requires auth)
- `GET /api/calendar/subscribe` - Get webcal:// subscription URL (requires auth)
- `POST /api/calendar/reset-token` - Reset subscription token (requires auth)
- `GET /api/calendar/org/export` - Export org events (admin only, requires auth)
- `GET /api/calendar/feed/{token}` - Public calendar feed (token-based, no auth required)

---

## 📊 Documentation

### Core Documentation
- [SAAS_DESIGN.md](docs/SAAS_DESIGN.md) - Comprehensive SaaS design with user stories
- [IMPLEMENTATION_COMPLETE.md](docs/IMPLEMENTATION_COMPLETE.md) - Implementation details
- [TEST_REPORT.md](TEST_REPORT.md) - Comprehensive test results (344 tests)

### Security Documentation
- [SECURITY_ANALYSIS.md](docs/SECURITY_ANALYSIS.md) - Security architecture and analysis
- [SECURITY_MIGRATION.md](docs/SECURITY_MIGRATION.md) - JWT & bcrypt migration guide

### Feature Documentation
- [DATETIME_ARCHITECTURE.md](docs/DATETIME_ARCHITECTURE.md) - Timezone implementation
- [Calendar Export Guide](docs/) - ICS export and webcal subscription setup

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Write tests for all new features
- Follow existing code style
- Update documentation
- Ensure all tests pass: `poetry run pytest`

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Made with ❤️ by the Rostio Team**

*Simplifying volunteer scheduling for organizations worldwide*
