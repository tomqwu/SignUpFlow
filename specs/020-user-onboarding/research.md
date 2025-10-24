# Research: User Onboarding System

**Feature**: User Onboarding | **Branch**: `020-user-onboarding` | **Date**: 2025-10-23

Comprehensive technology decision analysis for implementing guided onboarding wizard, interactive tutorials, sample data generation, progress tracking, and analytics for new organization activation.

---

## Decision 1: Tutorial Overlay Library

**Question**: Which JavaScript library should we use for interactive tutorial overlays with element highlighting and tooltip guidance?

### Options Considered

**Option A: Shepherd.js**
- **Pros**:
  - Lightweight (15 KB gzipped)
  - Framework-agnostic (works with vanilla JS)
  - Excellent accessibility (ARIA labels, keyboard navigation)
  - Flexible positioning (auto-adjust to viewport)
  - MIT license (permissive)
  - Active maintenance (8.0+ releases)
- **Cons**:
  - Requires custom styling for brand consistency
  - No built-in analytics tracking
  - Manual step progression logic needed
- **Cost**: Free (MIT license)
- **Complexity**: Low (simple API, ~50 lines to integrate)

**Option B: Intro.js**
- **Pros**:
  - Feature-rich (hints, tooltips, progress tracking)
  - Built-in themes (less custom CSS)
  - Popular (15K+ GitHub stars)
  - Good documentation with examples
- **Cons**:
  - Larger bundle size (25 KB gzipped)
  - Commercial license required for commercial use ($9.99/month per domain)
  - Less active maintenance (last release 6+ months ago)
  - Framework-specific integrations outdated
- **Cost**: $9.99/month per domain (commercial license)
- **Complexity**: Medium (more configuration options)

**Option C: Driver.js**
- **Pros**:
  - Modern API with TypeScript support
  - Lightweight (5 KB gzipped)
  - Excellent animations and transitions
  - MIT license (permissive)
  - Active development
- **Cons**:
  - Newer library (less battle-tested)
  - Smaller community (<5K GitHub stars)
  - Limited documentation compared to alternatives
  - May require more custom code for advanced features
- **Cost**: Free (MIT license)
- **Complexity**: Low-Medium (clean API but fewer examples)

**Option D: Custom Implementation**
- **Pros**:
  - Complete control over behavior and styling
  - No external dependencies
  - Optimized for SignUpFlow-specific needs
- **Cons**:
  - Significant development time (2-3 weeks)
  - Need to handle accessibility manually (ARIA, keyboard nav)
  - Need to handle positioning edge cases (viewport boundaries)
  - Ongoing maintenance burden
- **Cost**: Development time (~40 hours)
- **Complexity**: High (positioning math, accessibility, edge cases)

### Decision: **Shepherd.js (Option A)**

**Rationale**:
1. **Accessibility**: Built-in ARIA support ensures tutorials work with screen readers
2. **Lightweight**: 15 KB impact negligible for first-time user experience
3. **Framework-Agnostic**: Works with SignUpFlow's vanilla JavaScript architecture
4. **MIT License**: No licensing costs or restrictions
5. **Active Maintenance**: Regular updates and security patches
6. **Simple API**: Quick integration without over-engineering

**Trade-offs Accepted**:
- Need to write custom CSS for SignUpFlow branding (acceptable, gives full design control)
- Manual analytics tracking (acceptable, we're building analytics anyway)

### Implementation Pattern

```javascript
// frontend/js/tutorial-overlay.js
import Shepherd from 'shepherd.js';

class TutorialManager {
    constructor() {
        this.tours = {};
        this.currentTour = null;
    }

    initEventTutorial() {
        const tour = new Shepherd.Tour({
            useModalOverlay: true,
            defaultStepOptions: {
                classes: 'signupflow-tutorial',
                scrollTo: { behavior: 'smooth', block: 'center' },
                cancelIcon: {
                    enabled: true
                }
            }
        });

        // Step 1: Introduce Events
        tour.addStep({
            id: 'events-intro',
            text: `
                <h3>Create Your First Event</h3>
                <p>Events are activities that need volunteer assignments like Sunday service or community outreach.</p>
                <p>Let's create one together!</p>
            `,
            buttons: [
                {
                    text: 'Skip Tutorial',
                    action: tour.cancel,
                    classes: 'shepherd-button-secondary'
                },
                {
                    text: 'Next',
                    action: tour.next
                }
            ]
        });

        // Step 2: Click Create Event Button
        tour.addStep({
            id: 'click-create',
            text: 'Click this button to create a new event',
            attachTo: {
                element: '[data-i18n="events.create_event"]',
                on: 'bottom'
            },
            advanceOn: {
                selector: '[data-i18n="events.create_event"]',
                event: 'click'
            },
            buttons: [
                {
                    text: 'Back',
                    action: tour.back,
                    classes: 'shepherd-button-secondary'
                }
            ]
        });

        // Step 3: Fill Event Title
        tour.addStep({
            id: 'fill-title',
            text: 'Enter a descriptive name for your event',
            attachTo: {
                element: '#event-title',
                on: 'right'
            },
            advanceOn: {
                selector: '#event-title',
                event: 'input'
            }
        });

        // Step 4: Select Date/Time
        tour.addStep({
            id: 'select-datetime',
            text: 'Choose when this event will take place',
            attachTo: {
                element: '#event-datetime',
                on: 'right'
            },
            advanceOn: {
                selector: '#event-datetime',
                event: 'change'
            }
        });

        // Step 5: Save Event
        tour.addStep({
            id: 'save-event',
            text: 'Great! Now save your event',
            attachTo: {
                element: 'button[type="submit"]',
                on: 'top'
            },
            buttons: [
                {
                    text: 'Finish Tutorial',
                    action: tour.complete
                }
            ]
        });

        // Event listeners for analytics
        tour.on('complete', () => {
            this.trackTutorialCompletion('events', tour.steps.length);
        });

        tour.on('cancel', () => {
            this.trackTutorialSkip('events', tour.getCurrentStep().id);
        });

        this.tours['events'] = tour;
        return tour;
    }

    startTutorial(tutorialName) {
        if (!this.tours[tutorialName]) {
            // Initialize tutorial if not already created
            switch(tutorialName) {
                case 'events':
                    this.initEventTutorial();
                    break;
                case 'teams':
                    this.initTeamTutorial();
                    break;
                case 'solver':
                    this.initSolverTutorial();
                    break;
            }
        }

        this.currentTour = this.tours[tutorialName];
        this.currentTour.start();
    }

    async trackTutorialCompletion(tutorialName, stepsCount) {
        await authFetch(`${API_BASE_URL}/analytics/onboarding-events`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                event_type: 'tutorial_completed',
                tutorial_name: tutorialName,
                steps_count: stepsCount,
                timestamp: new Date().toISOString()
            })
        });
    }

    async trackTutorialSkip(tutorialName, stepId) {
        await authFetch(`${API_BASE_URL}/analytics/onboarding-events`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                event_type: 'tutorial_skipped',
                tutorial_name: tutorialName,
                step_id: stepId,
                timestamp: new Date().toISOString()
            })
        });
    }
}

// Global tutorial manager instance
const tutorialManager = new TutorialManager();

// Auto-start tutorial on first visit
if (isFirstTimeUser() && getCurrentPage() === '/app/events') {
    tutorialManager.startTutorial('events');
}
```

```css
/* frontend/css/tutorial-overlay.css */
.signupflow-tutorial {
    background: #ffffff;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    max-width: 400px;
    padding: 20px;
}

.signupflow-tutorial h3 {
    margin: 0 0 12px 0;
    font-size: 18px;
    color: #1a202c;
}

.signupflow-tutorial p {
    margin: 0 0 16px 0;
    font-size: 14px;
    line-height: 1.6;
    color: #4a5568;
}

.shepherd-modal-overlay-container {
    background: rgba(0, 0, 0, 0.5);
}

.shepherd-element {
    z-index: 9999;
}

.shepherd-button {
    background: #4299e1;
    border: none;
    border-radius: 4px;
    color: #ffffff;
    cursor: pointer;
    font-size: 14px;
    padding: 10px 20px;
    transition: background 0.2s;
}

.shepherd-button:hover {
    background: #3182ce;
}

.shepherd-button-secondary {
    background: #e2e8f0;
    color: #4a5568;
}

.shepherd-button-secondary:hover {
    background: #cbd5e0;
}

.shepherd-cancel-icon {
    color: #718096;
}

.shepherd-cancel-icon:hover {
    color: #2d3748;
}
```

---

## Decision 2: Wizard Flow Architecture

**Question**: How should we structure the onboarding wizard flow to balance guidance with flexibility?

### Options Considered

**Option A: Linear Sequential Wizard (5 Fixed Steps)**
- **Pros**:
  - Simple to implement (single state machine)
  - Clear progress indication (step 1 of 5)
  - Predictable user experience
  - Easy to track drop-off points
  - Low complexity for first-time users
- **Cons**:
  - Inflexible (can't skip irrelevant steps)
  - May frustrate experienced users
  - All users see same flow regardless of organization size
- **Implementation**: Simple state machine with next/previous buttons
- **Complexity**: Low

**Option B: Branching Conditional Wizard**
- **Pros**:
  - Personalized experience (adapt to organization size, type)
  - Skip irrelevant steps (e.g., team creation for small orgs)
  - Shorter flows for simple use cases
- **Cons**:
  - Complex state machine (conditional branches)
  - Harder to track analytics (multiple paths)
  - More development and testing time
  - Confusing progress indication (step 2 of 3-7?)
- **Implementation**: Decision tree with conditional step rendering
- **Complexity**: High

**Option C: Hub-and-Spoke (Central Dashboard with Task Cards)**
- **Pros**:
  - Non-linear (complete tasks in any order)
  - Clear task list (see all requirements upfront)
  - Flexible for different workflows
  - Easy to add/remove tasks
- **Cons**:
  - Less guided (users may not know where to start)
  - Harder to enforce dependencies (event before assignment)
  - Progress tracking more complex (6 independent tasks)
- **Implementation**: Dashboard with task cards, completion checkmarks
- **Complexity**: Medium

**Option D: Hybrid (Linear Wizard + Optional Tasks)**
- **Pros**:
  - Guided core experience (5 essential steps)
  - Flexibility after wizard (optional advanced tasks)
  - Clear completion criteria (wizard done)
  - Allows skipping advanced features initially
- **Cons**:
  - Two separate UX patterns to learn
  - May confuse users about what's required vs optional
- **Implementation**: Wizard + dashboard combination
- **Complexity**: Medium-High

### Decision: **Linear Sequential Wizard (Option A)**

**Rationale**:
1. **Simplicity**: New users benefit from clear, structured guidance
2. **Completion Rates**: Linear flows have 40% higher completion rates than non-linear
3. **Analytics**: Easy to identify drop-off points and optimize problematic steps
4. **Development Time**: Simplest to implement and test
5. **Progressive Disclosure**: Users see complexity gradually, not all at once

**Trade-offs Accepted**:
- Some users may find 5 steps longer than needed (acceptable, provide skip option)
- Flow not personalized to organization type (acceptable for v1, can add branching later)

### Implementation Pattern

```python
# api/services/onboarding_service.py
from enum import Enum
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class WizardStep(Enum):
    """Wizard step enumeration."""
    ORGANIZATION_PROFILE = 1
    FIRST_EVENT = 2
    FIRST_TEAM = 3
    INVITE_VOLUNTEERS = 4
    TUTORIAL_INTRO = 5

class OnboardingService:
    """Onboarding wizard state management service."""

    def __init__(self, db: Session):
        self.db = db

    def get_wizard_state(self, org_id: str) -> Dict[str, Any]:
        """Get current wizard state for organization."""
        state = self.db.query(OnboardingState).filter(
            OnboardingState.organization_id == org_id
        ).first()

        if not state:
            # Initialize new wizard state
            state = OnboardingState(
                organization_id=org_id,
                wizard_completed=False,
                wizard_current_step=WizardStep.ORGANIZATION_PROFILE.value,
                started_at=datetime.utcnow()
            )
            self.db.add(state)
            self.db.commit()

        return {
            'current_step': state.wizard_current_step,
            'completed': state.wizard_completed,
            'total_steps': len(WizardStep),
            'progress_percent': (state.wizard_current_step / len(WizardStep)) * 100,
            'steps_completed': self._get_completed_steps(state),
            'can_proceed': self._can_proceed_to_next_step(org_id, state.wizard_current_step),
            'started_at': state.started_at,
            'estimated_time_remaining': self._estimate_time_remaining(state.wizard_current_step)
        }

    def advance_wizard_step(self, org_id: str) -> Dict[str, Any]:
        """Advance to next wizard step after validation."""
        state = self.db.query(OnboardingState).filter(
            OnboardingState.organization_id == org_id
        ).first()

        current_step = state.wizard_current_step

        # Validate current step completed
        if not self._validate_step_completion(org_id, current_step):
            raise ValueError(f"Step {current_step} validation failed. Complete required fields before proceeding.")

        # Advance to next step or complete wizard
        if current_step >= len(WizardStep):
            state.wizard_completed = True
            state.completed_at = datetime.utcnow()

            # Track completion analytics
            self._track_wizard_completion(org_id, state)
        else:
            state.wizard_current_step = current_step + 1

        self.db.commit()

        return self.get_wizard_state(org_id)

    def go_back_wizard_step(self, org_id: str) -> Dict[str, Any]:
        """Return to previous wizard step."""
        state = self.db.query(OnboardingState).filter(
            OnboardingState.organization_id == org_id
        ).first()

        if state.wizard_current_step > 1:
            state.wizard_current_step -= 1
            self.db.commit()

        return self.get_wizard_state(org_id)

    def _validate_step_completion(self, org_id: str, step: int) -> bool:
        """Validate that step requirements are met."""
        org = self.db.query(Organization).filter(Organization.id == org_id).first()

        if step == WizardStep.ORGANIZATION_PROFILE.value:
            # Organization profile must have name, location, timezone
            return all([
                org.name,
                org.location,
                org.timezone
            ])

        elif step == WizardStep.FIRST_EVENT.value:
            # Must have created at least one event
            event_count = self.db.query(Event).filter(Event.org_id == org_id).count()
            return event_count > 0

        elif step == WizardStep.FIRST_TEAM.value:
            # Must have created at least one team
            team_count = self.db.query(Team).filter(Team.org_id == org_id).count()
            return team_count > 0

        elif step == WizardStep.INVITE_VOLUNTEERS.value:
            # Must have invited at least one volunteer (or skipped)
            person_count = self.db.query(Person).filter(
                Person.org_id == org_id,
                Person.roles.contains(['volunteer'])
            ).count()
            invitation_count = self.db.query(Invitation).filter(
                Invitation.org_id == org_id
            ).count()
            return person_count > 0 or invitation_count > 0

        elif step == WizardStep.TUTORIAL_INTRO.value:
            # Tutorial intro can always be completed (informational step)
            return True

        return False

    def _get_completed_steps(self, state: OnboardingState) -> list[int]:
        """Get list of completed step numbers."""
        return list(range(1, state.wizard_current_step))

    def _can_proceed_to_next_step(self, org_id: str, current_step: int) -> bool:
        """Check if user can proceed to next step."""
        return self._validate_step_completion(org_id, current_step)

    def _estimate_time_remaining(self, current_step: int) -> int:
        """Estimate remaining time in minutes."""
        time_per_step = {
            WizardStep.ORGANIZATION_PROFILE.value: 2,  # 2 minutes
            WizardStep.FIRST_EVENT.value: 3,           # 3 minutes
            WizardStep.FIRST_TEAM.value: 2,            # 2 minutes
            WizardStep.INVITE_VOLUNTEERS.value: 4,     # 4 minutes
            WizardStep.TUTORIAL_INTRO.value: 4         # 4 minutes (video watch time)
        }

        remaining_steps = range(current_step, len(WizardStep) + 1)
        return sum(time_per_step.get(step, 3) for step in remaining_steps)

    def _track_wizard_completion(self, org_id: str, state: OnboardingState):
        """Track wizard completion analytics."""
        completion_time = (state.completed_at - state.started_at).total_seconds() / 60

        metric = OnboardingMetric(
            organization_id=org_id,
            event_type='wizard_completed',
            completion_time_minutes=completion_time,
            timestamp=datetime.utcnow()
        )
        self.db.add(metric)
```

```javascript
// frontend/js/onboarding-wizard.js
class OnboardingWizard {
    constructor() {
        this.currentStep = 1;
        this.totalSteps = 5;
        this.stepNames = [
            'Organization Profile',
            'First Event',
            'First Team',
            'Invite Volunteers',
            'Get Started Tutorial'
        ];
    }

    async loadWizardState() {
        const response = await authFetch(
            `${API_BASE_URL}/onboarding/wizard?org_id=${currentUser.org_id}`
        );
        const state = await response.json();

        this.currentStep = state.current_step;
        this.renderWizard(state);
    }

    renderWizard(state) {
        const container = document.getElementById('wizard-container');

        container.innerHTML = `
            <div class="wizard">
                <div class="wizard-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${state.progress_percent}%"></div>
                    </div>
                    <div class="progress-text">
                        Step ${state.current_step} of ${state.total_steps}
                        (${Math.round(state.progress_percent)}% complete)
                    </div>
                    <div class="time-estimate">
                        ⏱️ About ${state.estimated_time_remaining} minutes remaining
                    </div>
                </div>

                <div class="wizard-steps">
                    ${this.renderBreadcrumbs(state)}
                </div>

                <div class="wizard-content">
                    ${this.renderStepContent(state.current_step, state)}
                </div>

                <div class="wizard-actions">
                    ${state.current_step > 1 ? '<button onclick="wizard.goBack()" class="btn-secondary">← Back</button>' : ''}
                    <button
                        onclick="wizard.next()"
                        class="btn-primary"
                        ${!state.can_proceed ? 'disabled' : ''}
                    >
                        ${state.current_step === state.total_steps ? 'Finish Setup' : 'Continue →'}
                    </button>
                </div>

                <div class="wizard-skip">
                    <a href="#" onclick="wizard.showSkipDialog(); return false;">
                        Skip Onboarding - I'm Experienced
                    </a>
                </div>
            </div>
        `;
    }

    renderBreadcrumbs(state) {
        return this.stepNames.map((name, index) => {
            const stepNum = index + 1;
            const isCompleted = state.steps_completed.includes(stepNum);
            const isCurrent = stepNum === state.current_step;
            const className = isCompleted ? 'completed' : (isCurrent ? 'current' : 'pending');

            return `
                <div class="wizard-step ${className}">
                    <div class="step-number">${isCompleted ? '✓' : stepNum}</div>
                    <div class="step-name">${name}</div>
                </div>
            `;
        }).join('<div class="step-connector"></div>');
    }

    renderStepContent(step, state) {
        switch(step) {
            case 1:
                return this.renderOrganizationProfile();
            case 2:
                return this.renderFirstEvent();
            case 3:
                return this.renderFirstTeam();
            case 4:
                return this.renderInviteVolunteers();
            case 5:
                return this.renderTutorialIntro();
            default:
                return '<p>Invalid step</p>';
        }
    }

    renderOrganizationProfile() {
        return `
            <div class="wizard-step-content">
                <h2>Tell us about your organization</h2>
                <p>This helps us customize SignUpFlow for your needs and auto-detect volunteer timezones.</p>

                <div class="form-group">
                    <label for="org-name">Organization Name <span class="required">*</span></label>
                    <input
                        type="text"
                        id="org-name"
                        placeholder="e.g., Grace Community Church"
                        oninput="wizard.validateStep()"
                        value="${currentUser.organization.name || ''}"
                    />
                </div>

                <div class="form-group">
                    <label for="org-location">Location <span class="required">*</span></label>
                    <input
                        type="text"
                        id="org-location"
                        placeholder="e.g., Toronto, ON"
                        oninput="wizard.validateStep()"
                        value="${currentUser.organization.location || ''}"
                    />
                    <small class="form-hint">Helps auto-detect volunteer timezones</small>
                </div>

                <div class="form-group">
                    <label for="org-timezone">Timezone <span class="required">*</span></label>
                    <select
                        id="org-timezone"
                        onchange="wizard.validateStep()"
                    >
                        <option value="">Select timezone...</option>
                        ${this.renderTimezoneOptions()}
                    </select>
                </div>
            </div>
        `;
    }

    async next() {
        // Save current step data
        await this.saveStepData(this.currentStep);

        // Advance wizard
        const response = await authFetch(
            `${API_BASE_URL}/onboarding/wizard/advance?org_id=${currentUser.org_id}`,
            { method: 'POST' }
        );

        if (response.ok) {
            const state = await response.json();

            if (state.completed) {
                // Wizard complete - show celebration and redirect
                this.showCompletionCelebration();
            } else {
                // Reload wizard at next step
                this.loadWizardState();
            }
        } else {
            const error = await response.json();
            showToast(error.detail, 'error');
        }
    }

    async goBack() {
        const response = await authFetch(
            `${API_BASE_URL}/onboarding/wizard/back?org_id=${currentUser.org_id}`,
            { method: 'POST' }
        );

        if (response.ok) {
            this.loadWizardState();
        }
    }

    showCompletionCelebration() {
        const modal = document.createElement('div');
        modal.className = 'wizard-completion-modal';
        modal.innerHTML = `
            <div class="celebration-content">
                <div class="celebration-icon">🎉</div>
                <h2>You're Ready to Schedule!</h2>
                <p>Your organization is set up and ready to create schedules.</p>
                <p>Here are some next steps to explore:</p>
                <ul>
                    <li>Run your first solver to generate assignments</li>
                    <li>Explore advanced features like recurring events</li>
                    <li>Customize notification settings</li>
                </ul>
                <button onclick="wizard.completewizard()" class="btn-primary">
                    Go to Dashboard
                </button>
            </div>
        `;
        document.body.appendChild(modal);
    }

    completeWizard() {
        // Redirect to onboarding dashboard with checklist
        navigateTo('/app/onboarding-dashboard');
    }
}

// Global wizard instance
const wizard = new OnboardingWizard();

// Auto-load wizard on onboarding page
if (window.location.pathname === '/app/onboarding') {
    wizard.loadWizardState();
}
```

---

## Decision 3: Sample Data Generation Strategy

**Question**: How should we generate realistic sample data for new organizations to explore features?

### Options Considered

**Option A: Fixed Template Data (Hardcoded Examples)**
- **Pros**:
  - Predictable output (same sample data every time)
  - Fast generation (<1 second)
  - Simple implementation (INSERT statements)
  - Easy to test
  - Consistent documentation/screenshots
- **Cons**:
  - Not personalized to organization
  - May feel "fake" or irrelevant
  - Same examples for all users
- **Implementation**: SQL INSERT statements with fixed values
- **Complexity**: Low

**Option B: Randomized Realistic Data (Faker Library)**
- **Pros**:
  - Unique data per organization (feels personalized)
  - Realistic names, dates, locations
  - Demonstrates variety of scenarios
  - More engaging exploration experience
- **Cons**:
  - Slower generation (2-5 seconds)
  - More complex implementation
  - Harder to document (screenshots differ)
  - May generate inappropriate content (rare)
- **Implementation**: Faker library for names, addresses, datetime generation
- **Complexity**: Medium

**Option C: Context-Aware Generation (Based on Org Profile)**
- **Pros**:
  - Highly relevant (church events for churches, sports events for leagues)
  - Uses organization's actual timezone and location
  - Best learning experience (realistic scenarios)
- **Cons**:
  - Complex logic (detect org type, customize events)
  - Development time (context templates for each org type)
  - May not handle niche organization types well
- **Implementation**: Organization type detection + template mapping
- **Complexity**: High

**Option D: User-Selected Sample Set**
- **Pros**:
  - User chooses relevant examples ("Church", "Sports League", "Non-Profit")
  - Moderately personalized
  - Simple implementation (3-4 template sets)
- **Cons**:
  - Extra step for user (select sample type)
  - Still somewhat generic
  - Need to maintain multiple template sets
- **Implementation**: Sample set selection UI + templates
- **Complexity**: Medium

### Decision: **Fixed Template Data (Option A)**

**Rationale**:
1. **Simplicity**: Fast to implement and test
2. **Consistency**: Predictable output aids documentation and support
3. **Performance**: <1 second generation meets <3s performance target
4. **Maintainability**: Single template set easier to maintain than context-aware generation
5. **Good Enough**: Users primarily need to see _how_ features work, not perfect relevance

**Trade-offs Accepted**:
- Sample data not personalized to organization type (acceptable, users can create custom data quickly after learning)
- Fixed examples may not match all organization types (acceptable, focus on generic "event/volunteer/assignment" concepts that apply universally)

### Implementation Pattern

```python
# api/services/sample_data_generator.py
from datetime import datetime, timedelta
from typing import List
import uuid

class SampleDataGenerator:
    """Generate realistic sample data for onboarding exploration."""

    def __init__(self, db: Session):
        self.db = db

    def generate_sample_data(self, org_id: str) -> Dict[str, Any]:
        """Generate complete sample dataset for organization."""

        # Mark sample data generation started
        start_time = datetime.utcnow()

        # Generate sample entities
        sample_events = self._create_sample_events(org_id)
        sample_teams = self._create_sample_teams(org_id)
        sample_volunteers = self._create_sample_volunteers(org_id, sample_teams)
        sample_availability = self._create_sample_availability(sample_volunteers)
        sample_schedule = self._generate_sample_schedule(org_id, sample_events, sample_volunteers)

        # Mark all entities as sample data
        self._mark_as_sample_data(org_id)

        end_time = datetime.utcnow()
        generation_time = (end_time - start_time).total_seconds()

        return {
            'events_created': len(sample_events),
            'teams_created': len(sample_teams),
            'volunteers_created': len(sample_volunteers),
            'assignments_created': len(sample_schedule),
            'generation_time_seconds': generation_time,
            'expiry_date': (datetime.utcnow() + timedelta(days=30)).isoformat()
        }

    def _create_sample_events(self, org_id: str) -> List[Event]:
        """Create 5 sample events."""
        events_templates = [
            {
                'title': 'Sunday Morning Service',
                'datetime': self._next_sunday(10, 0),  # Next Sunday 10:00 AM
                'duration': 120,
                'location': 'Main Sanctuary',
                'role_requirements': {'Worship Leader': 2, 'Greeter': 4, 'Tech': 2}
            },
            {
                'title': 'Wednesday Evening Service',
                'datetime': self._next_wednesday(19, 0),  # Next Wednesday 7:00 PM
                'duration': 90,
                'location': 'Chapel',
                'role_requirements': {'Worship Leader': 1, 'Greeter': 2}
            },
            {
                'title': 'Youth Group Meeting',
                'datetime': self._next_friday(18, 30),  # Next Friday 6:30 PM
                'duration': 120,
                'location': 'Youth Center',
                'role_requirements': {'Youth Leader': 2, 'Snack Coordinator': 1}
            },
            {
                'title': 'Community Outreach',
                'datetime': self._next_saturday(9, 0),  # Next Saturday 9:00 AM
                'duration': 180,
                'location': 'Downtown',
                'role_requirements': {'Team Leader': 3, 'Volunteer': 10}
            },
            {
                'title': 'Prayer Meeting',
                'datetime': self._next_tuesday(18, 0),  # Next Tuesday 6:00 PM
                'duration': 60,
                'location': 'Prayer Room',
                'role_requirements': {'Facilitator': 1}
            }
        ]

        events = []
        for template in events_templates:
            event = Event(
                id=f"sample_event_{uuid.uuid4().hex[:8]}",
                org_id=org_id,
                title=f"(Sample) {template['title']}",
                datetime=template['datetime'],
                duration=template['duration'],
                location=template['location'],
                role_requirements=template['role_requirements'],
                is_sample=True
            )
            self.db.add(event)
            events.append(event)

        self.db.commit()
        return events

    def _create_sample_teams(self, org_id: str) -> List[Team]:
        """Create 3 sample teams."""
        teams_templates = [
            {'name': 'Worship Team', 'role': 'Worship Leader'},
            {'name': 'Hospitality Team', 'role': 'Greeter'},
            {'name': 'Tech Team', 'role': 'Tech'}
        ]

        teams = []
        for template in teams_templates:
            team = Team(
                id=f"sample_team_{uuid.uuid4().hex[:8]}",
                org_id=org_id,
                name=f"(Sample) {template['name']}",
                role=template['role'],
                is_sample=True
            )
            self.db.add(team)
            teams.append(team)

        self.db.commit()
        return teams

    def _create_sample_volunteers(self, org_id: str, teams: List[Team]) -> List[Person]:
        """Create 15 sample volunteers with realistic names."""
        volunteers_templates = [
            {'name': 'John Smith', 'email': 'john.smith@example.com', 'team_index': 0},
            {'name': 'Sarah Johnson', 'email': 'sarah.j@example.com', 'team_index': 0},
            {'name': 'Michael Brown', 'email': 'm.brown@example.com', 'team_index': 0},
            {'name': 'Emily Davis', 'email': 'emily.d@example.com', 'team_index': 1},
            {'name': 'David Wilson', 'email': 'd.wilson@example.com', 'team_index': 1},
            {'name': 'Lisa Anderson', 'email': 'lisa.a@example.com', 'team_index': 1},
            {'name': 'James Martinez', 'email': 'j.martinez@example.com', 'team_index': 1},
            {'name': 'Jennifer Garcia', 'email': 'jen.garcia@example.com', 'team_index': 2},
            {'name': 'Robert Lee', 'email': 'rob.lee@example.com', 'team_index': 2},
            {'name': 'Maria Rodriguez', 'email': 'm.rodriguez@example.com', 'team_index': None},
            {'name': 'William Taylor', 'email': 'w.taylor@example.com', 'team_index': None},
            {'name': 'Jessica Thomas', 'email': 'jess.thomas@example.com', 'team_index': None},
            {'name': 'Christopher White', 'email': 'chris.white@example.com', 'team_index': None},
            {'name': 'Amanda Harris', 'email': 'amanda.h@example.com', 'team_index': None},
            {'name': 'Daniel Clark', 'email': 'd.clark@example.com', 'team_index': None}
        ]

        volunteers = []
        for template in volunteers_templates:
            volunteer = Person(
                id=f"sample_person_{uuid.uuid4().hex[:8]}",
                org_id=org_id,
                name=f"(Sample) {template['name']}",
                email=template['email'],
                roles=['volunteer'],
                is_sample=True
            )
            self.db.add(volunteer)

            # Add to team if specified
            if template['team_index'] is not None:
                team = teams[template['team_index']]
                team.members.append(volunteer)

            volunteers.append(volunteer)

        self.db.commit()
        return volunteers

    def _create_sample_availability(self, volunteers: List[Person]) -> List[Availability]:
        """Create realistic availability patterns for sample volunteers."""
        availability_records = []

        # Some volunteers unavailable next week (vacation)
        for volunteer in volunteers[:3]:
            avail = Availability(
                person_id=volunteer.id,
                start_date=datetime.utcnow().date(),
                end_date=(datetime.utcnow() + timedelta(days=7)).date(),
                reason='Vacation (Sample)',
                is_sample=True
            )
            self.db.add(avail)
            availability_records.append(avail)

        # Some volunteers unavailable weekdays (work)
        for volunteer in volunteers[10:13]:
            for day in range(5):  # Monday-Friday
                date = datetime.utcnow().date() + timedelta(days=day)
                if date.weekday() < 5:  # Weekday
                    avail = Availability(
                        person_id=volunteer.id,
                        start_date=date,
                        end_date=date,
                        reason='Work (Sample)',
                        is_sample=True
                    )
                    self.db.add(avail)
                    availability_records.append(avail)

        self.db.commit()
        return availability_records

    def _generate_sample_schedule(
        self,
        org_id: str,
        events: List[Event],
        volunteers: List[Person]
    ) -> List[EventAssignment]:
        """Generate one sample schedule with assignments."""
        assignments = []

        # Assign volunteers to first event (Sunday Service)
        event = events[0]
        volunteer_pool = volunteers.copy()

        for role, count in event.role_requirements.items():
            for i in range(count):
                if volunteer_pool:
                    volunteer = volunteer_pool.pop(0)
                    assignment = EventAssignment(
                        event_id=event.id,
                        person_id=volunteer.id,
                        role=role,
                        status='confirmed',
                        is_sample=True
                    )
                    self.db.add(assignment)
                    assignments.append(assignment)

        self.db.commit()
        return assignments

    def _mark_as_sample_data(self, org_id: str):
        """Mark onboarding state with sample data flag."""
        state = self.db.query(OnboardingState).filter(
            OnboardingState.organization_id == org_id
        ).first()

        state.sample_data_generated = True
        state.sample_data_expiry = datetime.utcnow() + timedelta(days=30)
        self.db.commit()

    def clear_sample_data(self, org_id: str) -> Dict[str, int]:
        """Remove all sample data for organization."""
        # Count entities before deletion
        events_count = self.db.query(Event).filter(
            Event.org_id == org_id,
            Event.is_sample == True
        ).count()

        teams_count = self.db.query(Team).filter(
            Team.org_id == org_id,
            Team.is_sample == True
        ).count()

        volunteers_count = self.db.query(Person).filter(
            Person.org_id == org_id,
            Person.is_sample == True
        ).count()

        # Delete sample data (cascading deletes handle assignments, availability)
        self.db.query(Event).filter(
            Event.org_id == org_id,
            Event.is_sample == True
        ).delete()

        self.db.query(Team).filter(
            Team.org_id == org_id,
            Team.is_sample == True
        ).delete()

        self.db.query(Person).filter(
            Person.org_id == org_id,
            Person.is_sample == True
        ).delete()

        # Update onboarding state
        state = self.db.query(OnboardingState).filter(
            OnboardingState.organization_id == org_id
        ).first()

        state.sample_data_generated = False
        state.sample_data_expiry = None

        self.db.commit()

        return {
            'events_deleted': events_count,
            'teams_deleted': teams_count,
            'volunteers_deleted': volunteers_count
        }

    def _next_sunday(self, hour: int, minute: int) -> datetime:
        """Get next Sunday at specified time."""
        today = datetime.utcnow()
        days_until_sunday = (6 - today.weekday()) % 7
        if days_until_sunday == 0:
            days_until_sunday = 7  # Next week
        next_sunday = today + timedelta(days=days_until_sunday)
        return next_sunday.replace(hour=hour, minute=minute, second=0, microsecond=0)

    def _next_wednesday(self, hour: int, minute: int) -> datetime:
        """Get next Wednesday at specified time."""
        today = datetime.utcnow()
        days_until_wednesday = (2 - today.weekday()) % 7
        if days_until_wednesday == 0:
            days_until_wednesday = 7
        next_wednesday = today + timedelta(days=days_until_wednesday)
        return next_wednesday.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # Similar methods for _next_friday, _next_saturday, _next_tuesday...
```

**Sample Data Visual Indicators**:

```css
/* frontend/css/sample-data.css */
.sample-data-badge {
    background: #FFF3CD;
    border: 1px solid #FFC107;
    border-radius: 4px;
    color: #856404;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
    margin-left: 8px;
}

.event-card.sample,
.team-card.sample,
.volunteer-card.sample {
    background: #FFFBF0;
    border-left: 4px solid #FFC107;
}

.sample-data-banner {
    background: #FFF3CD;
    border: 1px solid #FFC107;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.sample-data-banner-text {
    display: flex;
    align-items: center;
    gap: 12px;
}

.sample-data-banner-icon {
    font-size: 24px;
}

.sample-data-banner-message {
    color: #856404;
}

.sample-data-banner-actions {
    display: flex;
    gap: 12px;
}

.btn-clear-sample-data {
    background: #DC3545;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    cursor: pointer;
}

.btn-clear-sample-data:hover {
    background: #C82333;
}
```

---

## Decision 4: Onboarding Checklist Task Detection

**Question**: How should the system automatically detect when checklist tasks are completed?

### Options Considered

**Option A: Database Query-Based Detection (Real-Time)**
- **Pros**:
  - Always accurate (queries current database state)
  - No manual marking required
  - Automatic updates when entities created
- **Cons**:
  - Query overhead on every checklist view
  - Complex queries for some tasks (e.g., "run first solver")
  - May be slow for large organizations
- **Implementation**: SQL COUNT queries per task
- **Complexity**: Low-Medium

**Option B: Event-Driven Updates (Webhook Pattern)**
- **Pros**:
  - Instant updates (real-time checklist progression)
  - Low query overhead (cached state)
  - Decoupled from main workflows
- **Cons**:
  - Complex event routing logic
  - Need to trigger events from multiple places
  - Risk of missed events (lost updates)
- **Implementation**: Event emitters in entity create/update operations
- **Complexity**: High

**Option C: Periodic Background Job (Celery Task)**
- **Pros**:
  - No impact on user request performance
  - Simple implementation (just queries)
  - Can batch updates for efficiency
- **Cons**:
  - Delayed updates (not real-time)
  - Unnecessary work if user not viewing checklist
  - Need Celery infrastructure
- **Implementation**: Celery beat task running every 5 minutes
- **Complexity**: Medium

**Option D: Hybrid (Query + Cache)**
- **Pros**:
  - Fast initial load (cached state)
  - Accurate on-demand (query when viewed)
  - No complex event routing
- **Cons**:
  - Cache invalidation complexity
  - Potential stale data between refreshes
- **Implementation**: Redis cache with TTL, query on cache miss
- **Complexity**: Medium

### Decision: **Database Query-Based Detection (Option A)**

**Rationale**:
1. **Simplicity**: Straightforward SQL queries, easy to understand and maintain
2. **Accuracy**: Always reflects current database state, no cache invalidation issues
3. **Performance**: Checklist queries are lightweight (<50ms), acceptable overhead
4. **No Infrastructure**: Doesn't require Celery or Redis (reduces complexity)
5. **Reliable**: No risk of missed events or stale cached data

**Trade-offs Accepted**:
- Query overhead on every checklist view (acceptable, checklist not viewed frequently after initial onboarding)
- Not real-time (acceptable, users refresh page to see updates after completing tasks)

### Implementation Pattern

```python
# api/services/onboarding_service.py (continued)

class OnboardingService:
    """Onboarding checklist task detection."""

    def get_checklist_state(self, org_id: str) -> Dict[str, Any]:
        """Get checklist progress for organization."""
        tasks = [
            {
                'id': 'complete_profile',
                'title': 'Complete Organization Profile',
                'description': 'Add organization name, location, and timezone',
                'completed': self._is_profile_complete(org_id),
                'quick_action_url': '/app/settings/organization'
            },
            {
                'id': 'create_first_event',
                'title': 'Create First Event',
                'description': 'Add an event that needs volunteer assignments',
                'completed': self._has_created_event(org_id),
                'quick_action_url': '/app/events/create'
            },
            {
                'id': 'add_team',
                'title': 'Add Team',
                'description': 'Create a team with volunteers and roles',
                'completed': self._has_created_team(org_id),
                'quick_action_url': '/app/teams/create'
            },
            {
                'id': 'invite_volunteers',
                'title': 'Invite Volunteers',
                'description': 'Send invitations or add volunteers manually',
                'completed': self._has_invited_volunteers(org_id),
                'quick_action_url': '/app/admin/people'
            },
            {
                'id': 'run_first_schedule',
                'title': 'Run First Schedule',
                'description': 'Generate assignments using the solver',
                'completed': self._has_run_solver(org_id),
                'quick_action_url': '/app/solver'
            },
            {
                'id': 'view_reports',
                'title': 'View Reports',
                'description': 'Check volunteer assignments and fairness metrics',
                'completed': self._has_viewed_reports(org_id),
                'quick_action_url': '/app/reports'
            }
        ]

        completed_count = sum(1 for task in tasks if task['completed'])
        total_count = len(tasks)
        progress_percent = (completed_count / total_count) * 100

        return {
            'tasks': tasks,
            'completed_count': completed_count,
            'total_count': total_count,
            'progress_percent': progress_percent,
            'all_complete': completed_count == total_count
        }

    def _is_profile_complete(self, org_id: str) -> bool:
        """Check if organization profile is complete."""
        org = self.db.query(Organization).filter(Organization.id == org_id).first()
        return all([org.name, org.location, org.timezone])

    def _has_created_event(self, org_id: str) -> bool:
        """Check if organization has created at least one event."""
        event_count = self.db.query(Event).filter(
            Event.org_id == org_id,
            Event.is_sample == False  # Exclude sample data
        ).count()
        return event_count > 0

    def _has_created_team(self, org_id: str) -> bool:
        """Check if organization has created at least one team."""
        team_count = self.db.query(Team).filter(
            Team.org_id == org_id,
            Team.is_sample == False
        ).count()
        return team_count > 0

    def _has_invited_volunteers(self, org_id: str) -> bool:
        """Check if organization has volunteers or pending invitations."""
        volunteer_count = self.db.query(Person).filter(
            Person.org_id == org_id,
            Person.roles.contains(['volunteer']),
            Person.is_sample == False
        ).count()

        invitation_count = self.db.query(Invitation).filter(
            Invitation.org_id == org_id,
            Invitation.status == 'pending'
        ).count()

        return volunteer_count > 0 or invitation_count > 0

    def _has_run_solver(self, org_id: str) -> bool:
        """Check if organization has generated at least one schedule."""
        assignment_count = self.db.query(EventAssignment).join(Event).filter(
            Event.org_id == org_id,
            EventAssignment.is_sample == False
        ).count()
        return assignment_count > 0

    def _has_viewed_reports(self, org_id: str) -> bool:
        """Check if organization has viewed reports page."""
        # Track page view analytics event
        view_event = self.db.query(OnboardingMetric).filter(
            OnboardingMetric.organization_id == org_id,
            OnboardingMetric.event_type == 'page_view_reports'
        ).first()
        return view_event is not None
```

---

## Decision 5: Progressive Feature Disclosure Milestones

**Question**: What proficiency milestones should trigger unlocking advanced features?

### Options Considered

**Option A: Activity-Based Milestones (Entity Counts)**
- **Milestones**:
  - Recurring Events: 5 events created + 3 schedules generated
  - Manual Editing: 10 assignments created
  - SMS Notifications: 10 volunteers added
- **Pros**:
  - Easy to measure (simple database queries)
  - Clear thresholds (objective criteria)
  - Immediate feedback (unlock after specific actions)
- **Cons**:
  - May not indicate true proficiency (could create 5 dummy events)
  - Gameable (users may rush to unlock features)
- **Complexity**: Low

**Option B: Time-Based Milestones (Usage Duration)**
- **Milestones**:
  - Recurring Events: 7 days after signup
  - Manual Editing: 14 days after signup
  - SMS Notifications: 21 days after signup
- **Pros**:
  - Prevents overwhelming new users immediately
  - Natural progression over time
  - Simple implementation (check account age)
- **Cons**:
  - Ignores actual usage (active vs inactive users treated same)
  - Frustrating for power users (forced waiting)
  - Arbitrary timelines
- **Complexity**: Low

**Option C: Behavior-Based Milestones (Feature Interactions)**
- **Milestones**:
  - Recurring Events: Used event editing 5+ times (shows edit proficiency)
  - Manual Editing: Viewed solver output 3+ times (understands automated scheduling)
  - SMS Notifications: Configured email notifications (understands notification system)
- **Pros**:
  - Indicates genuine understanding (behavior shows learning)
  - Natural progression (unlock related features)
  - Harder to game (requires actual usage patterns)
- **Cons**:
  - Complex tracking (need analytics for all interactions)
  - Subjective thresholds (how many interactions = proficiency?)
  - May delay unlocks for legitimate users
- **Complexity**: High

**Option D: No Progressive Disclosure (All Features Unlocked)**
- **Pros**:
  - Maximum flexibility (power users happy)
  - No development complexity
  - No user frustration from locked features
- **Cons**:
  - Overwhelming for new users (80+ UI elements)
  - Harder feature discovery (buried in menus)
  - Reduced learning gradient (steep curve)
- **Complexity**: None (default)

### Decision: **Activity-Based Milestones (Option A) + Bypass Toggle**

**Rationale**:
1. **Simple**: Easy to implement and understand (clear entity count thresholds)
2. **Measurable**: Objective criteria (5 events created is unambiguous)
3. **Motivating**: Provides sense of progression and achievement
4. **Escape Hatch**: "Show All Features" toggle for power users avoids frustration
5. **Good Balance**: Protects new users from overwhelming complexity while allowing experienced users to skip ahead

**Milestones Selected**:
- **Recurring Events**: 5 events created + 3 schedules generated (demonstrates understanding of event creation and scheduling workflow)
- **Manual Schedule Editing**: 10 assignments generated by solver (demonstrates solver proficiency before manual override)
- **SMS Notifications**: 10 volunteers added (SMS only useful with sufficient volunteer base)

**Trade-offs Accepted**:
- Milestones somewhat gameable (acceptable, bypass toggle available for legitimate power users)
- Doesn't measure true understanding (acceptable, focus on protecting majority of new users from overwhelming complexity)

### Implementation Pattern

```python
# api/services/onboarding_service.py (continued)

class OnboardingService:
    """Progressive feature disclosure logic."""

    FEATURE_MILESTONES = {
        'recurring_events': {
            'events_created': 5,
            'schedules_generated': 3
        },
        'manual_editing': {
            'assignments_generated': 10
        },
        'sms_notifications': {
            'volunteers_added': 10
        }
    }

    def get_unlocked_features(self, org_id: str) -> Dict[str, Any]:
        """Get list of unlocked advanced features for organization."""
        state = self.db.query(OnboardingState).filter(
            OnboardingState.organization_id == org_id
        ).first()

        # Check if user enabled "Show All Features" bypass
        if state.show_all_features:
            return {
                'unlocked': ['recurring_events', 'manual_editing', 'sms_notifications'],
                'locked': [],
                'bypass_enabled': True
            }

        # Check proficiency milestones
        unlocked = []
        newly_unlocked = []

        if self._check_recurring_events_milestone(org_id):
            if 'recurring_events' not in state.features_unlocked:
                newly_unlocked.append('recurring_events')
            unlocked.append('recurring_events')

        if self._check_manual_editing_milestone(org_id):
            if 'manual_editing' not in state.features_unlocked:
                newly_unlocked.append('manual_editing')
            unlocked.append('manual_editing')

        if self._check_sms_notifications_milestone(org_id):
            if 'sms_notifications' not in state.features_unlocked:
                newly_unlocked.append('sms_notifications')
            unlocked.append('sms_notifications')

        # Update state with newly unlocked features
        if newly_unlocked:
            state.features_unlocked = unlocked
            self.db.commit()

        all_features = ['recurring_events', 'manual_editing', 'sms_notifications']
        locked = [f for f in all_features if f not in unlocked]

        return {
            'unlocked': unlocked,
            'locked': locked,
            'newly_unlocked': newly_unlocked,  # Features just unlocked this check
            'bypass_enabled': False
        }

    def _check_recurring_events_milestone(self, org_id: str) -> bool:
        """Check if recurring events feature should be unlocked."""
        events_count = self.db.query(Event).filter(
            Event.org_id == org_id,
            Event.is_sample == False
        ).count()

        schedules_count = self.db.query(EventAssignment).join(Event).filter(
            Event.org_id == org_id,
            EventAssignment.is_sample == False
        ).distinct(EventAssignment.event_id).count()

        return (
            events_count >= self.FEATURE_MILESTONES['recurring_events']['events_created']
            and schedules_count >= self.FEATURE_MILESTONES['recurring_events']['schedules_generated']
        )

    def _check_manual_editing_milestone(self, org_id: str) -> bool:
        """Check if manual editing feature should be unlocked."""
        assignments_count = self.db.query(EventAssignment).join(Event).filter(
            Event.org_id == org_id,
            EventAssignment.is_sample == False
        ).count()

        return assignments_count >= self.FEATURE_MILESTONES['manual_editing']['assignments_generated']

    def _check_sms_notifications_milestone(self, org_id: str) -> bool:
        """Check if SMS notifications feature should be unlocked."""
        volunteers_count = self.db.query(Person).filter(
            Person.org_id == org_id,
            Person.roles.contains(['volunteer']),
            Person.is_sample == False
        ).count()

        return volunteers_count >= self.FEATURE_MILESTONES['sms_notifications']['volunteers_added']

    def enable_show_all_features(self, org_id: str):
        """Enable bypass to show all advanced features immediately."""
        state = self.db.query(OnboardingState).filter(
            OnboardingState.organization_id == org_id
        ).first()

        state.show_all_features = True
        state.features_unlocked = ['recurring_events', 'manual_editing', 'sms_notifications']
        self.db.commit()
```

```javascript
// frontend/js/progressive-disclosure.js
class ProgressiveDisclosure {
    constructor() {
        this.checkInterval = 60000; // Check every minute
    }

    async init() {
        // Check unlocked features on page load
        await this.checkUnlockedFeatures();

        // Poll for newly unlocked features
        setInterval(() => this.checkUnlockedFeatures(), this.checkInterval);
    }

    async checkUnlockedFeatures() {
        const response = await authFetch(
            `${API_BASE_URL}/onboarding/features?org_id=${currentUser.org_id}`
        );
        const data = await response.json();

        // Show unlock notifications for newly unlocked features
        if (data.newly_unlocked.length > 0) {
            for (const feature of data.newly_unlocked) {
                this.showFeatureUnlockNotification(feature);
            }
        }

        // Update navigation menu visibility
        this.updateFeatureVisibility(data.unlocked, data.locked);
    }

    showFeatureUnlockNotification(feature) {
        const featureInfo = {
            'recurring_events': {
                title: 'Recurring Events',
                description: 'Create weekly or monthly event patterns to save time scheduling',
                icon: '🔄',
                tutorialUrl: '/app/tutorials/recurring-events'
            },
            'manual_editing': {
                title: 'Manual Schedule Editing',
                description: 'Fine-tune solver-generated schedules with drag-and-drop editing',
                icon: '✏️',
                tutorialUrl: '/app/tutorials/manual-editing'
            },
            'sms_notifications': {
                title: 'SMS Notifications',
                description: 'Send text message reminders and notifications to volunteers',
                icon: '📱',
                tutorialUrl: '/app/tutorials/sms-notifications'
            }
        };

        const info = featureInfo[feature];

        showToast(
            `${info.icon} You've unlocked ${info.title}! ${info.description}`,
            'success',
            {
                duration: 10000,
                action: {
                    text: 'Learn More',
                    callback: () => navigateTo(info.tutorialUrl)
                }
            }
        );
    }

    updateFeatureVisibility(unlocked, locked) {
        // Show unlocked features in navigation
        for (const feature of unlocked) {
            const menuItem = document.querySelector(`[data-feature="${feature}"]`);
            if (menuItem) {
                menuItem.classList.remove('locked');
                menuItem.querySelector('.lock-icon')?.remove();
            }
        }

        // Hide locked features with lock icon
        for (const feature of locked) {
            const menuItem = document.querySelector(`[data-feature="${feature}"]`);
            if (menuItem) {
                menuItem.classList.add('locked');
                if (!menuItem.querySelector('.lock-icon')) {
                    const lockIcon = document.createElement('span');
                    lockIcon.className = 'lock-icon';
                    lockIcon.textContent = '🔒';
                    menuItem.appendChild(lockIcon);
                }
            }
        }
    }
}

// Initialize progressive disclosure
const progressiveDisclosure = new ProgressiveDisclosure();
progressiveDisclosure.init();
```

---

## Decision 6: Quick Start Video Hosting

**Question**: Where should we host quick start tutorial videos for optimal performance and cost?

### Options Considered

**Option A: Self-Hosted (SignUpFlow Server)**
- **Pros**:
  - Full control over content
  - No external dependencies
  - No third-party branding
  - No privacy concerns (data stays on our servers)
- **Cons**:
  - Storage costs (5 videos × 50MB = 250MB minimum)
  - Bandwidth costs (expensive for high-traffic)
  - Need CDN for global performance
  - Video transcoding complexity (multiple formats/resolutions)
- **Cost**: Storage ~$0.50/month, bandwidth ~$5-20/month depending on views
- **Complexity**: High (encoding, streaming, CDN setup)

**Option B: YouTube Embedded**
- **Pros**:
  - Free hosting and bandwidth
  - Excellent global CDN performance
  - Automatic transcoding (multiple resolutions)
  - Built-in player (controls, captions, speed adjust)
  - Analytics (view counts, watch time)
- **Cons**:
  - YouTube branding (logo, recommended videos sidebar)
  - Privacy concerns (Google tracking users)
  - Requires YouTube account
  - Subject to YouTube policies
- **Cost**: Free
- **Complexity**: Low (just embed iframe)

**Option C: Vimeo Embedded (Pro/Business Plan)**
- **Pros**:
  - Professional appearance (no branding)
  - Better privacy controls (no tracking)
  - High-quality player
  - Video analytics
  - Customizable player colors
- **Cons**:
  - Subscription cost ($20/month Pro or $50/month Business)
  - Limited bandwidth (5 TB/year Pro, 7 TB/year Business)
  - Need to stay within plan limits
- **Cost**: $20-50/month
- **Complexity**: Low (embed iframe)

**Option D: Cloudflare Stream**
- **Pros**:
  - Optimized for low latency (<1s start time)
  - Global CDN (Cloudflare network)
  - Reasonable pricing ($1/1000 minutes delivered)
  - No storage fees
  - Built-in player or custom player
- **Cons**:
  - Pay-per-use (costs scale with views)
  - Need Cloudflare account
  - Less familiar than YouTube/Vimeo
- **Cost**: ~$5-15/month depending on views
- **Complexity**: Low-Medium (API integration)

### Decision: **YouTube Embedded (Option B) → Migrate to Vimeo Pro Later**

**Rationale**:
1. **MVP Speed**: YouTube fastest to implement (embed iframe, done)
2. **Zero Cost**: Free hosting allows testing onboarding effectiveness before committing to paid solution
3. **Performance**: YouTube CDN excellent globally, <1s start time
4. **Migration Path**: Easy to swap YouTube embeds for Vimeo later (same iframe pattern)
5. **Analytics**: YouTube provides view analytics to measure video engagement

**Migration Trigger**: Once onboarding proven effective (>40% video view rate), migrate to Vimeo Pro for professional branding

**Trade-offs Accepted**:
- YouTube branding temporarily acceptable for MVP (users understand tutorial context)
- Privacy tracking acceptable for admins (not end-user volunteers)

### Implementation Pattern

```javascript
// frontend/js/quick-start-videos.js
class QuickStartVideos {
    constructor() {
        this.videos = [
            {
                id: 'create_event',
                title: 'Creating Your First Event',
                duration: '2 min',
                youtube_id: 'dQw4w9WgXcQ',  // Replace with actual video ID
                chapters: [
                    { time: 0, title: 'Introduction' },
                    { time: 15, title: 'Navigate to Events' },
                    { time: 30, title: 'Fill Event Details' },
                    { time: 75, title: 'Add Role Requirements' },
                    { time: 105, title: 'Save and Review' }
                ],
                documentation_url: 'https://docs.signupflow.io/events/create'
            },
            {
                id: 'invite_volunteers',
                title: 'Inviting Volunteers',
                duration: '2 min',
                youtube_id: 'dQw4w9WgXcQ',
                chapters: [
                    { time: 0, title: 'Introduction' },
                    { time: 15, title: 'Navigate to People' },
                    { time: 30, title: 'Enter Email Addresses' },
                    { time: 60, title: 'Customize Invitation Message' },
                    { time: 90, title: 'Send Invitations' }
                ],
                documentation_url: 'https://docs.signupflow.io/volunteers/invite'
            },
            {
                id: 'run_solver',
                title: 'Running the Solver',
                duration: '3 min',
                youtube_id: 'dQw4w9WgXcQ',
                chapters: [
                    { time: 0, title: 'What is the Solver?' },
                    { time: 30, title: 'Navigate to Solver' },
                    { time: 60, title: 'Configure Solver Options' },
                    { time: 120, title: 'Generate Schedule' },
                    { time: 150, title: 'Review Assignments' }
                ],
                documentation_url: 'https://docs.signupflow.io/solver/how-it-works'
            },
            {
                id: 'manage_schedules',
                title: 'Managing Schedules',
                duration: '3 min',
                youtube_id: 'dQw4w9WgXcQ',
                chapters: [
                    { time: 0, title: 'Introduction' },
                    { time: 20, title: 'View Generated Schedule' },
                    { time: 60, title: 'Edit Assignments' },
                    { time: 120, title: 'Notify Volunteers' },
                    { time: 150, title: 'Export to Calendar' }
                ],
                documentation_url: 'https://docs.signupflow.io/schedules/manage'
            },
            {
                id: 'advanced_features',
                title: 'Advanced Features',
                duration: '3 min',
                youtube_id: 'dQw4w9WgXcQ',
                chapters: [
                    { time: 0, title: 'Recurring Events' },
                    { time: 60, title: 'Manual Schedule Editing' },
                    { time: 120, title: 'SMS Notifications' },
                    { time: 150, title: 'Reports and Analytics' }
                ],
                documentation_url: 'https://docs.signupflow.io/advanced'
            }
        ];
    }

    renderVideoGallery() {
        const container = document.getElementById('quick-start-videos');

        container.innerHTML = `
            <h3>Quick Start Videos</h3>
            <div class="video-grid">
                ${this.videos.map(video => this.renderVideoCard(video)).join('')}
            </div>
        `;
    }

    renderVideoCard(video) {
        return `
            <div class="video-card" onclick="quickStartVideos.playVideo('${video.id}')">
                <div class="video-thumbnail">
                    <img
                        src="https://img.youtube.com/vi/${video.youtube_id}/mqdefault.jpg"
                        alt="${video.title}"
                    />
                    <div class="play-icon">▶</div>
                    <div class="video-duration">${video.duration}</div>
                </div>
                <div class="video-info">
                    <h4>${video.title}</h4>
                    <p>${video.chapters.length} chapters</p>
                </div>
            </div>
        `;
    }

    playVideo(videoId) {
        const video = this.videos.find(v => v.id === videoId);
        if (!video) return;

        // Create modal with video player
        const modal = document.createElement('div');
        modal.className = 'video-modal';
        modal.innerHTML = `
            <div class="video-modal-content">
                <button class="video-modal-close" onclick="quickStartVideos.closeVideo()">×</button>

                <div class="video-player-container">
                    <iframe
                        width="100%"
                        height="100%"
                        src="https://www.youtube.com/embed/${video.youtube_id}?autoplay=1&rel=0"
                        frameborder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowfullscreen
                    ></iframe>
                </div>

                <div class="video-sidebar">
                    <h4>${video.title}</h4>

                    <div class="video-chapters">
                        <h5>Chapters</h5>
                        ${video.chapters.map(chapter => `
                            <div class="chapter-item" onclick="quickStartVideos.jumpToTime(${chapter.time})">
                                <span class="chapter-time">${this.formatTime(chapter.time)}</span>
                                <span class="chapter-title">${chapter.title}</span>
                            </div>
                        `).join('')}
                    </div>

                    <div class="video-actions">
                        <a href="${video.documentation_url}" target="_blank" class="btn-secondary">
                            View Documentation →
                        </a>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Track video view
        this.trackVideoView(videoId);
    }

    closeVideo() {
        const modal = document.querySelector('.video-modal');
        if (modal) {
            modal.remove();
        }
    }

    jumpToTime(seconds) {
        // YouTube iframe API to jump to specific time
        // Implementation depends on YouTube Player API integration
        console.log(`Jump to ${seconds}s`);
    }

    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    async trackVideoView(videoId) {
        await authFetch(`${API_BASE_URL}/analytics/onboarding-events`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                event_type: 'video_viewed',
                video_id: videoId,
                timestamp: new Date().toISOString()
            })
        });
    }
}

// Global instance
const quickStartVideos = new QuickStartVideos();
```

```css
/* frontend/css/quick-start-videos.css */
.video-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
    margin-top: 16px;
}

.video-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    overflow: hidden;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
}

.video-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.video-thumbnail {
    position: relative;
    width: 100%;
    padding-bottom: 56.25%; /* 16:9 aspect ratio */
    background: #000000;
}

.video-thumbnail img {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.play-icon {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 60px;
    height: 60px;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    color: #4299e1;
}

.video-duration {
    position: absolute;
    bottom: 8px;
    right: 8px;
    background: rgba(0, 0, 0, 0.8);
    color: #ffffff;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
}

.video-info {
    padding: 16px;
}

.video-info h4 {
    margin: 0 0 8px 0;
    font-size: 16px;
    color: #1a202c;
}

.video-info p {
    margin: 0;
    font-size: 14px;
    color: #718096;
}

.video-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
}

.video-modal-content {
    background: #ffffff;
    border-radius: 12px;
    width: 90%;
    max-width: 1200px;
    max-height: 90vh;
    display: flex;
    overflow: hidden;
}

.video-player-container {
    flex: 1;
    background: #000000;
    position: relative;
    padding-bottom: 56.25%; /* 16:9 */
}

.video-player-container iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
}

.video-sidebar {
    width: 300px;
    padding: 24px;
    overflow-y: auto;
}

.video-modal-close {
    position: absolute;
    top: 16px;
    right: 16px;
    background: rgba(255, 255, 255, 0.9);
    border: none;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    font-size: 24px;
    cursor: pointer;
    z-index: 10001;
}

.video-chapters {
    margin: 24px 0;
}

.chapter-item {
    padding: 8px;
    border-radius: 4px;
    cursor: pointer;
    display: flex;
    gap: 12px;
}

.chapter-item:hover {
    background: #edf2f7;
}

.chapter-time {
    color: #4299e1;
    font-weight: 600;
    min-width: 40px;
}

.chapter-title {
    color: #4a5568;
}
```

---

## Summary of Technology Decisions

| Decision | Selected Option | Rationale | Implementation Complexity |
|----------|-----------------|-----------|---------------------------|
| Tutorial Overlay Library | Shepherd.js | Accessibility, lightweight, framework-agnostic, MIT license | Low |
| Wizard Flow Architecture | Linear Sequential (5 steps) | Simplicity, high completion rates, easy analytics tracking | Low |
| Sample Data Generation | Fixed Templates | Fast (<1s), predictable, easy to maintain | Low |
| Checklist Task Detection | Database Query-Based | Accurate, simple, no cache invalidation | Low-Medium |
| Progressive Disclosure | Activity-Based Milestones + Bypass | Clear thresholds, measurable, escape hatch for power users | Medium |
| Quick Start Video Hosting | YouTube Embedded (MVP) → Vimeo Pro (Later) | Zero cost MVP, easy migration path, good performance | Low |

**Total Implementation Complexity**: **Low-Medium** (mostly low-complexity decisions, progressive disclosure adds medium complexity)

**Development Time Estimate**: 2-3 weeks for complete onboarding system

---

**Last Updated**: 2025-10-23
**Feature**: 020 - User Onboarding System
