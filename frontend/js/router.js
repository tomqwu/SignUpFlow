/**
 * URL-based Router for Rostio
 * Handles navigation with proper URL updates and browser history
 */

class Router {
    constructor() {
        this.routes = {
            '/': 'onboarding-screen',
            '/login': 'login-screen',
            '/join': 'join-screen',
            '/profile': 'profile-screen',
            '/app': 'main-app',
            '/app/schedule': 'main-app',
            '/app/events': 'main-app',
            '/app/availability': 'main-app',
            '/app/admin': 'main-app'
        };

        this.viewRoutes = {
            '/app/schedule': 'schedule',
            '/app/events': 'events',
            '/app/availability': 'availability',
            '/app/admin': 'admin'
        };

        this.pageTitles = {
            '/': 'Welcome to Rostio',
            '/login': 'Sign In - Rostio',
            '/join': 'Join Organization - Rostio',
            '/profile': 'Create Profile - Rostio',
            '/app/schedule': 'My Schedule - Rostio',
            '/app/events': 'Events - Rostio',
            '/app/availability': 'Availability - Rostio',
            '/app/admin': 'Admin Console - Rostio'
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
        const title = this.pageTitles[path] || 'Rostio';
        document.title = title;

        // Update meta description based on page
        this.updateMetaDescription(path);

        // Handle authentication screens
        if (path === '/' || path === '/login' || path === '/join' || path === '/profile') {
            const screenId = this.routes[path];
            console.log(`🛣️  Auth screen detected. Path: ${path}, screenId: ${screenId}`);
            if (screenId) {
                this.showScreen(screenId);
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
     * Update meta description for SEO
     */
    updateMetaDescription(path) {
        const descriptions = {
            '/': 'Join Rostio to manage your team schedule, availability, and events effortlessly. Perfect for churches, leagues, and organizations.',
            '/login': 'Sign in to Rostio to access your schedule and manage your availability.',
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
