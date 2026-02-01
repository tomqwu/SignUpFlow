// API Configuration
if (typeof API_BASE_URL === 'undefined') {
    var API_BASE_URL = '/api';
}

// State
// State
var currentOrg = null;
var currentUser = null;
var organizations = [];

try {
    const storedOrg = localStorage.getItem('currentOrg');
    if (storedOrg) currentOrg = JSON.parse(storedOrg);

    const storedUser = localStorage.getItem('currentUser');
    if (storedUser) currentUser = JSON.parse(storedUser);
} catch (e) {
    console.warn('Failed to restore state from localStorage', e);
}

// Note: Using window.addSampleBadge() from sample-data-manager.js (loaded via script tag)

// Initialize app
document.addEventListener('DOMContentLoaded', async () => {
    initTabs();
    checkAPIStatus();
    await loadOrganizations();
});

// Tab Navigation
function initTabs() {
    const tabButtons = document.querySelectorAll('.admin-tab-btn');
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;
            switchAdminTab(tabName);
        });
    });
}

window.switchAdminTab = function(tabName) {
    // Update buttons
    document.querySelectorAll('.admin-tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });

    // Update content
    document.querySelectorAll('.admin-tab-content').forEach(content => {
        content.classList.toggle('active', content.id === `admin-tab-${tabName}`);
    });

    // Load data for tab
    loadTabData(tabName);
}

function loadTabData(tabName) {
    switch (tabName) {
        case 'people':
            loadPeople();
            populateOrgSelects();
            break;
        case 'teams':
            loadAdminTeams();
            populateOrgSelects();
            break;
        case 'invitations':
            loadInvitations();
            populateOrgSelects();
            break;
        case 'events':
            loadEvents();
            populateOrgSelects();
            break;
        case 'solver':
        case 'schedule': // Verify this matches the tab name in index.html
            populateOrgSelects();
            // detailed init for solver if needed
            const today = new Date();
            const nextMonth = new Date();
            nextMonth.setMonth(nextMonth.getMonth() + 1);

            const fromDateEl = document.getElementById('solve-from-date');
            const toDateEl = document.getElementById('solve-to-date');

            if (fromDateEl && !fromDateEl.value) fromDateEl.valueAsDate = today;
            if (toDateEl && !toDateEl.value) toDateEl.valueAsDate = nextMonth;
            break;
        case 'solutions':
            loadSolutions();
            populateOrgSelects();
            break;
        case 'analytics':
            loadAnalytics();
            break;
        case 'constraints':
            loadConstraints();
            break;
    }
}

// Ensure populateOrgSelects updates the solver org id too
function populateOrgSelects() {
    const orgs = window.organizations || []; // Assuming global
    const options = '<option value="">Select Organization</option>' +
        orgs.map(o => `<option value="${o.id}">${o.name}</option>`).join('');

    const selects = [
        'events-org-filter',
        'people-org-filter',
        'teams-org-filter',
        'solutions-org-filter',
        // 'solve-org-id' is a hidden input, we set it differently or use a select if visible
    ];

    selects.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            const currentVal = el.value;
            el.innerHTML = options;
            if (currentVal) el.value = currentVal;
        }
    });

    // Sync hidden solver org ID with the first available org if not set
    const solveOrgInput = document.getElementById('solve-org-id');
    if (solveOrgInput && orgs.length > 0 && !solveOrgInput.value) {
        solveOrgInput.value = orgs[0].id; // Default to first
    }
}

// API Status Check
async function checkAPIStatus() {
    const statusEl = document.getElementById('api-status');
    try {
        const response = await fetch('/health');
        if (response.ok) {
            statusEl.textContent = '● API Online';
            statusEl.className = 'status-badge online';
        } else {
            throw new Error('API not responding');
        }
    } catch (error) {
        statusEl.textContent = '● API Offline';
        statusEl.className = 'status-badge offline';
    }
}

// Organizations
async function loadOrganizations() {
    const listEl = document.getElementById('organizations-list');
    try {
        const response = await authFetch(`${API_BASE_URL}/organizations/`);
        if (!response.ok) throw new Error(`API Error: ${response.status}`);
        const data = await response.json();
        organizations = data.organizations || [];

        // Always populate org selects, even if no list element
        populateOrgSelects();

        // One-time initialization of currentOrg to the first organization
        // Also persist to localStorage for other scripts
        if (organizations.length > 0) {
            if (!currentOrg) {
                currentOrg = organizations[0];
            }
            // Always update storage if currentOrg is valid (sync state)
            if (currentOrg) {
                localStorage.setItem('currentOrg', JSON.stringify(currentOrg));
                console.log('Persisted currentOrg:', currentOrg);
            }
        }

        // Only update UI if list element exists
        if (!listEl) return;

        if (organizations.length === 0) {
            listEl.innerHTML = '<div class="empty-state"><h3>No Organizations</h3><p>Create your first organization to get started</p></div>';
            return;
        }

        listEl.innerHTML = organizations.map(org => `
            <div class="data-card">
                <div class="data-card-header">
                    <div>
                        <div class="data-card-title">${org.name}</div>
                        <div class="data-card-id">ID: ${org.id}</div>
                    </div>
                </div>
                <div class="data-card-meta">
                    ${org.region ? `📍 ${org.region}` : ''}
                    <br>Created: ${new Date(org.created_at).toLocaleDateString()}
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading organizations:', error);
        if (listEl) {
            listEl.innerHTML = `<div class="loading">Error loading organizations: ${error.message}</div>`;
        }
    }
}

function showCreateOrgForm() {
    document.getElementById('create-org-form').classList.remove('hidden');
}

function hideCreateOrgForm() {
    document.getElementById('create-org-form').classList.add('hidden');
    document.querySelector('#create-org-form form').reset();
}

async function createOrganization(event) {
    event.preventDefault();
    const data = {
        id: document.getElementById('org-id').value,
        name: document.getElementById('org-name').value,
        region: document.getElementById('org-region').value || null,
        config: {}
    };

    try {
        // Get reCAPTCHA token for create_org action
        let fetchOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        };
        fetchOptions = await addRecaptchaToken('create_org', fetchOptions);

        const response = await fetch(`${API_BASE_URL}/organizations/`, fetchOptions);

        if (response.ok) {
            hideCreateOrgForm();
            loadOrganizations();
            showToast('Organization created successfully!', 'success');
        } else {
            const error = await response.json();
            alert(`Error: ${error.detail}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// People
async function loadPeople() {
    const listEl = document.getElementById('people-list');
    const orgId = document.getElementById('people-org-filter').value;

    if (!orgId) {
        listEl.innerHTML = '<div class="loading">Select an organization to view people</div>';
        return;
    }

    try {
        const response = await authFetch(`${API_BASE_URL}/people/?org_id=${orgId}`);
        const data = await response.json();

        if (data.people.length === 0) {
            listEl.innerHTML = '<div class="empty-state"><h3>No People</h3><p>Add people to this organization</p></div>';
            return;
        }

        listEl.innerHTML = data.people.map(person => `
            <div class="data-card">
                <div class="data-card-header">
                    <div>
                        <div class="data-card-title">${window.addSampleBadge(person.name, person.is_sample)}</div>
                        <div class="data-card-id">ID: ${person.id}</div>
                    </div>
                    <button class="btn btn-secondary btn-sm" onclick='showEditPersonModal(${JSON.stringify(person)})'>Edit Roles</button>
                </div>
                <div class="data-card-meta">
                    ${person.email ? `✉️ ${person.email}<br>` : ''}
                    ${person.roles && person.roles.length > 0 ? person.roles.map(r => `<span class="badge badge-primary">${r}</span>`).join('') : 'No roles'}
                </div>
            </div>
        `).join('');
    } catch (error) {
        listEl.innerHTML = `<div class="loading">Error: ${error.message}</div>`;
    }
}

function showCreatePersonForm() {
    document.getElementById('create-person-form').classList.remove('hidden');
}

function hideCreatePersonForm() {
    document.getElementById('create-person-form').classList.add('hidden');
    document.querySelector('#create-person-form form').reset();
}

async function createPerson(event) {
    event.preventDefault();
    const roles = document.getElementById('person-roles').value
        .split(',')
        .map(r => r.trim())
        .filter(r => r);

    const data = {
        id: document.getElementById('person-id').value,
        org_id: document.getElementById('person-org-id').value,
        name: document.getElementById('person-name').value,
        email: document.getElementById('person-email').value || null,
        roles: roles
    };

    try {
        const response = await authFetch(`${API_BASE_URL}/people/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            hideCreatePersonForm();
            loadPeople();
            showToast('Person created successfully!', 'success');
        } else {
            const error = await response.json();
            alert(`Error: ${error.detail}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// Teams
async function loadAdminTeams() {
    console.log('loadAdminTeams (app-admin.js) called');
    const listEl = document.getElementById('teams-list');
    const orgId = document.getElementById('teams-org-filter').value;
    console.log('loadAdminTeams orgId:', orgId);

    if (!orgId) {
        listEl.innerHTML = '<div class="loading">Select an organization to view teams</div>';
        return;
    }

    try {
        const response = await authFetch(`${API_BASE_URL}/teams/?org_id=${orgId}`);
        const data = await response.json();

        if (data.teams.length === 0) {
            listEl.innerHTML = '<div class="empty-state"><h3>No Teams</h3><p>Create teams for this organization</p></div>';
            return;
        }

        listEl.innerHTML = data.teams.map(team => `
            <div class="data-card">
                <div class="data-card-header">
                    <div>
                        <div class="data-card-title">${window.addSampleBadge(team.name, team.is_sample)}</div>
                        <div class="data-card-id">ID: ${team.id}</div>
                    </div>
                    <div class="data-card-actions">
                        <button class="btn btn-secondary btn-sm" onclick='showManageTeamMembersModal(${JSON.stringify(team)})'>Manage Members</button>
                        <button class="btn btn-secondary btn-sm" onclick='showEditTeamModal(${JSON.stringify(team)})'>Edit</button>
                        <button class="btn btn-danger btn-sm" onclick="deleteTeam('${team.id}')">Delete</button>
                    </div>
                </div>
                <div class="data-card-meta">
                    👥 ${team.member_count} members
                    ${team.description ? `<br>${team.description}` : ''}
                </div>
            </div>
        `).join('');
    } catch (error) {
        listEl.innerHTML = `<div class="loading">Error: ${error.message}</div>`;
    }
}

function showCreateTeamForm() {
    const modal = document.getElementById('create-team-modal');
    modal.classList.remove('hidden');

    // Populate Org Select from the filter
    const orgFilter = document.getElementById('teams-org-filter');
    const teamOrgSelect = document.getElementById('team-org-id');

    if (orgFilter && teamOrgSelect) {
        teamOrgSelect.innerHTML = orgFilter.innerHTML;
        teamOrgSelect.value = orgFilter.value;
    }
}

function hideCreateTeamForm() {
    document.getElementById('create-team-modal').classList.add('hidden');
    document.getElementById('create-team-form').reset();
}

async function createTeam(event) {
    event.preventDefault();
    const data = {
        id: document.getElementById('team-id').value,
        org_id: document.getElementById('team-org-id').value,
        name: document.getElementById('team-name').value,
        description: document.getElementById('team-description').value || null,
        member_ids: []
    };

    try {
        const response = await authFetch(`${API_BASE_URL}/teams/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            hideCreateTeamForm();
            loadAdminTeams();
            showToast('Team created successfully!', 'success');
        } else {
            const error = await response.json();
            alert(`Error: ${error.detail}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// Edit Team
function showEditTeamModal(team) {
    document.getElementById('edit-team-id-hidden').value = team.id;
    document.getElementById('edit-team-name').value = team.name;
    document.getElementById('edit-team-description').value = team.description || '';
    document.getElementById('edit-team-modal').classList.remove('hidden');
}

function hideEditTeamModal() {
    document.getElementById('edit-team-modal').classList.add('hidden');
    document.getElementById('edit-team-form').reset();
}

async function updateTeam(event) {
    event.preventDefault();
    const teamId = document.getElementById('edit-team-id-hidden').value;
    const data = {
        name: document.getElementById('edit-team-name').value,
        description: document.getElementById('edit-team-description').value || null
    };

    try {
        const response = await authFetch(`${API_BASE_URL}/teams/${teamId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            hideEditTeamModal();
            loadAdminTeams();
            showToast('Team updated successfully!', 'success');
        } else {
            const error = await response.json();
            showToast(`Error: ${error.detail}`, 'error');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

// Delete Team
let teamToDeleteId = null;

function deleteTeam(teamId) {
    console.log('deleteTeam called for:', teamId);
    teamToDeleteId = teamId;
    document.getElementById('delete-team-modal').classList.remove('hidden');
    console.log('delete-team-modal classList:', document.getElementById('delete-team-modal').classList.toString());
}

function hideDeleteTeamModal() {
    document.getElementById('delete-team-modal').classList.add('hidden');
    teamToDeleteId = null;
}

async function confirmDeleteTeam() {
    if (!teamToDeleteId) return;

    try {
        const response = await authFetch(`${API_BASE_URL}/teams/${teamToDeleteId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            hideDeleteTeamModal();
            loadAdminTeams();
            showToast('Team deleted successfully!', 'success');
        } else {
            const error = await response.json();
            showToast(`Error: ${error.detail}`, 'error');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

// Manage Team Members
let currentManageTeamId = null;

async function showManageTeamMembersModal(team) {
    currentManageTeamId = team.id;
    document.getElementById('manage-team-name-display').textContent = team.name;
    document.getElementById('manage-team-members-modal').classList.remove('hidden');

    await Promise.all([
        loadTeamMembers(team.id),
        populateAddMemberSelect(team.org_id)
    ]);
}

function hideManageTeamMembersModal() {
    document.getElementById('manage-team-members-modal').classList.add('hidden');
    currentManageTeamId = null;
}

async function loadTeamMembers(teamId) {
    const listEl = document.getElementById('team-members-list');
    listEl.innerHTML = '<div class="loading">Loading members...</div>';

    try {
        const teamResponse = await authFetch(`${API_BASE_URL}/teams/${teamId}`);
        const team = await teamResponse.json();

        const orgId = document.getElementById('teams-org-filter').value;
        const peopleResponse = await authFetch(`${API_BASE_URL}/people/?org_id=${orgId}`);
        const peopleData = await peopleResponse.json();

        const memberIds = team.member_ids || [];
        const members = peopleData.people.filter(p => memberIds.includes(p.id));

        if (members.length === 0) {
            listEl.innerHTML = '<div class="empty-state">No members in this team</div>';
        } else {
            listEl.innerHTML = members.map(person => `
                <div class="list-item">
                    <div class="list-item-content">
                        <div class="list-item-title">${person.name}</div>
                        <div class="list-item-subtitle">${person.email || 'No email'}</div>
                    </div>
                    <button class="btn btn-danger btn-sm" onclick="removeTeamMember('${person.id}')">Remove</button>
                </div>
            `).join('');
        }

    } catch (error) {
        listEl.innerHTML = `<div class="loading">Error: ${error.message}</div>`;
    }
}

async function populateAddMemberSelect(orgId) {
    const select = document.getElementById('add-team-member-select');
    try {
        const response = await authFetch(`${API_BASE_URL}/people/?org_id=${orgId}`);
        const data = await response.json();

        select.innerHTML = '<option value="">Select person to add...</option>' +
            data.people.map(p => `<option value="${p.id}">${p.name} (${p.email})</option>`).join('');

    } catch (error) {
        console.error('Error loading people for select:', error);
        select.innerHTML = '<option value="">Error loading people</option>';
    }
}

async function addTeamMember() {
    const personId = document.getElementById('add-team-member-select').value;
    if (!personId) return;

    try {
        const response = await authFetch(`${API_BASE_URL}/teams/${currentManageTeamId}/members`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ person_ids: [personId] })
        });

        if (response.ok) {
            showToast('Member added successfully', 'success');
            loadTeamMembers(currentManageTeamId);
            // Refresh main list to update count
            loadAdminTeams();
        } else {
            const error = await response.json();
            showToast(`Error: ${error.detail}`, 'error');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

async function removeTeamMember(personId) {
    if (!confirm('Remove this person from the team?')) return;

    try {
        const response = await authFetch(`${API_BASE_URL}/teams/${currentManageTeamId}/members`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ person_ids: [personId] })
        });

        if (response.ok) {
            showToast('Member removed successfully', 'success');
            loadTeamMembers(currentManageTeamId);
            // Refresh main list to update count
            loadAdminTeams();
        } else {
            const error = await response.json();
            showToast(`Error: ${error.detail}`, 'error');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

// Events
async function loadEvents() {
    const listEl = document.getElementById('admin-events-list');
    const orgId = document.getElementById('events-org-filter').value;

    if (!orgId) {
        listEl.innerHTML = '<div class="loading">Select an organization to view events</div>';
        return;
    }

    try {
        const [eventsResponse, peopleResponse, solutionsResponse] = await Promise.all([
            authFetch(`${API_BASE_URL}/events/?org_id=${orgId}`),
            authFetch(`${API_BASE_URL}/people/?org_id=${orgId}`),
            fetch(`${API_BASE_URL}/solutions/?org_id=${orgId}`)
        ]);

        const eventsData = await eventsResponse.json();
        const peopleData = await peopleResponse.json();
        const solutionsData = await solutionsResponse.json();

        if (eventsData.events.length === 0) {
            listEl.innerHTML = '<div class="empty-state"><h3>No Events</h3><p>Create events for this organization</p></div>';
            return;
        }

        // Get latest solution with assignments
        const latestSolution = solutionsData.solutions.find(s => s.assignment_count > 0);
        let assignments = {};

        if (latestSolution) {
            const assignmentsResponse = await fetch(`${API_BASE_URL}/solutions/${latestSolution.id}/assignments`);
            const assignmentsData = await assignmentsResponse.json();

            // Group assignments by event
            assignmentsData.assignments.forEach(a => {
                if (!assignments[a.event_id]) {
                    assignments[a.event_id] = [];
                }
                assignments[a.event_id].push(a);
            });
        }

        // Load all people's blocked dates
        const blockedDatesMap = {};
        await Promise.all(peopleData.people.map(async (person) => {
            try {
                const timeoffResponse = await fetch(`${API_BASE_URL}/availability/${person.id}/timeoff`);
                const timeoffData = await timeoffResponse.json();
                blockedDatesMap[person.id] = timeoffData.timeoff || [];
            } catch (e) {
                blockedDatesMap[person.id] = [];
            }
        }));

        // Check if person is blocked on event date
        const isPersonBlocked = (personId, eventDate) => {
            const eventDateStr = eventDate.toISOString().split('T')[0];
            const blocked = blockedDatesMap[personId] || [];
            return blocked.some(b => {
                const startDate = b.start_date.split('T')[0];
                const endDate = b.end_date.split('T')[0];
                return eventDateStr >= startDate && eventDateStr <= endDate;
            });
        };

        listEl.innerHTML = eventsData.events.map(event => {
            const eventAssignments = assignments[event.id] || [];
            const eventDate = new Date(event.start_time);

            let assignmentsHtml = '';
            if (eventAssignments.length > 0) {
                const assignmentsList = eventAssignments.map(a => {
                    const blocked = isPersonBlocked(a.person_id, eventDate);
                    const style = blocked ? 'color: #dc2626; font-weight: bold;' : '';
                    const warning = blocked ? ' ⚠️ BLOCKED' : '';
                    return `<div style="${style}">${a.person_name}${warning}</div>`;
                }).join('');
                assignmentsHtml = `<div class="data-card-meta"><strong>Assigned:</strong><br>${assignmentsList}</div>`;
            }

            return `
            <div class="data-card">
                <div class="data-card-header">
                    <div>
                        <div class="data-card-title">${window.addSampleBadge(event.type, event.is_sample)}</div>
                        <div class="data-card-id">ID: ${event.id}</div>
                    </div>
                    <span class="badge badge-primary">${event.type}</span>
                </div>
                <div class="data-card-meta">
                    📅 ${eventDate.toLocaleString()}<br>
                    ⏱️ ${new Date(event.end_time).toLocaleString()}
                </div>
                ${assignmentsHtml}
            </div>
            `;
        }).join('');
    } catch (error) {
        listEl.innerHTML = `<div class="loading">Error: ${error.message}</div>`;
    }
}

function showCreateEventForm() {
    document.getElementById('create-event-form').classList.remove('hidden');
}

function hideCreateEventForm() {
    document.getElementById('create-event-form').classList.add('hidden');
    document.querySelector('#create-event-form form').reset();
}

async function createEvent(event) {
    event.preventDefault();
    const data = {
        id: document.getElementById('event-id').value,
        org_id: document.getElementById('event-org-id').value,
        type: document.getElementById('event-type').value,
        start_time: document.getElementById('event-start').value,
        end_time: document.getElementById('event-end').value,
        team_ids: []
    };

    try {
        const response = await authFetch(`${API_BASE_URL}/events/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            hideCreateEventForm();
            loadEvents();
            showToast('Event created successfully!', 'success');
        } else {
            const error = await response.json();
            alert(`Error: ${error.detail}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// Solver
async function solveSchedule(event) {
    event.preventDefault();

    // Get org ID from hidden input or global filter or first org
    let orgId = document.getElementById('solve-org-id').value;
    if (!orgId && window.organizations && window.organizations.length > 0) {
        orgId = window.organizations[0].id;
    }

    if (!orgId) {
        showToast('Please create or select an organization first', 'error');
        return;
    }

    const data = {
        org_id: orgId,
        from_date: document.getElementById('solve-from-date').value,
        to_date: document.getElementById('solve-to-date').value,
        mode: document.getElementById('solve-mode').value,
        change_min: false
    };

    const resultsEl = document.getElementById('solve-results');
    const statusEl = document.getElementById('solver-status');
    const metricsEl = document.getElementById('solution-metrics');
    const btn = document.getElementById('run-solver-button');

    statusEl.classList.remove('hidden');
    statusEl.innerHTML = '<span id="solver-running-indicator" class="loading-spinner"></span> <span data-i18n="solver.status.solving">Solving schedule... please wait.</span>';
    statusEl.className = 'solver-status info';

    // Disable button
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span class="loading-spinner"></span> Solving...';
    }

    // Clear previous
    metricsEl.innerHTML = '';
    document.getElementById('solver-results-body').innerHTML = '';
    resultsEl.classList.add('hidden');

    try {
        const response = await authFetch(`${API_BASE_URL}/solver/solve`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            const result = await response.json();
            statusEl.innerHTML = '<span id="solver-success-message" data-i18n="solver.status.completed">Schedule generated successfully!</span>';
            statusEl.className = 'solver-status success';
            showToast('Schedule generated successfully!', 'success');

            displaySolutionMetrics(result);
            await loadSolutionAssignments(result.solution_id);

            resultsEl.classList.remove('hidden');
        } else {
            const error = await response.json();
            statusEl.textContent = `Error: ${error.detail}`;
            statusEl.className = 'solver-status error';
        }
    } catch (error) {
        statusEl.textContent = `Error: ${error.message}`;
        statusEl.className = 'solver-status error';
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<span class="btn-icon">✨</span> <span data-i18n="solver.run">Run Solver</span>';
        }
    }
}

async function loadSolutionAssignments(solutionId) {
    const tbody = document.getElementById('solver-results-body');
    tbody.innerHTML = '<tr><td colspan="6" class="loading">Loading assignments...</td></tr>';

    try {
        // We need to fetch assignments. The API might be /solutions/{id}/assignments or similar.
        // Based on previous code in loadEvents, it seems to be supported.
        const response = await authFetch(`${API_BASE_URL}/solutions/${solutionId}/assignments`);
        if (!response.ok) throw new Error('Failed to load assignments');

        const data = await response.json();
        const assignments = data.assignments || [];

        if (assignments.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">No assignments generated.</td></tr>';
            return;
        }

        // Sort by date/time
        assignments.sort((a, b) => new Date(a.event_start) - new Date(b.event_start));

        tbody.innerHTML = assignments.map(a => `
            <tr>
                <td>${a.event_type || 'Event'}</td>
                <td>${new Date(a.event_start).toLocaleDateString()}</td>
                <td>${new Date(a.event_start).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</td>
                <td><strong>${a.person_name}</strong></td>
                <td><span class="badge badge-primary">${a.role}</span></td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="alert('Edit implementation pending')">Edit</button>
                </td>
            </tr>
        `).join('');

    } catch (e) {
        console.error(e);
        tbody.innerHTML = `<tr><td colspan="6" class="error">Error loading assignments: ${e.message}</td></tr>`;
    }
}

function displaySolutionMetrics(solution) {
    const metricsEl = document.getElementById('solution-metrics');
    const m = solution.metrics;

    const healthClass = m.hard_violations === 0 ? 'metric-good' : 'metric-bad';

    metricsEl.innerHTML = `
        <div class="metric-grid">
            <div class="metric-item">
                <div class="metric-value">${solution.assignment_count}</div>
                <div class="metric-label">Assignments</div>
            </div>
            <div class="metric-item ${healthClass}">
                <div class="metric-value">${m.hard_violations}</div>
                <div class="metric-label">Hard Violations</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">${m.health_score.toFixed(0)}</div>
                <div class="metric-label">Health Score</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">${m.solve_ms.toFixed(0)}ms</div>
                <div class="metric-label">Solve Time</div>
            </div>
        </div>
        <div class="solution-message">
            ${solution.message} (ID: ${solution.solution_id})
        </div>
    `;
}

// Solutions
async function loadSolutions() {
    const listEl = document.getElementById('solutions-list');
    const orgId = document.getElementById('solutions-org-filter').value;

    const url = orgId ? `${API_BASE_URL}/solutions/?org_id=${orgId}` : `${API_BASE_URL}/solutions/`;

    try {
        const response = await fetch(url);
        const data = await response.json();

        if (data.solutions.length === 0) {
            listEl.innerHTML = '<div class="empty-state"><h3>No Solutions</h3><p>Generate a schedule to see solutions</p></div>';
            return;
        }

        listEl.innerHTML = data.solutions.map(sol => {
            const healthClass = sol.hard_violations === 0 ? 'success' : 'danger';
            return `
                <div class="data-card">
                    <div class="data-card-header">
                        <div>
                            <div class="data-card-title">Solution ${sol.id}</div>
                            <div class="data-card-id">${new Date(sol.created_at).toLocaleString()}</div>
                        </div>
                        <div class="data-card-actions">
                             <button class="btn btn-sm" onclick="viewSolutionDetails('${sol.id}')">Details</button>
                        </div>
                    </div>
                    <div class="data-card-meta">
                        Assignments: ${sol.assignment_count}<br>
                        Hard Violations: ${sol.hard_violations}<br>
                        Health: ${sol.health_score.toFixed(0)}
                    </div>
                </div>
            `;
        }).join('');
    } catch (error) {
        listEl.innerHTML = `<div class="loading">Error: ${error.message}</div>`;
    }
}

async function viewSolutionDetails(solutionId) {
    console.log('View solution details', solutionId);
}
