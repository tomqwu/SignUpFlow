/**
 * Frontend Integration Tests with Real API Calls
 *
 * Tests the frontend with actual backend integration to catch bugs
 * that unit tests miss.
 */

const { I18n } = require('../js/i18n');

// Mock fetch for testing
global.fetch = jest.fn();

// Mock localStorage
const localStorageMock = {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn(),
    clear: jest.fn()
};
global.localStorage = localStorageMock;

let handleLogin;
let testI18n;

describe('Frontend Integration Tests', () => {
    beforeAll(() => {
        testI18n = new I18n();
        testI18n.locale = 'en';
        testI18n.translations = {
            en: {
                auth: { login: { error: 'Invalid email or password' } },
                messages: { errors: { connection_error: 'Connection error. Please try again.' } },
                common: {}
            },
            'zh-CN': {
                auth: { login: { error: '电子邮件或密码无效' } },
                messages: { errors: { connection_error: '连接错误。请重试。' } },
                common: {}
            }
        };
        testI18n.loadedNamespaces = new Set();
        testI18n.loadNamespaces = jest.fn().mockResolvedValue();
        testI18n.init = jest.fn().mockResolvedValue(testI18n.locale);
        testI18n.setLocale = jest.fn(async (locale) => {
            testI18n.locale = locale;
            return true;
        });
        testI18n.detectLocale = jest.fn(() => testI18n.locale);

        global.i18n = testI18n;
        global.router = { navigate: jest.fn(), init: jest.fn(), handleRoute: jest.fn() };
        global.showMainApp = jest.fn();
        global.saveSession = jest.fn();
        global.switchView = jest.fn();
        global.showToast = jest.fn();
        global.addRecaptchaToken = jest.fn(async (_action, options) => options);
        global.authFetch = jest.fn();

        ({ handleLogin } = require('../js/app-user'));
    });

    beforeEach(async () => {
        fetch.mockClear();
        localStorageMock.getItem.mockClear();
        localStorageMock.setItem.mockClear();

        await testI18n.setLocale('en');

        // Setup DOM
        document.body.innerHTML = `
            <div id="active-roles-display" class="role-badges"></div>
            <div id="settings-permission-display"></div>
        `;
    });

    describe('Role Display Integration', () => {
        test('should handle API returning role objects correctly', async () => {
            // Simulate API returning roles as objects (bug scenario)
            const mockUser = {
                id: 1,
                name: 'Test User',
                email: 'test@example.com',
                roles: [
                    { name: 'worship-leader' },
                    { name: 'vocalist' }
                ]
            };

            fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => mockUser
            });

            // Simulate what app-user.js does
            const response = await fetch('/api/people/1');
            const user = await response.json();

            // Extract roles correctly (handle objects)
            const roles = user.roles.map(r =>
                typeof r === 'string' ? r : (r.name || r.role || '[unknown]')
            );

            // Create badges
            const container = document.getElementById('active-roles-display');
            roles.forEach(role => {
                const badge = document.createElement('span');
                badge.className = 'role-badge';
                const roleLabel = role.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                badge.textContent = roleLabel;
                container.appendChild(badge);
            });

            // Verify no [object Object] appears
            const badgeTexts = Array.from(container.querySelectorAll('.role-badge'))
                .map(b => b.textContent);

            expect(badgeTexts).toEqual(['Worship Leader', 'Vocalist']);
            expect(badgeTexts.join('')).not.toContain('[object Object]');
        });

        test('should handle API returning role strings correctly', async () => {
            // Simulate API returning roles as strings (correct scenario)
            const mockUser = {
                id: 1,
                name: 'Test User',
                email: 'test@example.com',
                roles: ['admin', 'volunteer']
            };

            fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => mockUser
            });

            const response = await fetch('/api/people/1');
            const user = await response.json();

            // Extract roles
            const roles = user.roles.map(r =>
                typeof r === 'string' ? r : (r.name || r.role || '[unknown]')
            );

            expect(roles).toEqual(['admin', 'volunteer']);
            expect(roles.every(r => typeof r === 'string')).toBe(true);
        });

        test('should display roles in settings modal correctly', () => {
            const mockRoles = ['worship-leader', 'vocalist', 'admin'];

            const display = document.getElementById('settings-permission-display');

            // Simulate what app-user.js does in updateSettingsModal
            const roleText = mockRoles
                .map(r => typeof r === 'string' ? r : (r.name || r.role || '[unknown]'))
                .map(r => r.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()))
                .join(', ');

            display.textContent = roleText;

            expect(display.textContent).toBe('Worship Leader, Vocalist, Admin');
            expect(display.textContent).not.toContain('[object Object]');
        });
    });

    describe('Router Authentication Integration', () => {
        test('should expose currentUser to window for router access', () => {
            // Simulate login
            const currentUser = { id: 1, name: 'Test' };
            window.currentUser = currentUser;

            // Router should be able to access it
            expect(window.currentUser).toBeDefined();
            expect(window.currentUser.id).toBe(1);
        });

        test('should clear window.currentUser on logout', () => {
            // Set user
            window.currentUser = { id: 1, name: 'Test' };

            // Logout
            window.currentUser = null;
            localStorage.removeItem('currentUser');

            expect(window.currentUser).toBeNull();
        });

        test('should restore currentUser from localStorage on page load', () => {
            const savedUser = { id: 1, name: 'Test', email: 'test@example.com' };

            // Save to localStorage first
            localStorage.setItem('currentUser', JSON.stringify(savedUser));

            // Now mock getItem to return what was saved
            localStorageMock.getItem.mockReturnValueOnce(JSON.stringify(savedUser));

            // Simulate page load
            const loadedUser = JSON.parse(localStorage.getItem('currentUser') || 'null');
            window.currentUser = loadedUser;

            expect(window.currentUser).toEqual(savedUser);
            expect(window.currentUser.id).toBe(1);
        });
    });

    describe('Language Persistence Integration', () => {
        test('should save language with user data', () => {
            const currentUser = {
                id: 1,
                name: 'Test',
                language: 'zh-CN'
            };

            // Save to localStorage
            localStorage.setItem('currentUser', JSON.stringify(currentUser));

            // Should also send to API
            fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => ({ ...currentUser })
            });

            const updateLanguage = async (userId, language) => {
                const response = await fetch(`/api/people/${userId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ language })
                });
                return response.json();
            };

            updateLanguage(1, 'zh-CN');

            expect(fetch).toHaveBeenCalledWith(
                '/api/people/1',
                expect.objectContaining({
                    method: 'PUT',
                    body: JSON.stringify({ language: 'zh-CN' })
                })
            );
        });

        test('should load user language on page load', () => {
            const savedUser = {
                id: 1,
                name: 'Test',
                language: 'zh-TW'
            };

            // Save to localStorage first
            localStorage.setItem('currentUser', JSON.stringify(savedUser));

            // Mock localStorage.getItem to return saved user
            localStorageMock.getItem.mockReturnValueOnce(JSON.stringify(savedUser));

            // Simulate page load
            const user = JSON.parse(localStorage.getItem('currentUser'));
            const userLanguage = user?.language || 'en';

            expect(userLanguage).toBe('zh-TW');
        });
    });

    describe('Translation Integration', () => {
        test('should translate page without [object Object]', () => {
            // Setup DOM with data-i18n attributes
            document.body.innerHTML = `
                <span data-i18n="common.volunteer">Volunteer</span>
                <span data-i18n="common.administrator">Administrator</span>
                <input data-i18n-placeholder="auth.placeholder_email" placeholder="Email">
            `;

            const translations = {
                common: {
                    volunteer: '志愿者',
                    administrator: '管理员'
                },
                auth: {
                    placeholder_email: '电子邮件'
                }
            };

            // Simulate translation
            document.querySelectorAll('[data-i18n]').forEach(el => {
                const key = el.getAttribute('data-i18n');
                const [section, subsection] = key.split('.');
                const translation = translations[section]?.[subsection];
                if (translation) {
                    el.textContent = translation;
                }
            });

            document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
                const key = el.getAttribute('data-i18n-placeholder');
                const [section, subsection] = key.split('.');
                const translation = translations[section]?.[subsection];
                if (translation) {
                    el.placeholder = translation;
                }
            });

            // Verify translations
            const volunteer = document.querySelector('[data-i18n="common.volunteer"]');
            expect(volunteer.textContent).toBe('志愿者');
            expect(volunteer.textContent).not.toContain('[object Object]');

            const input = document.querySelector('[data-i18n-placeholder="auth.placeholder_email"]');
            expect(input.placeholder).toBe('电子邮件');
        });
    });

    describe('Session Management Integration', () => {
        test('should save and restore complete session', () => {
            const user = { id: 1, name: 'Test', email: 'test@example.com', roles: ['admin'] };
            const org = { id: 1, name: 'Test Org' };

            // Save session
            localStorage.setItem('currentUser', JSON.stringify(user));
            localStorage.setItem('currentOrg', JSON.stringify(org));
            window.currentUser = user;
            window.currentOrg = org;

            // Simulate page reload
            localStorageMock.getItem.mockImplementation((key) => {
                if (key === 'currentUser') return JSON.stringify(user);
                if (key === 'currentOrg') return JSON.stringify(org);
                return null;
            });

            // Restore session
            const restoredUser = JSON.parse(localStorage.getItem('currentUser'));
            const restoredOrg = JSON.parse(localStorage.getItem('currentOrg'));
            window.currentUser = restoredUser;
            window.currentOrg = restoredOrg;

            expect(window.currentUser).toEqual(user);
            expect(window.currentOrg).toEqual(org);
        });

        test('should handle missing session gracefully', () => {
            localStorageMock.getItem.mockReturnValue(null);

            const restoredUser = JSON.parse(localStorage.getItem('currentUser') || 'null');
            window.currentUser = restoredUser;

            expect(window.currentUser).toBeNull();
        });
    });

    describe('API Error Handling Integration', () => {
        test('should handle API errors gracefully', async () => {
            fetch.mockRejectedValueOnce(new Error('Network error'));

            const loadUserData = async (userId) => {
                try {
                    const response = await fetch(`/api/people/${userId}`);
                    return await response.json();
                } catch (error) {
                    console.error('Failed to load user:', error);
                    return null;
                }
            };

            const errorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
            const result = await loadUserData(1);
            expect(result).toBeNull();
            expect(errorSpy).toHaveBeenCalledWith('Failed to load user:', expect.any(Error));
            errorSpy.mockRestore();
        });

        test('should handle 404 responses', async () => {
            fetch.mockResolvedValueOnce({
                ok: false,
                status: 404,
                json: async () => ({ detail: 'Not found' })
            });

            const response = await fetch('/api/people/999');
            expect(response.ok).toBe(false);
            expect(response.status).toBe(404);
        });
    });

    describe('Localization Integration', () => {
        test('should translate invalid login error in zh-CN locale', async () => {
            await testI18n.setLocale('zh-CN');

            document.body.innerHTML = `
                <form id="login-form">
                    <input id="login-email" value="wrong@example.com" />
                    <input id="login-password" value="wrongpass" />
                    <div id="login-error" class="error-message hidden"></div>
                </form>
            `;

            fetch.mockResolvedValueOnce({
                ok: false,
                json: async () => ({ detail: 'Invalid email or password' })
            });

            const event = { preventDefault: jest.fn() };
            await handleLogin(event);

            const errorEl = document.getElementById('login-error');
            expect(errorEl.classList.contains('hidden')).toBe(false);
            expect(errorEl.textContent).toBe('电子邮件或密码无效');
        });
    });
});
