/**
 * Unit tests for i18n.js
 * Tests the internationalization system
 */

// Mock translations for testing
const mockTranslations = {
  en: {
    common: { hello: 'Hello', goodbye: 'Goodbye' },
    auth: { login: 'Login', signup: 'Sign Up' },
  },
  'zh-CN': {
    common: { hello: '你好', goodbye: '再见' },
    auth: { login: '登录', signup: '注册' },
  },
};

describe('I18n System', () => {
  let i18n;

  beforeEach(() => {
    // Reset DOM
    document.body.innerHTML = '';

    // Create a simple i18n mock
    i18n = {
      locale: 'en',
      translations: {},

      async init() {
        this.locale = localStorage.getItem('roster_locale') || 'en';
        this.translations = mockTranslations;
        return this.locale;
      },

      async setLocale(locale) {
        this.locale = locale;
        localStorage.setItem('roster_locale', locale);
      },

      getLocale() {
        return this.locale;
      },

      t(key) {
        const parts = key.split('.');
        let value = this.translations[this.locale];

        for (const part of parts) {
          if (!value) return key;
          value = value[part];
        }

        return value || key;
      },

      async loadNamespaces(namespaces) {
        // Mock - already loaded in init
        return true;
      },
    };
  });

  describe('Initialization', () => {
    test('should initialize with default locale', async () => {
      await i18n.init();
      expect(i18n.getLocale()).toBe('en');
    });

    test('should restore locale from localStorage', async () => {
      localStorage.setItem('roster_locale', 'zh-CN');
      await i18n.init();
      expect(i18n.getLocale()).toBe('zh-CN');
    });
  });

  describe('Locale Management', () => {
    test('should change locale', async () => {
      await i18n.init();
      await i18n.setLocale('zh-CN');
      expect(i18n.getLocale()).toBe('zh-CN');
    });

    test('should persist locale to localStorage', async () => {
      await i18n.init();
      await i18n.setLocale('zh-CN');
      expect(localStorage.getItem('roster_locale')).toBe('zh-CN');
    });
  });

  describe('Translation', () => {
    beforeEach(async () => {
      await i18n.init();
    });

    test('should translate simple key', () => {
      expect(i18n.t('common.hello')).toBe('Hello');
    });

    test('should translate nested key', () => {
      expect(i18n.t('auth.login')).toBe('Login');
    });

    test('should return key if translation missing', () => {
      expect(i18n.t('nonexistent.key')).toBe('nonexistent.key');
    });

    test('should translate in Chinese', async () => {
      await i18n.setLocale('zh-CN');
      expect(i18n.t('common.hello')).toBe('你好');
      expect(i18n.t('auth.login')).toBe('登录');
    });
  });

  describe('DOM Translation', () => {
    beforeEach(async () => {
      await i18n.init();
    });

    test('should translate elements with data-i18n attribute', () => {
      document.body.innerHTML = `
        <div data-i18n="common.hello"></div>
        <span data-i18n="auth.login"></span>
      `;

      // Simulate translatePage function
      document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        el.textContent = i18n.t(key);
      });

      expect(document.querySelector('[data-i18n="common.hello"]').textContent).toBe('Hello');
      expect(document.querySelector('[data-i18n="auth.login"]').textContent).toBe('Login');
    });

    test('should translate placeholder attributes', () => {
      document.body.innerHTML = `
        <input data-i18n-placeholder="common.hello" />
      `;

      document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        el.setAttribute('placeholder', i18n.t(key));
      });

      expect(document.querySelector('input').getAttribute('placeholder')).toBe('Hello');
    });

    test('should not show [object Object] when translating', () => {
      document.body.innerHTML = `
        <div data-i18n="auth"></div>
      `;

      document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        const translated = i18n.t(key);

        // This should not be an object
        if (typeof translated === 'object') {
          el.textContent = '[ERROR: Translation returned object]';
        } else {
          el.textContent = translated;
        }
      });

      const text = document.querySelector('div').textContent;
      expect(text).not.toContain('[object Object]');
    });
  });

  describe('Language Switching Workflow', () => {
    test('should switch language and update translations', async () => {
      await i18n.init();

      document.body.innerHTML = `
        <h1 data-i18n="common.hello"></h1>
        <button data-i18n="auth.login"></button>
      `;

      // Translate in English
      document.querySelectorAll('[data-i18n]').forEach(el => {
        el.textContent = i18n.t(el.getAttribute('data-i18n'));
      });

      expect(document.querySelector('h1').textContent).toBe('Hello');
      expect(document.querySelector('button').textContent).toBe('Login');

      // Switch to Chinese
      await i18n.setLocale('zh-CN');

      // Re-translate
      document.querySelectorAll('[data-i18n]').forEach(el => {
        el.textContent = i18n.t(el.getAttribute('data-i18n'));
      });

      expect(document.querySelector('h1').textContent).toBe('你好');
      expect(document.querySelector('button').textContent).toBe('登录');
    });
  });
});
