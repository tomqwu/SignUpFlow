// Edit Role Functions

function showEditRoleModal(roleName, description) {
    document.getElementById('edit-role-old-name').value = roleName;
    document.getElementById('edit-role-name').value = roleName;
    document.getElementById('edit-role-description').value = description || '';

    document.getElementById('edit-role-modal').classList.remove('hidden');
}

function closeEditRoleModal() {
    document.getElementById('edit-role-modal').classList.add('hidden');
    document.getElementById('edit-role-form').reset();
}

async function saveEditRole(event) {
    event.preventDefault();

    const oldRoleName = document.getElementById('edit-role-old-name').value;
    const newRoleName = document.getElementById('edit-role-name').value;
    const newDescription = document.getElementById('edit-role-description').value;

    try {
        // Get current org config
        const orgResponse = await fetch(`${API_BASE_URL}/organizations/${currentOrg.id}`);
        const orgData = await orgResponse.json();

        const config = orgData.config || {};
        const customRoles = config.custom_roles || [];
        const roleDescriptions = config.role_descriptions || {};

        // If role name changed, update in people's roles array
        if (oldRoleName !== newRoleName) {
            // Get all people
            const peopleResponse = await authFetch(`${API_BASE_URL}/people/?org_id=${currentOrg.id}`);
            const peopleData = await peopleResponse.json();
            const people = peopleData.people || [];

            // Update each person that has the old role
            const updates = people
                .filter(p => p.roles && p.roles.includes(oldRoleName))
                .map(async (person) => {
                    const updatedRoles = person.roles.map(r => r === oldRoleName ? newRoleName : r);

                    const response = await authFetch(`${API_BASE_URL}/people/${person.id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ roles: updatedRoles })
                    });

                    if (!response.ok) {
                        throw new Error(`Failed to update ${person.name}`);
                    }
                });

            await Promise.all(updates);

            // Update role name in custom_roles array
            const roleIndex = customRoles.indexOf(oldRoleName);
            if (roleIndex !== -1) {
                customRoles[roleIndex] = newRoleName;
            }

            // Delete old description and add new one
            delete roleDescriptions[oldRoleName];
        }

        // Update description
        roleDescriptions[newRoleName] = newDescription;

        // Update org config
        const updateResponse = await fetch(`${API_BASE_URL}/organizations/${currentOrg.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                config: {
                    ...config,
                    custom_roles: customRoles,
                    role_descriptions: roleDescriptions
                }
            })
        });

        if (!updateResponse.ok) {
            throw new Error('Failed to update role');
        }

        closeEditRoleModal();
        loadAdminRoles(); // Refresh roles list
        showToast('Role updated successfully!', 'success');
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}
