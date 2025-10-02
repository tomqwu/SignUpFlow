// User-Friendly Roster App
const API_BASE_URL = '/api';

// User State
let currentUser = null;
let currentOrg = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkExistingSession();
});

// Session Management
function checkExistingSession() {
    const savedUser = localStorage.getItem('roster_user');
    const savedOrg = localStorage.getItem('roster_org');
    const savedView = localStorage.getItem('roster_current_view') || 'calendar';

    if (savedUser && savedOrg) {
        currentUser = JSON.parse(savedUser);
        currentOrg = JSON.parse(savedOrg);
        showMainApp();
        // Restore the last viewed tab
        setTimeout(() => switchView(savedView), 100);
    } else {
        showScreen('onboarding-screen');
    }
}

function saveSession() {
    localStorage.setItem('roster_user', JSON.stringify(currentUser));
    localStorage.setItem('roster_org', JSON.stringify(currentOrg));
}

function saveCurrentView(viewName) {
    localStorage.setItem('roster_current_view', viewName);
}

function logout() {
    localStorage.clear();
    currentUser = null;
    currentOrg = null;
    location.reload();
}

// Screen Navigation
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.add('hidden'));
    document.getElementById(screenId).classList.remove('hidden');
}

function startOnboarding() {
    showScreen('join-screen');
    loadOrganizations();
}

function showLogin() {
    showScreen('login-screen');
}

// ============================================================================
// AUTHENTICATION
// ============================================================================

async function handleLogin(event) {
    event.preventDefault();

    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const errorEl = document.getElementById('login-error');

    errorEl.classList.add('hidden');

    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        if (response.ok) {
            const data = await response.json();

            // Fetch organization details
            const orgResponse = await fetch(`${API_BASE_URL}/organizations/${data.org_id}`);
            const orgData = await orgResponse.json();

            currentUser = {
                id: data.person_id,
                name: data.name,
                email: data.email,
                roles: data.roles,
                token: data.token
            };
            currentOrg = orgData;

            saveSession();
            showMainApp();
        } else {
            const error = await response.json();
            errorEl.textContent = error.detail || 'Invalid email or password';
            errorEl.classList.remove('hidden');
        }
    } catch (error) {
        errorEl.textContent = 'Connection error. Please try again.';
        errorEl.classList.remove('hidden');
    }
}

function showLogin_old() {
    alert('Login functionality coming soon!\n\nFor now, go through the onboarding to create your profile.');
}

// Organization Selection
async function loadOrganizations() {
    const listEl = document.getElementById('org-list');
    try {
        const response = await fetch(`${API_BASE_URL}/organizations/`);
        const data = await response.json();

        if (data.organizations.length === 0) {
            listEl.innerHTML = '<p class="help-text">No organizations yet. Create one to get started!</p>';
            return;
        }

        listEl.innerHTML = data.organizations.map(org => `
            <div class="org-card" onclick="selectOrganization('${org.id}', '${org.name}')">
                <h3>${org.name}</h3>
                <p>${org.region || 'No location specified'}</p>
            </div>
        `).join('');
    } catch (error) {
        listEl.innerHTML = `<p class="help-text">Error loading organizations. Make sure the API is running.</p>`;
    }
}

function selectOrganization(orgId, orgName) {
    currentOrg = { id: orgId, name: orgName };
    showScreen('profile-screen');
}

function showCreateOrg() {
    document.getElementById('create-org-section').classList.toggle('hidden');
}

async function createAndJoinOrg(event) {
    event.preventDefault();

    const orgName = document.getElementById('new-org-name').value;
    const orgRegion = document.getElementById('new-org-region').value;
    const orgId = orgName.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '');

    try {
        const response = await fetch(`${API_BASE_URL}/organizations/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: orgId,
                name: orgName,
                region: orgRegion || null,
                config: {}
            })
        });

        if (response.ok || response.status === 409) {
            currentOrg = { id: orgId, name: orgName };
            showScreen('profile-screen');
        } else {
            alert('Error creating organization. Please try again.');
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// Profile Creation
async function createProfile(event) {
    event.preventDefault();

    const name = document.getElementById('user-name').value;
    const email = document.getElementById('user-email').value;
    const password = document.getElementById('user-password').value;
    const phone = document.getElementById('user-phone').value;

    const roles = Array.from(document.querySelectorAll('#role-selector input:checked'))
        .map(input => input.value);

    try {
        // Use signup endpoint with password
        const response = await fetch(`${API_BASE_URL}/auth/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                org_id: currentOrg.id,
                name: name,
                email: email,
                password: password,
                roles: roles
            })
        });

        if (response.ok) {
            const data = await response.json();

            currentUser = {
                id: data.person_id,
                name: data.name,
                email: data.email,
                roles: data.roles,
                token: data.token
            };
            saveSession();
            showMainApp();
        } else if (response.status === 409) {
            alert('This email is already registered. Please use the login page instead.');
        } else {
            const error = await response.json();
            alert(`Error creating profile: ${error.detail}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// Main App
async function showMainApp() {
    showScreen('main-app');
    document.getElementById('user-name-display').textContent = currentUser.name;

    // Load and display organization(s)
    await loadUserOrganizations();

    // Show admin features if user is admin
    if (currentUser.roles && currentUser.roles.includes('admin')) {
        document.querySelectorAll('.admin-only').forEach(el => {
            el.classList.remove('hidden');
            el.classList.add('visible');
        });
    }

    loadCalendar();
    loadMySchedule();
    loadTimeOff();
}

// Load all organizations user belongs to
async function loadUserOrganizations() {
    try {
        // Get all organizations
        const response = await fetch(`${API_BASE_URL}/organizations/`);
        const data = await response.json();

        // Filter organizations where user is a member
        // For now, we'll assume user belongs to the org they signed up with
        // Find all organizations where this user's email exists as a Person
        const userEmail = currentUser.email;
        const userOrgsResponse = await fetch(`${API_BASE_URL}/people/?org_id=*`);
        const allPeople = await userOrgsResponse.json();

        // Get unique org IDs where this email exists
        const userOrgIds = new Set();
        if (allPeople.people) {
            allPeople.people.forEach(person => {
                if (person.email === userEmail) {
                    userOrgIds.add(person.org_id);
                }
            });
        }

        // Filter to orgs user belongs to
        const userOrgs = data.organizations.filter(org => userOrgIds.has(org.id));

        // If user belongs to multiple orgs, show dropdown
        if (userOrgs.length > 1) {
            const dropdown = document.getElementById('org-dropdown');
            dropdown.innerHTML = userOrgs.map(org =>
                `<option value="${org.id}" ${org.id === currentOrg.id ? 'selected' : ''}>${org.name}</option>`
            ).join('');
            dropdown.style.display = 'block';
            document.getElementById('org-name-display').style.display = 'none';
        } else {
            // Single org - just show badge
            document.getElementById('org-name-display').textContent = currentOrg.name;
            document.getElementById('org-name-display').style.display = 'inline-block';
            document.getElementById('org-dropdown').style.display = 'none';
        }
    } catch (error) {
        console.error('Error loading organizations:', error);
        // Fallback: just show current org name
        document.getElementById('org-name-display').textContent = currentOrg.name;
        document.getElementById('org-name-display').style.display = 'inline-block';
    }
}

// Switch organization when dropdown changes
async function switchOrganization() {
    const dropdown = document.getElementById('org-dropdown');
    const newOrgId = dropdown.value;

    if (newOrgId !== currentOrg.id) {
        try {
            // Load new org data
            const response = await fetch(`${API_BASE_URL}/organizations/${newOrgId}`);
            const orgData = await response.json();

            currentOrg = {
                id: orgData.id,
                name: orgData.name
            };

            saveSession();

            // Reload the entire app with new org
            location.reload();
        } catch (error) {
            alert(`Error switching organization: ${error.message}`);
        }
    }
}

function switchView(viewName) {
    // Save current view to remember on refresh
    saveCurrentView(viewName);

    // Update nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.view === viewName);
    });

    // Update content
    document.querySelectorAll('.view-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${viewName}-view`).classList.add('active');

    // Load data
    if (viewName === 'calendar') loadCalendar();
    if (viewName === 'schedule') loadMySchedule();
    if (viewName === 'availability') loadTimeOff();
    if (viewName === 'admin') loadAdminDashboard();
}

// Calendar View
async function loadCalendar() {
    const calendarEl = document.getElementById('calendar-grid');
    calendarEl.innerHTML = '<div class="loading">Loading your calendar...</div>';

    try {
        // Get all events for the organization
        const eventsResponse = await fetch(`${API_BASE_URL}/events/?org_id=${currentOrg.id}`);
        const eventsData = await eventsResponse.json();

        // Get solutions to see assignments
        const solutionsResponse = await fetch(`${API_BASE_URL}/solutions/?org_id=${currentOrg.id}`);
        const solutionsData = await solutionsResponse.json();

        if (solutionsData.solutions.length === 0) {
            calendarEl.innerHTML = `
                <div class="loading">
                    <p>No schedule generated yet.</p>
                    <p style="margin-top: 10px; color: var(--text-light);">
                        An administrator needs to generate the schedule first.
                    </p>
                </div>
            `;
            return;
        }

        // Find solution with assignments (not just latest, but one with actual assignments)
        const solutionWithAssignments = solutionsData.solutions.find(s => s.assignment_count > 0);

        if (!solutionWithAssignments) {
            calendarEl.innerHTML = `
                <div class="loading">
                    <p>⚠️ No schedule has been generated yet.</p>
                    <p style="margin-top: 10px; color: var(--text-light);">
                        <strong>What does this mean?</strong><br>
                        An administrator needs to run the scheduler to assign people to events.
                    </p>
                    <p style="margin-top: 10px; color: var(--text-light);">
                        <strong>Next steps:</strong><br>
                        1. Make sure <a href="#" onclick="switchView('admin'); return false;" style="color: var(--primary); text-decoration: underline;">events have been created</a><br>
                        2. Make sure <a href="#" onclick="switchView('admin'); return false;" style="color: var(--primary); text-decoration: underline;">people have been added</a><br>
                        3. Ask an admin to <a href="#" onclick="switchView('admin'); return false;" style="color: var(--primary); text-decoration: underline;">run the scheduler</a>
                    </p>
                </div>
            `;
            return;
        }

        // Get assignments for this solution
        const assignmentsResponse = await fetch(
            `${API_BASE_URL}/solutions/${solutionWithAssignments.id}/assignments`
        );
        const assignmentsData = await assignmentsResponse.json();

        // Filter my assignments
        const myAssignments = assignmentsData.assignments.filter(
            a => a.person_id === currentUser.id
        );

        if (myAssignments.length === 0) {
            calendarEl.innerHTML = `
                <div class="loading">
                    <p title="Assignments are when you're scheduled to serve at an event">💡 You have no upcoming assignments.</p>
                    <p style="margin-top: 10px; color: var(--text-light);">
                        <strong>This could mean:</strong><br>
                        • The scheduler didn't assign you to any events yet<br>
                        • Your availability doesn't match any events<br>
                        • You may need to <a href="#" onclick="showSettings(); return false;" style="color: var(--primary); text-decoration: underline;">update your roles</a>
                    </p>
                    <button onclick="switchView('schedule')" title="View the full team schedule to see who's assigned to what" style="margin-top: 15px; padding: 10px 20px; background: var(--primary); color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px;">
                        View Full Schedule
                    </button>
                </div>
            `;
            return;
        }

        // Group by date
        const byDate = {};
        myAssignments.forEach(assignment => {
            const date = new Date(assignment.event_start).toDateString();
            if (!byDate[date]) byDate[date] = [];
            byDate[date].push(assignment);
        });

        // Render calendar
        calendarEl.innerHTML = Object.keys(byDate)
            .sort((a, b) => new Date(a) - new Date(b))
            .map(date => {
                const assignments = byDate[date];
                return `
                    <div class="calendar-day has-event">
                        <div class="calendar-date">${new Date(date).toLocaleDateString('en-US', {
                            weekday: 'long',
                            month: 'long',
                            day: 'numeric'
                        })}</div>
                        ${assignments.map(a => `
                            <div class="calendar-event">
                                <div class="event-time">
                                    ${new Date(a.event_start).toLocaleTimeString('en-US', {
                                        hour: 'numeric',
                                        minute: '2-digit'
                                    })}
                                </div>
                                <div class="event-title">${a.event_type}</div>
                            </div>
                        `).join('')}
                    </div>
                `;
            }).join('');

    } catch (error) {
        calendarEl.innerHTML = `<div class="loading">Error loading calendar: ${error.message}</div>`;
    }
}

async function exportMyCalendar() {
    try {
        const solutionsResponse = await fetch(`${API_BASE_URL}/solutions/?org_id=${currentOrg.id}`);
        const solutionsData = await solutionsResponse.json();

        if (solutionsData.solutions.length === 0) {
            alert('No schedule available to export.');
            return;
        }

        const latestSolution = solutionsData.solutions[0];

        const response = await fetch(`${API_BASE_URL}/solutions/${latestSolution.id}/export`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                format: 'ics',
                scope: `person:${currentUser.id}`
            })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `my_schedule_${currentUser.name.replace(/\s+/g, '_')}.ics`;
            a.click();
            alert('Calendar exported! Import this file into Google Calendar, Outlook, or Apple Calendar.');
        } else {
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
            const errorMsg = errorData.detail || 'Export failed';

            if (errorMsg.includes('no assignments')) {
                alert('No schedule to export yet.\n\nYou haven\'t been assigned to any events. This happens when:\n• The admin hasn\'t generated a schedule yet\n• You\'re not available during any events\n• Your roles don\'t match any event needs\n\nContact your admin if you think this is an error.');
            } else {
                alert(`Export failed: ${errorMsg}`);
            }
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// Schedule View
async function loadMySchedule() {
    const scheduleEl = document.getElementById('schedule-list');
    scheduleEl.innerHTML = '<div class="loading">Loading your schedule...</div>';

    try {
        const solutionsResponse = await fetch(`${API_BASE_URL}/solutions/?org_id=${currentOrg.id}`);
        const solutionsData = await solutionsResponse.json();

        if (solutionsData.solutions.length === 0) {
            scheduleEl.innerHTML = '<div class="loading">No schedule available yet.</div>';
            return;
        }

        // Find solution with assignments (use the one with actual assignments, not just latest)
        const solutionWithAssignments = solutionsData.solutions.find(s => s.assignment_count > 0);

        if (!solutionWithAssignments) {
            scheduleEl.innerHTML = '<div class="loading">⚠️ No assignments found. The scheduler hasn\'t run yet.</div>';
            return;
        }

        const assignmentsResponse = await fetch(
            `${API_BASE_URL}/solutions/${solutionWithAssignments.id}/assignments`
        );
        const assignmentsData = await assignmentsResponse.json();

        const myAssignments = assignmentsData.assignments
            .filter(a => a.person_id === currentUser.id)
            .sort((a, b) => new Date(a.event_start) - new Date(b.event_start));

        // Update stats
        const now = new Date();
        const upcoming = myAssignments.filter(a => new Date(a.event_start) > now);
        const thisMonth = upcoming.filter(a => {
            const eventDate = new Date(a.event_start);
            return eventDate.getMonth() === now.getMonth();
        });

        document.getElementById('upcoming-count').textContent = upcoming.length;
        document.getElementById('this-month-count').textContent = thisMonth.length;

        // Render schedule
        if (upcoming.length === 0) {
            scheduleEl.innerHTML = '<div class="loading">No upcoming assignments.</div>';
            return;
        }

        scheduleEl.innerHTML = upcoming.map(a => `
            <div class="schedule-item">
                <div class="schedule-info">
                    <h3>${a.event_type}</h3>
                    <div class="schedule-meta">
                        📅 ${new Date(a.event_start).toLocaleDateString('en-US', {
                            weekday: 'long',
                            month: 'long',
                            day: 'numeric',
                            year: 'numeric'
                        })}
                        <br>
                        ⏰ ${new Date(a.event_start).toLocaleTimeString('en-US', {
                            hour: 'numeric',
                            minute: '2-digit'
                        })} - ${new Date(a.event_end).toLocaleTimeString('en-US', {
                            hour: 'numeric',
                            minute: '2-digit'
                        })}
                    </div>
                </div>
                <span class="schedule-badge">Confirmed</span>
            </div>
        `).join('');

    } catch (error) {
        scheduleEl.innerHTML = `<div class="loading">Error: ${error.message}</div>`;
    }
}

// Availability Management
async function loadTimeOff() {
    const listEl = document.getElementById('timeoff-list');
    listEl.innerHTML = '<div class="loading">Loading...</div>';

    try {
        const response = await fetch(`${API_BASE_URL}/availability/${currentUser.id}/timeoff`);
        const data = await response.json();

        if (data.total === 0) {
            listEl.innerHTML = '<p class="help-text">No time-off periods set. Add one above!</p>';
            return;
        }

        listEl.innerHTML = '<h3>Your Blocked Dates</h3>' + data.timeoff.map(timeoff => `
            <div class="timeoff-item">
                <div>
                    <div class="timeoff-dates">
                        ${new Date(timeoff.start_date).toLocaleDateString()} -
                        ${new Date(timeoff.end_date).toLocaleDateString()}
                    </div>
                </div>
                <div class="timeoff-actions">
                    <button class="btn btn-small btn-secondary" onclick="editTimeOff(${timeoff.id}, '${timeoff.start_date}', '${timeoff.end_date}')">Edit</button>
                    <button class="btn btn-small btn-remove" onclick="removeTimeOff(${timeoff.id})">Remove</button>
                </div>
            </div>
        `).join('');

    } catch (error) {
        listEl.innerHTML = `<p class="help-text">Error loading time-off: ${error.message}</p>`;
    }
}

async function addTimeOff(event) {
    event.preventDefault();

    const start = document.getElementById('timeoff-start').value;
    const end = document.getElementById('timeoff-end').value;

    try {
        const response = await fetch(`${API_BASE_URL}/availability/${currentUser.id}/timeoff`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                start_date: start,
                end_date: end
            })
        });

        if (response.ok) {
            event.target.reset();
            loadTimeOff();
            alert('Time-off period added successfully!');
        } else {
            const error = await response.json();
            alert(`Error: ${error.detail}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

async function editTimeOff(timeoffId, startDate, endDate) {
    const newStart = prompt('Edit start date (YYYY-MM-DD):', startDate);
    if (!newStart) return;

    const newEnd = prompt('Edit end date (YYYY-MM-DD):', endDate);
    if (!newEnd) return;

    try {
        const response = await fetch(
            `${API_BASE_URL}/availability/${currentUser.id}/timeoff/${timeoffId}`,
            {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    start_date: newStart,
                    end_date: newEnd
                })
            }
        );

        if (response.ok) {
            loadTimeOff();
            alert('Time-off period updated successfully!');
        } else {
            const error = await response.json();
            alert(`Error: ${error.detail}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

async function removeTimeOff(timeoffId) {
    if (!confirm('Remove this time-off period?')) return;

    try {
        const response = await fetch(
            `${API_BASE_URL}/availability/${currentUser.id}/timeoff/${timeoffId}`,
            { method: 'DELETE' }
        );

        if (response.ok || response.status === 204) {
            loadTimeOff();
        } else {
            alert('Error removing time-off');
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// Settings
function showSettings() {
    document.getElementById('settings-modal').classList.remove('hidden');
    document.getElementById('settings-name').value = currentUser.name;
    document.getElementById('settings-email').value = currentUser.email || '';
    document.getElementById('settings-org').value = currentOrg.name;

    // Check the appropriate role checkboxes
    const roleCheckboxes = document.querySelectorAll('#settings-role-selector input[type="checkbox"]');
    roleCheckboxes.forEach(checkbox => {
        checkbox.checked = (currentUser.roles || []).includes(checkbox.value);
    });
}

async function saveSettings() {
    try {
        // Collect checked roles
        const roleCheckboxes = document.querySelectorAll('#settings-role-selector input[type="checkbox"]:checked');
        const roles = Array.from(roleCheckboxes).map(cb => cb.value);

        if (roles.length === 0) {
            alert('Please select at least one role');
            return;
        }

        const response = await fetch(`${API_BASE_URL}/people/${currentUser.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ roles })
        });

        if (response.ok) {
            currentUser.roles = roles;
            saveSession();
            alert('Settings saved successfully!');
            closeSettings();

            // Refresh admin UI if roles changed
            if (currentUser.roles.includes('admin')) {
                location.reload();
            }
        } else {
            const error = await response.json();
            alert(`Error: ${error.detail}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

function closeSettings() {
    document.getElementById('settings-modal').classList.add('hidden');
}

// ============================================================================
// ADMIN DASHBOARD
// ============================================================================

async function loadAdminDashboard() {
    loadAdminStats();
    loadAdminRoles();
    loadAdminEvents();
    loadAdminPeople();
    loadAdminSolutions();
}

async function loadAdminStats() {
    try {
        const [peopleRes, eventsRes, solutionsRes] = await Promise.all([
            fetch(`${API_BASE_URL}/people/?org_id=${currentOrg.id}`),
            fetch(`${API_BASE_URL}/events/?org_id=${currentOrg.id}`),
            fetch(`${API_BASE_URL}/solutions/?org_id=${currentOrg.id}`)
        ]);

        const peopleData = await peopleRes.json();
        const eventsData = await eventsRes.json();
        const solutionsData = await solutionsRes.json();

        document.getElementById('admin-people-count').textContent = peopleData.total || 0;
        document.getElementById('admin-events-count').textContent = eventsData.total || 0;
        document.getElementById('admin-solutions-count').textContent = solutionsData.total || 0;
    } catch (error) {
        console.error('Error loading admin stats:', error);
    }
}

async function loadAdminEvents() {
    const listEl = document.getElementById('admin-events-list');
    listEl.innerHTML = '<div class="loading">Loading events...</div>';

    try {
        const response = await fetch(`${API_BASE_URL}/events/?org_id=${currentOrg.id}`);
        const data = await response.json();

        if (data.total === 0) {
            listEl.innerHTML = '<p class="help-text">No events yet. Create one to get started!</p>';
            return;
        }

        listEl.innerHTML = data.events.map(event => `
            <div class="admin-item">
                <div class="admin-item-info">
                    <h4>${event.type}</h4>
                    <div class="admin-item-meta">
                        📅 ${new Date(event.start_time).toLocaleString('en-US', {
                            weekday: 'short',
                            month: 'short',
                            day: 'numeric',
                            hour: 'numeric',
                            minute: '2-digit'
                        })}
                        ${event.extra_data && event.extra_data.roles && event.extra_data.roles.length > 0 ?
                          `<br>Roles: ${event.extra_data.roles.join(', ')}` : ''}
                    </div>
                </div>
                <div class="admin-item-actions">
                    <button class="btn btn-small btn-remove" onclick="deleteEvent('${event.id}')">Delete</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        listEl.innerHTML = `<p class="help-text">Error loading events: ${error.message}</p>`;
    }
}

async function loadAdminPeople() {
    const listEl = document.getElementById('admin-people-list');
    listEl.innerHTML = '<div class="loading">Loading people...</div>';

    try {
        const response = await fetch(`${API_BASE_URL}/people/?org_id=${currentOrg.id}`);
        const data = await response.json();

        if (data.total === 0) {
            listEl.innerHTML = '<p class="help-text">No people registered yet.</p>';
            return;
        }

        listEl.innerHTML = data.people.map(person => `
            <div class="admin-item">
                <div class="admin-item-info">
                    <h4>${person.name}</h4>
                    <div class="admin-item-meta">
                        ${person.email || 'No email'}
                        ${person.roles && person.roles.length > 0 ? `<br>Roles: ${person.roles.join(', ')}` : ''}
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        listEl.innerHTML = `<p class="help-text">Error loading people: ${error.message}</p>`;
    }
}

async function loadAdminSolutions() {
    const listEl = document.getElementById('admin-solutions-list');
    listEl.innerHTML = '<div class="loading">Loading schedules...</div>';

    try {
        const response = await fetch(`${API_BASE_URL}/solutions/?org_id=${currentOrg.id}`);
        const data = await response.json();

        if (data.total === 0) {
            listEl.innerHTML = '<p class="help-text">No schedules generated yet. Click "Generate Schedule" above!</p>';
            return;
        }

        listEl.innerHTML = data.solutions.map(solution => `
            <div class="admin-item">
                <div class="admin-item-info">
                    <h4>Schedule ${solution.id}</h4>
                    <div class="admin-item-meta">
                        Created: ${new Date(solution.created_at).toLocaleString()}
                        <br>Health Score: ${solution.health_score?.toFixed(1) || 'N/A'}/100
                        <br>Assignments: ${solution.assignment_count || 0}
                    </div>
                </div>
                <div class="admin-item-actions">
                    <button class="btn btn-small btn-secondary" onclick="viewSolution(${solution.id})">View</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        listEl.innerHTML = `<p class="help-text">Error loading schedules: ${error.message}</p>`;
    }
}

// Event Management
function showCreateEventForm() {
    document.getElementById('create-event-modal').classList.remove('hidden');
}

function closeCreateEventForm() {
    document.getElementById('create-event-modal').classList.add('hidden');
    document.getElementById('create-event-form').reset();
}

async function createEvent(event) {
    event.preventDefault();

    const type = document.getElementById('event-type').value;
    const start = document.getElementById('event-start').value;
    const duration = parseFloat(document.getElementById('event-duration').value);
    const location = document.getElementById('event-location').value;
    const rolesInput = document.getElementById('event-roles').value;

    const roles = rolesInput.split(',').map(r => r.trim()).filter(r => r);

    // Calculate end time
    const startDate = new Date(start);
    const endDate = new Date(startDate.getTime() + duration * 60 * 60 * 1000);

    // Generate event ID
    const eventId = `${type.toLowerCase().replace(/\s+/g, '_')}_${Date.now()}`;

    try {
        const response = await fetch(`${API_BASE_URL}/events/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: eventId,
                org_id: currentOrg.id,
                type: type,
                start_time: startDate.toISOString(),
                end_time: endDate.toISOString(),
                resource_id: location || null,
                extra_data: { roles: roles.length > 0 ? roles : [] }
            })
        });

        if (response.ok) {
            closeCreateEventForm();
            loadAdminEvents();
            loadAdminStats();
            alert('Event created successfully!');
        } else {
            const error = await response.json();
            alert(`Error creating event: ${error.detail}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

async function deleteEvent(eventId) {
    if (!confirm('Delete this event? This cannot be undone.')) return;

    try {
        const response = await fetch(`${API_BASE_URL}/events/${eventId}`, {
            method: 'DELETE'
        });

        if (response.ok || response.status === 204) {
            loadAdminEvents();
            loadAdminStats();
            alert('Event deleted successfully!');
        } else {
            alert('Error deleting event');
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// Schedule Generation
async function generateSchedule() {
    const statusEl = document.getElementById('solver-status');
    statusEl.innerHTML = '<div class="solver-status running">⏳ Generating schedule... This may take a moment.</div>';

    try {
        // Calculate date range (next 90 days)
        const today = new Date();
        const futureDate = new Date(today.getTime() + 90 * 24 * 60 * 60 * 1000);

        const response = await fetch(`${API_BASE_URL}/solver/solve`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                org_id: currentOrg.id,
                from_date: today.toISOString().split('T')[0],
                to_date: futureDate.toISOString().split('T')[0]
            })
        });

        const data = await response.json();

        if (response.ok) {
            statusEl.innerHTML = `
                <div class="solver-status success">
                    ✓ Schedule generated successfully!<br>
                    Solution ID: ${data.solution_id}<br>
                    Assignments: ${data.metrics?.assignment_count || 0}<br>
                    Health Score: ${data.metrics?.health_score?.toFixed(1) || 'N/A'}/100
                </div>
            `;
            loadAdminSolutions();
            loadAdminStats();

            // Refresh user's calendar if they're viewing it
            loadCalendar();
            loadMySchedule();
        } else {
            statusEl.innerHTML = `
                <div class="solver-status error">
                    ✗ Error: ${data.detail || 'Failed to generate schedule'}
                </div>
            `;
        }
    } catch (error) {
        statusEl.innerHTML = `
            <div class="solver-status error">
                ✗ Error: ${error.message}
            </div>
        `;
    }
}

async function viewSolution(solutionId) {
    try {
        const response = await fetch(`${API_BASE_URL}/solutions/${solutionId}/export`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ format: 'csv' })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `schedule_${solutionId}.csv`;
            a.click();
            alert('Schedule downloaded! Open in spreadsheet software to view.');
        } else {
            // Get detailed error message
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
            const errorMsg = errorData.detail || errorData.message || 'Error exporting schedule';

            if (errorMsg.includes('no assignments')) {
                alert('Cannot export schedule: No assignments were generated.\n\nThis usually means:\n• Not enough people are available\n• People don\'t have matching roles for events\n• People are blocked during event times\n\nTry adding more people or adjusting availability settings.');
            } else {
                alert(`Error exporting schedule: ${errorMsg}`);
            }
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}
