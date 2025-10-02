# Rostio Screenshots

Visual guide to the Rostio team scheduling application.

## 🏠 Login & Onboarding

### Welcome Screen
![Welcome Screen](screenshots/01-welcome.png)

The initial onboarding screen where users can join an organization or login.

### Login
![Login Screen](screenshots/02-login.png)

Simple login with email and password.

---

## 📅 Main Application

### Calendar View
![Calendar View](screenshots/03-calendar.png)

See your upcoming assignments in an easy-to-read calendar format.

### Schedule List
![Schedule List](screenshots/04-schedule.png)

Detailed list view of all your assignments with dates and event types.

### No Assignments Yet
![No Assignments](screenshots/05-no-assignments.png)

Helpful message when you don't have any assignments yet, with explanations and links.

---

## ⚙️ User Features

### Settings Modal
![Settings](screenshots/06-settings.png)

Update your profile and select your roles using checkboxes.

### Time Off/Availability
![Availability](screenshots/07-availability.png)

Block out dates when you're unavailable to serve.

---

## 👨‍💼 Admin Panel

### Admin Dashboard
![Admin Dashboard](screenshots/08-admin-dashboard.png)

Manage people, teams, events, and run the scheduler.

### Event Creation
![Create Event](screenshots/09-create-event.png)

Create events with:
- Event type dropdown (Sunday Service, Bible Study, etc.)
- Recurrence options (once, daily, weekly, monthly)
- Role selection via checkboxes (not text input!)

### People Management
![People Management](screenshots/10-people.png)

View and manage all people in your organization.

### Schedule Solutions
![Solutions](screenshots/11-solutions.png)

View generated schedules with assignment counts and health scores.

---

## 📊 Key Features Shown

✅ **Automatic Role Detection** - Finds solutions with actual assignments  
✅ **Helpful Error Messages** - Tooltips and explanations when things are missing  
✅ **Role Checkboxes** - Select roles visually, not by typing  
✅ **Recurring Events** - Daily, weekly, monthly with end dates  
✅ **Clean UI** - Modern, responsive design  

---

## 🎯 How to Take Screenshots

If you need to update these screenshots:

1. Start the app: `./scripts/run_full_test_suite.sh`
2. Open: http://localhost:8000/
3. Login as: `sarah@grace.church` / `password123`
4. Take screenshots of each screen
5. Save to `docs/screenshots/` with appropriate names
6. Update this file if needed

---

## 📝 Notes

- Screenshots show the app with sample church volunteer data
- All features are functional and tested
- UI is responsive and works on mobile devices
