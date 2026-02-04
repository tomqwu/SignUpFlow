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

        if (progress && progress.wizard_data) {
            wizardData = progress.wizard_data;
        }

        // wizard_step_completed is the last COMPLETED step (0-4)
        if (progress && typeof progress.wizard_step_completed === 'number') {
            currentStep = progress.wizard_step_completed + 1;
        }

        if (currentStep > 4) {
            // Wizard already completed
            window.router.navigate('/app/onboarding-dashboard');
            return;
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
    const container = document.getElementById('wizard-container');
    if (!container) return;

    container.innerHTML = `
        <div class="wizard-card">
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
                <button id="wizard-back" class="btn btn-secondary" style="display: none;">Back</button>
                <button id="wizard-save-later" class="btn btn-secondary">Save & Continue Later</button>
                <button id="wizard-continue" class="btn btn-primary">Continue</button>
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
    const currentUser = JSON.parse(localStorage.getItem('roster_user') || '{}');
    const currentOrg = JSON.parse(localStorage.getItem('roster_org') || '{}');

    // Pre-fill from wizard data or current org
    const orgName = wizardData.org?.name || currentOrg.name || '';
    const orgLocation = wizardData.org?.location || currentOrg.region || currentOrg.location || '';
    const orgTimezone = wizardData.org?.timezone || currentOrg.timezone || currentUser.timezone || 'America/New_York';

    contentDiv.innerHTML = `
        <h2 data-i18n="onboarding.wizard.step1.title">Organization Profile</h2>
        <p data-i18n="onboarding.wizard.step1.description">Let's set up your organization profile.</p>
        <form id="step1-form">
            <div class="form-group">
                <label for="wizard-org-name">Organization Name *</label>
                <input type="text" id="wizard-org-name" value="${orgName}" required>
            </div>
            <div class="form-group">
                <label for="wizard-org-location">Location</label>
                <input type="text" id="wizard-org-location" value="${orgLocation}" placeholder="City, State">
            </div>
            <div class="form-group">
                <label for="wizard-org-timezone">Timezone *</label>
                <select id="wizard-org-timezone" required>
                    <option value="America/New_York" ${orgTimezone === 'America/New_York' ? 'selected' : ''}>Eastern Time</option>
                    <option value="America/Toronto" ${orgTimezone === 'America/Toronto' ? 'selected' : ''}>Toronto</option>
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

    const event = (wizardData && wizardData.event) ? wizardData.event : {};
    const eventTitle = event.title || '';
    const eventDate = event.date || '';
    const eventTime = event.time || '10:00';
    const eventDuration = event.duration || '90';

    contentDiv.innerHTML = `
        <h2 data-i18n="onboarding.wizard.step2.title">Create Your First Event</h2>
        <p data-i18n="onboarding.wizard.step2.description">Create an event to start scheduling volunteers.</p>
        <form id="step2-form">
            <div class="form-group">
                <label for="wizard-event-title">Event Title *</label>
                <input type="text" id="wizard-event-title" placeholder="Sunday Service" value="${eventTitle}" required>
            </div>
            <div class="form-group">
                <label for="wizard-event-date">Date *</label>
                <input type="date" id="wizard-event-date" value="${eventDate}" required>
            </div>
            <div class="form-group">
                <label for="wizard-event-time">Time *</label>
                <input type="time" id="wizard-event-time" value="${eventTime}" required>
            </div>
            <div class="form-group">
                <label for="wizard-event-duration">Duration (minutes)</label>
                <input type="number" id="wizard-event-duration" value="${eventDuration}">
            </div>
        </form>
    `;
}

/**
 * Step 3: First Team
 */
window.renderStep3 = function() {
    const contentDiv = document.getElementById('wizard-step-content');

    const team = (wizardData && wizardData.team) ? wizardData.team : {};
    const teamName = team.name || '';
    const teamRole = team.role || '';
    const teamDescription = team.description || '';

    contentDiv.innerHTML = `
        <h2 data-i18n="onboarding.wizard.step3.title">Create Your First Team</h2>
        <p data-i18n="onboarding.wizard.step3.description">Teams help organize volunteers by role.</p>
        <form id="step3-form">
            <div class="form-group">
                <label for="wizard-team-name">Team Name *</label>
                <input type="text" id="wizard-team-name" placeholder="Greeters" value="${teamName}" required>
            </div>
            <div class="form-group">
                <label for="wizard-team-role">Role *</label>
                <input type="text" id="wizard-team-role" placeholder="greeter" value="${teamRole}" required>
            </div>
            <div class="form-group">
                <label for="wizard-team-description">Description</label>
                <textarea id="wizard-team-description" placeholder="Optional team description">${teamDescription}</textarea>
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
                <label for="wizard-invite-emails">Email Addresses (one per line) *</label>
                <textarea id="wizard-invite-emails" rows="5" placeholder="john@example.com&#10;jane@example.com&#10;bob@example.com" required></textarea>
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
async function saveStepData({ completedStep = currentStep } = {}) {
    // Collect data from current step
    const form = document.querySelector(`#step${currentStep}-form`);
    if (!form) return;

    switch (currentStep) {
        case 1:
            // Organization Profile
            wizardData.org = {
                name: document.getElementById('wizard-org-name')?.value || '',
                location: document.getElementById('wizard-org-location')?.value || '',
                timezone: document.getElementById('wizard-org-timezone')?.value || 'UTC'
            };
            break;
        case 2:
            // First Event
            wizardData.event = {
                title: document.getElementById('wizard-event-title')?.value || '',
                date: document.getElementById('wizard-event-date')?.value || '',
                time: document.getElementById('wizard-event-time')?.value || '10:00',
                duration: document.getElementById('wizard-event-duration')?.value || '90'
            };
            break;
        case 3:
            // First Team
            wizardData.team = {
                name: document.getElementById('wizard-team-name')?.value || '',
                role: document.getElementById('wizard-team-role')?.value || '',
                description: document.getElementById('wizard-team-description')?.value || ''
            };
            break;
        case 4:
            // Invite Volunteers
            const emails = document.getElementById('wizard-invite-emails')?.value || '';
            wizardData.invitations = emails.split('\n').filter(e => e.trim());
            break;
    }

    // Save to API
    await window.saveProgress(completedStep, wizardData);
}

/**
 * Handle "Save & Continue Later"
 */
window.saveLater = async function() {
    // "Save & Continue Later" should NOT mark the current step as completed.
    // Example: If user is on Step 3, last completed step is still Step 2.
    const completedStep = Math.max(currentStep - 1, 0);
    await saveStepData({ completedStep });
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
        console.log('🧙 completeWizard started');
        // Save final progress
        await window.saveProgress(4, wizardData);

        // Get current org and user
        const currentUser = JSON.parse(localStorage.getItem('roster_user') || '{}');
        const orgId = currentUser.org_id;

        // 1. Update Org Profile (Step 1)
        if (wizardData.org && wizardData.org.name) {
            console.log('🧙 Updating org profile...');
            await window.authFetch(`/api/organizations/${orgId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: wizardData.org.name,
                    region: wizardData.org.location,
                    config: { timezone: wizardData.org.timezone }
                })
            });
            
            // Also update admin's timezone
            await window.authFetch(`/api/people/me`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    timezone: wizardData.org.timezone
                })
            });
        }

        // 2. Create event from wizard data (Step 2)
        if (wizardData.event && wizardData.event.title) {
            console.log('🧙 Creating first event...');
            const startStr = `${wizardData.event.date}T${wizardData.event.time}:00`;
            const startDate = new Date(startStr);
            const duration = parseInt(wizardData.event.duration) || 90;
            const endDate = new Date(startDate.getTime() + duration * 60 * 1000);
            
            await window.authFetch(`/api/events/?org_id=${orgId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    id: `event_${Date.now()}`,
                    org_id: orgId,
                    type: 'service',
                    start_time: startDate.toISOString(),
                    end_time: endDate.toISOString(),
                    extra_data: { title: wizardData.event.title }
                })
            });
        }

        // 3. Create team from wizard data (Step 3)
        if (wizardData.team && wizardData.team.name) {
            console.log('🧙 Creating first team...');
            const teamId = wizardData.team.name.toLowerCase().replace(/\s+/g, '_') + '_' + Date.now();
            await window.authFetch(`/api/teams/?org_id=${orgId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    id: teamId,
                    org_id: orgId,
                    name: wizardData.team.name,
                    description: wizardData.team.description || `First team created during setup`
                })
            });
        }

        // 4. Send invitations from wizard data (Step 4)
        if (wizardData.invitations && wizardData.invitations.length > 0) {
            console.log('🧙 Sending invitations...');
            for (const email of wizardData.invitations) {
                if (email.trim()) {
                    await window.authFetch(`/api/invitations?org_id=${orgId}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            email: email.trim(),
                            name: email.split('@')[0], // Default name to email prefix
                            roles: ['volunteer']
                        })
                    });
                }
            }
        }

        console.log('🧙 All API calls complete. Showing success message.');
        // Show success and redirect
        showSuccessMessage();
        
        // Wait 3 seconds for the user to celebrate, then go to dashboard
        setTimeout(() => {
            console.log('🧙 Redirecting to onboarding dashboard...');
            window.router.navigate('/app/onboarding-dashboard');
        }, 3000);

    } catch (error) {
        console.error('Failed to complete wizard:', error);
        alert('Failed to complete setup. Please try again.');
    }
}

/**
 * Show wizard completion success message
 */
window.showSuccessMessage = function() {
    console.log('🎉 showSuccessMessage called');
    const screen = document.getElementById('wizard-screen');
    if (screen) {
        screen.classList.remove('hidden');
        screen.style.display = 'block';
    }
    
    const container = document.getElementById('wizard-container');
    if (container) {
        container.innerHTML = `
            <div id="wizard-success" class="wizard-success" style="display: block !important; visibility: visible !important; opacity: 1 !important;">
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
        console.log('✅ Wizard success message injected into container');
    } else {
        console.error('❌ wizard-container not found for success message!');
    }

    // Initialize sample data controls after a brief delay
    setTimeout(() => {
        if (typeof window.renderSampleDataControls === 'function') {
            window.renderSampleDataControls('wizard-sample-data-controls');
        }
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

    if (backBtn) {
        if (currentStep > 1) {
            backBtn.style.display = 'inline-block';
            backBtn.disabled = false;
            backBtn.addEventListener('click', () => {
                currentStep--;
                renderWizard();
            });
        } else {
            // Keep it disabled on Step 1 (tests may still find it in the DOM)
            backBtn.style.display = 'none';
            backBtn.disabled = true;
        }
    }
}
