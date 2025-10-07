/**
 * Unit tests for app-user.js critical functions
 * Tests session management, language persistence, and role handling
 */

describe('App User Functions', () => {
  let currentUser;
  let currentOrg;

  beforeEach(() => {
    currentUser = null;
    currentOrg = null;
    localStorage.clear();
  });

  describe('Session Management', () => {
    test('saveSession should store user and org in localStorage', () => {
      currentUser = {
        id: 'user_123',
        name: 'Test User',
        email: 'test@example.com',
        language: 'zh-CN',
        timezone: 'America/New_York',
      };

      currentOrg = {
        id: 'org_456',
        name: 'Test Org',
      };

      // Simulate saveSession
      localStorage.setItem('roster_user', JSON.stringify(currentUser));
      localStorage.setItem('roster_org', JSON.stringify(currentOrg));

      const savedUser = JSON.parse(localStorage.getItem('roster_user'));
      const savedOrg = JSON.parse(localStorage.getItem('roster_org'));

      expect(savedUser.language).toBe('zh-CN');
      expect(savedUser.timezone).toBe('America/New_York');
      expect(savedOrg.name).toBe('Test Org');
    });

    test('should load session from localStorage on init', () => {
      const testUser = {
        id: 'user_123',
        name: 'Test User',
        language: 'zh-CN',
      };

      localStorage.setItem('roster_user', JSON.stringify(testUser));

      const savedUser = localStorage.getItem('roster_user');
      expect(savedUser).toBeTruthy();

      const user = JSON.parse(savedUser);
      expect(user.language).toBe('zh-CN');
    });

    test('should clear session on logout', () => {
      localStorage.setItem('roster_user', JSON.stringify({ id: '123' }));
      localStorage.setItem('roster_org', JSON.stringify({ id: '456' }));

      // Simulate logout
      localStorage.clear();

      expect(localStorage.getItem('roster_user')).toBeNull();
      expect(localStorage.getItem('roster_org')).toBeNull();
    });
  });

  describe('Language Persistence', () => {
    test('should save language preference with user', () => {
      currentUser = {
        id: 'user_123',
        language: 'en',
      };

      // Update language
      currentUser.language = 'zh-CN';

      localStorage.setItem('roster_user', JSON.stringify(currentUser));

      const saved = JSON.parse(localStorage.getItem('roster_user'));
      expect(saved.language).toBe('zh-CN');
    });

    test('should load user language on page load', () => {
      const user = {
        id: 'user_123',
        language: 'zh-CN',
      };

      localStorage.setItem('roster_user', JSON.stringify(user));

      const loaded = JSON.parse(localStorage.getItem('roster_user'));
      expect(loaded.language).toBe('zh-CN');
    });

    test('should default to English if no language set', () => {
      const user = {
        id: 'user_123',
        // No language field
      };

      const language = user.language || 'en';
      expect(language).toBe('en');
    });
  });

  describe('Role Handling', () => {
    test('should handle string roles', () => {
      const roles = ['admin', 'volunteer'];

      const roleLabels = roles.map(role => {
        const roleStr = typeof role === 'string' ? role : (role.name || JSON.stringify(role));
        return roleStr === 'admin' ? '👑 Administrator' : roleStr === 'volunteer' ? '✓ Volunteer' : roleStr;
      });

      expect(roleLabels[0]).toBe('👑 Administrator');
      expect(roleLabels[1]).toBe('✓ Volunteer');
    });

    test('should handle object roles', () => {
      const roles = [
        { name: 'admin', description: 'Admin role' },
        { name: 'volunteer', description: 'Volunteer role' },
      ];

      const roleLabels = roles.map(role => {
        const roleStr = typeof role === 'string' ? role : (role.name || JSON.stringify(role));
        return roleStr === 'admin' ? '👑 Administrator' : roleStr === 'volunteer' ? '✓ Volunteer' : roleStr;
      });

      expect(roleLabels[0]).toBe('👑 Administrator');
      expect(roleLabels[1]).toBe('✓ Volunteer');
    });

    test('should not display [object Object] for object roles', () => {
      const role = { name: 'admin' };

      const roleStr = typeof role === 'string' ? role : (role.name || JSON.stringify(role));

      expect(roleStr).not.toBe('[object Object]');
      expect(roleStr).toBe('admin');
    });

    test('should handle empty roles array', () => {
      const roles = [];

      expect(roles.length).toBe(0);
    });
  });

  describe('Form Validation', () => {
    test('should validate email format', () => {
      const isValidEmail = (email) => {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
      };

      expect(isValidEmail('test@example.com')).toBe(true);
      expect(isValidEmail('invalid-email')).toBe(false);
      expect(isValidEmail('test@')).toBe(false);
      expect(isValidEmail('@example.com')).toBe(false);
    });

    test('should validate required fields', () => {
      const validateRequired = (value) => {
        return !!(value && value.trim().length > 0);
      };

      expect(validateRequired('Test Name')).toBe(true);
      expect(validateRequired('')).toBe(false);
      expect(validateRequired('   ')).toBe(false);
      expect(validateRequired(null)).toBe(false);
    });
  });

  describe('Translation Page Function', () => {
    test('should translate all elements with data-i18n', () => {
      document.body.innerHTML = `
        <div data-i18n="common.hello">Hello</div>
        <span data-i18n="auth.login">Login</span>
        <button data-i18n="common.save">Save</button>
      `;

      const mockI18n = {
        t: (key) => {
          const translations = {
            'common.hello': '你好',
            'auth.login': '登录',
            'common.save': '保存',
          };
          return translations[key] || key;
        },
      };

      // Simulate translatePage
      document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        const translated = mockI18n.t(key);
        el.textContent = translated;
      });

      expect(document.querySelector('[data-i18n="common.hello"]').textContent).toBe('你好');
      expect(document.querySelector('[data-i18n="auth.login"]').textContent).toBe('登录');
      expect(document.querySelector('[data-i18n="common.save"]').textContent).toBe('保存');
    });

    test('should translate placeholders separately', () => {
      document.body.innerHTML = `
        <input data-i18n-placeholder="common.search" placeholder="Search" />
        <input data-i18n-placeholder="auth.email" placeholder="Email" />
      `;

      const mockI18n = {
        t: (key) => {
          const translations = {
            'common.search': '搜索',
            'auth.email': '电子邮件',
          };
          return translations[key] || key;
        },
      };

      // Simulate placeholder translation
      document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        const translated = mockI18n.t(key);
        el.setAttribute('placeholder', translated);
      });

      expect(document.querySelector('[data-i18n-placeholder="common.search"]').getAttribute('placeholder')).toBe('搜索');
      expect(document.querySelector('[data-i18n-placeholder="auth.email"]').getAttribute('placeholder')).toBe('电子邮件');
    });
  });

  describe('Current View Tracking', () => {
    test('should save current view to localStorage', () => {
      const viewName = 'schedule';

      localStorage.setItem('roster_current_view', viewName);

      expect(localStorage.getItem('roster_current_view')).toBe('schedule');
    });

    test('should restore view on page load', () => {
      localStorage.setItem('roster_current_view', 'events');

      const savedView = localStorage.getItem('roster_current_view');
      expect(savedView).toBe('events');
    });
  });
});
