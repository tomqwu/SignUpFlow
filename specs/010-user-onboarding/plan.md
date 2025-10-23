# Implementation Plan: User Onboarding System

**Branch**: `010-user-onboarding` | **Date**: 2025-10-20 | **Spec**: [spec.md](./spec.md)

## Summary

Guided onboarding system for new organizations with step-by-step wizard (organization profile → first event → first team → volunteer invitations), sample data generation for hands-on exploration, getting started checklist (6 tasks with progress tracking), interactive tooltips/tutorials, progressive feature disclosure (unlock recurring events after 3 events, manual editing after first solver run, SMS after 5 volunteers), onboarding dashboard with quick-start videos and documentation links, and skip option for experienced users.

**Key Capabilities**:
- 4-step setup wizard with progress saving and resume capability
- Sample data generation (5 events, 3 teams, 10 volunteers) with "SAMPLE" badges and one-click cleanup
- Getting started checklist: Complete Profile, Create Event, Add Team, Invite Volunteers, Run Solver, View Reports
- Contextual tutorials with spotlight overlays (first event creation, team management, solver)
- Progressive unlocks: recurring events (3+ events), manual editing (first solver), SMS (5+ volunteers)
- Quick-start videos (2-3 minutes each): Getting Started, Creating Events, Managing Volunteers, Running Solver
- Skip onboarding option with re-enable capability

**Total Additional Infrastructure Cost**: $0/month (pure frontend + backend enhancements)

## Technical Context

**Language/Version**: Python 3.11+ (backend), Vanilla JavaScript (frontend)
**Primary Dependencies**:
- Intro.js OR custom tooltip library (tutorial overlays)
- Video.js OR YouTube embed (tutorial videos)

**Storage**: PostgreSQL 14+ (OnboardingProgress table - per-user progress tracking)
**Testing**: Pytest (API), Playwright (E2E wizard workflow)
**Performance Goals**: <500ms wizard step transition, <1s sample data generation, <200ms checklist update
**Constraints**:
- Wizard max 4 steps (avoid onboarding fatigue)
- Sample data clearly marked (prevent confusion with real data)
- Progressive unlocks optional (can be disabled for experienced users)
- Videos max 3 minutes (attention span optimization)

**User Experience Goals**:
- Time to first event: <5 minutes (wizard-guided)
- Checklist completion rate: >70% (industry standard)
- Tutorial completion rate: >50% (contextual learning)
- Skip onboarding usage: <20% (majority benefit from guidance)

## Constitution Check ✅ ALL GATES PASS

E2E tests verify wizard workflow, sample data generation/cleanup, checklist progress tracking, tutorial triggers. All other gates pass.

## Project Structure

```
api/
├── routers/onboarding.py           # Onboarding API
├── services/sample_data_generator.py # Sample data creation
├── models.py                       # OnboardingProgress

frontend/
├── js/
│   ├── onboarding-wizard.js        # Step-by-step wizard
│   ├── onboarding-checklist.js     # Progress tracking
│   ├── tutorial-overlays.js        # Intro.js integration
│   └── feature-unlocks.js          # Progressive disclosure
└── videos/                         # Tutorial videos (hosted)

tests/
└── e2e/test_onboarding_wizard.py   # Wizard E2E tests
```

---

**Status**: Streamlined plan complete
