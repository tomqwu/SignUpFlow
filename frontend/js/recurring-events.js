// Recurring Events - Outlook-style

function toggleRecurrenceOptions() {
    const occurs = document.getElementById('event-occurs').value;
    const options = document.getElementById('recurrence-options');
    options.style.display = occurs !== 'once' ? 'block' : 'none';
}

window.createEvent = async function(event) {
    console.log('[recurring-events.js createEvent] Function called!');
    event.preventDefault();

    // Check if we're editing an existing event
    const form = document.getElementById('create-event-form');
    const editingEventId = form.dataset.editingEventId;

    const type = document.getElementById('event-type').value;
    const title = document.getElementById('event-title').value;
    const start = document.getElementById('event-start').value;
    const duration = parseFloat(document.getElementById('event-duration').value);
    const location = document.getElementById('event-location').value;
    // Collect checked roles from checkboxes
    const roleCheckboxes = document.querySelectorAll('#event-role-selector input[type="checkbox"]:checked');
    const occurs = document.getElementById('event-occurs').value;
    const endDate = document.getElementById('event-end-date').value;

    const eventName = title || type;
    const roles = Array.from(roleCheckboxes).map(cb => cb.value);

    // Collect role counts from number inputs
    const role_counts = {};
    roles.forEach(role => {
        const countInput = document.getElementById(`count-${role}`);
        role_counts[role] = countInput ? parseInt(countInput.value) || 1 : 1;
    });

    const startDate = new Date(start);
    const eventEndDate = new Date(startDate.getTime() + duration * 60 * 60 * 1000);

    try {
        // Handle UPDATE mode
        if (editingEventId) {
            const response = await fetch(`${API_BASE_URL}/events/${editingEventId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: eventName,
                    start_time: startDate.toISOString(),
                    end_time: eventEndDate.toISOString(),
                    resource_id: location || null,
                    extra_data: { roles: roles, role_counts: role_counts, event_type: type }
                })
            });

            if (response.ok) {
                closeCreateEventForm();
                showToast('Event updated successfully!', 'success');
                delete form.dataset.editingEventId; // Clear edit mode
                document.getElementById('create-event-form').reset();
                // Reset modal title and button
                document.querySelector('#create-event-modal h3').textContent = 'Create New Event';
                document.querySelector('#create-event-form button[type="submit"]').textContent = 'Create Event';

                if (typeof loadAdminEvents === 'function') {
                    loadAdminEvents();
                } else if (typeof loadUserData === 'function') {
                    loadUserData();
                }
            } else {
                const error = await response.json();
                showToast(`Failed to update event: ${error.detail || 'Unknown error'}`, 'error');
            }
            return;
        }

        // Handle CREATE mode
        if (occurs === 'once') {
            const eventId = type.toLowerCase().replace(/\s+/g, '_') + '_' + Date.now();
            const response = await fetch(API_BASE_URL + '/events/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    id: eventId, org_id: currentUser.org_id, type: eventName,
                    start_time: startDate.toISOString(),
                    end_time: eventEndDate.toISOString(),
                    resource_id: location || null,
                    extra_data: { roles: roles, role_counts: role_counts, occurs: 'once', event_type: type }
                })
            });
            if (response.ok) {
                closeCreateEventForm();
                showToast('Event created successfully!', 'success');
                document.getElementById('create-event-form').reset();
                // Reload admin page to show new event
                if (typeof loadAdminEvents === 'function') {
                    loadAdminEvents();
                } else if (typeof loadUserData === 'function') {
                    loadUserData();
                }
            } else {
                const error = await response.json();
                showToast(`Failed to create event: ${error.detail || 'Unknown error'}`, 'error');
            }
        } else {
            const events = [];
            const repeatUntil = endDate ? new Date(endDate) : new Date(startDate.getTime() + 365 * 24 * 60 * 60 * 1000);
            let current = new Date(startDate);
            let count = 0;

            while (current <= repeatUntil && count < 365) {
                const eventEndTime = new Date(current.getTime() + duration * 60 * 60 * 1000);
                events.push({
                    id: type.toLowerCase().replace(/\s+/g, '_') + '_' + current.getTime(),
                    org_id: currentUser.org_id, type: eventName,
                    start_time: current.toISOString(),
                    end_time: eventEndTime.toISOString(),
                    resource_id: location || null,
                    extra_data: { roles: roles, role_counts: role_counts, occurs: occurs, event_type: type }
                });

                if (occurs === 'daily') current.setDate(current.getDate() + 1);
                else if (occurs === 'weekly') current.setDate(current.getDate() + 7);
                else if (occurs === 'monthly') current.setMonth(current.getMonth() + 1);
                count++;
            }

            let successCount = 0;
            for (const evt of events) {
                const response = await fetch(API_BASE_URL + '/events/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(evt)
                });
                if (response.ok) successCount++;
            }

            closeCreateEventForm();
            showToast(`Created ${successCount} recurring events!`, 'success');
            document.getElementById('create-event-form').reset();
            if (typeof loadAdminEvents === 'function') {
                loadAdminEvents();
            } else if (typeof loadUserData === 'function') {
                loadUserData();
            }
        }
    } catch (error) {
        console.error('Event creation error:', error);
        showToast(`Error creating event: ${error.message}`, 'error');
    }
};

// Load roles when create event form opens
async function showCreateEventForm() {
    document.getElementById('create-event-modal').classList.remove('hidden');
    document.getElementById('create-event-form').reset();

    // Load org roles into the role selector with count inputs
    await renderRoleSelector('event-role-selector', true);
}

function closeCreateEventForm() {
    document.getElementById('create-event-modal').classList.add('hidden');
}
