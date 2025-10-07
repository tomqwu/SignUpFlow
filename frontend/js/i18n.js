/**
 * Rostio Internationalization (i18n) Manager
 *
 * Lightweight i18n solution for multi-language support
 * Supports: translation, interpolation, pluralization, fallback
 */

class I18n {
    constructor() {
        this.locale = 'en';
        this.fallbackLocale = 'en';
        this.translations = {};
        this.loadedNamespaces = new Set();
        this.supportedLocales = ['en', 'es', 'pt', 'fr'];
    }

    /**
     * Initialize i18n with locale detection
     */
    async init() {
        // Detect locale from: 1) localStorage, 2) browser, 3) fallback
        this.locale = this.detectLocale();

        // Load core namespaces
        await this.loadNamespaces(['common', 'auth', 'messages']);

        return this.locale;
    }

    /**
     * Detect user's preferred language
     */
    detectLocale() {
        // 1. Check localStorage (user preference)
        const stored = localStorage.getItem('rostio_locale');
        if (stored && this.supportedLocales.includes(stored)) {
            return stored;
        }

        // 2. Check browser language
        const browserLang = navigator.language.split('-')[0]; // 'en-US' -> 'en'
        if (this.supportedLocales.includes(browserLang)) {
            return browserLang;
        }

        // 3. Fallback
        return this.fallbackLocale;
    }

    /**
     * Load translation namespaces
     */
    async loadNamespaces(namespaces) {
        const promises = namespaces.map(ns => this.loadNamespace(ns));
        await Promise.all(promises);
    }

    /**
     * Load single namespace
     */
    async loadNamespace(namespace) {
        if (this.loadedNamespaces.has(`${this.locale}:${namespace}`)) {
            return; // Already loaded
        }

        try {
            const response = await fetch(`/locales/${this.locale}/${namespace}.json`);
            if (!response.ok) {
                throw new Error(`Failed to load ${namespace}`);
            }

            const translations = await response.json();

            // Store translations
            if (!this.translations[this.locale]) {
                this.translations[this.locale] = {};
            }
            this.translations[this.locale][namespace] = translations;
            this.loadedNamespaces.add(`${this.locale}:${namespace}`);

        } catch (error) {
            console.warn(`Failed to load translations for ${namespace}:`, error);

            // Load fallback if not already English
            if (this.locale !== this.fallbackLocale) {
                try {
                    const fallbackResponse = await fetch(`/locales/${this.fallbackLocale}/${namespace}.json`);
                    const fallbackTranslations = await fallbackResponse.json();

                    if (!this.translations[this.fallbackLocale]) {
                        this.translations[this.fallbackLocale] = {};
                    }
                    this.translations[this.fallbackLocale][namespace] = fallbackTranslations;
                } catch (e) {
                    console.error(`Failed to load fallback translations for ${namespace}:`, e);
                }
            }
        }
    }

    /**
     * Translate a key
     *
     * @param {string} key - Translation key (e.g., 'common.buttons.save')
     * @param {object} params - Parameters for interpolation
     * @returns {string} Translated string
     */
    t(key, params = {}) {
        // Parse key: 'namespace.section.key' or 'section.key' (defaults to 'common')
        const parts = key.split('.');
        let namespace, path;

        if (parts.length === 1) {
            // Just a key, use common namespace
            namespace = 'common';
            path = parts;
        } else if (parts.length === 2) {
            // Could be 'namespace.key' or 'section.key' in common
            // Check if first part is a known namespace
            const knownNamespaces = ['common', 'auth', 'events', 'schedule', 'settings', 'admin', 'messages'];
            if (knownNamespaces.includes(parts[0])) {
                namespace = parts[0];
                path = [parts[1]];
            } else {
                namespace = 'common';
                path = parts;
            }
        } else {
            // 'namespace.section.key' format
            namespace = parts[0];
            path = parts.slice(1);
        }

        // Get translation
        let value = this.getTranslation(namespace, path, this.locale);

        // Fallback to English if not found
        if (value === key && this.locale !== this.fallbackLocale) {
            value = this.getTranslation(namespace, path, this.fallbackLocale);
        }

        // Interpolate parameters
        if (params && Object.keys(params).length > 0) {
            value = this.interpolate(value, params);
        }

        return value;
    }

    /**
     * Get translation from nested object
     */
    getTranslation(namespace, path, locale) {
        const translations = this.translations[locale]?.[namespace];
        if (!translations) {
            return path.join('.'); // Return key as fallback
        }

        let value = translations;
        for (const key of path) {
            value = value[key];
            if (value === undefined) {
                return path.join('.'); // Return key as fallback
            }
        }

        return value;
    }

    /**
     * Interpolate parameters into string
     * Supports {param} syntax
     */
    interpolate(str, params) {
        return Object.entries(params).reduce(
            (result, [key, value]) => result.replace(new RegExp(`\\{${key}\\}`, 'g'), value),
            str
        );
    }

    /**
     * Change locale
     */
    async setLocale(locale) {
        if (!this.supportedLocales.includes(locale)) {
            console.warn(`Locale '${locale}' not supported`);
            return false;
        }

        this.locale = locale;
        localStorage.setItem('rostio_locale', locale);

        // Reload all loaded namespaces for new locale
        const namespacesToLoad = Array.from(this.loadedNamespaces)
            .map(ns => ns.split(':')[1])
            .filter((ns, index, self) => self.indexOf(ns) === index); // unique

        this.loadedNamespaces.clear();
        await this.loadNamespaces(namespacesToLoad);

        // Trigger locale change event
        window.dispatchEvent(new CustomEvent('localeChanged', { detail: { locale } }));

        return true;
    }

    /**
     * Get current locale
     */
    getLocale() {
        return this.locale;
    }

    /**
     * Get supported locales
     */
    getSupportedLocales() {
        return this.supportedLocales;
    }

    /**
     * Format date according to locale
     */
    formatDate(date, options = {}) {
        const defaultOptions = {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        };

        return new Intl.DateTimeFormat(this.locale, { ...defaultOptions, ...options }).format(date);
    }

    /**
     * Format time according to locale
     */
    formatTime(date, options = {}) {
        const defaultOptions = {
            hour: 'numeric',
            minute: '2-digit',
            hour12: this.locale === 'en' // 12h for English, 24h for others
        };

        return new Intl.DateTimeFormat(this.locale, { ...defaultOptions, ...options }).format(date);
    }

    /**
     * Format number according to locale
     */
    formatNumber(number, options = {}) {
        return new Intl.NumberFormat(this.locale, options).format(number);
    }
}

// Create global instance
const i18n = new I18n();

// Initialize on page load
if (typeof window !== 'undefined') {
    window.addEventListener('DOMContentLoaded', () => {
        i18n.init().then(locale => {
            console.log(`i18n initialized with locale: ${locale}`);
        });
    });
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { I18n, i18n };
}
