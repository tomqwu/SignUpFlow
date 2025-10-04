# Rostio - Modern Volunteer Scheduling & Roster Management

A comprehensive SaaS platform for managing volunteer schedules, events, and team assignments with advanced features like RBAC, user invitations, and calendar integration.

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
- ✅ **User Invitation System** - Invite volunteers via email with secure tokens
- ✅ **ICS Calendar Export** - Export schedules to Google Calendar, Apple Calendar, Outlook
- ✅ **Live Calendar Subscription** - Auto-updating calendar feeds (webcal://)
- ✅ **Tabbed Admin Console** - Organized management interface
- ✅ **Timezone Support** - User-specific timezone preferences
- ✅ **Enhanced RBAC** - Granular permissions and invitation workflows

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

```bash
# Clone the repository
git clone https://github.com/yourusername/rostio.git
cd rostio

# Install dependencies
poetry install

# Run database migrations
poetry run python migrate_timezone.py
poetry run python migrate_invitations.py

# Start the server
poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Visit `http://localhost:8000` to access the application.

### Default Admin Account
- **Email:** jane@test.com
- **Password:** password

---

## 🧪 Testing

### Run All Tests

```bash
# Run all tests
poetry run pytest tests/ -v

# Run specific test suites
poetry run pytest tests/unit/ -v                    # Unit tests
poetry run pytest tests/integration/ -v            # Integration tests

# Run new feature tests
poetry run pytest tests/integration/test_invitations.py -v     # Invitation tests (16)
poetry run pytest tests/unit/test_calendar.py -v              # Calendar tests (18)
```

### Test Coverage

- **97 tests passing** (100% pass rate)
- **34 new feature tests** (invitations + calendar export)
- **63 core API tests** (organizations, people, teams, events, availability)
- **Runtime:** ~4 seconds

See [TEST_RESULTS.md](docs/TEST_RESULTS.md) for detailed test results.

---

## 📚 API Documentation

### Interactive API Docs
Visit `http://localhost:8000/docs` for Swagger UI documentation.

### Key Endpoints

#### Authentication
- `POST /api/auth/signup` - Create new user account
- `POST /api/auth/login` - User login

#### Invitations (NEW)
- `POST /api/invitations` - Create invitation (admin only)
- `GET /api/invitations` - List invitations (admin only)
- `GET /api/invitations/{token}` - Verify invitation token
- `POST /api/invitations/{token}/accept` - Accept invitation
- `DELETE /api/invitations/{id}` - Cancel invitation (admin only)
- `POST /api/invitations/{id}/resend` - Resend invitation (admin only)

#### Calendar Export (NEW)
- `GET /api/calendar/export` - Download personal schedule as ICS
- `GET /api/calendar/subscribe` - Get webcal:// subscription URL
- `POST /api/calendar/reset-token` - Reset subscription token
- `GET /api/calendar/org/export` - Export org events (admin only)
- `GET /api/calendar/feed/{token}` - Public calendar feed

---

## 📊 Documentation

- [SAAS_DESIGN.md](docs/SAAS_DESIGN.md) - Comprehensive SaaS design with user stories
- [IMPLEMENTATION_COMPLETE.md](docs/IMPLEMENTATION_COMPLETE.md) - Implementation details
- [TEST_RESULTS.md](docs/TEST_RESULTS.md) - Test coverage and results
- [DATETIME_ARCHITECTURE.md](docs/DATETIME_ARCHITECTURE.md) - Timezone implementation

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
