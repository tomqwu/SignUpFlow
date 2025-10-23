/**
 * Tutorial Overlays System
 *
 * Interactive tutorials using Intro.js for contextual learning:
 * - Event Creation Tutorial (first event creation)
 * - Team Management Tutorial (first team creation)
 * - Solver Tutorial (first solver run)
 * - Invitation Tutorial (first volunteer invitation)
 */

// Note: Using window.authFetch and window.i18n (loaded via script tags)
// No ES6 imports needed since this is loaded as a regular script

// Tutorial definitions
const TUTORIALS = {
    event_creation: {
        id: 'event_creation',
        steps: [
            {
                element: '#event-title',
                intro: 'Give your event a descriptive title (e.g., "Sunday Service 10am")',
                position: 'bottom'
            },
            {
                element: '#event-date',
                intro: 'Select the date when this event will occur',
                position: 'bottom'
            },
            {
                element: '#event-time',
                intro: 'Set the start time for this event',
                position: 'bottom'
            },
            {
                element: '#event-duration',
                intro: 'Specify how long the event will last (in minutes)',
                position: 'bottom'
            },
            {
                element: '#role-requirements',
                intro: 'Define which roles are needed and how many volunteers per role',
                position: 'top'
            },
            {
                element: '#create-event-btn',
                intro: 'Click here to create your event!',
                position: 'top'
            }
        ]
    },

    team_management: {
        id: 'team_management',
        steps: [
            {
                element: '#team-name',
                intro: 'Give your team a name (e.g., "Greeters", "Worship Team")',
                position: 'bottom'
            },
            {
                element: '#team-role',
                intro: 'Assign a role identifier for this team (e.g., "greeter", "worship")',
                position: 'bottom'
            },
            {
                element: '#team-members',
                intro: 'Add volunteers to this team. They will be available for assignments.',
                position: 'top'
            },
            {
                element: '#save-team-btn',
                intro: 'Save your team configuration',
                position: 'top'
            }
        ]
    },

    solver_tutorial: {
        id: 'solver_tutorial',
        steps: [
            {
                intro: 'Welcome to the AI Scheduling Solver! This will automatically generate fair schedules.',
                position: 'center'
            },
            {
                element: '#solver-date-range',
                intro: 'Select the date range for which you want to generate schedules',
                position: 'bottom'
            },
            {
                element: '#solver-constraints',
                intro: 'Review fairness constraints (max assignments per person, minimum gaps between assignments)',
                position: 'bottom'
            },
            {
                element: '#run-solver-btn',
                intro: 'Click here to generate your schedule! The AI will find the optimal assignment.',
                position: 'top'
            },
            {
                element: '#solver-results',
                intro: 'Review the generated schedule here. Green = assigned, Yellow = no availability, Red = conflicts.',
                position: 'top'
            }
        ]
    },

    invitation_flow: {
        id: 'invitation_flow',
        steps: [
            {
                element: '#invite-email',
                intro: 'Enter the email address of the volunteer you want to invite',
                position: 'bottom'
            },
            {
                element: '#invite-role',
                intro: 'Select what role(s) this person will have (Volunteer or Admin)',
                position: 'bottom'
            },
            {
                element: '#invite-message',
                intro: 'Add a personal message to the invitation email (optional)',
                position: 'top'
            },
            {
                element: '#send-invitation-btn',
                intro: 'Send the invitation! They will receive an email with a signup link.',
                position: 'top'
            }
        ]
    }
};

/**
 * Initialize Intro.js library
 */
function initIntroJs() {
    if (typeof introJs === 'undefined') {
        console.error('Intro.js library not loaded');
        return null;
    }
    return introJs();
}

/**
 * Start a tutorial by ID
 */
window.startTutorial = function(tutorialId) {
    const tutorial = TUTORIALS[tutorialId];
    if (!tutorial) {
        console.error(`Tutorial not found: ${tutorialId}`);
        return;
    }

    const intro = initIntroJs();
    if (!intro) return;

    intro.setOptions({
        steps: tutorial.steps,
        showProgress: true,
        showBullets: true,
        exitOnOverlayClick: false,
        doneLabel: window.i18n?.t('onboarding.tutorials.done') || 'Done',
        skipLabel: window.i18n?.t('onboarding.tutorials.skip') || 'Skip',
        nextLabel: window.i18n?.t('onboarding.tutorials.next') || 'Next',
        prevLabel: window.i18n?.t('onboarding.tutorials.prev') || 'Previous'
    });

    intro.oncomplete(() => {
        markTutorialComplete(tutorialId);
    });

    intro.onexit(() => {
        // User exited without completing
        showDismissOption(tutorialId);
    });

    intro.start();
}

/**
 * Trigger tutorial if first use
 */
window.triggerTutorialIfFirstUse = async function(tutorialId, condition = true) {
    if (!condition) return;

    try {
        const response = await window.authFetch('/api/onboarding/progress');
        if (response.ok) {
            const progress = await response.json();
            const tutorialsCompleted = progress.tutorials_completed || [];

            // Check if tutorial already completed
            if (tutorialsCompleted.includes(tutorialId)) {
                return;
            }

            // Check if user dismissed all tutorials
            if (progress.tutorials_dismissed) {
                return;
            }

            // Show tutorial after short delay (let page load)
            setTimeout(() => {
                window.startTutorial(tutorialId);
            }, 1000);
        }
    } catch (error) {
        console.error('Failed to check tutorial status:', error);
    }
}

/**
 * Mark tutorial as completed
 */
async function markTutorialComplete(tutorialId) {
    try {
        const response = await window.authFetch('/api/onboarding/progress');
        if (!response.ok) return;

        const progress = await response.json();
        const tutorialsCompleted = progress.tutorials_completed || [];

        if (!tutorialsCompleted.includes(tutorialId)) {
            tutorialsCompleted.push(tutorialId);

            await window.authFetch('/api/onboarding/progress', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    tutorials_completed: tutorialsCompleted
                })
            });

            // Show completion message
            showTutorialCompletionMessage(tutorialId);
        }
    } catch (error) {
        console.error('Failed to mark tutorial complete:', error);
    }
}

/**
 * Show tutorial completion message
 */
function showTutorialCompletionMessage(tutorialId) {
    const message = document.createElement('div');
    message.className = 'tutorial-completion-toast';
    message.innerHTML = `
        <div class="toast-content">
            <span class="toast-icon">✅</span>
            <span data-i18n="onboarding.tutorials.completed">Tutorial completed!</span>
        </div>
    `;

    document.body.appendChild(message);

    setTimeout(() => {
        message.classList.add('fade-out');
        setTimeout(() => message.remove(), 500);
    }, 3000);
}

/**
 * Show dismiss option when tutorial exited
 */
function showDismissOption(tutorialId) {
    const modal = document.createElement('div');
    modal.className = 'tutorial-dismiss-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h3 data-i18n="onboarding.tutorials.dismiss_title">Skip Tutorial?</h3>
            <p data-i18n="onboarding.tutorials.dismiss_message">
                You can always replay tutorials from the Help menu.
            </p>
            <div class="modal-actions">
                <button class="btn-secondary" id="dismiss-tutorial-later">
                    <span data-i18n="onboarding.tutorials.remind_later">Remind Me Later</span>
                </button>
                <button class="btn-secondary" id="dismiss-tutorial-forever">
                    <span data-i18n="onboarding.tutorials.dont_show">Don't Show Again</span>
                </button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    document.getElementById('dismiss-tutorial-later')?.addEventListener('click', () => {
        modal.remove();
    });

    document.getElementById('dismiss-tutorial-forever')?.addEventListener('click', async () => {
        await dismissTutorial(tutorialId, true);
        modal.remove();
    });
}

/**
 * Dismiss tutorial (don't show again)
 */
window.dismissTutorial = async function(tutorialId, permanent = false) {
    try {
        if (permanent) {
            await window.authFetch('/api/onboarding/progress', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    tutorials_dismissed: true
                })
            });
        } else {
            // Just mark as complete without showing
            await markTutorialComplete(tutorialId);
        }
    } catch (error) {
        console.error('Failed to dismiss tutorial:', error);
    }
}

/**
 * Show list of available tutorials in Help menu
 */
window.showTutorialList = function() {
    const listHtml = Object.entries(TUTORIALS).map(([id, tutorial]) => `
        <div class="tutorial-list-item">
            <span class="tutorial-name" data-i18n="onboarding.tutorials.${id}.name">
                ${id.replace('_', ' ')}
            </span>
            <button class="replay-tutorial-btn" data-tutorial-id="${id}">
                <span data-i18n="onboarding.tutorials.replay">Replay</span>
            </button>
        </div>
    `).join('');

    const modal = document.createElement('div');
    modal.className = 'tutorial-list-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h3 data-i18n="onboarding.tutorials.list_title">Available Tutorials</h3>
            <div class="tutorial-list">
                ${listHtml}
            </div>
            <button class="btn-secondary close-modal">
                <span data-i18n="common.buttons.close">Close</span>
            </button>
        </div>
    `;

    document.body.appendChild(modal);

    // Attach replay handlers
    modal.querySelectorAll('.replay-tutorial-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const tutorialId = e.target.closest('.replay-tutorial-btn').getAttribute('data-tutorial-id');
            modal.remove();
            window.startTutorial(tutorialId);
        });
    });

    modal.querySelector('.close-modal')?.addEventListener('click', () => {
        modal.remove();
    });
}

/**
 * Replay a tutorial (from Help menu)
 */
window.replayTutorial = function(tutorialId) {
    window.startTutorial(tutorialId);
}

/**
 * Get tutorial completion status
 */
window.getTutorialStatus = async function() {
    try {
        const response = await window.authFetch('/api/onboarding/progress');
        if (response.ok) {
            const progress = await response.json();
            return {
                completed: progress.tutorials_completed || [],
                dismissed: progress.tutorials_dismissed || false
            };
        }
    } catch (error) {
        console.error('Failed to get tutorial status:', error);
    }
    return { completed: [], dismissed: false };
}
