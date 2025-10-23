/**
 * Onboarding Wizard
 *
 * Manages the 4-step guided setup wizard for new organizations.
 * Steps: 1) Organization Profile, 2) First Event, 3) First Team, 4) Invite Volunteers
 */

// Note: Using window.authFetch, window.router, window.i18n, window.renderSampleDataControls (loaded via script tags)
// No ES6 imports needed since this is loaded as a regular script

// Current wizard state
let currentStep = 1;
let wizardData = {
    org: {},
    event: {},
    team: {},
    invitations: []
};

/**
 * Initialize wizard and load saved progress
 */
window.initWizard = async function() {
    try {
        const progress = await loadProgress();
        if (progress && progress.wizard_step_completed > 0) {
            currentStep = progress.wizard_step_completed + 1;
            if (currentStep > 4) {
                // Wizard already completed
                window.router.navigate('/app/onboarding-dashboard');
                return;
            }
        }
        renderWizard();
    } catch (error) {
        console.error('Failed to initialize wizard:', error);
        renderWizard(); // Render anyway with step 1
    }
}

/**
 * Load onboarding progress from API
 */
async function loadProgress() {
    const response = await window.authFetch('/api/onboarding/progress');
    if (response.ok) {
        return await response.json();
    }
    return null;
}

/**
 * Save wizard progress to API
 */
window.saveProgress = async function(step, data) {
    const response = await window.authFetch('/api/onboarding/progress', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            wizard_step_completed: step,
            wizard_data: data
        })
    });
    return response.ok;
}

/**
 * Render the wizard UI
 */
function renderWizard() {
    const container = document.getElementById('main-app');
    if (!container) return;

    container.innerHTML = `
        <div class="onboarding-wizard">
            <div class="wizard-header">
                <h1 data-i18n="onboarding.wizard.title">Welcome to SignUpFlow</h1>
                <div class="wizard-progress">
                    <div class="progress-bar" id="wizard-progress-bar"></div>
                </div>
                <p class="step-indicator" id="step-indicator">Step ${currentStep} of 4</p>
            </div>
            <div class="wizard-content" id="wizard-step-content">
                <!-- Step content will be rendered here -->
            </div>
            <div class="wizard-actions">
                <button id="wizard-back" class="btn-secondary" style="display: none;">Back</button>
                <button id="wizard-save-later" class="btn-secondary">Save & Continue Later</button>
                <button id="wizard-continue" class="btn-primary">Continue</button>
            </div>
        </div>
    `;

    updateProgressBar();
    renderCurrentStep();
    attachWizardEvents();
}

/**
 * Update progress bar visual
 */
window.updateProgressBar = function() {
    const progressBar = document.getElementById('wizard-progress-bar');
    const indicator = document.getElementById('step-indicator');

    if (progressBar) {
        const percentage = (currentStep / 4) * 100;
        progressBar.style.width = `${percentage}%`;
    }

    if (indicator) {
        indicator.textContent = `Step ${currentStep} of 4 (${Math.round((currentStep / 4) * 100)}%)`;
    }
}

/**
 * Render current step content
 */
function renderCurrentStep() {
    const contentDiv = document.getElementById('wizard-step-content');
    if (!contentDiv) return;

    switch (currentStep) {
        case 1:
            renderStep1();
            break;
        case 2:
            renderStep2();
            break;
        case 3:
            renderStep3();
            break;
        case 4:
            renderStep4();
            break;
        default:
            contentDiv.innerHTML = '<p>Invalid step</p>';
    }
}

/**
 * Step 1: Organization Profile
 */
window.renderStep1 = function() {
    const contentDiv = document.getElementById('wizard-step-content');

    // Get current user/org from session for pre-filling
    const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
    const currentOrg = JSON.parse(localStorage.getItem('currentOrg') || '{}');

    // Pre-fill from wizard data or current org
    const orgName = wizardData.org?.name || currentOrg.name || '';
    const orgLocation = wizardData.org?.location || currentOrg.location || '';
    const orgTimezone = wizardData.org?.timezone || currentOrg.timezone || currentUser.timezone || 'America/New_York';

    contentDiv.innerHTML = `
        <h2 data-i18n="onboarding.wizard.step1.title">Organization Profile</h2>
        <p data-i18n="onboarding.wizard.step1.description">Let's set up your organization profile.</p>
        <form id="step1-form">
            <div class="form-group">
                <label for="org-name">Organization Name *</label>
                <input type="text" id="org-name" value="${orgName}" required>
            </div>
            <div class="form-group">
                <label for="org-location">Location</label>
                <input type="text" id="org-location" value="${orgLocation}" placeholder="City, State">
            </div>
            <div class="form-group">
                <label for="org-timezone">Timezone *</label>
                <select id="org-timezone" required>
                    <option value="America/New_York" ${orgTimezone === 'America/New_York' ? 'selected' : ''}>Eastern Time</option>
                    <option value="America/Chicago" ${orgTimezone === 'America/Chicago' ? 'selected' : ''}>Central Time</option>
                    <option value="America/Denver" ${orgTimezone === 'America/Denver' ? 'selected' : ''}>Mountain Time</option>
                    <option value="America/Los_Angeles" ${orgTimezone === 'America/Los_Angeles' ? 'selected' : ''}>Pacific Time</option>
                    <option value="America/Phoenix" ${orgTimezone === 'America/Phoenix' ? 'selected' : ''}>Arizona</option>
                    <option value="America/Anchorage" ${orgTimezone === 'America/Anchorage' ? 'selected' : ''}>Alaska</option>
                    <option value="Pacific/Honolulu" ${orgTimezone === 'Pacific/Honolulu' ? 'selected' : ''}>Hawaii</option>
                </select>
            </div>
        </form>
    `;
}

/**
 * Step 2: First Event
 */
window.renderStep2 = function() {
    const contentDiv = document.getElementById('wizard-step-content');
    contentDiv.innerHTML = `
        <h2 data-i18n="onboarding.wizard.step2.title">Create Your First Event</h2>
        <p data-i18n="onboarding.wizard.step2.description">Create an event to start scheduling volunteers.</p>
        <form id="step2-form">
            <div class="form-group">
                <label for="event-title">Event Title *</label>
                <input type="text" id="event-title" placeholder="Sunday Service" required>
            </div>
            <div class="form-group">
                <label for="event-date">Date *</label>
                <input type="date" id="event-date" required>
            </div>
            <div class="form-group">
                <label for="event-time">Time *</label>
                <input type="time" id="event-time" value="10:00" required>
            </div>
        </form>
    `;
}

/**
 * Step 3: First Team
 */
window.renderStep3 = function() {
    const contentDiv = document.getElementById('wizard-step-content');
    contentDiv.innerHTML = `
        <h2 data-i18n="onboarding.wizard.step3.title">Create Your First Team</h2>
        <p data-i18n="onboarding.wizard.step3.description">Teams help organize volunteers by role.</p>
        <form id="step3-form">
            <div class="form-group">
                <label for="team-name">Team Name *</label>
                <input type="text" id="team-name" placeholder="Greeters" required>
            </div>
            <div class="form-group">
                <label for="team-role">Role *</label>
                <input type="text" id="team-role" placeholder="greeter" required>
            </div>
        </form>
    `;
}

/**
 * Step 4: Invite Volunteers
 */
window.renderStep4 = function() {
    const contentDiv = document.getElementById('wizard-step-content');
    contentDiv.innerHTML = `
        <h2 data-i18n="onboarding.wizard.step4.title">Invite Volunteers</h2>
        <p data-i18n="onboarding.wizard.step4.description">Invite your team members to join.</p>
        <form id="step4-form">
            <div class="form-group">
                <label for="invite-emails">Email Addresses (one per line) *</label>
                <textarea id="invite-emails" rows="5" placeholder="john@example.com&#10;jane@example.com&#10;bob@example.com" required></textarea>
            </div>
        </form>
    `;
}

/**
 * Validate current step
 */
window.validateStep = function() {
    const form = document.querySelector(`#step${currentStep}-form`);
    if (!form) return false;
    return form.checkValidity();
}

/**
 * Handle step navigation
 */
async function handleContinue() {
    if (!window.validateStep()) {
        alert('Please fill in all required fields');
        return;
    }

    // Save step data
    await saveStepData();

    // Move to next step or complete
    if (currentStep < 4) {
        currentStep++;
        renderWizard();
    } else {
        await completeWizard();
    }
}

/**
 * Save current step data
 */
async function saveStepData() {
    // Collect data from current step
    const form = document.querySelector(`#step${currentStep}-form`);
    if (!form) return;

    switch (currentStep) {
        case 1:
            // Organization Profile
            wizardData.org = {
                name: document.getElementById('org-name')?.value || '',
                location: document.getElementById('org-location')?.value || '',
                timezone: document.getElementById('org-timezone')?.value || 'UTC'
            };
            break;
        case 2:
            // First Event
            wizardData.event = {
                title: document.getElementById('event-title')?.value || '',
                date: document.getElementById('event-date')?.value || '',
                time: document.getElementById('event-time')?.value || '10:00'
            };
            break;
        case 3:
            // First Team
            wizardData.team = {
                name: document.getElementById('team-name')?.value || '',
                role: document.getElementById('team-role')?.value || ''
            };
            break;
        case 4:
            // Invite Volunteers
            const emails = document.getElementById('invite-emails')?.value || '';
            wizardData.invitations = emails.split('\n').filter(e => e.trim());
            break;
    }

    // Save to API
    await window.saveProgress(currentStep, wizardData);
}

/**
 * Handle "Save & Continue Later"
 */
window.saveLater = async function() {
    await saveStepData();
    alert('Progress saved! You can continue later.');
    window.router.navigate('/app/dashboard');
}

/**
 * Resume wizard from saved state
 */
window.resumeWizard = async function() {
    const progress = await loadProgress();
    if (progress && progress.wizard_step_completed > 0) {
        currentStep = progress.wizard_step_completed + 1;
        if (progress.wizard_data) {
            wizardData = progress.wizard_data;
        }
    }
    renderWizard();
}

/**
 * Complete wizard and redirect
 */
window.completeWizard = async function() {
    try {
        // Save final progress
        await window.saveProgress(4, wizardData);

        // Get current org and user
        const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
        const orgId = currentUser.org_id;

        // Create event from wizard data (Step 2)
        if (wizardData.event && wizardData.event.title) {
            const eventDatetime = `${wizardData.event.date}T${wizardData.event.time}:00`;
            await window.authFetch(`/api/events?org_id=${orgId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: wizardData.event.title,
                    datetime: eventDatetime,
                    duration: 90,  // Default 90 minutes
                    role_requirements: {}
                })
            });
        }

        // Create team from wizard data (Step 3)
        if (wizardData.team && wizardData.team.name) {
            await window.authFetch(`/api/teams?org_id=${orgId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: wizardData.team.name,
                    role: wizardData.team.role
                })
            });
        }

        // Send invitations from wizard data (Step 4)
        if (wizardData.invitations && wizardData.invitations.length > 0) {
            for (const email of wizardData.invitations) {
                if (email.trim()) {
                    await window.authFetch(`/api/invitations?org_id=${orgId}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            email: email.trim(),
                            roles: ['volunteer']
                        })
                    });
                }
            }
        }

        // Show success and redirect
        showSuccessMessage();
        setTimeout(() => {
            window.router.navigate('/app/onboarding-dashboard');
        }, 2000);

    } catch (error) {
        console.error('Failed to complete wizard:', error);
        alert('Failed to complete setup. Please try again.');
    }
}

/**
 * Show wizard completion success message
 */
window.showSuccessMessage = function() {
    const container = document.getElementById('main-app');
    container.innerHTML = `
        <div class="wizard-success">
            <div class="success-icon">✓</div>
            <h1 data-i18n="onboarding.wizard.complete.title">Setup Complete!</h1>
            <p data-i18n="onboarding.wizard.complete.message">Your organization is ready. Redirecting to dashboard...</p>

            <div class="success-next-steps">
                <h2 data-i18n="onboarding.wizard.complete.explore">Explore Features</h2>
                <p data-i18n="onboarding.wizard.complete.sample_data_intro">
                    Want to try out features before adding real data? Generate sample data to explore.
                </p>
                <div id="wizard-sample-data-controls"></div>
            </div>
        </div>
    `;

    // Initialize sample data controls after a brief delay
    setTimeout(() => {
        window.renderSampleDataControls('wizard-sample-data-controls');
    }, 500);
}

/**
 * Attach event listeners to wizard buttons
 */
function attachWizardEvents() {
    const continueBtn = document.getElementById('wizard-continue');
    const saveLaterBtn = document.getElementById('wizard-save-later');
    const backBtn = document.getElementById('wizard-back');

    if (continueBtn) {
        continueBtn.addEventListener('click', handleContinue);
    }

    if (saveLaterBtn) {
        saveLaterBtn.addEventListener('click', window.saveLater);
    }

    if (backBtn && currentStep > 1) {
        backBtn.style.display = 'inline-block';
        backBtn.addEventListener('click', () => {
            currentStep--;
            renderWizard();
        });
    }
}
