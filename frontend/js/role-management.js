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
async function loadOrgRoles() {
    try {
        const response = await fetch(`${API_BASE_URL}/organizations/${currentUser.org_id}`);
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
async function renderRoleSelector(containerId) {
    const roles = await loadOrgRoles();
    const container = document.getElementById(containerId);

    container.innerHTML = roles.map(role => `
        <label class="role-option">
            <input type="checkbox" value="${role}">
            ${capitalizeRole(role)}
        </label>
    `).join('');
}

// Capitalize role names for display
function capitalizeRole(role) {
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
        const orgResponse = await fetch(`${API_BASE_URL}/organizations/${currentUser.org_id}`);
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
        const updateResponse = await fetch(`${API_BASE_URL}/organizations/${currentUser.org_id}`, {
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
        const orgResponse = await fetch(`${API_BASE_URL}/organizations/${currentOrg.id}`);
        const orgData = await orgResponse.json();
        const descriptions = orgData.config?.role_descriptions || {};

        listEl.innerHTML = roles.map(role => `
            <div class="role-item">
                <div class="role-info">
                    <h4>${capitalizeRole(role)}</h4>
                    <p class="role-description">${descriptions[role] || 'No description'}</p>
                </div>
                <button class="btn btn-danger btn-sm" onclick="deleteRole('${role}')">Delete</button>
            </div>
        `).join('');
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
        const orgResponse = await fetch(`${API_BASE_URL}/organizations/${currentUser.org_id}`);
        const orgData = await orgResponse.json();

        // Remove role
        const currentRoles = orgData.config?.custom_roles || DEFAULT_ROLES;
        const updatedRoles = currentRoles.filter(r => r !== roleName);

        // Remove description
        const descriptions = orgData.config?.role_descriptions || {};
        delete descriptions[roleName];

        // Update org config
        const updateResponse = await fetch(`${API_BASE_URL}/organizations/${currentUser.org_id}`, {
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
