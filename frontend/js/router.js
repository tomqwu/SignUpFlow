/**
 * URL-based Router for SignUpFlow
 * Handles navigation with proper URL updates and browser history
 */

// Define API_BASE_URL if not already defined
if (typeof API_BASE_URL === 'undefined') {
    var API_BASE_URL = '/api';
}

class Router {
    constructor() {
        this.routes = {
            '/': 'onboarding-screen',
            '/login': 'login-screen',
            '/forgot-password': 'forgot-password-screen',
            '/reset-password': 'reset-password-screen',
            '/join': 'join-screen',
            '/profile': 'profile-screen',
            '/app': 'main-app',
            '/app/schedule': 'main-app',
            '/app/events': 'main-app',
            '/app/availability': 'main-app',
            '/app/admin': 'main-app',
            '/app/onboarding-dashboard': 'onboarding-dashboard'
        };

        this.viewRoutes = {
            '/app/schedule': 'schedule',
            '/app/events': 'events',
            '/app/availability': 'availability',
            '/app/admin': 'admin'
        };

        this.pageTitles = {
            '/': 'Welcome to SignUpFlow',
            '/login': 'Sign In - SignUpFlow',
            '/forgot-password': 'Reset Password - SignUpFlow',
            '/reset-password': 'Create New Password - SignUpFlow',
            '/join': 'Join Organization - SignUpFlow',
            '/profile': 'Create Profile - SignUpFlow',
            '/app/schedule': 'My Schedule - SignUpFlow',
            '/app/events': 'Events - SignUpFlow',
            '/app/availability': 'Availability - SignUpFlow',
            '/app/admin': 'Admin Console - SignUpFlow',
            '/app/onboarding-dashboard': 'Getting Started - SignUpFlow'
        };

        // Listen for browser back/forward
        window.addEventListener('popstate', (e) => {
            this.handleRoute(window.location.pathname, false);
        });
    }

    /**
     * Navigate to a route
     */
    navigate(path, addToHistory = true) {
        if (addToHistory) {
            window.history.pushState({ path }, '', path);
        }
        this.handleRoute(path, false);
    }

    /**
     * Handle route change
     */
    handleRoute(path, addToHistory = true) {
        console.log(`🛣️  router.handleRoute called with path: ${path}, addToHistory: ${addToHistory}`);

        // Update page title
        const title = this.pageTitles[path] || 'SignUpFlow';
        document.title = title;

        // Update meta description based on page
        this.updateMetaDescription(path);

        // Handle authentication screens
        if (path === '/' || path === '/login' || path === '/forgot-password' || path === '/reset-password' || path === '/join' || path === '/profile') {
            const screenId = this.routes[path];
            console.log(`🛣️  Auth screen detected. Path: ${path}, screenId: ${screenId}`);

            // Special handling for /join route with invitation token
            if (path === '/join' && window.location.search) {
                const urlParams = new URLSearchParams(window.location.search);
                const invitationToken = urlParams.get('token');

                if (invitationToken) {
                    console.log(`🎟️  Invitation token detected: ${invitationToken.substring(0, 20)}...`);
                    // Automatically verify invitation token and navigate to profile screen
                    this.handleInvitationToken(invitationToken);
                    return;
                }
            }

            // Special handling for /reset-password route with reset token
            if (path === '/reset-password' && window.location.search) {
                const urlParams = new URLSearchParams(window.location.search);
                const resetToken = urlParams.get('token');

                if (resetToken) {
                    console.log(`🔑  Reset password token detected: ${resetToken.substring(0, 20)}...`);
                    // Pre-fill token and show reset password screen
                    this.handleResetPasswordToken(resetToken);
                    return;
                }
            }

            if (screenId) {
                this.showScreen(screenId);
            }
            return;
        }

        // Handle onboarding dashboard (special app screen)
        if (path === '/app/onboarding-dashboard') {
            this.showScreen('onboarding-dashboard');

            // Initialize onboarding dashboard components
            if (window.initChecklist) {
                window.initChecklist();
            }

            // Initialize sample data controls
            if (window.renderSampleDataControls) {
                setTimeout(() => {
                    window.renderSampleDataControls('dashboard-sample-data-controls');
                }, 100);
            }
            return;
        }

        // Handle app views
        if (path.startsWith('/app')) {
            // Make sure user is logged in
            if (!window.currentUser) {
                this.navigate('/login', true);
                return;
            }

            // Show main app screen
            this.showScreen('main-app');

            // Initialize main app components (name display, org dropdown, roles)
            if (window.currentUser) {
                const nameDisplay = document.getElementById('user-name-display');
                if (nameDisplay) nameDisplay.textContent = window.currentUser.name;

                if (window.updateRoleBadgesDisplay) window.updateRoleBadgesDisplay();
                if (window.loadUserOrganizations) window.loadUserOrganizations();

                // Show admin features if user is admin (critical for page refresh)
                if (window.currentUser.roles && window.currentUser.roles.includes('admin')) {
                    document.querySelectorAll('.admin-only').forEach(el => {
                        el.classList.remove('hidden');
                        el.classList.add('visible');
                    });
                }
            }

            // Switch to specific view
            const view = this.viewRoutes[path];
            if (view) {
                // Update nav buttons
                document.querySelectorAll('.nav-btn').forEach(btn => {
                    btn.classList.toggle('active', btn.dataset.view === view);
                });

                // Update content
                document.querySelectorAll('.view-content').forEach(content => {
                    content.classList.remove('active');
                });
                const targetView = document.getElementById(`${view}-view`);
                if (targetView) {
                    targetView.classList.add('active');
                }

                // Load data for the view
                if (view === 'schedule' && window.loadMySchedule) window.loadMySchedule();
                if (view === 'events' && window.loadAllEvents) window.loadAllEvents();
                if (view === 'availability' && window.loadTimeOff) window.loadTimeOff();
                if (view === 'admin' && window.loadAdminDashboard) window.loadAdminDashboard();
            } else if (path === '/app') {
                // Default to schedule view
                this.navigate('/app/schedule', false);
            }
        }
    }

    /**
     * Show a screen (for authentication flows)
     */
    showScreen(screenId) {
        console.log(`🎬 router.showScreen called with: ${screenId}`);
        document.querySelectorAll('.screen').forEach(s => s.classList.add('hidden'));
        const screen = document.getElementById(screenId);
        if (screen) {
            screen.classList.remove('hidden');
            console.log(`🎬 router.showScreen: ${screenId} is now visible`);
        } else {
            console.error(`🎬 router.showScreen: ${screenId} not found!`);
        }
    }

    /**
     * Handle invitation token from URL
     */
    async handleInvitationToken(token) {
        console.log(`🎟️  Processing invitation token...`);
        const errorEl = document.getElementById('invitation-error');

        try {
            // Call invitation verification API
            const response = await fetch(`${API_BASE_URL}/invitations/${token}`);
            const data = await response.json();

            if (!response.ok || !data.valid) {
                console.error('🎟️  Invalid invitation token');
                // Show join screen with error
                this.showScreen('join-screen');
                if (errorEl) {
                    errorEl.textContent = data.message || 'Invalid or expired invitation link';
                    errorEl.classList.remove('hidden');
                }
                return;
            }

            // Store invitation data globally
            window.currentInvitation = data.invitation;
            console.log('🎟️  Invitation verified:', window.currentInvitation);

            // Pre-fill profile form with invitation data
            document.getElementById('user-name').value = window.currentInvitation.name;
            document.getElementById('user-email').value = window.currentInvitation.email;
            document.getElementById('invitation-token-hidden').value = token;

            // Make name and email readonly for invitations
            document.getElementById('user-name').setAttribute('readonly', true);
            document.getElementById('user-email').setAttribute('readonly', true);

            // Display assigned roles
            const rolesDisplay = document.getElementById('invitation-roles-display');
            const rolesDisplayParent = rolesDisplay?.closest('.form-group');
            if (window.currentInvitation.roles && window.currentInvitation.roles.length > 0) {
                rolesDisplay.innerHTML = window.currentInvitation.roles.map(role =>
                    `<span class="role-badge">${role}</span>`
                ).join('');
                if (rolesDisplayParent) {
                    rolesDisplayParent.style.display = 'block';
                }
            } else {
                rolesDisplay.innerHTML = '<span class="role-badge">volunteer</span>';
                if (rolesDisplayParent) {
                    rolesDisplayParent.style.display = 'block';
                }
            }

            // Auto-detect and set timezone
            const detectedTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            const timezoneSelect = document.getElementById('user-timezone');
            if (timezoneSelect && detectedTimezone) {
                const option = Array.from(timezoneSelect.options).find(opt => opt.value === detectedTimezone);
                if (option) {
                    timezoneSelect.value = detectedTimezone;
                }
            }
            console.log('🌍 Auto-detected timezone:', detectedTimezone);

            // Change form handler to invitation signup
            const profileForm = document.querySelector('#profile-screen form');
            if (profileForm && window.completeInvitationSignup) {
                profileForm.onsubmit = window.completeInvitationSignup;
            }

            // Show profile screen
            this.showScreen('profile-screen');
            console.log('🎟️  Navigated to profile screen with invitation data');

        } catch (error) {
            console.error('🎟️  Error processing invitation token:', error);
            this.showScreen('join-screen');
            if (errorEl) {
                errorEl.textContent = 'Error processing invitation link. Please try again.';
                errorEl.classList.remove('hidden');
            }
        }
    }

    /**
     * Handle reset password token from URL
     */
    handleResetPasswordToken(token) {
        console.log(`🔑  Processing reset password token...`);

        // Pre-fill the hidden token field
        const tokenField = document.getElementById('reset-token');
        if (tokenField) {
            tokenField.value = token;
            console.log(`🔑  Token pre-filled in hidden field`);
        }

        // Show reset password screen
        this.showScreen('reset-password-screen');
        console.log(`🔑  Navigated to reset password screen with token`);
    }

    /**
     * Update meta description for SEO
     */
    updateMetaDescription(path) {
        const descriptions = {
            '/': 'Join SignUpFlow to manage your team schedule, availability, and events effortlessly. Perfect for churches, leagues, and organizations.',
            '/login': 'Sign in to SignUpFlow to access your schedule and manage your availability.',
            '/app/schedule': 'View your upcoming schedule and assignments.',
            '/app/events': 'Browse and join upcoming events in your organization.',
            '/app/availability': 'Manage your availability and time off preferences.',
            '/app/admin': 'Admin console for managing your organization, events, and team members.'
        };

        let metaDesc = document.querySelector('meta[name="description"]');
        if (!metaDesc) {
            metaDesc = document.createElement('meta');
            metaDesc.setAttribute('name', 'description');
            document.head.appendChild(metaDesc);
        }
        metaDesc.setAttribute('content', descriptions[path] || descriptions['/']);
    }

    /**
     * Get current route
     */
    getCurrentPath() {
        return window.location.pathname;
    }

    /**
     * Initialize router on page load
     */
    init() {
        const currentPath = this.getCurrentPath();

        // If on root and user is logged in, redirect to /app
        if (currentPath === '/' && window.currentUser) {
            this.navigate('/app/schedule', true);
        } else {
            this.handleRoute(currentPath, false);
        }
    }
}

// Create global router instance
const router = new Router();
