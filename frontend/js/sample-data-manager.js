/**
 * Sample Data Manager
 *
 * Handles generation and cleanup of sample data for new organizations.
 * Allows users to explore features with demo data before adding real data.
 */

// Note: Using window.authFetch and window.i18n (loaded via script tags)
// No ES6 imports needed since this is loaded as a regular script

/**
 * Generate sample data for organization
 */
window.generateSampleData = async function () {
    const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
    const orgId = currentUser.org_id;

    if (!orgId) {
        showMessage('error', 'No organization found');
        return false;
    }

    try {
        showMessage('info', 'Generating sample data...');

        const response = await window.authFetch(`/api/onboarding/sample-data/generate?org_id=${orgId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (response.ok) {
            const data = await response.json();
            showMessage('success', `Sample data generated: ${data.created.events.length} events, ${data.created.teams.length} teams, ${data.created.people.length} volunteers`);

            // Refresh current page to show new data
            setTimeout(() => {
                window.location.reload();
            }, 1500);

            return true;
        } else {
            const error = await response.json();
            showMessage('error', error.detail || 'Failed to generate sample data');
            return false;
        }
    } catch (error) {
        console.error('Failed to generate sample data:', error);
        showMessage('error', 'Failed to generate sample data');
        return false;
    }
}

/**
 * Clear all sample data for organization
 */
window.clearSampleData = async function () {
    const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
    const orgId = currentUser.org_id;

    if (!orgId) {
        showMessage('error', 'No organization found');
        return false;
    }

    // Confirm before deleting
    const confirmed = confirm(
        'Are you sure you want to remove all sample data?\n\n' +
        'This will delete all entities marked as "SAMPLE" including:\n' +
        '- Sample events\n' +
        '- Sample teams\n' +
        '- Sample volunteers\n\n' +
        'This action cannot be undone.'
    );

    if (!confirmed) return false;

    try {
        showMessage('info', 'Clearing sample data...');

        const response = await window.authFetch(`/api/onboarding/sample-data?org_id=${orgId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            const data = await response.json();
            showMessage('success', `Sample data cleared: ${data.deleted.events} events, ${data.deleted.teams} teams, ${data.deleted.people} volunteers`);

            // Refresh current page to update lists
            setTimeout(() => {
                window.location.reload();
            }, 1500);

            return true;
        } else {
            const error = await response.json();
            showMessage('error', error.detail || 'Failed to clear sample data');
            return false;
        }
    } catch (error) {
        console.error('Failed to clear sample data:', error);
        showMessage('error', 'Failed to clear sample data');
        return false;
    }
}

/**
 * Check if organization has sample data
 */
window.hasSampleData = async function () {
    const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
    const orgId = currentUser.org_id;

    if (!orgId) return false;

    try {
        const response = await window.authFetch(`/api/onboarding/sample-data/status?org_id=${orgId}`);
        if (response.ok) {
            const data = await response.json();
            return data.has_sample_data;
        }
    } catch (error) {
        console.error('Failed to check sample data status:', error);
    }

    return false;
}

/**
 * Get sample data summary counts
 */
window.getSampleDataSummary = async function () {
    const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
    const orgId = currentUser.org_id;

    if (!orgId) return null;

    try {
        const response = await window.authFetch(`/api/onboarding/sample-data/status?org_id=${orgId}`);
        if (response.ok) {
            const data = await response.json();
            return data.summary;
        }
    } catch (error) {
        console.error('Failed to get sample data summary:', error);
    }

    return null;
}

/**
 * Render sample data control panel
 */
window.renderSampleDataControls = async function (containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const hasData = await window.hasSampleData();
    const summary = await window.getSampleDataSummary();

    if (hasData) {
        // Show clear button and summary
        container.innerHTML = `
            <div class="sample-data-controls">
                <div class="sample-data-info">
                    <span class="sample-badge">SAMPLE DATA</span>
                    <p class="sample-summary">
                        ${summary.events || 0} events, ${summary.teams || 0} teams, ${summary.people || 0} volunteers
                    </p>
                </div>
                <button id="clear-sample-data" class="btn-secondary btn-sm">
                    🗑️ <span data-i18n="onboarding.sample_data.clear">Clear Sample Data</span>
                </button>
            </div>
        `;

        // Attach event listener
        const clearBtn = document.getElementById('clear-sample-data');
        if (clearBtn) {
            clearBtn.addEventListener('click', window.clearSampleData);
        }
    } else {
        // Show generate button
        container.innerHTML = `
            <div class="sample-data-controls">
                <p class="sample-data-description" data-i18n="onboarding.sample_data.description">
                    Generate sample data to explore features before adding real data
                </p>
                <button id="generate-sample-data" class="btn-primary btn-sm">
                    ✨ <span data-i18n="onboarding.sample_data.generate">Generate Sample Data</span>
                </button>
            </div>
        `;

        // Attach event listener
        const generateBtn = document.getElementById('generate-sample-data');
        if (generateBtn) {
            generateBtn.addEventListener('click', window.generateSampleData);
        }
    }
}

/**
 * Add SAMPLE badge to entity name in UI
 */
window.addSampleBadge = function (entityName, isSample) {
    if (!isSample) return entityName;

    return `<span class="sample-badge-inline" style="background: #fef3c7; color: #92400e; padding: 2px 6px; border-radius: 3px; font-size: 0.75rem; margin-right: 6px;">SAMPLE</span>${entityName}`;
}

/**
 * Show toast message
 */
function showMessage(type, message) {
    // Create toast notification
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <span class="toast-icon">${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span>
            <span class="toast-message">${message}</span>
        </div>
    `;

    document.body.appendChild(toast);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => toast.remove(), 500);
    }, 5000);
}

/**
 * Initialize sample data manager on page load
 */
window.initSampleDataManager = function () {
    // Check if sample data controls container exists
    const container = document.getElementById('sample-data-controls');
    if (container) {
        renderSampleDataControls('sample-data-controls');
    }
}
