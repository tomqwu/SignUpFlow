/**
 * Onboarding Checklist Widget
 *
 * Displays getting started checklist with 6 tasks:
 * 1. Complete Profile
 * 2. Create First Event
 * 3. Add First Team
 * 4. Invite Volunteers
 * 5. Run First Schedule
 * 6. View Reports
 */

// Note: Using window.authFetch and window.navigateTo (loaded via script tags)
// No ES6 imports needed since this is loaded as a regular script

// Checklist items configuration
const CHECKLIST_ITEMS = [
    { id: 'complete_profile', route: '/profile', icon: '👤' },
    { id: 'create_event', route: '/app/events', icon: '📅' },
    { id: 'add_team', route: '/app/admin', icon: '👥' },
    { id: 'invite_volunteers', route: '/app/admin', icon: '✉️' },
    { id: 'run_solver', route: '/app/admin', icon: '🤖' },
    { id: 'view_reports', route: '/app/schedule', icon: '📊' }
];

/**
 * Render checklist widget in sidebar or dashboard
 */
window.renderChecklist = async function(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const state = await getChecklistState();
    const progress = calculateProgress(state);
    const percentage = Math.round((progress.completed / progress.total) * 100);

    container.innerHTML = `
        <div class="onboarding-checklist">
            <div class="checklist-header">
                <h3 data-i18n="onboarding.checklist.title">Getting Started</h3>
                <span class="progress-badge">${percentage}%</span>
            </div>
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: ${percentage}%"></div>
            </div>
            <div class="checklist-items" id="checklist-items">
                ${CHECKLIST_ITEMS.map(item => renderChecklistItem(item, state)).join('')}
            </div>
            ${percentage === 100 ? `
                <button class="dismiss-checklist" onclick="window.hideChecklist()">
                    <span data-i18n="onboarding.checklist.dismiss">Dismiss</span>
                </button>
            ` : ''}
        </div>
    `;

    attachChecklistEvents();

    if (percentage === 100) {
        showCompletionCelebration();
    }
}

/**
 * Render individual checklist item
 */
function renderChecklistItem(item, state) {
    const completed = state[item.id] || false;

    return `
        <div class="checklist-item ${completed ? 'completed' : ''}" data-item-id="${item.id}">
            <div class="item-icon">${completed ? '✅' : item.icon}</div>
            <div class="item-content">
                <span class="item-title" data-i18n="onboarding.checklist.items.${item.id}">
                    ${item.id.replace('_', ' ')}
                </span>
            </div>
            <button class="item-action" data-route="${item.route}">
                ${completed ?
                    `<span data-i18n="common.buttons.view">View</span>` :
                    `<span data-i18n="common.buttons.start">Start</span>`
                }
            </button>
        </div>
    `;
}

/**
 * Calculate checklist progress
 */
function calculateProgress(state) {
    const total = CHECKLIST_ITEMS.length;
    const completed = Object.values(state).filter(v => v === true).length;

    return { completed, total };
}

/**
 * Get checklist state from API
 */
async function getChecklistState() {
    try {
        const response = await window.authFetch('/api/onboarding/progress');
        if (response.ok) {
            const data = await response.json();
            return data.checklist_state || {};
        }
    } catch (error) {
        console.error('Failed to load checklist state:', error);
    }
    return {};
}

/**
 * Update checklist item completion status
 */
window.updateChecklistItem = async function(itemId, completed = true) {
    try {
        const state = await getChecklistState();
        state[itemId] = completed;

        const response = await window.authFetch('/api/onboarding/progress', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                checklist_state: state
            })
        });

        if (response.ok) {
            // Refresh checklist UI
            window.renderChecklist('onboarding-checklist-container');
            return true;
        }
    } catch (error) {
        console.error('Failed to update checklist item:', error);
    }
    return false;
}

/**
 * Auto-update checklist based on user actions
 */
window.autoUpdateChecklist = async function() {
    // Called after key actions to update checklist
    // Check conditions and mark items complete

    const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
    const orgId = currentUser.org_id;

    if (!orgId) return;

    try {
        // Check profile completion
        if (currentUser.name && currentUser.email) {
            await window.updateChecklistItem('complete_profile', true);
        }

        // Check event creation
        const eventsResponse = await window.authFetch(`/api/events/?org_id=${orgId}`);
        if (eventsResponse.ok) {
            const events = await eventsResponse.json();
            if (events.length > 0) {
                await window.updateChecklistItem('create_event', true);
            }
        }

        // Check team creation
        const teamsResponse = await window.authFetch(`/api/teams/?org_id=${orgId}`);
        if (teamsResponse.ok) {
            const teams = await teamsResponse.json();
            if (teams.length > 0) {
                await window.updateChecklistItem('add_team', true);
            }
        }

        // Check volunteer invitations
        const peopleResponse = await window.authFetch(`/api/people/?org_id=${orgId}`);
        if (peopleResponse.ok) {
            const people = await peopleResponse.json();
            if (people.length > 1) { // More than just admin
                await window.updateChecklistItem('invite_volunteers', true);
            }
        }

        // Check solver runs (stored in localStorage for now)
        const solverRuns = localStorage.getItem('solver_runs_count') || '0';
        if (parseInt(solverRuns) > 0) {
            await window.updateChecklistItem('run_solver', true);
        }

        // Check report views (stored in localStorage for now)
        const reportViews = localStorage.getItem('report_views_count') || '0';
        if (parseInt(reportViews) > 0) {
            await window.updateChecklistItem('view_reports', true);
        }

    } catch (error) {
        console.error('Failed to auto-update checklist:', error);
    }
}

/**
 * Navigate to checklist item section
 */
function navigateToSection(route) {
    window.router.navigate(route);
}

/**
 * Show completion celebration
 */
function showCompletionCelebration() {
    const celebration = document.createElement('div');
    celebration.className = 'completion-celebration';
    celebration.innerHTML = `
        <div class="celebration-content">
            <div class="celebration-icon">🎉</div>
            <h2 data-i18n="onboarding.checklist.celebration.title">Congratulations!</h2>
            <p data-i18n="onboarding.checklist.celebration.message">
                You've completed all getting started tasks!
            </p>
        </div>
    `;

    document.body.appendChild(celebration);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        celebration.classList.add('fade-out');
        setTimeout(() => celebration.remove(), 500);
    }, 5000);
}

/**
 * Hide checklist permanently
 */
window.hideChecklist = async function() {
    try {
        const response = await window.authFetch('/api/onboarding/progress', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                checklist_dismissed: true
            })
        });

        if (response.ok) {
            const container = document.getElementById('onboarding-checklist-container');
            if (container) {
                container.style.display = 'none';
            }
        }
    } catch (error) {
        console.error('Failed to dismiss checklist:', error);
    }
}

/**
 * Attach event listeners to checklist items
 */
function attachChecklistEvents() {
    const actionButtons = document.querySelectorAll('.checklist-item .item-action');

    actionButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            const route = button.getAttribute('data-route');
            navigateToSection(route);
        });
    });
}

/**
 * Initialize checklist on page load
 */
window.initChecklist = async function() {
    // Check if checklist should be shown
    const checklistContainer = document.getElementById('onboarding-checklist-container');
    if (!checklistContainer) return;

    await window.renderChecklist('onboarding-checklist-container');
    await window.autoUpdateChecklist();
}
