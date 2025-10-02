// Recurring Events - Outlook-style

function toggleRecurrenceOptions() {
    const occurs = document.getElementById('event-occurs').value;
    const options = document.getElementById('recurrence-options');
    options.style.display = occurs !== 'once' ? 'block' : 'none';
}

window.createEvent = async function(event) {
    event.preventDefault();
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
    const startDate = new Date(start);
    const eventEndDate = new Date(startDate.getTime() + duration * 60 * 60 * 1000);

    try {
        if (occurs === 'once') {
            const eventId = type.toLowerCase().replace(/\s+/g, '_') + '_' + Date.now();
            const response = await fetch(API_BASE_URL + '/events/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    id: eventId, org_id: currentOrg.id, type: eventName,
                    start_time: startDate.toISOString(),
                    end_time: eventEndDate.toISOString(),
                    resource_id: location || null,
                    extra_data: { roles: roles, occurs: 'once', event_type: type }
                })
            });
            if (response.ok) {
                closeCreateEventForm();
                loadAdminEvents();
                alert('Event created!');
                document.getElementById('create-event-form').reset();
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
                    org_id: currentOrg.id, type: eventName,
                    start_time: current.toISOString(),
                    end_time: eventEndTime.toISOString(),
                    resource_id: location || null,
                    extra_data: { roles: roles, occurs: occurs, event_type: type }
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
            loadAdminEvents();
            alert('Created ' + successCount + ' recurring events!');
            document.getElementById('create-event-form').reset();
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
};

// Load roles when create event form opens
async function showCreateEventForm() {
    document.getElementById('create-event-modal').classList.remove('hidden');
    document.getElementById('create-event-form').reset();
    
    // Load org roles into the role selector
    await renderRoleSelector('event-role-selector');
}

function closeCreateEventForm() {
    document.getElementById('create-event-modal').classList.add('hidden');
}
