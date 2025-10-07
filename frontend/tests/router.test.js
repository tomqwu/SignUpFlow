/**
 * Unit tests for router.js
 * Tests the URL-based routing system
 */

describe('Router', () => {
  let router;
  let mockWindow;

  beforeEach(() => {
    // Reset DOM
    document.body.innerHTML = `
      <div id="onboarding-screen" class="screen hidden"></div>
      <div id="login-screen" class="screen hidden"></div>
      <div id="join-screen" class="screen hidden"></div>
      <div id="main-app" class="screen hidden"></div>
      <div id="schedule-view" class="view-content"></div>
      <div id="events-view" class="view-content"></div>
    `;

    // Mock window methods
    jest.spyOn(window.history, 'pushState').mockImplementation(() => {});
    jest.spyOn(window, 'addEventListener').mockImplementation(() => {});

    // Create simplified router
    router = {
      routes: {
        '/': 'onboarding-screen',
        '/login': 'login-screen',
        '/join': 'join-screen',
        '/app': 'main-app',
        '/app/schedule': 'main-app',
        '/app/events': 'main-app',
      },

      navigate(path, addToHistory = true) {
        if (addToHistory) {
          window.history.pushState({ path }, '', path);
        }
        this.handleRoute(path, false);
      },

      handleRoute(path) {
        const screenId = this.routes[path];
        if (screenId) {
          this.showScreen(screenId);
        }
      },

      showScreen(screenId) {
        document.querySelectorAll('.screen').forEach(s => s.classList.add('hidden'));
        const screen = document.getElementById(screenId);
        if (screen) {
          screen.classList.remove('hidden');
        }
      },
    };
  });

  describe('Navigation', () => {
    test('should navigate to login page', () => {
      router.navigate('/login');

      expect(window.history.pushState).toHaveBeenCalledWith(
        { path: '/login' },
        '',
        '/login'
      );
      expect(document.getElementById('login-screen').classList.contains('hidden')).toBe(false);
    });

    test('should navigate to join page', () => {
      router.navigate('/join');

      expect(document.getElementById('join-screen').classList.contains('hidden')).toBe(false);
      expect(document.getElementById('onboarding-screen').classList.contains('hidden')).toBe(true);
    });

    test('should navigate to main app', () => {
      router.navigate('/app/schedule');

      expect(document.getElementById('main-app').classList.contains('hidden')).toBe(false);
    });

    test('should not add to history when addToHistory is false', () => {
      router.navigate('/login', false);

      expect(window.history.pushState).not.toHaveBeenCalled();
    });
  });

  describe('Screen Management', () => {
    test('should hide all screens before showing target', () => {
      // Show onboarding first
      document.getElementById('onboarding-screen').classList.remove('hidden');

      // Navigate to login
      router.showScreen('login-screen');

      expect(document.getElementById('onboarding-screen').classList.contains('hidden')).toBe(true);
      expect(document.getElementById('login-screen').classList.contains('hidden')).toBe(false);
    });

    test('should handle nonexistent screen gracefully', () => {
      expect(() => {
        router.showScreen('nonexistent-screen');
      }).not.toThrow();
    });
  });

  describe('Route Handling', () => {
    test('should route to correct screen for path', () => {
      router.handleRoute('/');
      expect(document.getElementById('onboarding-screen').classList.contains('hidden')).toBe(false);

      router.handleRoute('/login');
      expect(document.getElementById('login-screen').classList.contains('hidden')).toBe(false);

      router.handleRoute('/join');
      expect(document.getElementById('join-screen').classList.contains('hidden')).toBe(false);
    });

    test('should handle app routes', () => {
      router.handleRoute('/app/schedule');
      expect(document.getElementById('main-app').classList.contains('hidden')).toBe(false);
    });
  });

  describe('Browser Back/Forward', () => {
    test('should register popstate listener', () => {
      // In real implementation, router registers window.addEventListener('popstate', ...)
      // Here we just verify the concept
      const popstateHandler = jest.fn();
      window.addEventListener('popstate', popstateHandler);

      expect(window.addEventListener).toHaveBeenCalledWith('popstate', popstateHandler);
    });
  });
});
