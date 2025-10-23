/**
 * Feature Unlocks System
 *
 * Progressive disclosure of advanced features based on usage milestones:
 * - Recurring Events: Unlock after creating 3 events
 * - Manual Editing: Unlock after first solver run
 * - SMS Notifications: Unlock after 5 volunteers
 */

// Note: Using window.authFetch and window.router (loaded via script tags)
// No ES6 imports needed since this is loaded as a regular script

// Feature unlock conditions
const FEATURE_UNLOCKS = {
    recurring_events: {
        id: 'recurring_events',
        condition: async () => {
            const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
            const orgId = currentUser.org_id;
            if (!orgId) return false;

            const response = await window.authFetch(`/api/events/?org_id=${orgId}`);
            if (response.ok) {
                const events = await response.json();
                return events.length >= 3;
            }
            return false;
        },
        milestone: '3 events created',
        feature_route: '/app/events/recurring'
    },

    manual_editing: {
        id: 'manual_editing',
        condition: async () => {
            const solverRuns = localStorage.getItem('solver_runs_count') || '0';
            return parseInt(solverRuns) >= 1;
        },
        milestone: '1 schedule generated',
        feature_route: '/app/schedule/edit'
    },

    sms_notifications: {
        id: 'sms_notifications',
        condition: async () => {
            const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
            const orgId = currentUser.org_id;
            if (!orgId) return false;

            const response = await window.authFetch(`/api/people/?org_id=${orgId}`);
            if (response.ok) {
                const people = await response.json();
                return people.length >= 5;
            }
            return false;
        },
        milestone: '5 volunteers added',
        feature_route: '/app/settings/notifications'
    }
};

/**
 * Check all unlock conditions and trigger notifications
 */
window.checkUnlockConditions = async function() {
    try {
        const response = await window.authFetch('/api/onboarding/progress');
        if (!response.ok) return;

        const progress = await response.json();
        const featuresUnlocked = progress.features_unlocked || [];

        for (const [featureId, feature] of Object.entries(FEATURE_UNLOCKS)) {
            // Skip if already unlocked
            if (featuresUnlocked.includes(featureId)) {
                continue;
            }

            // Check condition
            const conditionMet = await feature.condition();

            if (conditionMet) {
                // Unlock feature
                await unlockFeature(featureId);

                // Show celebration notification
                window.showUnlockNotification(featureId, feature);
            }
        }
    } catch (error) {
        console.error('Failed to check unlock conditions:', error);
    }
}

/**
 * Check specific feature unlock condition
 */
window.checkFeatureUnlock = async function(featureId) {
    const feature = FEATURE_UNLOCKS[featureId];
    if (!feature) {
        console.error(`Feature not found: ${featureId}`);
        return false;
    }

    try {
        const response = await window.authFetch('/api/onboarding/progress');
        if (!response.ok) return false;

        const progress = await response.json();
        const featuresUnlocked = progress.features_unlocked || [];

        // Already unlocked
        if (featuresUnlocked.includes(featureId)) {
            return true;
        }

        // Check condition
        const conditionMet = await feature.condition();

        if (conditionMet) {
            await unlockFeature(featureId);
            window.showUnlockNotification(featureId, feature);
            return true;
        }

        return false;
    } catch (error) {
        console.error('Failed to check feature unlock:', error);
        return false;
    }
}

/**
 * Unlock a feature
 */
async function unlockFeature(featureId) {
    try {
        const response = await window.authFetch('/api/onboarding/progress');
        if (!response.ok) return;

        const progress = await response.json();
        const featuresUnlocked = progress.features_unlocked || [];

        if (!featuresUnlocked.includes(featureId)) {
            featuresUnlocked.push(featureId);

            await window.authFetch('/api/onboarding/progress', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    features_unlocked: featuresUnlocked
                })
            });
        }
    } catch (error) {
        console.error('Failed to unlock feature:', error);
    }
}

/**
 * Show unlock celebration notification
 */
window.showUnlockNotification = function(featureId, feature) {
    const notification = document.createElement('div');
    notification.className = 'feature-unlock-notification';
    notification.innerHTML = `
        <div class="unlock-content">
            <div class="unlock-icon">🎉</div>
            <h3 data-i18n="onboarding.unlocks.new_feature">New Feature Unlocked!</h3>
            <h4 data-i18n="onboarding.unlocks.${featureId}.name">
                ${featureId.replace('_', ' ')}
            </h4>
            <p class="unlock-milestone">
                <span data-i18n="onboarding.unlocks.milestone">Milestone:</span>
                ${feature.milestone}
            </p>
            <p data-i18n="onboarding.unlocks.${featureId}.description">
                Feature description here
            </p>
            <div class="unlock-actions">
                <button class="btn-primary explore-feature" data-route="${feature.feature_route}">
                    <span data-i18n="onboarding.unlocks.explore">Explore Feature</span>
                </button>
                <button class="btn-secondary dismiss-unlock">
                    <span data-i18n="common.buttons.dismiss">Dismiss</span>
                </button>
            </div>
        </div>
    `;

    document.body.appendChild(notification);

    // Attach event handlers
    notification.querySelector('.explore-feature')?.addEventListener('click', () => {
        const route = notification.querySelector('.explore-feature').getAttribute('data-route');
        notification.remove();
        revealFeature(featureId);
        window.router.navigate(route);
    });

    notification.querySelector('.dismiss-unlock')?.addEventListener('click', () => {
        notification.remove();
        revealFeature(featureId);
    });

    // Auto-dismiss after 30 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.classList.add('fade-out');
            setTimeout(() => notification.remove(), 500);
            revealFeature(featureId);
        }
    }, 30000);
}

/**
 * Reveal feature in UI (remove disabled state, show in menu)
 */
window.revealFeature = function(featureId) {
    switch (featureId) {
        case 'recurring_events':
            revealRecurringEvents();
            break;
        case 'manual_editing':
            revealManualEditing();
            break;
        case 'sms_notifications':
            revealSmsNotifications();
            break;
    }
}

/**
 * Reveal recurring events feature
 */
function revealRecurringEvents() {
    // Show "Recurring" tab in events page
    const recurringTab = document.querySelector('[data-feature="recurring_events"]');
    if (recurringTab) {
        recurringTab.style.display = 'block';
        showNewBadge(recurringTab, 'recurring_events');
    }

    // Enable recurring checkbox in event creation form
    const recurringCheckbox = document.getElementById('event-recurring');
    if (recurringCheckbox) {
        recurringCheckbox.disabled = false;
        recurringCheckbox.parentElement.classList.remove('disabled');
    }
}

/**
 * Reveal manual editing feature
 */
function revealManualEditing() {
    // Show "Edit Schedule" button in schedule view
    const editButton = document.querySelector('[data-feature="manual_editing"]');
    if (editButton) {
        editButton.style.display = 'inline-block';
        showNewBadge(editButton, 'manual_editing');
    }

    // Enable drag-and-drop in schedule grid
    const scheduleGrid = document.getElementById('schedule-grid');
    if (scheduleGrid) {
        scheduleGrid.classList.add('editable');
    }
}

/**
 * Reveal SMS notifications feature
 */
function revealSmsNotifications() {
    // Show SMS section in settings
    const smsSection = document.querySelector('[data-feature="sms_notifications"]');
    if (smsSection) {
        smsSection.style.display = 'block';
        showNewBadge(smsSection, 'sms_notifications');
    }

    // Enable SMS toggle in notification preferences
    const smsToggle = document.getElementById('enable-sms');
    if (smsToggle) {
        smsToggle.disabled = false;
        smsToggle.parentElement.classList.remove('disabled');
    }
}

/**
 * Show "New!" badge on feature for 7 days
 */
window.showNewBadge = function(element, featureId) {
    const unlockDate = getFeatureUnlockDate(featureId);
    if (!unlockDate) return;

    const daysSinceUnlock = Math.floor((Date.now() - unlockDate) / (1000 * 60 * 60 * 24));

    if (daysSinceUnlock <= 7) {
        const badge = document.createElement('span');
        badge.className = 'new-feature-badge';
        badge.innerHTML = '<span data-i18n="onboarding.unlocks.new_badge">New!</span>';
        element.appendChild(badge);
    }
}

/**
 * Get feature unlock date from localStorage
 */
function getFeatureUnlockDate(featureId) {
    const unlockDates = JSON.parse(localStorage.getItem('feature_unlock_dates') || '{}');
    return unlockDates[featureId] || null;
}

/**
 * Save feature unlock date
 */
function saveFeatureUnlockDate(featureId) {
    const unlockDates = JSON.parse(localStorage.getItem('feature_unlock_dates') || '{}');
    unlockDates[featureId] = Date.now();
    localStorage.setItem('feature_unlock_dates', JSON.stringify(unlockDates));
}

/**
 * Check if feature is unlocked
 */
window.isFeatureUnlocked = async function(featureId) {
    try {
        const response = await window.authFetch('/api/onboarding/progress');
        if (response.ok) {
            const progress = await response.json();
            const featuresUnlocked = progress.features_unlocked || [];
            return featuresUnlocked.includes(featureId);
        }
    } catch (error) {
        console.error('Failed to check if feature unlocked:', error);
    }
    return false;
}

/**
 * Get list of unlocked features
 */
window.getUnlockedFeatures = async function() {
    try {
        const response = await window.authFetch('/api/onboarding/progress');
        if (response.ok) {
            const progress = await response.json();
            return progress.features_unlocked || [];
        }
    } catch (error) {
        console.error('Failed to get unlocked features:', error);
    }
    return [];
}

/**
 * Initialize feature unlocks on page load
 */
window.initFeatureUnlocks = async function() {
    // Check unlock conditions
    await window.checkUnlockConditions();

    // Reveal already unlocked features
    const unlockedFeatures = await window.getUnlockedFeatures();
    unlockedFeatures.forEach(featureId => {
        window.revealFeature(featureId);
    });
}

/**
 * Manual unlock for testing/admin override
 */
window.forceUnlockFeature = async function(featureId) {
    await unlockFeature(featureId);
    const feature = FEATURE_UNLOCKS[featureId];
    if (feature) {
        window.showUnlockNotification(featureId, feature);
    }
}
