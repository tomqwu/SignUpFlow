/**
 * Constraints Management Logic
 */

let loadedConstraints = [];

async function loadConstraints() {
    console.log('loadConstraints called');
    const listEl = document.getElementById('constraints-list');
    
    // Debug: Check if currentOrg is available
    console.log('loadConstraints currentOrg:', currentOrg);

    if (!currentOrg) {
        // Try to recover from localStorage if possible (redundant but safe)
        try {
            const stored = localStorage.getItem('currentOrg');
            if (stored) currentOrg = JSON.parse(stored);
        } catch (e) { console.error(e); }
        
        if (!currentOrg) {
            listEl.innerHTML = '<div class="loading">Please select an organization first.</div>';
            return;
        }
    }

    try {
        listEl.innerHTML = '<div class="loading">Loading constraints...</div>';

        const response = await authFetch(`${API_BASE_URL}/constraints/?org_id=${currentOrg.id}`);
        if (!response.ok) throw new Error('Failed to fetch constraints');

        const data = await response.json();
        loadedConstraints = data.constraints || [];

        renderConstraintsList();
    } catch (error) {
        console.error('Error loading constraints:', error);
        listEl.innerHTML = `<div class="error-state">Error loading constraints: ${error.message}</div>`;
    }
}

function renderConstraintsList() {
    const listEl = document.getElementById('constraints-list');

    if (loadedConstraints.length === 0) {
        listEl.innerHTML = '<div class="empty-state">No constraints defined. Add one to control the schedule.</div>';
        return;
    }

    listEl.innerHTML = loadedConstraints.map(c => `
        <div class="data-card constraint-card" data-constraint-id="${c.id}">
            <div class="data-card-header">
                <div class="constraint-title">
                    <strong>${c.key}</strong>
                    <span class="badge ${c.type === 'hard' ? 'badge-danger' : 'badge-info'}">${c.type}</span>
                    <span class="badge badge-secondary">Weight: ${c.weight}</span>
                </div>
                <div class="constraint-actions">
                     <label class="switch">
                        <input type="checkbox" ${c.params?.active !== false ? 'checked' : ''} onchange="toggleConstraint(${c.id})" class="toggle-switch">
                        <span class="slider round"></span>
                    </label>
                    <button class="btn btn-sm btn-secondary" onclick='openEditConstraintModal(${JSON.stringify(c)})' title="Edit">Edit</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteConstraint(${c.id}, '${c.key}')" title="Delete">Delete</button>
                </div>
            </div>
            <div class="constraint-details">
                <code>${c.predicate}</code>
            </div>
        </div>
    `).join('');
}

// Add/Edit Modal Logic
function showAddConstraintModal() {
    const modal = document.getElementById('constraint-modal');
    // Reset form
    document.getElementById('constraint-id').value = '';
    document.getElementById('constraint-key').value = '';
    document.getElementById('constraint-key').disabled = false;
    document.getElementById('constraint-type').value = 'soft';
    document.getElementById('constraint-weight').value = '10';
    document.getElementById('constraint-predicate').value = '';

    modal.classList.remove('hidden');
}

function openEditConstraintModal(constraint) {
    const modal = document.getElementById('constraint-modal');

    document.getElementById('constraint-id').value = constraint.id;
    document.getElementById('constraint-key').value = constraint.key;
    document.getElementById('constraint-key').disabled = true; // Key cannot be changed
    document.getElementById('constraint-type').value = constraint.type;
    document.getElementById('constraint-weight').value = constraint.weight;
    document.getElementById('constraint-predicate').value = constraint.predicate;

    modal.classList.remove('hidden');
}

function closeConstraintModal() {
    document.getElementById('constraint-modal').classList.add('hidden');
}

async function saveConstraint(event) {
    event.preventDefault();

    const id = document.getElementById('constraint-id').value;
    const key = document.getElementById('constraint-key').value;
    const type = document.getElementById('constraint-type').value;
    const weight = parseInt(document.getElementById('constraint-weight').value);
    const predicate = document.getElementById('constraint-predicate').value;

    const payload = {
        org_id: currentOrg.id,
        key,
        type,
        weight,
        predicate,
        params: { active: true } // Default
    };

    try {
        let response;
        if (id) {
            // Update existing
            response = await authFetch(`${API_BASE_URL}/constraints/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
        } else {
            // Create new
            response = await authFetch(`${API_BASE_URL}/constraints/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
        }

        if (response.ok) {
            showToast('Constraint saved successfully', 'success');
            closeConstraintModal();
            loadConstraints();
        } else {
            const error = await response.json();
            alert(`Error: ${error.detail}`);
        }
    } catch (e) {
        alert(`Error saving constraint: ${e.message}`);
    }
}

async function deleteConstraint(id, key) {
    if (!confirm(`Delete constraint "${key}"?`)) return;

    try {
        const response = await authFetch(`${API_BASE_URL}/constraints/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showToast('Constraint deleted', 'success');
            loadConstraints();
        } else {
            const error = await response.json();
            showToast(`Error: ${error.detail}`, 'error');
        }
    } catch (e) {
        console.error(e);
        showToast('Error deleting constraint', 'error');
    }
}

// Expose functions to window
exposeToWindow('loadConstraints', loadConstraints);
exposeToWindow('showAddConstraintModal', showAddConstraintModal);
exposeToWindow('closeConstraintModal', closeConstraintModal);
exposeToWindow('saveConstraint', saveConstraint);
exposeToWindow('openEditConstraintModal', openEditConstraintModal);
exposeToWindow('deleteConstraint', deleteConstraint);
exposeToWindow('toggleConstraint', toggleConstraint);
