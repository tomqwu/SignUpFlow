// API Configuration
const API_BASE_URL = window.API_BASE_URL || '/api';

// State
let currentOrg = null;
let organizations = [];

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    checkAPIStatus();
    loadOrganizations();
});

// Tab Navigation
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Update buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });

    // Update content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.toggle('active', content.id === `${tabName}-tab`);
    });

    // Load data for tab
    loadTabData(tabName);
}

function loadTabData(tabName) {
    switch(tabName) {
        case 'people':
            loadPeople();
            populateOrgSelects();
            break;
        case 'teams':
            loadTeams();
            populateOrgSelects();
            break;
        case 'events':
            loadEvents();
            populateOrgSelects();
            break;
        case 'solver':
            populateOrgSelects();
            break;
        case 'solutions':
            loadSolutions();
            populateOrgSelects();
            break;
    }
}

// API Status Check
async function checkAPIStatus() {
    const statusEl = document.getElementById('api-status');
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
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
        const response = await fetch(`${API_BASE_URL}/organizations/`);
        const data = await response.json();
        organizations = data.organizations;

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

        populateOrgSelects();
    } catch (error) {
        listEl.innerHTML = `<div class="loading">Error loading organizations: ${error.message}</div>`;
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
        const response = await fetch(`${API_BASE_URL}/organizations/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

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
        const response = await fetch(`${API_BASE_URL}/people/?org_id=${orgId}`);
        const data = await response.json();

        if (data.people.length === 0) {
            listEl.innerHTML = '<div class="empty-state"><h3>No People</h3><p>Add people to this organization</p></div>';
            return;
        }

        listEl.innerHTML = data.people.map(person => `
            <div class="data-card">
                <div class="data-card-header">
                    <div>
                        <div class="data-card-title">${person.name}</div>
                        <div class="data-card-id">ID: ${person.id}</div>
                    </div>
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
        const response = await fetch(`${API_BASE_URL}/people/`, {
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
async function loadTeams() {
    const listEl = document.getElementById('teams-list');
    const orgId = document.getElementById('teams-org-filter').value;

    if (!orgId) {
        listEl.innerHTML = '<div class="loading">Select an organization to view teams</div>';
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/teams/?org_id=${orgId}`);
        const data = await response.json();

        if (data.teams.length === 0) {
            listEl.innerHTML = '<div class="empty-state"><h3>No Teams</h3><p>Create teams for this organization</p></div>';
            return;
        }

        listEl.innerHTML = data.teams.map(team => `
            <div class="data-card">
                <div class="data-card-header">
                    <div>
                        <div class="data-card-title">${team.name}</div>
                        <div class="data-card-id">ID: ${team.id}</div>
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
    document.getElementById('create-team-form').classList.remove('hidden');
}

function hideCreateTeamForm() {
    document.getElementById('create-team-form').classList.add('hidden');
    document.querySelector('#create-team-form form').reset();
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
        const response = await fetch(`${API_BASE_URL}/teams/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            hideCreateTeamForm();
            loadTeams();
            showToast('Team created successfully!', 'success');
        } else {
            const error = await response.json();
            alert(`Error: ${error.detail}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
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
        const response = await fetch(`${API_BASE_URL}/events/?org_id=${orgId}`);
        const data = await response.json();

        if (data.events.length === 0) {
            listEl.innerHTML = '<div class="empty-state"><h3>No Events</h3><p>Create events for this organization</p></div>';
            return;
        }

        listEl.innerHTML = data.events.map(event => `
            <div class="data-card">
                <div class="data-card-header">
                    <div>
                        <div class="data-card-title">${event.type}</div>
                        <div class="data-card-id">ID: ${event.id}</div>
                    </div>
                    <span class="badge badge-primary">${event.type}</span>
                </div>
                <div class="data-card-meta">
                    📅 ${new Date(event.start_time).toLocaleString()}<br>
                    ⏱️ ${new Date(event.end_time).toLocaleString()}
                </div>
            </div>
        `).join('');
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
        const response = await fetch(`${API_BASE_URL}/events/`, {
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

    const data = {
        org_id: document.getElementById('solve-org-id').value,
        from_date: document.getElementById('solve-from-date').value,
        to_date: document.getElementById('solve-to-date').value,
        mode: document.getElementById('solve-mode').value,
        change_min: false
    };

    const resultsEl = document.getElementById('solve-results');
    const metricsEl = document.getElementById('solution-metrics');

    resultsEl.classList.remove('hidden');
    metricsEl.innerHTML = '<div class="loading">Solving schedule...</div>';

    try {
        const response = await fetch(`${API_BASE_URL}/solver/solve`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            const result = await response.json();
            displaySolutionMetrics(result);
        } else {
            const error = await response.json();
            metricsEl.innerHTML = `<div class="loading">Error: ${error.detail}</div>`;
        }
    } catch (error) {
        metricsEl.innerHTML = `<div class="loading">Error: ${error.message}</div>`;
    }
}

function displaySolutionMetrics(solution) {
    const metricsEl = document.getElementById('solution-metrics');
    const m = solution.metrics;

    const healthClass = m.hard_violations === 0 ? 'success' : 'danger';

    metricsEl.innerHTML = `
        <div class="metric-grid">
            <div class="metric-item ${healthClass}">
                <div class="metric-value">${solution.assignment_count}</div>
                <div class="metric-label">Assignments</div>
            </div>
            <div class="metric-item ${healthClass}">
                <div class="metric-value">${m.hard_violations}</div>
                <div class="metric-label">Hard Violations</div>
            </div>
            <div class="metric-item ${healthClass}">
                <div class="metric-value">${m.health_score.toFixed(0)}</div>
                <div class="metric-label">Health Score</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">${m.solve_ms.toFixed(0)}ms</div>
                <div class="metric-label">Solve Time</div>
            </div>
        </div>
        <p style="margin-top: 20px; text-align: center;">
            <strong>Solution ID: ${solution.solution_id}</strong><br>
            ${solution.message}
        </p>
        <div style="margin-top: 20px; text-align: center;">
            <button class="btn btn-primary" onclick="switchTab('solutions')">View Solutions →</button>
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
                            <div class="data-card-title">Solution #${sol.id}</div>
                            <div class="data-card-id">${sol.org_id}</div>
                        </div>
                        <span class="badge badge-${healthClass}">${sol.health_score.toFixed(0)}/100</span>
                    </div>
                    <div class="data-card-meta">
                        📊 ${sol.assignment_count} assignments<br>
                        ⚠️ ${sol.hard_violations} violations<br>
                        📅 ${new Date(sol.created_at).toLocaleString()}
                    </div>
                    <div class="data-card-actions">
                        <button class="btn btn-small btn-primary" onclick="viewSolutionDetails(${sol.id})">View Details</button>
                        <button class="btn btn-small btn-secondary" onclick="exportSolution(${sol.id}, 'csv')">Export CSV</button>
                        <button class="btn btn-small btn-secondary" onclick="exportSolution(${sol.id}, 'json')">Export JSON</button>
                    </div>
                </div>
            `;
        }).join('');
    } catch (error) {
        listEl.innerHTML = `<div class="loading">Error: ${error.message}</div>`;
    }
}

async function viewSolutionDetails(solutionId) {
    try {
        const response = await fetch(`${API_BASE_URL}/solutions/${solutionId}/assignments`);
        const data = await response.json();
        showToast(`Solution generated with ${data.total} assignments`, 'success');
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

async function exportSolution(solutionId, format) {
    try {
        const response = await fetch(`${API_BASE_URL}/solutions/${solutionId}/export`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ format, scope: 'org' })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `solution_${solutionId}.${format}`;
            a.click();
        } else {
            showToast('Export failed', 'error');
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// Utility Functions
function populateOrgSelects() {
    const selects = [
        'person-org-id',
        'team-org-id',
        'event-org-id',
        'solve-org-id',
        'people-org-filter',
        'teams-org-filter',
        'events-org-filter',
        'solutions-org-filter'
    ];

    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        if (!select) return;

        const currentValue = select.value;
        const options = organizations.map(org =>
            `<option value="${org.id}" ${org.id === currentValue ? 'selected' : ''}>${org.name}</option>`
        ).join('');

        if (selectId.includes('filter')) {
            select.innerHTML = '<option value="">All Organizations</option>' + options;
        } else {
            select.innerHTML = '<option value="">Select Organization</option>' + options;
        }
    });
}
