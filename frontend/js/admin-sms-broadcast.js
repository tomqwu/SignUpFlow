/**
 * Admin SMS Broadcast Module
 */
console.log('admin-sms-broadcast.js loaded');


// Assumes authFetch, showToast, i18n, and API_BASE_URL are loaded globally

/**
 * Initialize SMS broadcast UI
 */
async function initSmsBroadcast() {
    const currentUser = JSON.parse(localStorage.getItem('currentUser') || 'null');
    if (!currentUser || !currentUser.roles.includes('admin')) {
        console.error('SMS broadcast requires admin access');
        return;
    }

    renderBroadcastInterface();
    await loadOrganizationMembers();
    await loadSmsUsageStats();
    attachBroadcastEventListeners();
}

/**
 * Render broadcast interface
 */
function renderBroadcastInterface() {
    const container = document.getElementById('sms-broadcast-container');
    if (!container) return;

    container.innerHTML = `
        <div class="sms-broadcast-section">
            <h2 data-i18n="admin.sms.broadcast_title">SMS Broadcast</h2>
            <p class="text-muted" data-i18n="admin.sms.broadcast_desc">
                Send SMS messages to multiple volunteers. Max 200 recipients per broadcast.
            </p>

            <!-- Usage Statistics -->
            <div id="sms-usage-stats" class="usage-stats-card">
                <h3 data-i18n="admin.sms.usage_stats">This Month's Usage</h3>
                <div class="stats-grid">
                    <div class="stat-item">
                        <span class="stat-label" data-i18n="admin.sms.messages_sent">Messages Sent:</span>
                        <span id="total-messages-sent" class="stat-value">-</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label" data-i18n="admin.sms.total_cost">Total Cost:</span>
                        <span id="total-cost" class="stat-value">-</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label" data-i18n="admin.sms.budget_remaining">Budget Remaining:</span>
                        <span id="budget-remaining" class="stat-value">-</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label" data-i18n="admin.sms.budget_utilization">Budget Utilization:</span>
                        <div class="progress-container">
                            <div id="budget-progress-bar" class="progress-bar" style="width: 0%"></div>
                            <span id="budget-percentage" class="progress-text">0%</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Broadcast Form -->
            <div class="broadcast-form-card">
                <h3 data-i18n="admin.sms.compose_broadcast">Compose Broadcast</h3>

                <!-- Recipient Selection -->
                <div class="form-group">
                    <label data-i18n="admin.sms.recipients">Recipients</label>

                    <!-- Quick Filters -->
                    <div class="recipient-filters">
                        <button id="select-all-volunteers" class="btn btn-sm btn-secondary" data-i18n="admin.sms.select_all">
                            Select All Volunteers
                        </button>
                        <button id="select-verified-only" class="btn btn-sm btn-secondary" data-i18n="admin.sms.select_verified">
                            Select Verified Only
                        </button>
                        <button id="select-by-team" class="btn btn-sm btn-secondary" data-i18n="admin.sms.select_by_team">
                            Select by Team
                        </button>
                        <button id="clear-selection" class="btn btn-sm btn-outline" data-i18n="admin.sms.clear_selection">
                            Clear Selection
                        </button>
                    </div>

                    <!-- Recipient List -->
                    <div id="recipient-list" class="recipient-list">
                        <p class="text-muted" data-i18n="admin.sms.loading_volunteers">Loading volunteers...</p>
                    </div>

                    <div class="selection-summary">
                        <span data-i18n="admin.sms.selected">Selected:</span>
                        <strong id="selected-count">0</strong>
                        <span data-i18n="admin.sms.of">of</span>
                        <span id="total-count">0</span>
                        <span data-i18n="admin.sms.volunteers">volunteers</span>
                    </div>
                </div>

                <!-- Message Composition -->
                <div class="form-group">
                    <label for="broadcast-message" data-i18n="admin.sms.message">Message</label>
                    <textarea
                        id="broadcast-message"
                        class="form-control"
                        rows="5"
                        maxlength="1600"
                        placeholder="Type your message here..."
                        data-i18n-placeholder="admin.sms.message_placeholder"></textarea>
                    <div class="message-info">
                        <small class="text-muted">
                            <span id="char-count">0</span>/1600 characters
                            (<span id="segment-count">0</span> SMS segments)
                        </small>
                    </div>
                </div>

                <!-- Message Options -->
                <div class="form-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="is-urgent-checkbox">
                        <span data-i18n="admin.sms.mark_urgent">Mark as Urgent</span>
                        <small class="text-muted" data-i18n="admin.sms.urgent_desc">
                            Urgent messages bypass rate limits (use sparingly)
                        </small>
                    </label>
                </div>

                <!-- Cost Estimation -->
                <div class="cost-estimation">
                    <h4 data-i18n="admin.sms.cost_estimate">Cost Estimate</h4>
                    <div class="cost-breakdown">
                        <p>
                            <span data-i18n="admin.sms.estimated_cost">Estimated Cost:</span>
                            <strong id="estimated-cost">$0.00</strong>
                        </p>
                        <small class="text-muted" data-i18n="admin.sms.cost_note">
                            Based on selected recipients and message length. Actual cost may vary.
                        </small>
                    </div>
                </div>

                <!-- Send Button -->
                <div class="form-actions">
                    <button id="send-broadcast-btn" class="btn btn-primary" disabled data-i18n="admin.sms.send_broadcast">
                        Send Broadcast
                    </button>
                    <button id="preview-broadcast-btn" class="btn btn-secondary" data-i18n="admin.sms.preview">
                        Preview
                    </button>
                </div>
            </div>

            <!-- Team Selection Modal (hidden) -->
            <div id="team-selection-modal" class="modal" style="display: none;">
                <div class="modal-content">
                    <h3 data-i18n="admin.sms.select_team">Select Team</h3>
                    <div id="team-list" class="team-list"></div>
                    <div class="modal-actions">
                        <button id="apply-team-filter" class="btn btn-primary" data-i18n="common.buttons.apply">Apply</button>
                        <button id="cancel-team-filter" class="btn btn-secondary" data-i18n="common.buttons.cancel">Cancel</button>
                    </div>
                </div>
            </div>

            <!-- Preview Modal (hidden) -->
            <div id="preview-modal" class="modal" style="display: none;">
                <div class="modal-content">
                    <h3 data-i18n="admin.sms.preview_title">Broadcast Preview</h3>
                    <div class="preview-content">
                        <p><strong data-i18n="admin.sms.preview_recipients">Recipients:</strong> <span id="preview-recipient-count"></span></p>
                        <p><strong data-i18n="admin.sms.preview_message">Message:</strong></p>
                        <div class="message-preview" id="preview-message-text"></div>
                        <p><strong data-i18n="admin.sms.preview_cost">Estimated Cost:</strong> <span id="preview-cost"></span></p>
                    </div>
                    <div class="modal-actions">
                        <button id="confirm-send" class="btn btn-primary" data-i18n="admin.sms.confirm_send">Confirm & Send</button>
                        <button id="close-preview" class="btn btn-secondary" data-i18n="common.buttons.close">Close</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Re-translate
    if (window.translatePage) {
        window.translatePage();
    }
}

/**
 * Load organization members
 */
async function loadOrganizationMembers() {
    const currentUser = JSON.parse(localStorage.getItem('currentUser') || 'null');
    if (!currentUser) return;

    try {
        const response = await authFetch(`${API_BASE_URL}/api/people/?org_id=${currentUser.org_id}`);
        if (!response.ok) {
            throw new Error('Failed to load volunteers');
        }

        const people = await response.json();
        renderRecipientList(people);

    } catch (error) {
        console.error('Error loading volunteers:', error);
        showToast(i18n.t('messages.error.load_failed'), 'error');
    }
}

/**
 * Render recipient list with checkboxes
 */
function renderRecipientList(people) {
    const container = document.getElementById('recipient-list');
    if (!container) return;

    const volunteers = people.filter(p => p.roles.includes('volunteer'));

    if (volunteers.length === 0) {
        container.innerHTML = `<p class="text-muted" data-i18n="admin.sms.no_volunteers">No volunteers found</p>`;
        return;
    }

    container.innerHTML = volunteers.map(person => {
        const hasPhone = person.sms_preferences?.phone_number;
        const isVerified = person.sms_preferences?.verified;
        const isOptedOut = person.sms_preferences?.opt_out_date !== null;

        const canReceiveSms = hasPhone && isVerified && !isOptedOut;

        return `
            <label class="recipient-item ${!canReceiveSms ? 'disabled' : ''}">
                <input
                    type="checkbox"
                    class="recipient-checkbox"
                    data-person-id="${person.id}"
                    ${!canReceiveSms ? 'disabled' : ''}>
                <span class="recipient-name">${person.name}</span>
                ${!hasPhone ? '<span class="badge badge-secondary">No Phone</span>' : ''}
                ${hasPhone && !isVerified ? '<span class="badge badge-warning">Not Verified</span>' : ''}
                ${isOptedOut ? '<span class="badge badge-danger">Opted Out</span>' : ''}
                ${canReceiveSms ? '<span class="badge badge-success">Can Receive SMS</span>' : ''}
            </label>
        `;
    }).join('');

    // Update total count
    document.getElementById('total-count').textContent = volunteers.filter(p =>
        p.sms_preferences?.verified && !p.sms_preferences?.opt_out_date
    ).length;

    // Re-translate
    if (window.translatePage) {
        window.translatePage();
    }
}

/**
 * Load SMS usage statistics
 */
async function loadSmsUsageStats() {
    const currentUser = JSON.parse(localStorage.getItem('currentUser') || 'null');
    if (!currentUser) return;

    try {
        const response = await authFetch(`${API_BASE_URL}/api/organizations/${currentUser.org_id}/sms-usage`);
        if (!response.ok) {
            // If endpoint doesn't exist yet, show defaults
            renderUsageStats({
                total_messages: 0,
                total_cost_cents: 0,
                budget_limit_cents: 10000,
                utilization_percent: 0
            });
            return;
        }

        const stats = await response.json();
        renderUsageStats(stats);

    } catch (error) {
        console.error('Error loading usage stats:', error);
    }
}

/**
 * Render usage statistics
 */
function renderUsageStats(stats) {
    const totalMessages = stats.total_messages || 0;
    const totalCostCents = stats.total_cost_cents || 0;
    const budgetLimitCents = stats.budget_limit_cents || 10000;
    const utilizationPercent = stats.utilization_percent || 0;

    document.getElementById('total-messages-sent').textContent = totalMessages;
    document.getElementById('total-cost').textContent = `$${(totalCostCents / 100).toFixed(2)}`;
    document.getElementById('budget-remaining').textContent =
        `$${((budgetLimitCents - totalCostCents) / 100).toFixed(2)}`;

    // Update progress bar
    const progressBar = document.getElementById('budget-progress-bar');
    const progressText = document.getElementById('budget-percentage');

    if (progressBar && progressText) {
        progressBar.style.width = `${Math.min(utilizationPercent, 100)}%`;
        progressText.textContent = `${utilizationPercent.toFixed(1)}%`;

        // Color code based on utilization
        if (utilizationPercent >= 100) {
            progressBar.className = 'progress-bar progress-bar-danger';
        } else if (utilizationPercent >= 80) {
            progressBar.className = 'progress-bar progress-bar-warning';
        } else {
            progressBar.className = 'progress-bar progress-bar-success';
        }
    }
}

/**
 * Attach event listeners
 */
function attachBroadcastEventListeners() {
    // Message textarea character count
    document.addEventListener('input', (e) => {
        if (e.target.id === 'broadcast-message') {
            updateCharacterCount();
            updateEstimatedCost();
            updateSendButtonState();
        }
    });

    // Recipient checkboxes
    document.addEventListener('change', (e) => {
        if (e.target.classList.contains('recipient-checkbox')) {
            updateSelectedCount();
            updateEstimatedCost();
            updateSendButtonState();
        }
    });

    // Select all volunteers
    document.addEventListener('click', (e) => {
        if (e.target.id === 'select-all-volunteers') {
            selectAllRecipients();
        }
    });

    // Select verified only
    document.addEventListener('click', (e) => {
        if (e.target.id === 'select-verified-only') {
            selectVerifiedOnly();
        }
    });

    // Clear selection
    document.addEventListener('click', (e) => {
        if (e.target.id === 'clear-selection') {
            clearSelection();
        }
    });

    // Send broadcast
    document.addEventListener('click', async (e) => {
        if (e.target.id === 'send-broadcast-btn') {
            await sendBroadcast();
        }
    });

    // Preview broadcast
    document.addEventListener('click', (e) => {
        if (e.target.id === 'preview-broadcast-btn') {
            showPreviewModal();
        }
    });

    // Confirm send from preview
    document.addEventListener('click', async (e) => {
        if (e.target.id === 'confirm-send') {
            closePreviewModal();
            await sendBroadcast();
        }
    });

    // Close preview
    document.addEventListener('click', (e) => {
        if (e.target.id === 'close-preview') {
            closePreviewModal();
        }
    });
}

/**
 * Update character count
 */
function updateCharacterCount() {
    const textarea = document.getElementById('broadcast-message');
    if (!textarea) return;

    const charCount = textarea.value.length;
    const segments = calculateSegments(textarea.value);

    document.getElementById('char-count').textContent = charCount;
    document.getElementById('segment-count').textContent = segments;
}

/**
 * Calculate SMS segments
 */
function calculateSegments(text) {
    const length = text.length;
    if (length === 0) return 0;
    if (length <= 160) return 1;
    return Math.ceil(length / 153); // Multi-part messages use 153 chars per segment
}

/**
 * Update selected recipient count
 */
function updateSelectedCount() {
    const checkboxes = document.querySelectorAll('.recipient-checkbox:checked');
    document.getElementById('selected-count').textContent = checkboxes.length;
}

/**
 * Update estimated cost
 */
function updateEstimatedCost() {
    const message = document.getElementById('broadcast-message')?.value || '';
    const checkboxes = document.querySelectorAll('.recipient-checkbox:checked');

    const segments = calculateSegments(message);
    const recipients = checkboxes.length;
    const costPerSegment = 0.01; // $0.01 per segment (simplified from $0.0079)

    const totalCost = segments * recipients * costPerSegment;

    document.getElementById('estimated-cost').textContent = `$${totalCost.toFixed(2)}`;
}

/**
 * Update send button state
 */
function updateSendButtonState() {
    const sendBtn = document.getElementById('send-broadcast-btn');
    if (!sendBtn) return;

    const message = document.getElementById('broadcast-message')?.value || '';
    const checkboxes = document.querySelectorAll('.recipient-checkbox:checked');

    const hasMessage = message.trim().length > 0;
    const hasRecipients = checkboxes.length > 0;
    const withinLimit = checkboxes.length <= 200;

    sendBtn.disabled = !(hasMessage && hasRecipients && withinLimit);

    if (!withinLimit) {
        sendBtn.textContent = 'Too Many Recipients (max 200)';
        sendBtn.classList.add('btn-danger');
    } else {
        sendBtn.textContent = i18n.t('admin.sms.send_broadcast') || 'Send Broadcast';
        sendBtn.classList.remove('btn-danger');
    }
}

/**
 * Select all recipients
 */
function selectAllRecipients() {
    const checkboxes = document.querySelectorAll('.recipient-checkbox:not(:disabled)');
    checkboxes.forEach(cb => cb.checked = true);
    updateSelectedCount();
    updateEstimatedCost();
    updateSendButtonState();
}

/**
 * Select verified only
 */
function selectVerifiedOnly() {
    const checkboxes = document.querySelectorAll('.recipient-checkbox:not(:disabled)');
    checkboxes.forEach(cb => cb.checked = true);
    updateSelectedCount();
    updateEstimatedCost();
    updateSendButtonState();
}

/**
 * Clear selection
 */
function clearSelection() {
    const checkboxes = document.querySelectorAll('.recipient-checkbox');
    checkboxes.forEach(cb => cb.checked = false);
    updateSelectedCount();
    updateEstimatedCost();
    updateSendButtonState();
}

/**
 * Show preview modal
 */
function showPreviewModal() {
    const message = document.getElementById('broadcast-message')?.value || '';
    const checkboxes = document.querySelectorAll('.recipient-checkbox:checked');
    const estimatedCost = document.getElementById('estimated-cost')?.textContent || '$0.00';

    document.getElementById('preview-recipient-count').textContent = checkboxes.length;
    document.getElementById('preview-message-text').textContent = message;
    document.getElementById('preview-cost').textContent = estimatedCost;

    document.getElementById('preview-modal').style.display = 'flex';
}

/**
 * Close preview modal
 */
function closePreviewModal() {
    document.getElementById('preview-modal').style.display = 'none';
}

/**
 * Send broadcast message
 */
async function sendBroadcast() {
    const message = document.getElementById('broadcast-message')?.value || '';
    const isUrgent = document.getElementById('is-urgent-checkbox')?.checked || false;
    const checkboxes = document.querySelectorAll('.recipient-checkbox:checked');

    const recipientIds = Array.from(checkboxes).map(cb => {
        const personId = cb.dataset.personId;
        return parseInt(personId.split('_').pop()); // Extract numeric ID
    });

    if (recipientIds.length === 0) {
        showToast(i18n.t('messages.error.no_recipients'), 'error');
        return;
    }

    if (recipientIds.length > 200) {
        showToast(i18n.t('messages.error.too_many_recipients'), 'error');
        return;
    }

    try {
        const response = await authFetch(`${API_BASE_URL}/api/sms/send-broadcast`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                recipient_ids: recipientIds,
                message_text: message,
                is_urgent: isUrgent
            })
        });

        if (!response.ok) {
            throw new Error('Failed to send broadcast');
        }

        const result = await response.json();

        showToast(
            i18n.t('messages.success.broadcast_sent') ||
            `Broadcast sent to ${result.queued_count} recipients`,
            'success'
        );

        // Clear form
        document.getElementById('broadcast-message').value = '';
        clearSelection();
        updateCharacterCount();

        // Reload usage stats
        await loadSmsUsageStats();

    } catch (error) {
        console.error('Error sending broadcast:', error);
        showToast(i18n.t('messages.error.broadcast_failed'), 'error');
    }
}

// Expose functions globally for non-module scripts
window.initSmsBroadcast = initSmsBroadcast;
window.loadOrganizationMembers = loadOrganizationMembers;
window.loadSmsUsageStats = loadSmsUsageStats;
window.sendBroadcast = sendBroadcast;
