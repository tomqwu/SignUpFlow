// Conflict Detection Module
// Check for scheduling conflicts before assigning people to events

/**
 * Check if a person has conflicts with an event
 * @param {string} personId - Person ID to check
 * @param {string} eventId - Event ID to assign to
 * @returns {Promise<Object>} Conflict check response
 */
async function checkConflicts(personId, eventId) {
    try {
        const response = await authFetch(`${API_BASE_URL}/conflicts/check`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                person_id: personId,
                event_id: eventId
            })
        });

        if (!response.ok) {
            throw new Error(`Failed to check conflicts: ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error checking conflicts:', error);
        showToast('Error checking for conflicts', 'error');
        return null;
    }
}

/**
 * Display conflicts in a modal dialog
 * @param {Array} conflicts - Array of conflict objects
 * @param {string} personName - Person's name
 * @param {Function} onConfirm - Callback if user wants to proceed anyway
 */
function showConflictsDialog(conflicts, personName, onConfirm) {
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
    `;

    const modal = document.createElement('div');
    modal.className = 'conflict-modal';
    modal.style.cssText = `
        background: white;
        border-radius: 8px;
        padding: 24px;
        max-width: 500px;
        max-height: 80vh;
        overflow-y: auto;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    `;

    // Create conflict list HTML
    const conflictItems = conflicts.map(c => {
        const iconMap = {
            'already_assigned': '⚠️',
            'time_off': '🏖️',
            'double_booked': '📅'
        };
        const icon = iconMap[c.type] || '⚠️';

        return `<li style="margin: 8px 0; padding: 8px; background: #fff3cd; border-left: 3px solid #ffc107; border-radius: 4px;">
            <strong>${icon} ${c.type.replace('_', ' ').toUpperCase()}</strong><br>
            <span style="font-size: 14px;">${c.message}</span>
        </li>`;
    }).join('');

    modal.innerHTML = `
        <div style="display: flex; align-items: center; margin-bottom: 16px;">
            <span style="font-size: 32px; margin-right: 12px;">⚠️</span>
            <h2 style="margin: 0; font-size: 20px; color: #333;">Scheduling Conflicts Detected</h2>
        </div>
        <p style="margin-bottom: 16px; color: #666;">
            <strong>${personName}</strong> has the following conflicts:
        </p>
        <ul style="list-style: none; padding: 0; margin: 0 0 20px 0;">
            ${conflictItems}
        </ul>
        <div style="display: flex; gap: 12px; justify-content: flex-end;">
            <button id="conflict-cancel" style="padding: 8px 16px; background: #6c757d; color: white; border: none; border-radius: 4px; cursor: pointer;">
                Cancel
            </button>
            ${onConfirm ? '<button id="conflict-confirm" style="padding: 8px 16px; background: #ffc107; color: #333; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">Assign Anyway</button>' : ''}
        </div>
    `;

    overlay.appendChild(modal);
    document.body.appendChild(overlay);

    // Event listeners
    const cancelBtn = modal.querySelector('#conflict-cancel');
    cancelBtn.addEventListener('click', () => {
        document.body.removeChild(overlay);
    });

    if (onConfirm) {
        const confirmBtn = modal.querySelector('#conflict-confirm');
        confirmBtn.addEventListener('click', () => {
            document.body.removeChild(overlay);
            onConfirm();
        });
    }

    // Close on overlay click
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            document.body.removeChild(overlay);
        }
    });

    // Close on Escape key
    const escapeHandler = (e) => {
        if (e.key === 'Escape') {
            document.body.removeChild(overlay);
            document.removeEventListener('keydown', escapeHandler);
        }
    };
    document.addEventListener('keydown', escapeHandler);
}

/**
 * Check conflicts and confirm before creating assignment
 * @param {string} personId - Person ID
 * @param {string} personName - Person's name
 * @param {string} eventId - Event ID
 * @param {Function} createAssignmentFn - Function to create assignment if confirmed
 */
async function checkConflictsAndConfirm(personId, personName, eventId, createAssignmentFn) {
    // Check for conflicts
    const conflictCheck = await checkConflicts(personId, eventId);

    if (!conflictCheck) {
        // Error checking conflicts - don't proceed
        return;
    }

    if (!conflictCheck.has_conflicts) {
        // No conflicts - proceed directly
        await createAssignmentFn();
        return;
    }

    // Has conflicts
    if (!conflictCheck.can_assign) {
        // Blocking conflicts (already assigned or time-off) - show dialog without "Assign Anyway"
        showConflictsDialog(conflictCheck.conflicts, personName, null);
        return;
    }

    // Non-blocking conflicts (double-booked) - allow override
    showConflictsDialog(conflictCheck.conflicts, personName, async () => {
        await createAssignmentFn();
    });
}

// Export for use in other modules
if (typeof window !== 'undefined') {
    window.checkConflicts = checkConflicts;
    window.showConflictsDialog = showConflictsDialog;
    window.checkConflictsAndConfirm = checkConflictsAndConfirm;
}
