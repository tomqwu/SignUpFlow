
async function loadInvitations() {
    if (!currentOrg) return;

    const container = document.getElementById('invitations-list');
    if (!container) return; // Should exist in index-admin.html

    container.innerHTML = '<div class="loading">Loading invitations...</div>';

    try {
        const response = await authFetch(`${API_BASE_URL}/invitations?org_id=${currentOrg.id}`);
        if (!response.ok) throw new Error('Failed to load invitations');

        const data = await response.json();
        const invitations = data.invitations || [];

        if (invitations.length === 0) {
            container.innerHTML = '<div class="empty-state">No invitations found.</div>';
            return;
        }

        let html = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Email</th>
                        <th>Name</th>
                        <th>Roles</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
        `;

        invitations.forEach(inv => {
            const statusClass = `status-${inv.status}`;
            // e.g. status-pending, status-accepted

            html += `
                <tr>
                    <td>${inv.email}</td>
                    <td>${inv.name || '-'}</td>
                    <td>${inv.roles.join(', ')}</td>
                    <td><span class="status-badge ${statusClass}">${inv.status}</span></td>
                    <td>
                        ${inv.status === 'pending' ? `
                        <button class="btn-icon danger" onclick="cancelInvitation('${inv.id}')" title="Cancel">
                            <svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" fill="none"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                        </button>
                        ` : ''}
                    </td>
                </tr>
            `;
        });

        html += '</tbody></table>';
        container.innerHTML = html;

    } catch (error) {
        console.error('Error loading invitations:', error);
        container.innerHTML = `<div class="error-state">Failed to load invitations: ${error.message}</div>`;
    }
}

async function sendInvitation(event) {
    if (event) event.preventDefault();

    if (!currentOrg) {
        showToast('Please select an organization first', 'error');
        return;
    }

    const emailInput = document.getElementById('invite-email');
    const nameInput = document.getElementById('invite-name'); // If exists
    // Role selector handling - looking for checked input
    const roleInput = document.querySelector('input[name="invite-role"]:checked');

    const email = emailInput ? emailInput.value : '';
    // name might not be in the form, defaulting to Email prefix or empty
    const name = nameInput ? nameInput.value : email.split('@')[0];
    const role = roleInput ? roleInput.value : 'volunteer';

    if (!email) {
        showToast('Please enter an email address', 'error');
        return;
    }

    try {
        const response = await authFetch(`${API_BASE_URL}/invitations?org_id=${currentOrg.id}`, {
            method: 'POST',
            body: JSON.stringify({
                email,
                name,
                roles: [role]
            })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Failed to send invitation');
        }

        showToast('Invitation sent successfully', 'success');

        // Clear form
        if (emailInput) emailInput.value = '';
        if (nameInput) nameInput.value = '';

        // Refresh list
        loadInvitations();

    } catch (error) {
        console.error('Error sending invitation:', error);
        showToast(error.message, 'error');
    }
}

// Make globally available
window.loadInvitations = loadInvitations;
window.sendInvitation = sendInvitation;
