/**
 * Recurring Events UI Module
 *
 * Implements comprehensive recurring event creation UI with:
 * - Pattern selection (weekly, biweekly, monthly, custom)
 * - Day selection for weekly patterns
 * - Monthly pattern configuration (Nth weekday)
 * - End conditions (date, count, indefinite)
 * - Calendar preview with real-time updates
 * - Holiday conflict detection
 *
 * Spec: 006-recurring-events-ui
 */

// State management
let calendarPreviewData = [];
let isLoadingPreview = false;

/**
 * Initialize recurring events UI when checkbox is clicked
 */
function initRecurringEventsUI() {
    const checkbox = document.getElementById('is-recurring');
    if (!checkbox) return;

    checkbox.addEventListener('change', (e) => {
        toggleRecurringOptions(e.target.checked);
    });

    // Initialize pattern type change handler
    const patternType = document.getElementById('recurrence-pattern');
    if (patternType) {
        patternType.addEventListener('change', updatePatternOptions);
    }

    // Initialize end condition change handler
    const endCondition = document.getElementById('end-condition');
    if (endCondition) {
        endCondition.addEventListener('change', updateEndConditionFields);
    }

    // Initialize preview trigger on all relevant fields
    attachPreviewTriggers();
}

/**
 * Show/hide recurring options based on checkbox state
 */
function toggleRecurringOptions(isRecurring) {
    const container = document.getElementById('recurring-options-container');
    if (!container) return;

    container.style.display = isRecurring ? 'block' : 'none';

    if (isRecurring) {
        // Reset to default pattern
        document.getElementById('recurrence-pattern').value = 'weekly';
        updatePatternOptions();
        // Trigger initial preview
        updateCalendarPreview();
    } else {
        // Clear preview
        calendarPreviewData = [];
        renderCalendarPreview([]);
    }
}

/**
 * Update pattern-specific options when pattern type changes
 */
function updatePatternOptions() {
    const patternType = document.getElementById('recurrence-pattern').value;

    // Hide all pattern-specific options
    document.getElementById('weekly-options').style.display = 'none';
    document.getElementById('monthly-options').style.display = 'none';
    document.getElementById('custom-options').style.display = 'none';

    // Show relevant options based on pattern
    if (patternType === 'weekly' || patternType === 'biweekly') {
        document.getElementById('weekly-options').style.display = 'block';
    } else if (patternType === 'monthly') {
        document.getElementById('monthly-options').style.display = 'block';
    } else if (patternType === 'custom') {
        document.getElementById('custom-options').style.display = 'block';
    }

    // Update preview
    updateCalendarPreview();
}

/**
 * Update end condition fields based on selection
 */
function updateEndConditionFields() {
    const endCondition = document.getElementById('end-condition').value;

    document.getElementById('end-date-field').style.display =
        endCondition === 'date' ? 'block' : 'none';
    document.getElementById('occurrence-count-field').style.display =
        endCondition === 'count' ? 'block' : 'none';

    // Update preview
    updateCalendarPreview();
}

/**
 * Attach change listeners to all fields that should trigger preview update
 */
function attachPreviewTriggers() {
    const triggerFields = [
        'recurrence-pattern',
        'end-condition',
        'end-date',
        'occurrence-count',
        'custom-interval',
        'event-start'
    ];

    triggerFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            field.addEventListener('change', debounce(updateCalendarPreview, 300));
        }
    });

    // Day checkboxes
    const dayCheckboxes = document.querySelectorAll('#day-selection input[type="checkbox"]');
    dayCheckboxes.forEach(cb => {
        cb.addEventListener('change', debounce(updateCalendarPreview, 300));
    });

    // Monthly pattern fields
    const monthlyFields = ['weekday-position', 'weekday-name'];
    monthlyFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            field.addEventListener('change', debounce(updateCalendarPreview, 300));
        }
    });
}

/**
 * Debounce helper to avoid excessive preview updates
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Update calendar preview by calling preview API
 */
async function updateCalendarPreview() {
    if (!document.getElementById('is-recurring').checked) {
        return;
    }

    if (isLoadingPreview) {
        return; // Avoid concurrent requests
    }

    try {
        isLoadingPreview = true;
        showPreviewLoading();

        const previewData = collectPreviewData();
        if (!previewData) {
            renderCalendarPreview([]);
            return;
        }

        const response = await authFetch(
            `${API_BASE_URL}/recurring-series/preview?org_id=${currentUser.org_id}`,
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(previewData)
            }
        );

        if (response.ok) {
            const occurrences = await response.json();
            calendarPreviewData = occurrences;
            renderCalendarPreview(occurrences);

            // Show warning if too many occurrences
            if (occurrences.length >= 100) {
                showPreviewWarning(occurrences.length);
            }
        } else {
            const error = await response.json();
            showPreviewError(error.detail || 'Failed to generate preview');
        }
    } catch (error) {
        console.error('Preview error:', error);
        showPreviewError(error.message);
    } finally {
        isLoadingPreview = false;
    }
}

/**
 * Collect form data for preview request
 */
function collectPreviewData() {
    const patternType = document.getElementById('recurrence-pattern').value;
    const startDate = document.getElementById('event-start').value;
    const duration = parseInt(document.getElementById('event-duration').value) * 60; // Convert hours to minutes

    if (!startDate) {
        return null; // Can't preview without start date
    }

    const startDateTime = new Date(startDate);
    const data = {
        pattern_type: patternType,
        start_date: startDateTime.toISOString().split('T')[0], // YYYY-MM-DD
        start_time: startDateTime.toISOString().split('T')[1].substring(0, 8), // HH:MM:SS
        duration: duration,
        end_condition_type: document.getElementById('end-condition').value
    };

    // Pattern-specific data
    if (patternType === 'weekly' || patternType === 'biweekly') {
        const selectedDays = Array.from(
            document.querySelectorAll('#day-selection input[type="checkbox"]:checked')
        ).map(cb => cb.value);
        data.selected_days = selectedDays;
    } else if (patternType === 'monthly') {
        data.weekday_position = document.getElementById('weekday-position').value;
        data.weekday_name = document.getElementById('weekday-name').value;
    } else if (patternType === 'custom') {
        data.frequency_interval = parseInt(document.getElementById('custom-interval').value);
        const selectedDays = Array.from(
            document.querySelectorAll('#day-selection input[type="checkbox"]:checked')
        ).map(cb => cb.value);
        data.selected_days = selectedDays;
    }

    // End condition data
    if (data.end_condition_type === 'date') {
        const endDate = document.getElementById('end-date').value;
        data.end_date = endDate || null;
    } else if (data.end_condition_type === 'count') {
        data.occurrence_count = parseInt(document.getElementById('occurrence-count').value) || 10;
    }

    return data;
}

/**
 * Render calendar preview
 */
function renderCalendarPreview(occurrences) {
    const container = document.getElementById('calendar-preview');
    if (!container) return;

    if (occurrences.length === 0) {
        container.innerHTML = '<p class="preview-empty">Select pattern options to see preview</p>';
        return;
    }

    const maxDisplay = 10; // Show first 10 occurrences
    const displayOccurrences = occurrences.slice(0, maxDisplay);

    let html = `<div class="preview-list">`;
    html += `<h4>Upcoming Occurrences (showing ${displayOccurrences.length} of ${occurrences.length})</h4>`;
    html += `<ul>`;

    displayOccurrences.forEach(occ => {
        const date = new Date(occ.start_time);
        const dateStr = date.toLocaleDateString();
        const timeStr = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const warningClass = occ.is_holiday_conflict ? 'holiday-warning' : '';

        html += `<li class="${warningClass}">`;
        html += `<strong>#${occ.occurrence_sequence}</strong>: ${dateStr} at ${timeStr}`;
        if (occ.is_holiday_conflict && occ.holiday_label) {
            html += ` <span class="warning-badge">⚠️ ${occ.holiday_label}</span>`;
        }
        html += `</li>`;
    });

    html += `</ul>`;

    if (occurrences.length > maxDisplay) {
        html += `<p class="preview-note">+ ${occurrences.length - maxDisplay} more occurrences...</p>`;
    }

    html += `</div>`;
    container.innerHTML = html;
}

/**
 * Show preview loading state
 */
function showPreviewLoading() {
    const container = document.getElementById('calendar-preview');
    if (container) {
        container.innerHTML = '<p class="preview-loading">Loading preview...</p>';
    }
}

/**
 * Show preview warning for large series
 */
function showPreviewWarning(count) {
    const warningDiv = document.getElementById('preview-warning');
    if (warningDiv) {
        warningDiv.style.display = 'block';
        warningDiv.innerHTML = `⚠️ This pattern generates ${count} occurrences. Consider using a shorter duration or fewer repetitions.`;
    }
}

/**
 * Show preview error
 */
function showPreviewError(message) {
    const container = document.getElementById('calendar-preview');
    if (container) {
        container.innerHTML = `<p class="preview-error">Preview error: ${message}</p>`;
    }
}

// Export functions for global access
window.initRecurringEventsUI = initRecurringEventsUI;
window.toggleRecurringOptions = toggleRecurringOptions;
window.updateCalendarPreview = updateCalendarPreview;
