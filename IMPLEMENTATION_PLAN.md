# Implementation Plan

> Auto-generated breakdown of specs into tasks using the Ralph Wiggum framework.

## 🚀 Active Spec: 000-user-onboarding
**Goal:** Guide new admins through organization setup in < 15 minutes.

- [x] [HIGH] Implement backend `OnboardingService` for state tracking
- [x] [HIGH] Hook `OnboardingService` into FastAPI router
- [x] [HIGH] Create `/wizard` route in frontend SPA
- [x] [HIGH] Add i18n translation files for 6 languages
- [/] [HIGH] Implement Step 1 (Org Profile) auto-launch logic
- [ ] [HIGH] Implement Step 2 (First Event) form & persistence
- [ ] [HIGH] Implement Step 3 (First Team) form & persistence
- [ ] [HIGH] Implement Step 4 (Invite Volunteers) form & persistence
- [ ] [MEDIUM] Implement "Sample Data" generation toggle
- [ ] [MEDIUM] Implement onboarding checklist on dashboard

## 📋 Next Priorities

- [ ] [HIGH] Spec 001-email-notifications: Implement core assignment notifications (Safe Mode)
- [ ] [HIGH] Spec 019-sms-notifications: Implement core SMS notifications (Safe Mode)
- [ ] [MEDIUM] Spec 016-recurring-events-ui: Build UI for repeating schedule patterns
- [ ] [MEDIUM] Spec 017-manual-schedule-editing: Implement drag-and-drop schedule adjustments

## ✅ Completed

- [x] [P0] Spec 000-safety-verification: Disable real mail/sms/billing in development.
