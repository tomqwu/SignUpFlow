// User-Friendly Roster App
// Only declare API_BASE_URL if not already defined
if (typeof API_BASE_URL === 'undefined') {
    var API_BASE_URL = '/api';
}

// User State - attach to window so router can access it
let currentUser = null;
let currentOrg = null;

// Expose to window for router access
window.currentUser = currentUser;
window.currentOrg = currentOrg;

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    // Initialize i18n first
    await i18n.init();

    // Check if user has a saved language preference
    const savedUser = localStorage.getItem('roster_user');
    console.log('🔄 DOMContentLoaded - localStorage roster_user:', savedUser ? JSON.parse(savedUser) : null);
    if (savedUser) {
        const user = JSON.parse(savedUser);
        console.log('🌐 DOMContentLoaded - User language from localStorage:', user.language, 'Current i18n locale:', i18n.getLocale());
        if (user.language && user.language !== i18n.getLocale()) {
            console.log('🔧 DOMContentLoaded - Setting locale to:', user.language);
            await i18n.setLocale(user.language);
        }
    }

    // Translate the page
    translatePage();

    checkExistingSession();
});

// Translate all elements with data-i18n attribute
function translatePage() {
    // Translate text content
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        const translated = i18n.t(key);

        // Handle placeholders
        if (el.hasAttribute('placeholder')) {
            el.setAttribute('placeholder', translated);
        } else if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
            // Don't change value, only placeholder
        } else {
            el.textContent = translated;
        }
    });

    // Translate placeholders separately
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        const translated = i18n.t(key);
        el.setAttribute('placeholder', translated);
    });
}

/**
 * Translate an API response message.
 *
 * The backend returns message_key and message_params for i18n support.
 * This function translates the key using the user's selected language.
 *
 * @param {Object} response - API response with message_key and message_params
 * @returns {string} Translated message
 */
function translateApiMessage(response) {
    if (response && response.message_key) {
        return i18n.t(response.message_key, response.message_params || {});
    }
    // Fallback for old responses that don't have message_key
    return response?.message || response?.detail || 'Unknown error';
}

/**
 * Handle API error and return translated error message.
 *
 * @param {Error|Response} error - Fetch error or response object
 * @returns {Promise<string>} Translated error message
 */
async function getApiErrorMessage(error) {
    let message;

    if (error.response) {
        try {
            const data = await error.response.json();
            // Check if detail is an object with message_key (new format)
            if (typeof data.detail === 'object' && data.detail.message_key) {
                message = i18n.t(data.detail.message_key, data.detail.message_params || {});
            } else {
                // Old format: detail is a string
                message = data.detail || data.message || 'Unknown error';
            }
        } catch (e) {
            message = error.message;
        }
    } else if (error.message_key) {
        // Direct error object with message_key
        message = i18n.t(error.message_key, error.message_params || {});
    } else {
        message = error.message || 'Unknown error';
    }

    return message;
}

// Session Management
function checkExistingSession() {
    const savedUser = localStorage.getItem('roster_user');
    const savedOrg = localStorage.getItem('roster_org');
    const currentPath = window.location.pathname;

    if (savedUser && savedOrg) {
        currentUser = JSON.parse(savedUser);
        currentOrg = JSON.parse(savedOrg);
        window.currentUser = currentUser;
        window.currentOrg = currentOrg;

        // If on a protected /app route, handle it with router
        if (currentPath.startsWith('/app')) {
            router.handleRoute(currentPath, false);
        } else {
            // Default to schedule view if logged in but on root/login page
            router.navigate('/app/schedule', true);
            showMainApp();
        }
    } else {
        // Not logged in - initialize router for auth screens
        // router.init() handles all routing including protected routes
        router.init();
    }
}

function saveSession() {
    console.log('💿 saveSession - Saving to localStorage:', {
        user: { id: currentUser.id, name: currentUser.name, timezone: currentUser.timezone, language: currentUser.language },
        org: currentOrg.name
    });
    localStorage.setItem('roster_user', JSON.stringify(currentUser));
    localStorage.setItem('roster_org', JSON.stringify(currentOrg));
}

function saveCurrentView(viewName) {
    localStorage.setItem('roster_current_view', viewName);
}

function logout() {
    // Clear all session data including auth token
    localStorage.clear();  // Clears authToken, currentUser, currentOrg
    currentUser = null;
    currentOrg = null;
    window.currentUser = null;
    window.currentOrg = null;
    router.navigate('/', true);
    location.reload();
}

function goToHome() {
    // Navigate to schedule view if logged in, otherwise go to onboarding
    if (currentUser && currentOrg) {
        switchView('schedule');
    } else {
        router.navigate('/');
    }
}

// Screen Navigation (Note: router.js also has a showScreen method)
function showScreen(screenId) {
    console.log(`📺 showScreen called with: ${screenId}`);
    document.querySelectorAll('.screen').forEach(s => s.classList.add('hidden'));
    const screen = document.getElementById(screenId);
    if (screen) {
        screen.classList.remove('hidden');
        console.log(`📺 Showing screen: ${screenId}`);
    } else {
        console.error(`📺 Screen not found: ${screenId}`);
    }
}

function startOnboarding() {
    console.log('📝 startOnboarding called');
    router.navigate('/join');
}

function showLogin() {
    console.log('🔐 showLogin called');
    router.navigate('/login');
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

            console.log('🔐 handleLogin - Backend response data:', data);

            // Save JWT token to localStorage
            localStorage.setItem('authToken', data.token);

            currentUser = {
                id: data.person_id,
                name: data.name,
                email: data.email,
                org_id: data.org_id,
                roles: data.roles,
                timezone: data.timezone,
                language: data.language || 'en'
            };
            currentOrg = orgData;
            window.currentUser = currentUser;
            window.currentOrg = currentOrg;

            console.log('👤 handleLogin - Created currentUser:', { id: currentUser.id, name: currentUser.name, timezone: currentUser.timezone, language: currentUser.language });
            console.log('🔐 Auth token saved to localStorage');

            // Debug: Log roles to check structure
            console.log('Login - currentUser.roles:', currentUser.roles, 'Type:', typeof currentUser.roles);

            // Set user's language preference
            if (currentUser.language && currentUser.language !== i18n.getLocale()) {
                console.log('🌐 handleLogin - Setting language to:', currentUser.language);
                await i18n.setLocale(currentUser.language);
                translatePage();
            }

            saveSession();
            router.navigate('/app/schedule', true);
            showMainApp();
        } else {
            let errorMessage = '';
            try {
                const error = await response.json();
                errorMessage = translateApiMessage(error);
            } catch (parseError) {
                console.warn('Login error response was not JSON:', parseError);
            }

            if (typeof errorMessage === 'string' && errorMessage.trim().toLowerCase() === 'invalid email or password') {
                errorMessage = i18n.t('auth.login.error');
            }

            errorEl.textContent = errorMessage || i18n.t('auth.login.error');
            errorEl.classList.remove('hidden');
        }
    } catch (error) {
        errorEl.textContent = i18n.t('messages.errors.connection_error');
        errorEl.classList.remove('hidden');
    }
}

// ============================================================================
// PASSWORD RESET
// ============================================================================

function showForgotPassword() {
    console.log('🔑 showForgotPassword called');
    router.navigate('/forgot-password');
}

async function handleForgotPassword(event) {
    event.preventDefault();

    const email = document.getElementById('forgot-email').value;
    const errorEl = document.getElementById('forgot-error');
    const successEl = document.getElementById('forgot-success');

    errorEl.classList.add('hidden');
    successEl.classList.add('hidden');

    try {
        // Get reCAPTCHA token for password_reset action
        let fetchOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        };
        fetchOptions = await addRecaptchaToken('password_reset', fetchOptions);

        const response = await fetch(`${API_BASE_URL}/auth/forgot-password`, fetchOptions);

        if (response.ok) {
            const data = await response.json();
            successEl.textContent = i18n.t('auth.password_reset_email_sent') || 'Check your email for reset instructions';
            successEl.classList.remove('hidden');

            // In development, show the reset link
            if (data.reset_link) {
                console.log('🔑 Password reset link (dev only):', data.reset_link);
                // Extract token from link and show reset screen directly in dev mode
                const token = data.reset_link.split('token=')[1];
                setTimeout(() => {
                    showResetPasswordWithToken(token);
                }, 2000);
            }
        } else {
            // Show same success message even on error to prevent email enumeration
            successEl.textContent = i18n.t('auth.password_reset_email_sent') || 'Check your email for reset instructions';
            successEl.classList.remove('hidden');
        }
    } catch (error) {
        console.error('Password reset request error:', error);
        successEl.textContent = i18n.t('auth.password_reset_email_sent') || 'Check your email for reset instructions';
        successEl.classList.remove('hidden');
    }
}

function showResetPasswordWithToken(token) {
    console.log('🔑 showResetPasswordWithToken called with token');
    document.getElementById('reset-token').value = token;
    router.navigate('/reset-password');
}

async function handleResetPassword(event) {
    event.preventDefault();

    const token = document.getElementById('reset-token').value;
    const password = document.getElementById('reset-password').value;
    const confirmPassword = document.getElementById('reset-password-confirm').value;
    const errorEl = document.getElementById('reset-error');
    const successEl = document.getElementById('reset-success');

    errorEl.classList.add('hidden');
    successEl.classList.add('hidden');

    // Validate password match
    if (password !== confirmPassword) {
        errorEl.textContent = i18n.t('auth.passwords_dont_match') || 'Passwords do not match';
        errorEl.classList.remove('hidden');
        return;
    }

    // Validate password length
    if (password.length < 8) {
        errorEl.textContent = i18n.t('auth.password_too_short') || 'Password must be at least 8 characters';
        errorEl.classList.remove('hidden');
        return;
    }

    try {
        // Get reCAPTCHA token for password_reset_confirm action
        let fetchOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token, new_password: password })
        };
        fetchOptions = await addRecaptchaToken('password_reset_confirm', fetchOptions);

        const response = await fetch(`${API_BASE_URL}/auth/reset-password`, fetchOptions);

        if (response.ok) {
            successEl.textContent = i18n.t('auth.password_reset_success') || 'Password reset successful! Redirecting to login...';
            successEl.classList.remove('hidden');

            // Redirect to login after 2 seconds
            setTimeout(() => {
                showLogin();
            }, 2000);
        } else {
            const error = await response.json();
            errorEl.textContent = error.detail || i18n.t('auth.password_reset_failed');
            errorEl.classList.remove('hidden');
        }
    } catch (error) {
        console.error('Password reset error:', error);
        errorEl.textContent = i18n.t('messages.errors.connection_error');
        errorEl.classList.remove('hidden');
    }
}

function showLogin_old() {
    showToast(i18n.t('messages.info.login_coming_soon'), 'info');
}

// Organization Selection - Search-based for privacy
// Global variable to store invitation data
let currentInvitation = null;

// Detect user's timezone from browser
function detectTimezone() {
    try {
        return Intl.DateTimeFormat().resolvedOptions().timeZone;
    } catch (error) {
        console.warn('Could not detect timezone, defaulting to UTC:', error);
        return 'UTC';
    }
}

// Verify invitation token
async function verifyInvitationToken(event) {
    event.preventDefault();

    const token = document.getElementById('invitation-token').value.trim();
    const errorEl = document.getElementById('invitation-error');

    if (!token) {
        errorEl.textContent = i18n.t('auth.invitation_required');
        errorEl.classList.remove('hidden');
        return;
    }

    try {
        // Call invitation verification API
        const response = await fetch(`${API_BASE_URL}/invitations/${token}`);
        const data = await response.json();

        if (!response.ok || !data.valid) {
            errorEl.textContent = data.message || i18n.t('auth.invalid_invitation');
            errorEl.classList.remove('hidden');
            return;
        }

        // Store invitation data
        currentInvitation = data.invitation;

        // Pre-fill profile form with invitation data
        document.getElementById('user-name').value = currentInvitation.name;
        document.getElementById('user-email').value = currentInvitation.email;
        document.getElementById('invitation-token-hidden').value = token;

        // Display assigned roles
        const rolesDisplay = document.getElementById('invitation-roles-display');
        if (currentInvitation.roles && currentInvitation.roles.length > 0) {
            rolesDisplay.innerHTML = currentInvitation.roles.map(role =>
                `<span class="role-badge">${role}</span>`
            ).join('');
        } else {
            rolesDisplay.innerHTML = '<span class="role-badge">volunteer</span>';
        }

        // Auto-detect and set timezone
        const detectedTimezone = detectTimezone();
        const timezoneSelect = document.getElementById('user-timezone');
        timezoneSelect.value = detectedTimezone;
        console.log('🌍 Detected timezone:', detectedTimezone);

        // Show profile screen
        showScreen('profile-screen');

    } catch (error) {
        errorEl.textContent = i18n.t('messages.errors.generic') + ': ' + error.message;
        errorEl.classList.remove('hidden');
    }
}

// Complete invitation-based signup
async function completeInvitationSignup(event) {
    event.preventDefault();

    const token = document.getElementById('invitation-token-hidden').value;
    const password = document.getElementById('user-password').value;
    const timezone = document.getElementById('user-timezone').value;

    if (!token || !password) {
        showToast(i18n.t('messages.errors.missing_fields'), 'error');
        return;
    }

    try {
        // Accept invitation and create account
        const response = await fetch(`${API_BASE_URL}/invitations/${token}/accept`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                password: password,
                timezone: timezone
            })
        });

        if (!response.ok) {
            const error = await response.json();
            showToast(error.detail || i18n.t('messages.errors.signup_failed'), 'error');
            return;
        }

        const data = await response.json();

        // Fetch organization details to get the org name
        const orgResponse = await fetch(`${API_BASE_URL}/organizations/${data.org_id}`);
        const orgData = await orgResponse.json();

        // Save JWT token to localStorage
        localStorage.setItem('authToken', data.token);

        // Store user session
        currentUser = {
            id: data.person_id,
            name: data.name,
            email: data.email,
            roles: data.roles,
            timezone: data.timezone,
            language: i18n.getLocale(),
            org_id: data.org_id
        };

        currentOrg = {
            id: data.org_id,
            name: orgData.name || data.org_id
        };

        window.currentUser = currentUser;
        window.currentOrg = currentOrg;

        saveSession();

        // Show success message
        showToast(i18n.t('auth.welcome_message') || data.message, 'success');

        // Load main app
        await showMainApp();

    } catch (error) {
        showToast(i18n.t('messages.errors.generic') + ': ' + error.message, 'error');
    }
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
        // Get reCAPTCHA token for create_org action
        let fetchOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: orgId,
                name: orgName,
                region: orgRegion || null,
                config: {}
            })
        };
        fetchOptions = await addRecaptchaToken('create_org', fetchOptions);

        const response = await fetch(`${API_BASE_URL}/organizations/`, fetchOptions);

        if (response.ok || response.status === 409) {
            currentOrg = { id: orgId, name: orgName };

            // Clear and prepare the profile form for new org creator signup
            document.getElementById('user-name').value = '';
            document.getElementById('user-email').value = '';
            document.getElementById('user-password').value = '';
            document.getElementById('invitation-token-hidden').value = '';

            // Auto-detect and set timezone from browser
            const detectedTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            const timezoneSelect = document.getElementById('user-timezone');
            if (timezoneSelect && detectedTimezone) {
                // Try to set to detected timezone, fall back to UTC if not in list
                const option = Array.from(timezoneSelect.options).find(opt => opt.value === detectedTimezone);
                if (option) {
                    timezoneSelect.value = detectedTimezone;
                }
            }

            // Hide invitation-specific UI elements (roles section)
            const rolesDisplayParent = document.getElementById('invitation-roles-display')?.closest('.form-group');
            if (rolesDisplayParent) {
                rolesDisplayParent.style.display = 'none';
            }

            // Change the form submission handler to createProfile instead of completeInvitationSignup
            const profileForm = document.querySelector('#profile-screen form');
            profileForm.onsubmit = createProfile;

            showScreen('profile-screen');
        } else {
            showToast(i18n.t('messages.errors.create_org_failed'), 'error');
        }
    } catch (error) {
        showToast(i18n.t('messages.errors.generic') + ': ' + error.message, 'error');
    }
}

// Profile Creation
async function createProfile(event) {
    event.preventDefault();

    const name = document.getElementById('user-name').value;
    const email = document.getElementById('user-email').value;
    const password = document.getElementById('user-password').value;

    // For new org creators, default to admin role
    // Role selector may not exist on profile-screen, so provide fallback
    const roleSelector = document.querySelector('#role-selector');
    const roles = roleSelector
        ? Array.from(document.querySelectorAll('#role-selector input:checked')).map(input => input.value)
        : ['admin'];  // Default role for organization creators

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

            // Save JWT token to localStorage
            localStorage.setItem('authToken', data.token);

            currentUser = {
                id: data.person_id,
                name: data.name,
                email: data.email,
                org_id: data.org_id,
                roles: data.roles
            };
            window.currentUser = currentUser;
            console.log('🔐 Auth token saved to localStorage');
            saveSession();
            showMainApp();
        } else if (response.status === 409) {
            showToast(i18n.t('messages.errors.email_already_registered'), 'error');
        } else {
            const error = await response.json();
            showToast(i18n.t('messages.errors.create_profile_failed', { detail: error.detail }), 'error');
        }
    } catch (error) {
        showToast(i18n.t('messages.errors.generic') + ': ' + error.message, 'error');
    }
}

// Main App
async function showMainApp() {
    showScreen('main-app');
    router.navigate('/app/schedule', true);  // Update URL to /app/schedule
    document.getElementById('user-name-display').textContent = currentUser.name;

    // Load and display organization(s)
    await loadUserOrganizations();

    // Update role badges display
    updateRoleBadgesDisplay();

    // Show admin features if user is admin
    if (currentUser.roles && currentUser.roles.includes('admin')) {
        document.querySelectorAll('.admin-only').forEach(el => {
            el.classList.remove('hidden');
            el.classList.add('visible');
        });
    }

    loadMySchedule();
    loadTimeOff();
}

// Load all organizations user belongs to
async function loadUserOrganizations() {
    try {
        // User belongs to their org_id from currentUser
        // Simplified to avoid N+1 query problem
        const dropdown = document.getElementById('org-dropdown');
        const visibleDropdown = document.getElementById('org-dropdown-visible');

        const singleOrgHTML = `<option value="${currentOrg.id}" selected>${currentOrg.name}</option>`;
        if (dropdown) dropdown.innerHTML = singleOrgHTML;
        if (visibleDropdown) visibleDropdown.innerHTML = singleOrgHTML;

        const orgDisplay = document.getElementById('org-name-display');
        if (orgDisplay) {
            orgDisplay.textContent = currentOrg.name;
            orgDisplay.style.display = 'inline-block';
        }
        if (dropdown) dropdown.style.display = 'none';
    } catch (error) {
        console.error('Error loading organizations:', error);
    }
}

// Switch organization when dropdown changes
async function switchOrganization() {
    // Check both the old hidden dropdown and the new visible one
    const dropdown = document.getElementById('org-dropdown');
    const visibleDropdown = document.getElementById('org-dropdown-visible');

    // Get value from whichever dropdown was changed
    const newOrgId = (visibleDropdown && visibleDropdown.value) ? visibleDropdown.value : dropdown.value;

    // Sync both dropdowns
    if (visibleDropdown && dropdown) {
        visibleDropdown.value = newOrgId;
        dropdown.value = newOrgId;
    }

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
            showToast(i18n.t('messages.errors.switch_org_failed', { message: error.message }), 'error');
        }
    }
}

function switchView(viewName, skipUrlUpdate = false) {
    // Update URL (unless called from router to avoid double navigation)
    if (!skipUrlUpdate) {
        router.navigate(`/app/${viewName}`, true);
    }

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
    const targetView = document.getElementById(`${viewName}-view`);
    if (targetView) {
        targetView.classList.add('active');
    }

    // Load data
    if (viewName === 'schedule') loadMySchedule();
    if (viewName === 'events') loadAllEvents();
    if (viewName === 'availability') loadTimeOff();
    if (viewName === 'admin') loadAdminDashboard();
}

// All Events View
async function loadAllEvents() {
    const eventsEl = document.getElementById('all-events-list');
    eventsEl.innerHTML = `<div class="loading">${i18n.t('messages.loading.events')}</div>`;

    try {
        // Get all events
        const eventsResponse = await authFetch(`${API_BASE_URL}/events/?org_id=${currentUser.org_id}`);
        const eventsData = await eventsResponse.json();

        // Get ALL assignments (both from solutions and manual)
        const assignmentsResponse = await authFetch(`${API_BASE_URL}/events/assignments/all?org_id=${currentUser.org_id}`);
        const assignmentsData = await assignmentsResponse.json();
        const assignments = assignmentsData.assignments;

        // Get all people to show names
        const peopleResponse = await authFetch(`${API_BASE_URL}/people/?org_id=${currentUser.org_id}`);
        const peopleData = await peopleResponse.json();
        const peopleMap = {};
        // Defensive check: peopleData.people might be undefined
        if (peopleData.people && Array.isArray(peopleData.people)) {
            peopleData.people.forEach(p => peopleMap[p.id] = p.name);
        }

        // Filter and sort events
        const now = new Date();
        const upcomingEvents = eventsData.events
            .filter(e => new Date(e.start_time) > now)
            .sort((a, b) => new Date(a.start_time) - new Date(b.start_time));

        if (upcomingEvents.length === 0) {
            eventsEl.innerHTML = `<div class="loading">${i18n.t('messages.empty.no_upcoming_events')}</div>`;
            return;
        }

        // Render events with participants
        eventsEl.innerHTML = upcomingEvents.map(event => {
            const eventDate = new Date(event.start_time);
            const eventAssignments = assignments.filter(a => a.event_id === event.id);
            const isUserAssigned = eventAssignments.some(a => a.person_id === currentUser.id);

            return `
            <div class="event-card ${isUserAssigned ? 'event-card-assigned' : ''}">
                <div class="event-header">
                    <h3>${event.type}</h3>
                    <div class="event-actions">
                        ${isUserAssigned ?
                            `<button class="btn btn-small btn-remove" onclick="leaveEvent('${event.id}')">${i18n.t('events.leave_event')}</button>` :
                            `<button class="btn btn-small btn-primary" onclick="joinEvent('${event.id}')">${i18n.t('events.join_event')}</button>`
                        }
                    </div>
                </div>
                <div class="event-details">
                    <div class="event-time">
                        📅 ${eventDate.toLocaleDateString('en-US', {
                            weekday: 'long',
                            month: 'long',
                            day: 'numeric',
                            year: 'numeric'
                        })}
                        <br>
                        ⏰ ${eventDate.toLocaleTimeString('en-US', {
                            hour: 'numeric',
                            minute: '2-digit'
                        })} - ${new Date(event.end_time).toLocaleTimeString('en-US', {
                            hour: 'numeric',
                            minute: '2-digit'
                        })}
                    </div>
                    ${event.location ? `<div class="event-location">📍 ${event.location}</div>` : ''}
                </div>
                <div class="event-participants">
                    <h4>Volunteers (${eventAssignments.length}):</h4>
                    ${eventAssignments.length > 0 ? `
                        <ul class="participants-list">
                            ${eventAssignments.map(a => {
                                const roleBadge = a.role ? ` <span class="role-badge">${a.role}</span>` : '';
                                return `
                                    <li class="${a.person_id === currentUser.id ? 'participant-me' : ''}">
                                        ${peopleMap[a.person_id] || a.person_id}${roleBadge}
                                        ${a.person_id === currentUser.id ? ' (You)' : ''}
                                    </li>
                                `;
                            }).join('')}
                        </ul>
                    ` : `<p class="help-text">${i18n.t('messages.empty.no_volunteers_yet')}</p>`}
                </div>
            </div>
            `;
        }).join('');

    } catch (error) {
        eventsEl.innerHTML = `<div class="loading">Error: ${error.message}</div>`;
    }
}

// Calendar View
async function loadCalendar() {
    const calendarEl = document.getElementById('calendar-grid');
    calendarEl.innerHTML = `<div class="loading">${i18n.t('messages.loading.calendar')}</div>`;

    try {
        // Get all events for the organization
        const eventsResponse = await authFetch(`${API_BASE_URL}/events/?org_id=${currentUser.org_id}`);
        const eventsData = await eventsResponse.json();

        // Get solutions to see assignments
        const solutionsResponse = await fetch(`${API_BASE_URL}/solutions/?org_id=${currentUser.org_id}`);
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

        // Load blocked dates
        const timeoffResponse = await fetch(`${API_BASE_URL}/availability/${currentUser.id}/timeoff`);
        const timeoffData = await timeoffResponse.json();
        const blockedDates = timeoffData.timeoff || [];

        // Check if date is blocked
        const isBlocked = (eventDate) => {
            const eventDateStr = eventDate.toISOString().split('T')[0];
            return blockedDates.some(blocked => {
                const startDate = blocked.start_date.split('T')[0];
                const endDate = blocked.end_date.split('T')[0];
                return eventDateStr >= startDate && eventDateStr <= endDate;
            });
        };

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
                const dateObj = new Date(date);
                const hasBlockedEvents = assignments.some(a => isBlocked(new Date(a.event_start)));

                return `
                    <div class="calendar-day has-event ${hasBlockedEvents ? 'has-blocked' : ''}">
                        <div class="calendar-date">${dateObj.toLocaleDateString('en-US', {
                            weekday: 'long',
                            month: 'long',
                            day: 'numeric'
                        })}</div>
                        ${assignments.map(a => {
                            const blocked = isBlocked(new Date(a.event_start));
                            return `
                            <div class="calendar-event ${blocked ? 'calendar-event-blocked' : ''}">
                                <div class="event-time">
                                    ${new Date(a.event_start).toLocaleTimeString('en-US', {
                                        hour: 'numeric',
                                        minute: '2-digit'
                                    })}
                                </div>
                                <div class="event-title">${a.event_type}</div>
                                ${blocked ? `<div class="event-blocked-badge">⚠️ ${i18n.t('schedule.badges.blocked').toUpperCase()}</div>` : ''}
                            </div>
                            `;
                        }).join('')}
                    </div>
                `;
            }).join('');

    } catch (error) {
        calendarEl.innerHTML = `<div class="loading">${i18n.t('messages.error_loading.calendar', {message: error.message})}</div>`;
    }
}

async function exportMyCalendar() {
    try {
        const response = await fetch(`${API_BASE_URL}/calendar/export?person_id=${currentUser.id}`);

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${currentUser.id}_schedule.ics`;
            a.click();
            showToast(i18n.t('messages.success.calendar_exported'), 'success');
        } else {
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
            const errorMsg = errorData.detail || 'Export failed';

            if (errorMsg.includes('No assignments found')) {
                showToast(i18n.t('messages.warnings.no_schedule_export'), 'warning', 5000);
            } else {
                showToast(i18n.t('messages.errors.export_failed', { message: errorMsg }), 'error');
            }
        }
    } catch (error) {
        showToast(i18n.t('messages.errors.error_exporting_calendar', { message: error.message }), 'error');
    }
}

async function showCalendarSubscription() {
    try {
        const response = await fetch(`${API_BASE_URL}/calendar/subscribe?person_id=${currentUser.id}`);

        if (response.ok) {
            const data = await response.json();

            // Populate the modal with subscription URLs
            document.getElementById('webcal-url').value = data.webcal_url;
            document.getElementById('https-url').value = data.https_url;

            // Show the modal
            document.getElementById('calendar-subscription-modal').classList.remove('hidden');
            showToast(i18n.t('messages.success.subscription_generated'), 'success');
        } else {
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
            showToast(i18n.t('messages.errors.error_subscription_url', { message: errorData.detail }), 'error');
        }
    } catch (error) {
        showToast(i18n.t('messages.errors.generic') + ': ' + error.message, 'error');
    }
}

function closeCalendarSubscriptionModal() {
    document.getElementById('calendar-subscription-modal').classList.add('hidden');
}

function copyToClipboard(elementId) {
    const input = document.getElementById(elementId);
    input.select();
    document.execCommand('copy');
    showToast(i18n.t('messages.success.url_copied'), 'success');
}

async function resetCalendarToken() {
    if (!confirm(i18n.t('messages.confirm.reset_calendar_token'))) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/calendar/reset-token?person_id=${currentUser.id}`, {
            method: 'POST'
        });

        if (response.ok) {
            const data = await response.json();

            // Update the modal with new URLs
            document.getElementById('webcal-url').value = data.webcal_url;
            document.getElementById('https-url').value = data.https_url;

            showToast(i18n.t('messages.success.subscription_reset'), 'success');
        } else {
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
            showToast(i18n.t('messages.errors.error_reset_subscription', { message: errorData.detail }), 'error');
        }
    } catch (error) {
        showToast(i18n.t('messages.errors.generic') + ': ' + error.message, 'error');
    }
}

// Schedule View
async function loadMySchedule() {
    const scheduleEl = document.getElementById('schedule-list');
    scheduleEl.innerHTML = `<div class="loading">${i18n.t('messages.loading.schedule')}</div>`;

    try {
        // Load blocked dates
        const timeoffResponse = await fetch(`${API_BASE_URL}/availability/${currentUser.id}/timeoff`);
        const timeoffData = await timeoffResponse.json();
        const blockedDates = timeoffData.timeoff || [];

        // Get ALL assignments (both from solutions and manual) for the user
        const assignmentsResponse = await authFetch(`${API_BASE_URL}/events/assignments/all?org_id=${currentUser.org_id}`);
        const assignmentsData = await assignmentsResponse.json();

        const myAssignments = assignmentsData.assignments
            .filter(a => a.person_id === currentUser.id)
            .sort((a, b) => new Date(a.event_start) - new Date(b.event_start));

        // Check if date falls within blocked dates
        const isBlocked = (eventDate) => {
            const eventDateStr = eventDate.toISOString().split('T')[0];
            return blockedDates.some(blocked => {
                const startDate = blocked.start_date.split('T')[0];
                const endDate = blocked.end_date.split('T')[0];
                return eventDateStr >= startDate && eventDateStr <= endDate;
            });
        };

        // Update stats
        const now = new Date();
        const upcoming = myAssignments.filter(a => new Date(a.event_start) > now);
        const confirmedUpcoming = upcoming.filter(a => !isBlocked(new Date(a.event_start)));
        const thisMonth = confirmedUpcoming.filter(a => {
            const eventDate = new Date(a.event_start);
            return eventDate.getMonth() === now.getMonth();
        });

        document.getElementById('upcoming-count').textContent = confirmedUpcoming.length;
        document.getElementById('this-month-count').textContent = thisMonth.length;

        // Render schedule
        if (upcoming.length === 0) {
            scheduleEl.innerHTML = `<div class="loading">${i18n.t('messages.empty.no_assignments')}</div>`;
            return;
        }

        scheduleEl.innerHTML = upcoming.map(a => {
            const eventDate = new Date(a.event_start);
            const blocked = isBlocked(eventDate);
            const badge = blocked ?
                `<span class="schedule-badge schedule-badge-blocked">${i18n.t('schedule.badges.blocked')}</span>` :
                `<span class="schedule-badge">${i18n.t('schedule.badges.confirmed')}</span>`;

            const roleDisplay = a.role ? `<br>📋 Role: <strong>${translateRole(a.role)}</strong>` : '';

            return `
            <div class="schedule-item ${blocked ? 'schedule-item-blocked' : ''}">
                <div class="schedule-info">
                    <h3>${a.event_type}</h3>
                    <div class="schedule-meta">
                        📅 ${eventDate.toLocaleDateString('en-US', {
                            weekday: 'long',
                            month: 'long',
                            day: 'numeric',
                            year: 'numeric'
                        })}
                        <br>
                        ⏰ ${eventDate.toLocaleTimeString('en-US', {
                            hour: 'numeric',
                            minute: '2-digit'
                        })} - ${new Date(a.event_end).toLocaleTimeString('en-US', {
                            hour: 'numeric',
                            minute: '2-digit'
                        })}
                        ${roleDisplay}
                    </div>
                </div>
                ${badge}
            </div>
            `;
        }).join('');

    } catch (error) {
        scheduleEl.innerHTML = `<div class="loading">Error: ${error.message}</div>`;
    }
}

// Availability Management
async function loadTimeOff() {
    const listEl = document.getElementById('timeoff-list');
    listEl.innerHTML = '<div class="loading">Loading...</div>';

    try {
        // Add cache-busting timestamp to prevent browser caching
        const response = await fetch(`${API_BASE_URL}/availability/${currentUser.id}/timeoff?_=${Date.now()}`);
        const data = await response.json();

        // Defensive check: data.timeoff might be undefined or not an array
        if (data.total === 0 || !data.timeoff || !Array.isArray(data.timeoff) || data.timeoff.length === 0) {
            listEl.innerHTML = `<p class="help-text">${i18n.t('messages.empty.no_timeoff')}</p>`;
            return;
        }

        listEl.innerHTML = '<h3>Your Blocked Dates</h3>' + data.timeoff.map(timeoff => {
            // Parse dates without timezone conversion (just take the date part)
            const startDate = timeoff.start_date.split('T')[0];
            const endDate = timeoff.end_date.split('T')[0];
            const reason = timeoff.reason || '';
            const escapedReason = reason.replace(/"/g, '&quot;').replace(/'/g, '&#39;');

            return `
            <div class="timeoff-item">
                <div>
                    <div class="timeoff-dates">
                        ${startDate} - ${endDate}
                    </div>
                    <div class="timeoff-reason">${reason || '(no reason specified)'}</div>
                </div>
                <div class="timeoff-actions">
                    <button class="btn btn-small btn-secondary"
                            data-timeoff-id="${timeoff.id}"
                            data-start="${startDate}"
                            data-end="${endDate}"
                            data-reason="${escapedReason}"
                            onclick="editTimeOffFromButton(this)">Edit</button>
                    <button class="btn btn-small btn-remove" onclick="removeTimeOff(${timeoff.id})">Remove</button>
                </div>
            </div>
            `;
        }).join('');

    } catch (error) {
        listEl.innerHTML = `<p class="help-text">${i18n.t('messages.error_loading.timeoff', {message: error.message})}</p>`;
    }
}

async function addTimeOff(event) {
    event.preventDefault();

    const start = document.getElementById('timeoff-start').value;
    const end = document.getElementById('timeoff-end').value;
    const reason = document.getElementById('timeoff-reason').value;

    try {
        const response = await fetch(`${API_BASE_URL}/availability/${currentUser.id}/timeoff`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                start_date: start,
                end_date: end,
                reason: reason || null
            })
        });

        if (response.ok) {
            event.target.reset();
            loadTimeOff();
            showToast(i18n.t('messages.success.timeoff_added'), 'success');
        } else {
            const error = await response.json();
            showToast(i18n.t('messages.errors.error_adding_timeoff', { message: error.detail }), 'error');
        }
    } catch (error) {
        showToast(i18n.t('messages.errors.generic') + ': ' + error.message, 'error');
    }
}

function editTimeOffFromButton(button) {
    const timeoffId = button.dataset.timeoffId;
    const startDate = button.dataset.start;
    const endDate = button.dataset.end;
    const reason = button.dataset.reason || '';

    // Show modal with current values
    document.getElementById('edit-timeoff-modal').classList.remove('hidden');
    document.getElementById('edit-timeoff-id').value = timeoffId;
    document.getElementById('edit-timeoff-start').value = startDate;
    document.getElementById('edit-timeoff-end').value = endDate;
    document.getElementById('edit-timeoff-reason').value = reason;
}

function closeEditTimeOffModal() {
    document.getElementById('edit-timeoff-modal').classList.add('hidden');
    document.getElementById('edit-timeoff-form').reset();
}

async function saveEditedTimeOff(event) {
    event.preventDefault();

    const timeoffId = document.getElementById('edit-timeoff-id').value;
    const startDate = document.getElementById('edit-timeoff-start').value;
    const endDate = document.getElementById('edit-timeoff-end').value;
    const reason = document.getElementById('edit-timeoff-reason').value;

    try {
        const response = await fetch(
            `${API_BASE_URL}/availability/${currentUser.id}/timeoff/${timeoffId}`,
            {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    start_date: startDate,
                    end_date: endDate,
                    reason: reason || null
                })
            }
        );

        if (response.ok) {
            closeEditTimeOffModal();
            loadTimeOff();
            showToast(i18n.t('messages.success.timeoff_updated'), 'success');
        } else {
            const error = await response.json();
            showToast(error.detail || i18n.t('messages.errors.error_updating_timeoff'), 'error');
        }
    } catch (error) {
        showToast(i18n.t('messages.errors.generic') + ': ' + error.message, 'error');
    }
}

async function removeTimeOff(timeoffId) {
    showConfirmDialog('Remove this time-off period?', async (confirmed) => {
        if (!confirmed) return;

        try {
            const response = await fetch(
                `${API_BASE_URL}/availability/${currentUser.id}/timeoff/${timeoffId}`,
                { method: 'DELETE' }
            );

            if (response.ok || response.status === 204) {
                loadTimeOff();
                showToast(i18n.t('messages.success.timeoff_removed'), 'success');
            } else {
                showToast(i18n.t('messages.errors.error_removing_timeoff'), 'error');
            }
        } catch (error) {
            showToast(i18n.t('messages.errors.generic') + ': ' + error.message, 'error');
        }
    });
}

// Settings
async function showSettings() {
    document.getElementById('settings-modal').classList.remove('hidden');
    document.getElementById('settings-name').value = currentUser.name;
    document.getElementById('settings-email').value = currentUser.email || '';
    document.getElementById('settings-org').value = currentOrg.name;
    document.getElementById('settings-timezone').value = currentUser.timezone || 'UTC';

    // Set current language
    const currentLocale = i18n.getLocale();
    const languageSelect = document.getElementById('settings-language');
    languageSelect.value = currentLocale;

    // Add event listener for immediate language change on dropdown selection
    // Remove any existing listener first to prevent duplicates
    const newLanguageSelect = languageSelect.cloneNode(true);
    languageSelect.parentNode.replaceChild(newLanguageSelect, languageSelect);
    newLanguageSelect.addEventListener('change', async (e) => {
        const newLocale = e.target.value;
        await changeLanguage(newLocale);
    });

    // Display user's permission roles (read-only)
    const permissionDisplay = document.getElementById('settings-permission-display');

    // Debug: Check existing content BEFORE we modify it
    console.log('🔍 BEFORE update - innerHTML:', permissionDisplay.innerHTML);
    console.log('🔍 BEFORE update - textContent:', permissionDisplay.textContent);

    const roles = currentUser.roles || [];

    // Debug: Log roles structure
    console.log('🔍 DEBUG showSettings - roles:', roles);
    console.log('  - Type:', typeof roles);
    console.log('  - IsArray:', Array.isArray(roles));
    console.log('  - JSON:', JSON.stringify(roles, null, 2));
    if (roles.length > 0) {
        console.log('  - First role:', roles[0], 'Type:', typeof roles[0]);
        if (typeof roles[0] === 'object') {
            console.log('  - First role keys:', Object.keys(roles[0]));
            console.log('  - First role values:', Object.values(roles[0]));
        }
    }

    if (roles.length > 0) {
        // Process and filter roles
        const processedRoles = roles.map((role, index) => {
            console.log(`  Processing role ${index}:`, role, 'type:', typeof role);

            // Handle both string roles and object roles
            let roleStr;
            if (typeof role === 'string') {
                roleStr = role;
            } else if (typeof role === 'object' && role !== null) {
                // Try multiple properties
                roleStr = role.name || role.role || role.id || role.type || '';
                console.log(`    Extracted roleStr from object:`, roleStr, 'type:', typeof roleStr);

                // If we got an object from these properties, or empty string, skip this role
                if (typeof roleStr === 'object' || roleStr === '') {
                    console.error('⚠️ Skipping malformed role:', role);
                    return null;  // Mark for filtering
                }
            } else {
                console.error('Unexpected role type:', typeof role, role);
                return null;  // Mark for filtering
            }

            // Ensure roleStr is a string
            roleStr = String(roleStr);
            console.log(`    Final roleStr: "${roleStr}"`);

            // Map common role names to friendly labels
            const roleLabel = roleStr === 'admin' ? '👑 Administrator'
                : roleStr === 'volunteer' ? '✓ Volunteer'
                : roleStr.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()); // Convert kebab-case to Title Case

            console.log(`    Final roleLabel: "${roleLabel}"`);
            return `<span style="display: inline-block; margin: 5px; padding: 5px 10px; background: var(--primary); color: white; border-radius: 4px;">${roleLabel}</span>`;
        }).filter(html => html !== null);  // Remove null entries from malformed roles

        if (processedRoles.length > 0) {
            permissionDisplay.innerHTML = processedRoles.join('');
        } else {
            permissionDisplay.innerHTML = `<em>${i18n.t('messages.empty.no_permissions_found')}</em>`;
        }
    } else {
        permissionDisplay.innerHTML = `<em>${i18n.t('messages.empty.no_permissions_assigned')}</em>`;
    }

    // Initialize SMS preferences UI (if module loaded)
    if (typeof initSmsPreferences === 'function') {
        await initSmsPreferences();
    }

    // Add Escape key handler to close modal (accessibility requirement)
    const escapeHandler = (event) => {
        if (event.key === 'Escape' || event.keyCode === 27) {
            closeSettings();
            // Remove the listener after closing
            document.removeEventListener('keydown', escapeHandler);
        }
    };
    document.addEventListener('keydown', escapeHandler);
}

// Change language immediately
async function changeLanguage(locale) {
    console.log(`🌐 Changing language to: ${locale}`);

    // Update i18n locale
    await i18n.setLocale(locale);

    // Sync all language dropdowns
    const dropdowns = [
        'welcome-language',
        'login-language',
        'header-language',
        'settings-language'
    ];

    dropdowns.forEach(id => {
        const dropdown = document.getElementById(id);
        if (dropdown) {
            dropdown.value = locale;
        }
    });

    // Re-translate the page
    translatePage();

    // If user is logged in, save preference to backend
    if (currentUser && currentUser.id) {
        try {
            await authFetch(`${API_BASE_URL}/people/${currentUser.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ language: locale })
            });

            currentUser.language = locale;
            saveSession();
            console.log('✅ Language preference saved to backend');
        } catch (error) {
            console.warn('Could not save language preference:', error);
            // Don't show error toast - language change still works locally
        }
    }
}

async function saveSettings() {
    try {
        const timezone = document.getElementById('settings-timezone').value;
        const language = document.getElementById('settings-language').value;

        console.log('💾 saveSettings - Saving timezone:', timezone, 'language:', language);

        // Save both timezone and language
        const response = await authFetch(`${API_BASE_URL}/people/${currentUser.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ timezone, language })
        });

        if (response.ok) {
            const updatedData = await response.json();
            console.log('✅ saveSettings - Backend response:', updatedData);

            const needsReload = currentUser.language !== language;
            currentUser.timezone = timezone;
            currentUser.language = language;
            console.log('📝 saveSettings - Updated currentUser:', { timezone: currentUser.timezone, language: currentUser.language });
            saveSession();

            // Set language in i18n
            await i18n.setLocale(language);

            // Re-translate the page immediately
            if (needsReload) {
                translatePage();
            }

            showToast(i18n.t('messages.success.saved'), 'success');
            closeSettings();
        } else {
            const error = await response.json();
            showToast(error.detail || i18n.t('messages.errors.error_saving_settings'), 'error');
        }
    } catch (error) {
        showToast(i18n.t('messages.errors.generic') + ': ' + error.message, 'error');
    }
}

function closeSettings() {
    document.getElementById('settings-modal').classList.add('hidden');
}

// ============================================================================
// ADMIN DASHBOARD
// ============================================================================

async function loadAdminDashboard() {
    // Load the current tab from URL hash or default to 'events'
    const hash = window.location.hash.slice(1); // Remove #
    const currentTab = hash.startsWith('admin-') ? hash.replace('admin-', '') : 'events';

    switchAdminTab(currentTab);
}

// Switch between admin tabs
function switchAdminTab(tabName) {
    // Update URL hash for bookmarking
    window.location.hash = `admin-${tabName}`;

    // Save current admin tab
    localStorage.setItem('roster_admin_tab', tabName);

    // Update tab buttons
    document.querySelectorAll('.admin-tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });

    // Update tab content
    document.querySelectorAll('.admin-tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`admin-tab-${tabName}`).classList.add('active');

    // Load content for the tab
    switch(tabName) {
        case 'events':
            loadAdminEvents();
            loadAdminStats();
            break;
        case 'roles':
            loadAdminRoles();
            break;
        case 'schedule':
            loadAdminSolutions();
            loadAdminStats();
            loadAdminCalendarView();
            break;
        case 'people':
            loadAdminPeople();
            loadAdminStats();
            loadInvitations();
            break;
        case 'reports':
            // Reports tab is static, no loading needed
            break;
    }
}

async function loadAdminStats() {
    try {
        const orgId = currentUser.org_id;
        const [peopleRes, eventsRes, solutionsRes] = await Promise.all([
            authFetch(`${API_BASE_URL}/people/?org_id=${orgId}`),
            authFetch(`${API_BASE_URL}/events/?org_id=${orgId}`),
            fetch(`${API_BASE_URL}/solutions/?org_id=${orgId}`)
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
    listEl.innerHTML = `<div class="loading">${i18n.t('messages.loading.events')}</div>`;

    try {
        const orgId = currentUser.org_id;
        console.log('[loadAdminEvents] currentUser:', currentUser);
        console.log('[loadAdminEvents] orgId:', orgId);
        const response = await authFetch(`${API_BASE_URL}/events/?org_id=${orgId}`);
        const data = await response.json();
        console.log('[loadAdminEvents] API response:', data);
        console.log('[loadAdminEvents] Total events:', data.total);

        if (data.total === 0 || !data.events || !Array.isArray(data.events) || data.events.length === 0) {
            console.log('[loadAdminEvents] No events found, showing message');
            listEl.innerHTML = `<p class="help-text">${i18n.t('messages.empty.no_events_yet')}</p>`;
            return;
        }

        console.log('[loadAdminEvents] Rendering', data.events.length, 'events');

        listEl.innerHTML = data.events.map(event => `
            <div class="admin-item" id="event-${event.id}">
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
                        ${event.extra_data && event.extra_data.role_counts ?
                          `<br>📋 Needs: ${Object.entries(event.extra_data.role_counts).map(([role, count]) => `${role} (${count})`).join(', ')}` : ''}
                    </div>
                    <div id="assignments-${event.id}" class="event-assignments"></div>
                </div>
                <div class="admin-item-actions">
                    <button class="btn btn-small" onclick="showAssignments('${event.id}')">${i18n.t('events.assign_people')}</button>
                    <button class="btn btn-small" onclick="editEvent('${event.id}')">${i18n.t('common.buttons.edit')}</button>
                    <button class="btn btn-small btn-remove" onclick="deleteEvent('${event.id}')">${i18n.t('common.buttons.delete')}</button>
                </div>
            </div>
        `).join('');

        // Load assignments for each event (defensive check)
        if (data.events && Array.isArray(data.events)) {
            data.events.forEach(event => loadEventAssignments(event.id));
        }
    } catch (error) {
        console.error('[loadAdminEvents] Error loading events:', error);
        listEl.innerHTML = `<p class="help-text">${i18n.t('messages.error_loading.events', {message: error.message})}</p>`;
    }
}

async function loadAdminPeople() {
    const listEl = document.getElementById('admin-people-list');
    listEl.innerHTML = '<div class="loading">Loading people...</div>';

    try {
        const orgId = currentUser.org_id;
        const response = await authFetch(`${API_BASE_URL}/people/?org_id=${orgId}`);
        const data = await response.json();

        // Defensive check: data.people might be undefined or not an array
        if (data.total === 0 || !data.people || !Array.isArray(data.people) || data.people.length === 0) {
            listEl.innerHTML = `<p class="help-text">${i18n.t('messages.empty.no_people_yet')}</p>`;
            return;
        }

        // Fetch blocked dates for each person
        const peopleWithAvailability = await Promise.all(data.people.map(async (person) => {
            try {
                const timeoffResp = await fetch(`${API_BASE_URL}/availability/${person.id}/timeoff`);
                const timeoffData = await timeoffResp.json();
                return {
                    ...person,
                    blockedDates: timeoffData.timeoff || []
                };
            } catch (e) {
                return {
                    ...person,
                    blockedDates: []
                };
            }
        }));

        listEl.innerHTML = peopleWithAvailability.map(person => {
            const today = new Date();
            const upcomingBlocked = person.blockedDates.filter(b => {
                const endDate = new Date(b.end_date);
                return endDate >= today;
            }).sort((a, b) => new Date(a.start_date) - new Date(b.start_date));

            let blockedHtml = '';
            if (upcomingBlocked.length > 0) {
                const blockedList = upcomingBlocked.slice(0, 3).map(b => {
                    // Use string splitting to avoid timezone conversion
                    const startStr = b.start_date.split('T')[0]; // YYYY-MM-DD
                    const endStr = b.end_date.split('T')[0];

                    // Format as "Oct 11"
                    const formatDate = (dateStr) => {
                        const [year, month, day] = dateStr.split('-');
                        const date = new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
                        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                    };

                    const start = formatDate(startStr);
                    const end = formatDate(endStr);
                    const dateRange = startStr === endStr ? start : `${start} - ${end}`;
                    const reason = b.reason ? `: ${b.reason}` : '';
                    return `${dateRange}${reason}`;
                }).join('<br>');

                const moreCount = upcomingBlocked.length > 3 ? ` (+${upcomingBlocked.length - 3} more)` : '';
                blockedHtml = `<br><div style="margin-top: 8px; color: #dc2626; font-size: 0.9rem;">
                    <strong>${i18n.t('schedule.blocked_dates')}:</strong><br>${blockedList}${moreCount}
                </div>`;
            }

            return `
                <div class="admin-item">
                    <div class="admin-item-info">
                        <h4>${person.name}</h4>
                        <div class="admin-item-meta">
                            ${person.email || 'No email'}
                            ${person.roles && person.roles.length > 0 ? `<br>Roles: ${person.roles.map(r => typeof r === 'string' ? r : (r.name || r.role || '[unknown]')).join(', ')}` : ''}
                            ${blockedHtml}
                        </div>
                    </div>
                    <button class="btn btn-secondary btn-sm" onclick='showEditPersonModal(${JSON.stringify(person)})'>${i18n.t('common.buttons.edit_roles')}</button>
                </div>
            `;
        }).join('');
    } catch (error) {
        listEl.innerHTML = `<p class="help-text">${i18n.t('messages.error_loading.people', {message: error.message})}</p>`;
    }
}

async function loadAdminSolutions() {
    const listEl = document.getElementById('admin-solutions-list');
    listEl.innerHTML = '<div class="loading">Loading schedules...</div>';

    try {
        const orgId = currentUser.org_id;
        const response = await fetch(`${API_BASE_URL}/solutions/?org_id=${orgId}`);
        const data = await response.json();

        // Defensive check: data.solutions might be undefined or not an array
        if (data.total === 0 || !data.solutions || !Array.isArray(data.solutions) || data.solutions.length === 0) {
            listEl.innerHTML = `<p class="help-text">${i18n.t('messages.empty.no_schedules_yet')}</p>`;
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
                    <button class="btn btn-small btn-remove" onclick="deleteSolution(${solution.id})">Delete</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        listEl.innerHTML = `<p class="help-text">${i18n.t('messages.error_loading.schedules', {message: error.message})}</p>`;
    }
}

// Event Management
// Note: showCreateEventForm(), closeCreateEventForm(), and createEvent()
// are all defined in recurring-events.js

async function editEvent(eventId) {
    try {
        // Fetch event details
        const response = await authFetch(`${API_BASE_URL}/events/${eventId}`);
        const event = await response.json();

        // Load role selector first
        if (typeof renderRoleSelector === 'function') {
            await renderRoleSelector('event-role-selector', true);
        }

        // Populate the create event modal with existing data
        document.getElementById('event-type').value = event.type;

        // Convert ISO datetime to local datetime-local format
        const startDate = new Date(event.start_time);
        const localStart = new Date(startDate.getTime() - (startDate.getTimezoneOffset() * 60000))
            .toISOString().slice(0, 16);
        document.getElementById('event-start').value = localStart;

        // Calculate duration in hours
        const endDate = new Date(event.end_time);
        const durationHours = (endDate - startDate) / (1000 * 60 * 60);
        document.getElementById('event-duration').value = durationHours;

        // Set custom title if exists
        if (event.extra_data && event.extra_data.custom_title) {
            document.getElementById('event-custom-title').value = event.extra_data.custom_title;
        }

        // Check the role checkboxes that are assigned to this event
        if (event.extra_data && event.extra_data.roles) {
            const roleCheckboxes = document.querySelectorAll('#event-role-selector input[type="checkbox"]');
            roleCheckboxes.forEach(checkbox => {
                checkbox.checked = event.extra_data.roles.includes(checkbox.value);
            });
        }

        // Store event ID for update
        document.getElementById('create-event-form').dataset.editingEventId = eventId;

        // Change modal title and button text
        document.querySelector('#create-event-modal h3').textContent = i18n.t('events.edit_event');
        document.querySelector('#create-event-form button[type="submit"]').textContent = i18n.t('events.update_event');

        // Show modal
        document.getElementById('create-event-modal').classList.remove('hidden');
    } catch (error) {
        showToast(i18n.t('messages.errors.error_loading_event', { message: error.message }), 'error');
    }
}

async function deleteEvent(eventId) {
    showConfirmDialog('Delete this event? This cannot be undone.', async (confirmed) => {
        if (!confirmed) return;

        try {
            const response = await authFetch(`${API_BASE_URL}/events/${eventId}`, {
                method: 'DELETE'
            });

            if (response.ok || response.status === 204) {
                loadAdminEvents();
                loadAdminStats();
                showToast(i18n.t('messages.success.event_deleted'), 'success');
            } else {
                showToast(i18n.t('messages.errors.error_deleting_event'), 'error');
            }
        } catch (error) {
            showToast(i18n.t('messages.errors.generic') + ': ' + error.message, 'error');
        }
    });
}

// Load and display current assignments for an event
async function loadEventAssignments(eventId) {
    try {
        const [peopleResp, validationResp, eventResp] = await Promise.all([
            authFetch(`${API_BASE_URL}/events/${eventId}/available-people`),
            authFetch(`${API_BASE_URL}/events/${eventId}/validation`),
            authFetch(`${API_BASE_URL}/events/${eventId}`)
        ]);

        const people = await peopleResp.json();
        const validation = await validationResp.json();
        const event = await eventResp.json();

        const assignedPeople = people.filter(p => p.is_assigned);
        const container = document.getElementById(`assignments-${eventId}`);

        let html = '';

        // Show validation warnings
        if (!validation.is_valid && validation.warnings.length > 0) {
            html += '<div class="event-warnings">';
            validation.warnings.forEach(w => {
                // Translate warning message using message_key if available
                const message = translateApiMessage(w);
                if (w.type === 'missing_config') {
                    html += `<div class="warning">⚠️ ${message}</div>`;
                } else if (w.type === 'insufficient_people') {
                    html += `<div class="warning">⚠️ ${message}</div>`;
                } else if (w.type === 'blocked_assignments') {
                    html += `<div class="warning">⚠️ ${message}</div>`;
                }
            });
            html += '</div>';
        } else if (validation.is_valid) {
            html += '<div class="event-status-ok">✓ Properly configured</div>';
        }

        // Show assignments with blocked status
        if (assignedPeople.length > 0) {
            const blockedPeople = assignedPeople.filter(p => p.is_blocked);
            const availablePeople = assignedPeople.filter(p => !p.is_blocked);

            html += '<div class="event-assignments-summary">';

            // Show available people first
            if (availablePeople.length > 0) {
                html += `<div class="assigned-ok">✓ ${availablePeople.map(p => p.name).join(', ')}</div>`;
            }

            // Show blocked warnings
            if (blockedPeople.length > 0) {
                html += `<div class="assigned-blocked">⚠️ ${blockedPeople.map(p => p.name).join(', ')} (blocked)</div>`;
            }

            html += '</div>';
        } else {
            html += `<div class="help-text">No assignments</div>`;
        }

        container.innerHTML = html;
    } catch (error) {
        console.error('Error loading assignments:', error);
    }
}

// Show assignment modal for an event
async function showAssignments(eventId) {
    try {
        const [peopleResponse, eventResponse] = await Promise.all([
            authFetch(`${API_BASE_URL}/events/${eventId}/available-people`),
            authFetch(`${API_BASE_URL}/events/${eventId}`)
        ]);

        const people = await peopleResponse.json();
        const event = await eventResponse.json();

        const modal = document.getElementById('assignment-modal');
        const listEl = document.getElementById('assignment-people-list');

        if (people.length === 0) {
            listEl.innerHTML = `<p class="help-text">${i18n.t('messages.empty.no_matching_roles')}</p>`;
        } else {
            // Get required roles from event
            const roleCount = event.extra_data?.role_counts || {};
            const requiredRoles = Object.keys(roleCount);

            // If event has no role requirements, show all people in a single group
            if (requiredRoles.length === 0) {
                listEl.innerHTML = `
                    <div class="role-group">
                        <h4 class="role-header">All People</h4>
                        <div class="role-people">
                            ${people.map(person => `
                                <div class="person-assignment-item ${person.is_blocked ? 'person-blocked' : ''}">
                                    <div class="person-info">
                                        <strong>${person.name}</strong>
                                        ${person.is_blocked ? `<span class="schedule-badge-blocked">${i18n.t('schedule.badges.blocked').toUpperCase()}</span>` : ''}
                                        <span class="person-roles">${person.roles.map(r => typeof r === 'string' ? r : (r.name || r.role || '[unknown]')).join(', ')}</span>
                                    </div>
                                    <button
                                        class="btn btn-small ${person.is_assigned ? 'btn-remove' : ''}"
                                        onclick="toggleAssignment('${eventId}', '${person.id}', ${person.is_assigned})"
                                    >
                                        ${person.is_assigned ? 'Unassign' : 'Assign'}
                                    </button>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            } else {
                // Group people by role
                const roleGroups = {};
                requiredRoles.forEach(role => {
                    roleGroups[role] = people.filter(p => p.roles.includes(role));
                });

                // Build HTML grouped by role
                let html = '';
                for (const [role, rolePeople] of Object.entries(roleGroups)) {
                    const needed = roleCount[role] || 0;
                    const assigned = rolePeople.filter(p => p.is_assigned).length;

                    html += `
                        <div class="role-group">
                            <h4 class="role-header">
                                ${role.charAt(0).toUpperCase() + role.slice(1)}
                                <span class="role-count">(${assigned}/${needed} assigned)</span>
                            </h4>
                            <div class="role-people">
                                ${rolePeople.length === 0 ?
                                    '<p class="help-text">No one has this role</p>' :
                                    rolePeople.map(person => `
                                        <div class="person-assignment-item ${person.is_blocked ? 'person-blocked' : ''}">
                                            <div class="person-info">
                                                <strong>${person.name}</strong>
                                                ${person.is_blocked ? `<span class="schedule-badge-blocked">${i18n.t('schedule.badges.blocked').toUpperCase()}</span>` : ''}
                                            </div>
                                            <button
                                                class="btn btn-small ${person.is_assigned ? 'btn-remove' : ''}"
                                                onclick="toggleAssignment('${eventId}', '${person.id}', ${person.is_assigned})"
                                            >
                                                ${person.is_assigned ? 'Unassign' : 'Assign'}
                                            </button>
                                        </div>
                                    `).join('')
                                }
                            </div>
                        </div>
                    `;
                }

                listEl.innerHTML = html;
            }
        }

        modal.dataset.eventId = eventId;
        modal.classList.remove('hidden');
    } catch (error) {
        showToast(i18n.t('messages.errors.error_loading_people', { message: error.message }), 'error');
    }
}

// Toggle assignment for a person
async function toggleAssignment(eventId, personId, isCurrentlyAssigned) {
    try {
        const action = isCurrentlyAssigned ? 'unassign' : 'assign';
        const response = await authFetch(`${API_BASE_URL}/events/${eventId}/assignments`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ person_id: personId, action })
        });

        if (response.ok) {
            const result = await response.json();
            // Use translateApiMessage to get the translated message from backend
            const message = translateApiMessage(result) || i18n.t('messages.success.assignment_updated');
            showToast(message, 'success');

            // Refresh the modal and the event card
            showAssignments(eventId);
            loadEventAssignments(eventId);
        } else {
            const error = await response.json();
            // Try to translate error message from backend
            const errorMsg = (typeof error.detail === 'object' && error.detail.message_key)
                ? i18n.t(error.detail.message_key, error.detail.message_params || {})
                : (error.detail || i18n.t('messages.errors.error_updating_assignment'));
            showToast(errorMsg, 'error');
        }
    } catch (error) {
        showToast(i18n.t('messages.errors.generic') + ': ' + error.message, 'error');
    }
}

function closeAssignmentModal() {
    document.getElementById('assignment-modal').classList.add('hidden');
}

async function deleteSolution(solutionId) {
    showConfirmDialog('Delete this schedule? This cannot be undone.', async (confirmed) => {
        if (!confirmed) return;

        try {
            const response = await fetch(`${API_BASE_URL}/solutions/${solutionId}`, {
                method: 'DELETE'
            });

            if (response.ok || response.status === 204) {
                loadAdminSolutions();
                loadAdminStats();
                showToast(i18n.t('messages.success.schedule_deleted'), 'success');
            } else {
                showToast(i18n.t('messages.errors.error_deleting_schedule'), 'error');
            }
        } catch (error) {
            showToast(i18n.t('messages.errors.generic') + ': ' + error.message, 'error');
        }
    });
}

// Schedule Generation
async function generateSchedule() {
    const statusEl = document.getElementById('solver-status');
    statusEl.innerHTML = `<div class="solver-status running">${i18n.t('messages.loading.generating_schedule')}</div>`;

    try {
        // Calculate date range (next 90 days)
        const today = new Date();
        const futureDate = new Date(today.getTime() + 90 * 24 * 60 * 60 * 1000);

        const response = await authFetch(`${API_BASE_URL}/solver/solve`, {
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
            // Get assignment count from either metrics.assignment_count or assignment_count field
            const assignmentCount = data.assignment_count || data.metrics?.assignment_count || 0;

            // Check if solver generated 0 assignments - this is a problem!
            if (assignmentCount === 0) {
                statusEl.innerHTML = `
                    <div class="solver-status error">
                        ⚠️ Schedule generated but no assignments were made!<br>
                        <br><strong>Possible issues:</strong>
                        <ul style="text-align: left; margin: 10px 20px;">
                            <li>Events don't specify how many people are needed for each role</li>
                            <li>No people have the required roles</li>
                            <li>People are unavailable during event times</li>
                        </ul>
                        <strong>To fix:</strong>
                        <ol style="text-align: left; margin: 10px 20px;">
                            <li>Edit your events and check roles with counts (e.g., "Volunteer: 2")</li>
                            <li>Make sure people have matching roles in their profiles</li>
                            <li>Check people's availability/time-off settings</li>
                        </ol>
                    </div>
                `;
                showToast(i18n.t('messages.errors.no_assignments_created'), 'error');
                return;
            }

            statusEl.innerHTML = `
                <div class="solver-status success">
                    ✓ Schedule generated successfully!<br>
                    Solution ID: ${data.solution_id}<br>
                    Assignments: ${assignmentCount}<br>
                    Health Score: ${data.metrics?.health_score?.toFixed(1) || 'N/A'}/100
                </div>
            `;
            showToast(i18n.t('messages.success.schedule_created', { count: assignmentCount }), 'success');
            loadAdminSolutions();
            loadAdminStats();

            // Refresh user's schedule if they're viewing it
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
            body: JSON.stringify({ format: 'pdf' })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `schedule_${solutionId}.pdf`;
            a.click();
            showToast(i18n.t('messages.success.schedule_downloaded'), 'success');
        } else {
            // Get detailed error message
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
            const errorMsg = errorData.detail || errorData.message || 'Error exporting schedule';

            if (errorMsg.includes('no assignments')) {
                showToast(i18n.t('messages.warnings.cannot_export_no_assignments'), 'warning', 5000);
            } else {
                showToast(i18n.t('messages.errors.error_exporting_schedule', { message: errorMsg }), 'error');
            }
        }
    } catch (error) {
        showToast(i18n.t('messages.errors.generic') + ': ' + error.message, 'error');
    }
}

// ========================================
// Profile Context Panel Functions
// ========================================

/**
 * Translate a role ID to localized display name.
 *
 * Translation priority:
 * 1. Organization-specific role translations (future: org.config.roles[roleId].translations[lang])
 * 2. Global i18n translations (locales/{lang}/common.json roles.*)
 * 3. Fallback: Convert kebab-case to Title Case (e.g., "worship-leader" → "Worship Leader")
 *
 * @param {string} roleId - Role identifier (e.g., "admin", "worship-leader")
 * @param {string|null} locale - Optional locale override (defaults to current locale)
 * @returns {string} Translated role name
 */
function translateRole(roleId, locale = null) {
    if (!roleId) return '';

    const lang = locale || i18n.getLocale();

    // 1. Check organization config for role definition (future enhancement)
    // if (currentOrg && currentOrg.config && currentOrg.config.roles) {
    //     const roleDef = currentOrg.config.roles[roleId];
    //     if (roleDef && roleDef.translations && roleDef.translations[lang]) {
    //         return roleDef.translations[lang];
    //     }
    //     // Fallback to English if current language not available
    //     if (roleDef && roleDef.translations && roleDef.translations.en) {
    //         return roleDef.translations.en;
    //     }
    // }

    // 2. Check global translations for common roles
    // Try exact match first (e.g., "admin" → common.admin)
    let translation = i18n.t(`common.${roleId}`);
    if (translation && translation !== `common.${roleId}`) {
        return translation;
    }

    // Try with 'role_' prefix (e.g., "worship-leader" → common.role_worship_leader)
    translation = i18n.t(`common.role_${roleId.replace(/-/g, '_')}`);
    if (translation && translation !== `common.role_${roleId.replace(/-/g, '_')}`) {
        return translation;
    }

    // 3. Fallback: Convert kebab-case to Title Case
    // "worship-leader" → "Worship Leader"
    return roleId.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

/**
 * Update the role badges display in the profile context panel
 */
function updateRoleBadgesDisplay() {
    const rolesDisplay = document.getElementById('active-roles-display');
    if (!rolesDisplay || !currentUser) return;

    // Clear existing badges
    rolesDisplay.innerHTML = '';

    // Get user's roles
    const roles = currentUser.roles || [];

    // Debug: Log roles structure with detailed inspection
    debug.group('updateRoleBadgesDisplay');
    debug.log('roles:', roles);
    debug.log('Type:', typeof roles);
    debug.log('IsArray:', Array.isArray(roles));
    debug.log('JSON:', JSON.stringify(roles));
    if (roles.length > 0) {
        debug.log('First role:', roles[0], 'Type:', typeof roles[0]);
    }
    debug.groupEnd();

    if (roles.length === 0) {
        rolesDisplay.innerHTML = `<span class="role-badge" style="background: #9ca3af;">${i18n.t('messages.empty.no_roles_set')}</span>`;
        // Show setup hint for users without roles
        showSetupHint();
    } else {
        // Create badge for each role
        roles.forEach(role => {
            const badge = document.createElement('span');
            badge.className = 'role-badge';

            // Handle both string and object roles
            let roleStr = typeof role === 'string' ? role : (role.name || role.role || '');

            // If still an object at this point, show error instead of [object Object]
            if (typeof roleStr === 'object') {
                console.error('Role is still an object after extraction:', role);
                roleStr = JSON.stringify(role);
            }

            // Translate role (checks global translations first, then falls back to title case)
            const roleLabel = translateRole(roleStr);

            badge.textContent = roleLabel;
            rolesDisplay.appendChild(badge);
        });
    }
}

/**
 * Populate the visible organization dropdown in the profile context panel
 */
function updateOrgDropdownDisplay() {
    const orgDropdown = document.getElementById('org-dropdown-visible');
    const oldOrgDropdown = document.getElementById('org-dropdown');
    
    if (!orgDropdown || !oldOrgDropdown) return;

    // Copy options from the old hidden dropdown to the new visible one
    orgDropdown.innerHTML = oldOrgDropdown.innerHTML;
    orgDropdown.value = oldOrgDropdown.value;
}

/**
 * Show setup hint for first-time users
 */
function showSetupHint() {
    const hint = document.getElementById('setup-hint');
    if (!hint) return;

    // Check if user has dismissed the hint before
    const dismissed = localStorage.getItem('setup_hint_dismissed');
    if (dismissed) return;

    // Show hint if user has no roles or no availability set
    const hasRoles = currentUser && currentUser.roles && currentUser.roles.length > 0;
    
    if (!hasRoles) {
        hint.classList.remove('hidden');
    }
}

/**
 * Dismiss the setup hint
 */
function dismissSetupHint() {
    const hint = document.getElementById('setup-hint');
    if (hint) {
        hint.classList.add('hidden');
        localStorage.setItem('setup_hint_dismissed', 'true');
    }
}


// Hook into existing functions to update the profile panel
const originalLoadOrganizations = window.loadOrganizations;
if (typeof loadOrganizations === 'function') {
    window.loadOrganizations = async function() {
        await originalLoadOrganizations();
        updateOrgDropdownDisplay();
    };
}

// Update profile panel when settings are saved
const originalSaveSettings = window.saveSettings;
if (typeof saveSettings === 'function') {
    window.saveSettings = async function() {
        await originalSaveSettings();
        updateRoleBadgesDisplay();
        updateOrgDropdownDisplay();
    };
}

// Initialize profile context panel when main app loads
window.addEventListener('DOMContentLoaded', () => {
    // Wait a bit for currentUser to be loaded
    setTimeout(() => {
        updateRoleBadgesDisplay();
        updateOrgDropdownDisplay();
        showSetupHint();
    }, 500);
});

console.log('Profile context panel functions loaded');

// ============================================================================
// INVITATIONS MANAGEMENT (People Tab)
// ============================================================================

function showInviteUserModal() {
    document.getElementById('invite-user-modal').classList.remove('hidden');
}

function closeInviteUserModal() {
    document.getElementById('invite-user-modal').classList.add('hidden');
    document.getElementById('invite-user-form').reset();
}

async function sendInvitation(event) {
    event.preventDefault();

    const email = document.getElementById('invite-email').value;
    const name = document.getElementById('invite-name').value;
    const roleCheckboxes = document.querySelectorAll('#invite-role-selector input:checked');
    const roles = Array.from(roleCheckboxes).map(cb => cb.value);

    if (roles.length === 0) {
        showToast(i18n.t('messages.errors.select_at_least_one_role'), 'warning');
        return;
    }

    try {
        const response = await authFetch(`${API_BASE_URL}/invitations?org_id=${currentUser.org_id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: email,
                name: name,
                roles: roles
            })
        });

        if (response.ok) {
            const data = await response.json();
            showToast(i18n.t('messages.success.invitation_sent'), 'success');
            closeInviteUserModal();
            loadInvitations();
        } else {
            const error = await response.json();
            showToast(error.detail || i18n.t('messages.errors.error_sending_invitation'), 'error');
        }
    } catch (error) {
        showToast(i18n.t('messages.errors.generic') + ': ' + error.message, 'error');
    }
}

async function loadInvitations() {
    const listEl = document.getElementById('invitations-list');
    listEl.innerHTML = '<div class="loading">Loading invitations...</div>';

    try {
        const authToken = localStorage.getItem('authToken');
        const response = await authFetch(`${API_BASE_URL}/invitations?org_id=${currentUser.org_id}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.status === 404) {
            // Invitations feature not implemented yet
            listEl.innerHTML = `<p class="help-text">${i18n.t('messages.empty.invitations_coming_soon')}</p>`;
            document.getElementById('pending-invitations').textContent = '-';
            document.getElementById('accepted-invitations').textContent = '-';
            document.getElementById('expired-invitations').textContent = '-';
            return;
        }

        const data = await response.json();
        const invitations = data.invitations || [];

        // Update summary counts
        const pending = invitations.filter(inv => inv.status === 'pending').length;
        const accepted = invitations.filter(inv => inv.status === 'accepted').length;
        const expired = invitations.filter(inv => inv.status === 'expired').length;

        document.getElementById('pending-invitations').textContent = pending;
        document.getElementById('accepted-invitations').textContent = accepted;
        document.getElementById('expired-invitations').textContent = expired;

        if (invitations.length === 0) {
            listEl.innerHTML = `<p class="help-text">${i18n.t('messages.empty.no_invitations_yet')}</p>`;
            return;
        }

        // Render invitations list
        listEl.innerHTML = invitations.map(inv => `
            <div class="invitation-item">
                <div class="invitation-info">
                    <h5>${inv.name}</h5>
                    <div class="invitation-meta">
                        ${inv.email} • Roles: ${inv.roles.map(r => typeof r === 'string' ? r : (r.name || r.role || '[unknown]')).join(', ')}<br>
                        Sent: ${new Date(inv.created_at).toLocaleDateString()}
                        ${inv.status === 'pending' ? ` • Expires: ${new Date(inv.expires_at).toLocaleDateString()}` : ''}
                    </div>
                </div>
                <div style="display: flex; gap: 10px; align-items: center;">
                    <span class="invitation-status ${inv.status}">${inv.status}</span>
                    ${inv.status === 'pending' ? `
                        <button class="btn btn-small btn-secondary" onclick="resendInvitation('${inv.id}')">Resend</button>
                        <button class="btn btn-small btn-remove" onclick="cancelInvitation('${inv.id}')">Cancel</button>
                    ` : ''}
                </div>
            </div>
        `).join('');
    } catch (error) {
        listEl.innerHTML = `<p class="help-text">${i18n.t('messages.error_loading.invitations', {message: error.message})}</p>`;
        document.getElementById('pending-invitations').textContent = '0';
        document.getElementById('accepted-invitations').textContent = '0';
        document.getElementById('expired-invitations').textContent = '0';
    }
}

async function resendInvitation(invitationId) {
    try {
        const response = await authFetch(`${API_BASE_URL}/invitations/${invitationId}/resend`, {
            method: 'POST'
        });

        if (response.ok) {
            showToast(i18n.t('messages.success.invitation_resent'), 'success');
            loadInvitations();
        } else {
            const error = await response.json();
            showToast(error.detail || i18n.t('messages.errors.error_resending_invitation'), 'error');
        }
    } catch (error) {
        showToast(i18n.t('messages.errors.generic') + ': ' + error.message, 'error');
    }
}

async function cancelInvitation(invitationId) {
    showConfirmDialog('Cancel this invitation?', async (confirmed) => {
        if (!confirmed) return;

        try {
            const response = await authFetch(`${API_BASE_URL}/invitations/${invitationId}`, {
                method: 'DELETE'
            });

            if (response.ok || response.status === 204) {
                showToast(i18n.t('messages.success.invitation_cancelled'), 'success');
                loadInvitations();
            } else {
                const error = await response.json();
                showToast(error.detail || i18n.t('messages.errors.error_cancelling_invitation'), 'error');
            }
        } catch (error) {
            showToast(i18n.t('messages.errors.generic') + ': ' + error.message, 'error');
        }
    });
}

// ============================================================================
// REPORTS TAB FUNCTIONS
// ============================================================================

async function exportLatestSchedulePDF() {
    try {
        const solutionsResponse = await fetch(`${API_BASE_URL}/solutions/?org_id=${currentUser.org_id}`);
        const solutionsData = await solutionsResponse.json();

        if (solutionsData.solutions.length === 0) {
            showToast(i18n.t('messages.warnings.no_schedule_available'), 'warning');
            return;
        }

        const latestSolution = solutionsData.solutions[0];
        viewSolution(latestSolution.id);
    } catch (error) {
        showToast(i18n.t('messages.errors.generic') + ': ' + error.message, 'error');
    }
}

async function exportOrgCalendar() {
    try {
        const solutionsResponse = await fetch(`${API_BASE_URL}/solutions/?org_id=${currentUser.org_id}`);
        const solutionsData = await solutionsResponse.json();

        if (solutionsData.solutions.length === 0) {
            showToast(i18n.t('messages.warnings.no_schedule_available'), 'warning');
            return;
        }

        const latestSolution = solutionsData.solutions[0];

        const response = await fetch(`${API_BASE_URL}/solutions/${latestSolution.id}/export`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                format: 'ics',
                scope: 'organization'
            })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${currentOrg.name.replace(/\s+/g, '_')}_schedule.ics`;
            a.click();
            showToast(i18n.t('messages.success.calendar_exported'), 'success');
        } else {
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
            showToast(i18n.t('messages.errors.export_failed', { message: errorData.detail }), 'error');
        }
    } catch (error) {
        showToast(i18n.t('messages.errors.generic') + ': ' + error.message, 'error');
    }
}

async function showScheduleStats() {
    const statsDisplay = document.getElementById('schedule-stats-display');
    const statsContent = document.getElementById('stats-content');

    statsDisplay.classList.remove('hidden');
    statsContent.innerHTML = `<div class="loading">${i18n.t('messages.loading.statistics')}</div>`;

    try {
        const solutionsResponse = await fetch(`${API_BASE_URL}/solutions/?org_id=${currentUser.org_id}`);
        const solutionsData = await solutionsResponse.json();

        if (solutionsData.solutions.length === 0) {
            statsContent.innerHTML = `<p class="help-text">${i18n.t('messages.empty.no_schedule_data')}</p>`;
            return;
        }

        const latestSolution = solutionsData.solutions[0];
        const assignmentsResponse = await fetch(`${API_BASE_URL}/solutions/${latestSolution.id}/assignments`);
        const assignmentsData = await assignmentsResponse.json();

        // Defensive check: assignmentsData.assignments might be undefined or not an array
        if (!assignmentsData.assignments || !Array.isArray(assignmentsData.assignments) || assignmentsData.assignments.length === 0) {
            statsContent.innerHTML = `<p class="help-text">${i18n.t('messages.empty.no_assignments_yet')}</p>`;
            return;
        }

        // Calculate statistics
        const assignments = assignmentsData.assignments;
        const peopleCount = new Set(assignments.map(a => a.person_id)).size;
        const eventCount = new Set(assignments.map(a => a.event_id)).size;

        // Count assignments per person
        const assignmentsPerPerson = {};
        assignments.forEach(a => {
            assignmentsPerPerson[a.person_name] = (assignmentsPerPerson[a.person_name] || 0) + 1;
        });

        const sortedPeople = Object.entries(assignmentsPerPerson)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10);

        statsContent.innerHTML = `
            <div class="stats-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 25px;">
                <div class="stat-card">
                    <div class="stat-value">${assignments.length}</div>
                    <div class="stat-label">Total Assignments</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${peopleCount}</div>
                    <div class="stat-label">People Assigned</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${eventCount}</div>
                    <div class="stat-label">Events Covered</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${(assignments.length / peopleCount).toFixed(1)}</div>
                    <div class="stat-label">Avg Assignments/Person</div>
                </div>
            </div>

            <h5 style="margin: 20px 0 15px 0;">Top 10 Most Assigned People</h5>
            <div style="background: white; border-radius: 8px; padding: 15px;">
                ${sortedPeople.map(([name, count], index) => `
                    <div style="display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid var(--border);">
                        <span>${index + 1}. ${name}</span>
                        <span style="font-weight: 600; color: var(--primary);">${count} assignments</span>
                    </div>
                `).join('')}
            </div>
        `;
    } catch (error) {
        statsContent.innerHTML = `<p class="help-text">${i18n.t('messages.error_loading.statistics', {message: error.message})}</p>`;
    }
}

async function loadAdminCalendarView() {
    const calendarEl = document.getElementById('admin-calendar-view');
    calendarEl.innerHTML = '<div class="loading">Loading calendar...</div>';

    try {
        const solutionsResponse = await fetch(`${API_BASE_URL}/solutions/?org_id=${currentUser.org_id}`);
        const solutionsData = await solutionsResponse.json();

        if (solutionsData.solutions.length === 0) {
            calendarEl.innerHTML = `<div class="loading">${i18n.t('messages.empty.no_schedule_generated')}</div>`;
            return;
        }

        const latestSolution = solutionsData.solutions.find(s => s.assignment_count > 0);
        if (!latestSolution) {
            calendarEl.innerHTML = `<div class="loading">${i18n.t('messages.empty.no_assignments_in_schedule')}</div>`;
            return;
        }

        const assignmentsResponse = await fetch(`${API_BASE_URL}/solutions/${latestSolution.id}/assignments`);
        const assignmentsData = await assignmentsResponse.json();

        // Defensive check: assignmentsData.assignments might be undefined or not an array
        if (!assignmentsData.assignments || !Array.isArray(assignmentsData.assignments) || assignmentsData.assignments.length === 0) {
            calendarEl.innerHTML = `<div class="loading">${i18n.t('messages.empty.no_assignments_yet')}</div>`;
            return;
        }

        // Group by date
        const byDate = {};
        assignmentsData.assignments.forEach(assignment => {
            const date = new Date(assignment.event_start).toDateString();
            if (!byDate[date]) byDate[date] = [];
            byDate[date].push(assignment);
        });

        // Render calendar
        calendarEl.innerHTML = Object.keys(byDate)
            .sort((a, b) => new Date(a) - new Date(b))
            .slice(0, 10) // Show next 10 days
            .map(date => {
                const assignments = byDate[date];
                const dateObj = new Date(date);

                return `
                    <div class="calendar-day has-event" style="margin-bottom: 15px;">
                        <div class="calendar-date">${dateObj.toLocaleDateString('en-US', {
                            weekday: 'long',
                            month: 'long',
                            day: 'numeric'
                        })}</div>
                        ${assignments.map(a => `
                            <div class="calendar-event" style="margin-top: 10px;">
                                <div class="event-time">
                                    ${new Date(a.event_start).toLocaleTimeString('en-US', {
                                        hour: 'numeric',
                                        minute: '2-digit'
                                    })}
                                </div>
                                <div class="event-title">${a.event_type}</div>
                                <div style="font-size: 0.85rem; color: var(--text-light); margin-top: 5px;">
                                    ${a.person_name}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
            }).join('');
    } catch (error) {
        calendarEl.innerHTML = `<div class="loading">${i18n.t('messages.error_loading.calendar', {message: error.message})}</div>`;
    }
}

// Update help text based on number of organizations
function updateOrgHelpText(orgCount) {
    const helpText = document.querySelector('.context-item .context-help');
    if (helpText && orgCount !== undefined) {
        if (orgCount > 1) {
            helpText.textContent = i18n.t('common.switch_organizations', { count: orgCount });
        } else {
            helpText.textContent = i18n.t('common.current_organization');
        }
    }
}

// Edit Person Roles Modal Functions
async function showEditPersonModal(person) {
    // Set person info
    document.getElementById('edit-person-id').value = person.id;
    document.getElementById('edit-person-name').textContent = person.name;

    // Load available roles
    const roles = await loadOrgRoles();
    const container = document.getElementById('edit-person-roles-checkboxes');

    // Create checkboxes for each role
    container.innerHTML = roles.map(role => {
        const isChecked = person.roles && person.roles.includes(role) ? 'checked' : '';
        return `
            <label class="role-option">
                <input type="checkbox" value="${role}" ${isChecked}>
                ${capitalizeRole(role)}
            </label>
        `;
    }).join('');

    // Show modal
    document.getElementById('edit-person-modal').classList.remove('hidden');
}

function closeEditPersonModal() {
    document.getElementById('edit-person-modal').classList.add('hidden');
    document.getElementById('edit-person-form').reset();
}

async function updatePersonRoles(event) {
    event.preventDefault();

    const personId = document.getElementById('edit-person-id').value;
    const checkboxes = document.querySelectorAll('#edit-person-roles-checkboxes input[type="checkbox"]');
    const selectedRoles = Array.from(checkboxes)
        .filter(cb => cb.checked)
        .map(cb => cb.value);

    try {
        const response = await authFetch(`${API_BASE_URL}/people/${personId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                roles: selectedRoles
            })
        });

        if (response.ok) {
            closeEditPersonModal();
            loadAdminPeople();
            showToast(i18n.t('messages.success.roles_updated'), 'success');
        } else {
            const error = await response.json();
            showToast(i18n.t('messages.errors.error_updating_roles', { message: error.detail }), 'error');
        }
    } catch (error) {
        showToast(i18n.t('messages.errors.generic') + ': ' + error.message, 'error');
    }
}

// Event Signup Functions
async function joinEvent(eventId) {
    // Show role selection modal
    document.getElementById('role-event-id').value = eventId;
    document.getElementById('select-role-modal').classList.remove('hidden');

    // Reset form
    document.getElementById('event-role-select').value = '';
    document.getElementById('custom-role-group').style.display = 'none';
    document.getElementById('custom-role-input').value = '';
}

function closeSelectRoleModal() {
    document.getElementById('select-role-modal').classList.add('hidden');
}

// Handle role select change to show/hide custom role input
function initRoleSelectHandler() {
    const roleSelect = document.getElementById('event-role-select');
    if (roleSelect && !roleSelect.hasEventListener) {
        roleSelect.addEventListener('change', function() {
            const customRoleGroup = document.getElementById('custom-role-group');
            if (this.value === 'other') {
                customRoleGroup.style.display = 'block';
                document.getElementById('custom-role-input').required = true;
            } else {
                customRoleGroup.style.display = 'none';
                document.getElementById('custom-role-input').required = false;
            }
        });
        roleSelect.hasEventListener = true;
    }
}

// Initialize role select handler when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initRoleSelectHandler);
} else {
    initRoleSelectHandler();
}

async function submitEventRole(event) {
    event.preventDefault();

    const eventId = document.getElementById('role-event-id').value;
    let role = document.getElementById('event-role-select').value;

    // If "other" is selected, use custom role name
    if (role === 'other') {
        role = document.getElementById('custom-role-input').value.trim();
        if (!role) {
            showToast(i18n.t('messages.errors.enter_custom_role_name'), 'error');
            return;
        }
    }

    try {
        const response = await authFetch(`${API_BASE_URL}/events/${eventId}/assignments`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                person_id: currentUser.id,
                action: 'assign',
                role: role
            })
        });

        if (response.ok) {
            const data = await response.json();
            closeSelectRoleModal();
            showToast(i18n.t('messages.success.joined_event', { role: role }), 'success');
            loadAllEvents(); // Reload to show updated participant list
            loadMySchedule(); // Refresh user's schedule
        } else {
            const error = await response.json();
            showToast(i18n.t('messages.errors.error_joining_event', { message: error.detail }), 'error');
        }
    } catch (error) {
        showToast(i18n.t('messages.errors.error_joining_event', { message: error.message }), 'error');
    }
}

async function leaveEvent(eventId) {
    showConfirmDialog('Are you sure you want to leave this event?', async (confirmed) => {
        if (!confirmed) return;

        try {
            const response = await authFetch(`${API_BASE_URL}/events/${eventId}/assignments`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    person_id: currentUser.id,
                    action: 'unassign'
                })
            });

            if (response.ok) {
                showToast(i18n.t('messages.success.left_event'), 'success');
                loadAllEvents(); // Reload to show updated participant list
                loadMySchedule(); // Refresh user's schedule
            } else {
                const error = await response.json();
                showToast(i18n.t('messages.errors.error_leaving_event', { message: error.detail }), 'error');
            }
        } catch (error) {
            showToast(i18n.t('messages.errors.error_leaving_event', { message: error.message }), 'error');
        }
    });
}

// ============================================================================
// EXPOSE FUNCTIONS TO GLOBAL SCOPE FOR ONCLICK HANDLERS
// ============================================================================

// Onboarding and authentication
window.startOnboarding = startOnboarding;
function exposeToWindow(name, fn) {
    if (typeof fn === 'function') {
        window[name] = fn;
    }
}

exposeToWindow('showLogin', showLogin);
exposeToWindow('handleLogin', handleLogin);
exposeToWindow('showForgotPassword', showForgotPassword);
exposeToWindow('handleForgotPassword', handleForgotPassword);
exposeToWindow('handleResetPassword', handleResetPassword);
exposeToWindow('createProfile', createProfile);
exposeToWindow('createAndJoinOrg', createAndJoinOrg);

// Navigation
exposeToWindow('switchView', switchView);
exposeToWindow('goToHome', goToHome);

// Settings and profile
exposeToWindow('showSettings', showSettings);
exposeToWindow('closeSettings', closeSettings);
exposeToWindow('saveSettings', saveSettings);
exposeToWindow('dismissSetupHint', dismissSetupHint);
exposeToWindow('logout', logout);

// Calendar
exposeToWindow('exportMyCalendar', exportMyCalendar);
exposeToWindow('showCalendarSubscription', showCalendarSubscription);
exposeToWindow('closeCalendarSubscriptionModal', closeCalendarSubscriptionModal);
exposeToWindow('resetCalendarToken', resetCalendarToken);
exposeToWindow('copyToClipboard', copyToClipboard);

// Events
exposeToWindow('joinEvent', joinEvent);
exposeToWindow('leaveEvent', leaveEvent);
// Teams Management
async function loadAdminTeams() {
    const listEl = document.getElementById('teams-list');
    const orgSelect = document.getElementById('teams-org-filter');
    const orgId = orgSelect ? orgSelect.value : (currentUser ? currentUser.org_id : null);

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
                        <div class="data-card-title">${team.name}</div>
                        <div class="data-card-id">ID: ${team.id}</div>
                    </div>
                    <div class="data-card-actions">
                        <button class="btn btn-sm" onclick="showEditTeamForm('${team.id}')" title="Edit">Edit</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteTeam('${team.id}', '${team.name.replace(/'/g, "\\'")}', '${orgId}')" title="Delete">Delete</button>
                    </div>
                </div>
                <div class="data-card-meta">
                    👥 ${team.member_count || 0} members
                    ${team.description ? `<br>${team.description}` : ''}
                </div>
            </div>
        `).join('');
    } catch (error) {
        listEl.innerHTML = `<div class="loading">Error: ${error.message}</div>`;
    }
}

async function showEditTeamForm(teamId) {
    const orgSelect = document.getElementById('teams-org-filter');
    const orgId = orgSelect ? orgSelect.value : (currentUser ? currentUser.org_id : null);

    try {
        // Fetch team details
        const response = await authFetch(`${API_BASE_URL}/teams/${teamId}?org_id=${orgId}`);
        const team = await response.json();

        // Create modal with edit form
        const modal = document.createElement('div');
        modal.id = 'edit-team-modal';
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Edit Team</h3>
                    <button class="btn-close" onclick="closeEditTeamModal()">×</button>
                </div>
                <div class="modal-body">
                    <form id="edit-team-form" onsubmit="editTeam(event); return false;">
                        <input type="hidden" id="edit-team-id" value="${team.id}">
                        <input type="hidden" id="edit-team-org-id" value="${orgId}">
                        <div class="form-group">
                            <label>Team Name</label>
                            <input type="text" id="team-name" name="name" value="${team.name}" required>
                        </div>
                        <div class="form-group">
                            <label>Description</label>
                            <textarea id="team-description" name="description" rows="3">${team.description || ''}</textarea>
                        </div>
                        <div class="form-actions">
                            <button type="button" class="btn btn-secondary" onclick="closeEditTeamModal()">Cancel</button>
                            <button type="submit" class="btn btn-primary">Save Changes</button>
                        </div>
                    </form>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        modal.classList.remove('hidden');

        // Focus first input
        document.getElementById('team-name').focus();
    } catch (error) {
        showToast(`Error loading team: ${error.message}`, 'error');
    }
}

function closeEditTeamModal() {
    const modal = document.getElementById('edit-team-modal');
    if (modal) {
        modal.remove();
    }
}

async function editTeam(event) {
    event.preventDefault();

    const teamId = document.getElementById('edit-team-id').value;
    const orgId = document.getElementById('edit-team-org-id').value;
    const name = document.getElementById('team-name').value;
    const description = document.getElementById('team-description').value;

    try {
        const response = await authFetch(`${API_BASE_URL}/teams/${teamId}?org_id=${orgId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, description: description || null })
        });

        if (response.ok) {
            closeEditTeamModal();
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

async function deleteTeam(teamId, teamName, orgId) {
    if (!confirm(`Delete team "${teamName}"?\n\nThis action cannot be undone.`)) {
        return;
    }

    try {
        const response = await authFetch(`${API_BASE_URL}/teams/${teamId}?org_id=${orgId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
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

function showCreateTeamForm() {
    const orgSelect = document.getElementById('teams-org-filter');
    const orgId = orgSelect ? orgSelect.value : (currentUser ? currentUser.org_id : null);

    if (!orgId) {
        showToast('Please select an organization first', 'error');
        return;
    }

    // Create modal with create form
    const modal = document.createElement('div');
    modal.id = 'create-team-modal';
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Create Team</h3>
                <button class="btn-close" onclick="closeCreateTeamModal()">×</button>
            </div>
            <div class="modal-body">
                <form id="create-team-form" onsubmit="createTeam(event); return false;">
                    <input type="hidden" id="create-team-org-id" value="${orgId}">
                    <div class="form-group">
                        <label>Team ID</label>
                        <input type="text" id="create-team-id" name="id" placeholder="team_example" required>
                        <small class="form-help">Unique identifier for the team (e.g., team_worship, team_parking)</small>
                    </div>
                    <div class="form-group">
                        <label>Team Name</label>
                        <input type="text" id="create-team-name" name="name" placeholder="Worship Team" required>
                    </div>
                    <div class="form-group">
                        <label>Description</label>
                        <textarea id="create-team-description" name="description" rows="3" placeholder="Team description..."></textarea>
                    </div>
                    <div class="form-actions">
                        <button type="button" class="btn btn-secondary" onclick="closeCreateTeamModal()">Cancel</button>
                        <button type="submit" class="btn btn-primary">Create Team</button>
                    </div>
                </form>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    modal.classList.remove('hidden');

    // Focus first input
    document.getElementById('create-team-id').focus();
}

function closeCreateTeamModal() {
    const modal = document.getElementById('create-team-modal');
    if (modal) {
        modal.remove();
    }
}

async function createTeam(event) {
    event.preventDefault();

    const orgId = document.getElementById('create-team-org-id').value;
    const teamId = document.getElementById('create-team-id').value;
    const name = document.getElementById('create-team-name').value;
    const description = document.getElementById('create-team-description').value;

    try {
        const response = await authFetch(`${API_BASE_URL}/teams/?org_id=${orgId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: teamId,
                org_id: orgId,
                name,
                description: description || null,
                member_ids: []
            })
        });

        if (response.ok) {
            closeCreateTeamModal();
            loadAdminTeams();
            showToast('Team created successfully!', 'success');
        } else {
            const error = await response.json();
            showToast(`Error: ${error.detail}`, 'error');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

exposeToWindow('showCreateEventForm', typeof showCreateEventForm === 'function' ? showCreateEventForm : undefined);
exposeToWindow('closeCreateEventForm', typeof closeCreateEventForm === 'function' ? closeCreateEventForm : undefined);
exposeToWindow('loadAdminEvents', loadAdminEvents);
exposeToWindow('showAssignments', showAssignments);
exposeToWindow('editEvent', editEvent);
exposeToWindow('deleteEvent', deleteEvent);
exposeToWindow('closeAssignmentModal', closeAssignmentModal);
exposeToWindow('toggleAssignment', toggleAssignment);

// Time off / blocked dates
exposeToWindow('closeEditTimeOffModal', closeEditTimeOffModal);
exposeToWindow('editTimeOffFromButton', editTimeOffFromButton);
exposeToWindow('removeTimeOff', removeTimeOff);

// Admin
exposeToWindow('switchAdminTab', switchAdminTab);
exposeToWindow('generateSchedule', generateSchedule);
exposeToWindow('exportLatestSchedulePDF', exportLatestSchedulePDF);
exposeToWindow('exportOrgCalendar', exportOrgCalendar);
exposeToWindow('showScheduleStats', showScheduleStats);
exposeToWindow('viewSolution', viewSolution);
exposeToWindow('deleteSolution', deleteSolution);

// Teams
exposeToWindow('loadAdminTeams', loadAdminTeams);
exposeToWindow('showCreateTeamForm', showCreateTeamForm);
exposeToWindow('closeCreateTeamModal', closeCreateTeamModal);
exposeToWindow('createTeam', createTeam);
exposeToWindow('showEditTeamForm', showEditTeamForm);
exposeToWindow('closeEditTeamModal', closeEditTeamModal);
exposeToWindow('editTeam', editTeam);
exposeToWindow('deleteTeam', deleteTeam);

// Organization
exposeToWindow('showCreateOrg', showCreateOrg);

// Roles
exposeToWindow('showAddRoleForm', typeof showAddRoleForm === 'function' ? showAddRoleForm : undefined);
exposeToWindow('closeAddRoleForm', typeof closeAddRoleForm === 'function' ? closeAddRoleForm : undefined);
exposeToWindow('showEditRoleModal', typeof showEditRoleModal === 'function' ? showEditRoleModal : undefined);
exposeToWindow('closeEditRoleModal', typeof closeEditRoleModal === 'function' ? closeEditRoleModal : undefined);
exposeToWindow('showManageRolePeopleModal', typeof showManageRolePeopleModal === 'function' ? showManageRolePeopleModal : undefined);
exposeToWindow('closeManageRolePeopleModal', typeof closeManageRolePeopleModal === 'function' ? closeManageRolePeopleModal : undefined);
exposeToWindow('deleteRole', typeof deleteRole === 'function' ? deleteRole : undefined);

// People
exposeToWindow('showEditPersonModal', showEditPersonModal);
exposeToWindow('closeEditPersonModal', closeEditPersonModal);
exposeToWindow('showInviteUserModal', showInviteUserModal);
exposeToWindow('closeInviteUserModal', closeInviteUserModal);
exposeToWindow('resendInvitation', resendInvitation);
exposeToWindow('cancelInvitation', cancelInvitation);
exposeToWindow('closeSelectRoleModal', closeSelectRoleModal);

// Expose selected functions for testing when running in Node environment
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        handleLogin,
        translateApiMessage,
        getApiErrorMessage,
    };
}
