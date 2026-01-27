// Role Management System
// Handles custom roles per organization

// Default roles if org hasn't customized
const DEFAULT_ROLES = [
    'volunteer',
    'leader',
    'musician',
    'tech',
    'childcare',
    'hospitality',
    'admin'
];

// Load roles from organization config
// Load roles from organization config
async function loadOrgRoles() {
    try {
        if (!currentUser || !currentUser.org_id) {
            console.warn('No current user or org ID, skipping role load');
            return DEFAULT_ROLES;
        }
        const response = await authFetch(`${API_BASE_URL}/organizations/${currentUser.org_id}`);

        if (response.status === 404) {
            console.warn('Organization not found in loadOrgRoles, logging out...');
            // Clear session and redirect
            localStorage.removeItem('authToken');
            localStorage.removeItem('currentUser');
            localStorage.removeItem('currentOrg');
            window.location.href = '/';
            return DEFAULT_ROLES;
        }

        if (response.ok) {
            const data = await response.json();
            // Try custom_roles first, then roles, then default
            const roles = data.config?.custom_roles || data.config?.roles || DEFAULT_ROLES;
            currentOrg.customRoles = roles;
            return roles;
        }
    } catch (error) {
        console.error('Error loading roles:', error);
    }
    return DEFAULT_ROLES;
}

// Render role checkboxes dynamically
async function renderRoleSelector(containerId, includeCount = false) {
    const roles = await loadOrgRoles();
    const container = document.getElementById(containerId);

    if (includeCount) {
        // For event creation - include count input
        container.innerHTML = roles.map(role => `
            <label class="role-option role-option-with-count">
                <input type="checkbox" value="${role}" onchange="toggleRoleCount('${role}')">
                ${capitalizeRole(role)}
                <input type="number" id="count-${role}" min="1" max="10" value="1"
                       style="width: 50px; margin-left: 10px; display: none;"
                       placeholder="# needed">
            </label>
        `).join('');
    } else {
        // For settings/people - just checkboxes
        container.innerHTML = roles.map(role => `
            <label class="role-option">
                <input type="checkbox" value="${role}">
                ${capitalizeRole(role)}
            </label>
        `).join('');
    }
}

// Toggle role count input visibility
function toggleRoleCount(role) {
    const checkbox = document.querySelector(`input[type="checkbox"][value="${role}"]`);
    const countInput = document.getElementById(`count-${role}`);
    if (countInput) {
        countInput.style.display = checkbox.checked ? 'inline-block' : 'none';
    }
}

// Translate and capitalize role names for display
function capitalizeRole(role) {
    // Use translateRole() if available (from app-user.js)
    if (typeof translateRole === 'function') {
        return translateRole(role);
    }
    // Fallback: capitalize the role name
    return role.split(/[-_]/).map(word =>
        word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
}

// Admin: Show add role form
function showAddRoleForm() {
    document.getElementById('add-role-modal').classList.remove('hidden');
    document.getElementById('role-name').value = '';
    document.getElementById('role-description').value = '';
}

// Admin: Close add role form
function closeAddRoleForm() {
    document.getElementById('add-role-modal').classList.add('hidden');
}

// Admin: Add custom role
async function addCustomRole(event) {
    event.preventDefault();

    const roleName = document.getElementById('role-name').value.trim().toLowerCase().replace(/\s+/g, '-');
    const roleDescription = document.getElementById('role-description').value.trim();

    try {
        // Load current org config
        const orgResponse = await authFetch(`${API_BASE_URL}/organizations/${currentUser.org_id}`);
        const orgData = await orgResponse.json();

        // Get current roles or default
        const currentRoles = orgData.config?.custom_roles || DEFAULT_ROLES;

        // Check if role already exists
        if (currentRoles.includes(roleName)) {
            showToast('This role already exists!', 'warning');
            return;
        }

        // Add new role
        const updatedRoles = [...currentRoles, roleName];

        // Update org config
        const updateResponse = await authFetch(`${API_BASE_URL}/organizations/${currentUser.org_id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                config: {
                    ...(orgData.config || {}),
                    custom_roles: updatedRoles,
                    role_descriptions: {
                        ...(orgData.config?.role_descriptions || {}),
                        [roleName]: roleDescription
                    }
                }
            })
        });

        if (updateResponse.ok) {
            showToast('Role added successfully!', 'success');
            closeAddRoleForm();
            loadAdminRoles();

            // Refresh role selectors
            await renderRoleSelector('role-selector');
            await renderRoleSelector('settings-role-selector');
        } else {
            const error = await updateResponse.json();
            alert(`Error: ${error.detail}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// Admin: Load roles list
async function loadAdminRoles() {
    const listEl = document.getElementById('admin-roles-list');
    listEl.innerHTML = '<div class="loading">Loading roles...</div>';

    try {
        const roles = await loadOrgRoles();
        const orgResponse = await authFetch(`${API_BASE_URL}/organizations/${currentOrg.id}`);
        const orgData = await orgResponse.json();
        const descriptions = orgData.config?.role_descriptions || {};

        // Fetch people to count role assignments
        const peopleResponse = await authFetch(`${API_BASE_URL}/people/?org_id=${currentOrg.id}`);
        const peopleData = await peopleResponse.json();
        const people = peopleData.people || [];

        // Count people per role
        const roleStats = {};
        roles.forEach(role => {
            roleStats[role] = people.filter(p => p.roles && p.roles.includes(role)).length;
        });

        // Define role colors for visual identification
        const roleColors = {
            'volunteer': '#3b82f6',
            'admin': '#f59e0b',
            'leader': '#8b5cf6',
            'musician': '#ec4899',
            'tech': '#10b981',
            'childcare': '#f97316',
            'hospitality': '#06b6d4'
        };

        listEl.innerHTML = roles.map(role => {
            const color = roleColors[role] || '#64748b';
            const count = roleStats[role] || 0;

            return `
            <div class="role-item">
                <div class="role-info">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div style="width: 12px; height: 12px; border-radius: 50%; background: ${color};"></div>
                        <h4>${capitalizeRole(role)}</h4>
                    </div>
                    <p class="role-description">${descriptions[role] || 'No description'}</p>
                    <div style="margin-top: 8px; font-size: 0.9rem; color: var(--text-light);">
                        ${count} ${count === 1 ? 'person has' : 'people have'} this role
                    </div>
                </div>
                <div style="display: flex; gap: 8px;">
                    <button class="btn btn-secondary btn-sm" onclick="showEditRoleModal('${role}', '${(descriptions[role] || '').replace(/'/g, "\\'")}')">Edit</button>
                    <button class="btn btn-secondary btn-sm" onclick="showManageRolePeopleModal('${role}')">Manage People</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteRole('${role}')">Delete</button>
                </div>
            </div>
        `}).join('');
    } catch (error) {
        listEl.innerHTML = `<div class="loading">Error: ${error.message}</div>`;
    }
}

// Admin: Delete role
async function deleteRole(roleName) {
    showConfirmDialog(`Are you sure you want to delete the "${capitalizeRole(roleName)}" role?`, async (confirmed) => {
        if (!confirmed) return;

        // Check if it's a default role
        if (DEFAULT_ROLES.includes(roleName)) {
            showConfirmDialog('This is a default role. Deleting it may affect system functionality. Continue?', async (confirmedAgain) => {
                if (!confirmedAgain) return;
                await performDeleteRole(roleName);
            });
        } else {
            await performDeleteRole(roleName);
        }
    });
}

// Helper function to perform the actual role deletion
async function performDeleteRole(roleName) {

    try {
        // Load current org config
        const orgResponse = await authFetch(`${API_BASE_URL}/organizations/${currentUser.org_id}`);
        const orgData = await orgResponse.json();

        // Remove role
        const currentRoles = orgData.config?.custom_roles || DEFAULT_ROLES;
        const updatedRoles = currentRoles.filter(r => r !== roleName);

        // Remove description
        const descriptions = orgData.config?.role_descriptions || {};
        delete descriptions[roleName];

        // Update org config
        const updateResponse = await authFetch(`${API_BASE_URL}/organizations/${currentUser.org_id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                config: {
                    ...(orgData.config || {}),
                    custom_roles: updatedRoles,
                    role_descriptions: descriptions
                }
            })
        });

        if (updateResponse.ok) {
            showToast('Role deleted successfully!', 'success');
            loadAdminRoles();

            // Refresh role selectors
            await renderRoleSelector('role-selector');
            await renderRoleSelector('settings-role-selector');
        } else {
            const error = await updateResponse.json();
            showToast(`Error: ${error.detail}`, 'error');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

// Initialize roles on page load
document.addEventListener('DOMContentLoaded', async () => {
    // Wait a bit for currentOrg to be set
    setTimeout(async () => {
        if (currentOrg) {
            await loadOrgRoles();
        }
    }, 500);
});

// Manage People for a specific Role
async function showManageRolePeopleModal(roleName) {
    // Set role info
    document.getElementById('manage-role-id').value = roleName;
    document.getElementById('manage-role-name').textContent = capitalizeRole(roleName);

    // Load all people in the organization
    const peopleResponse = await authFetch(`${API_BASE_URL}/people/?org_id=${currentOrg.id}`);
    const peopleData = await peopleResponse.json();
    const people = peopleData.people || [];

    const container = document.getElementById('manage-role-people-checkboxes');

    // Create checkboxes for each person
    container.innerHTML = people.map(person => {
        const hasRole = person.roles && person.roles.includes(roleName);
        return `
            <label class="role-option">
                <input type="checkbox" value="${person.id}" ${hasRole ? 'checked' : ''}>
                ${person.name}${person.email ? ` (${person.email})` : ''}
            </label>
        `;
    }).join('');

    // Show modal
    document.getElementById('manage-role-people-modal').classList.remove('hidden');
}

function closeManageRolePeopleModal() {
    document.getElementById('manage-role-people-modal').classList.add('hidden');
    document.getElementById('manage-role-people-form').reset();
}

async function saveRolePeople(event) {
    event.preventDefault();

    const roleName = document.getElementById('manage-role-id').value;
    const checkboxes = document.querySelectorAll('#manage-role-people-checkboxes input[type="checkbox"]');

    // Get all people IDs that should have this role
    const selectedPeopleIds = Array.from(checkboxes)
        .filter(cb => cb.checked)
        .map(cb => cb.value);

    try {
        // Fetch all people to update their roles
        const peopleResponse = await authFetch(`${API_BASE_URL}/people/?org_id=${currentOrg.id}`);
        const peopleData = await peopleResponse.json();
        const people = peopleData.people || [];

        // Update each person's roles
        const updates = people.map(async (person) => {
            const shouldHaveRole = selectedPeopleIds.includes(person.id);
            const currentlyHasRole = person.roles && person.roles.includes(roleName);

            // Only update if there's a change
            if (shouldHaveRole !== currentlyHasRole) {
                let newRoles;
                if (shouldHaveRole) {
                    // Add role
                    newRoles = [...(person.roles || []), roleName];
                } else {
                    // Remove role
                    newRoles = (person.roles || []).filter(r => r !== roleName);
                }

                const response = await authFetch(`${API_BASE_URL}/people/${person.id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ roles: newRoles })
                });

                if (!response.ok) {
                    throw new Error(`Failed to update ${person.name}`);
                }
            }
        });

        await Promise.all(updates);

        closeManageRolePeopleModal();
        loadAdminRoles(); // Refresh the roles list to show updated counts
        showToast('Role assignments updated successfully!', 'success');
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}
