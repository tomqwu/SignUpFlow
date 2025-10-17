/**
 * reCAPTCHA v3 integration for SignUpFlow
 * Provides invisible bot protection with score-based verification
 */

// Define API_BASE_URL if not already defined
if (typeof API_BASE_URL === 'undefined') {
    var API_BASE_URL = '/api';
}

let recaptchaConfig = {
    enabled: false,
    siteKey: null,
    ready: false
};

/**
 * Initialize reCAPTCHA configuration
 */
async function initRecaptcha() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/recaptcha-site-key`);
        if (response.ok) {
            const config = await response.json();
            recaptchaConfig.enabled = config.enabled;
            recaptchaConfig.siteKey = config.site_key;

            console.log('🔒 reCAPTCHA v3 config loaded:', config.enabled ? 'enabled' : 'disabled');

            // Load reCAPTCHA script if enabled
            if (recaptchaConfig.enabled && recaptchaConfig.siteKey) {
                await loadRecaptchaScript();
            }
        }
    } catch (error) {
        console.warn('⚠️  Could not load reCAPTCHA config:', error);
        recaptchaConfig.enabled = false;
    }
}

/**
 * Load reCAPTCHA v3 script dynamically
 */
function loadRecaptchaScript() {
    return new Promise((resolve, reject) => {
        if (window.grecaptcha && window.grecaptcha.ready) {
            recaptchaConfig.ready = true;
            resolve();
            return;
        }

        const script = document.createElement('script');
        script.src = `https://www.google.com/recaptcha/api.js?render=${recaptchaConfig.siteKey}`;
        script.async = true;
        script.defer = true;

        script.onload = () => {
            window.grecaptcha.ready(() => {
                recaptchaConfig.ready = true;
                console.log('🔒 reCAPTCHA v3 ready');
                resolve();
            });
        };

        script.onerror = () => {
            console.warn('⚠️  Failed to load reCAPTCHA script');
            recaptchaConfig.enabled = false;
            reject(new Error('Failed to load reCAPTCHA'));
        };

        document.head.appendChild(script);
    });
}

/**
 * Get reCAPTCHA v3 token for an action
 * @param {string} action - Action name (e.g., 'login', 'signup', 'password_reset')
 * @returns {Promise<string|null>} reCAPTCHA token or null if disabled
 */
async function getRecaptchaToken(action = 'submit') {
    if (!recaptchaConfig.enabled) {
        return null;
    }

    if (!recaptchaConfig.ready || !window.grecaptcha) {
        console.warn('⚠️  reCAPTCHA not ready');
        return null;
    }

    try {
        const token = await window.grecaptcha.execute(recaptchaConfig.siteKey, { action });
        console.log(`🔒 reCAPTCHA v3 token obtained for action: ${action}`);
        return token;
    } catch (error) {
        console.error('❌ reCAPTCHA execution failed:', error);
        return null;
    }
}

/**
 * Execute reCAPTCHA and add token to request headers
 * @param {string} action - Action name
 * @param {object} fetchOptions - Fetch options object
 * @returns {Promise<object>} Updated fetch options with reCAPTCHA token
 */
async function addRecaptchaToken(action, fetchOptions = {}) {
    const token = await getRecaptchaToken(action);

    if (!token) {
        return fetchOptions;
    }

    if (!fetchOptions.headers) {
        fetchOptions.headers = {};
    }

    fetchOptions.headers['X-Recaptcha-Token'] = token;
    return fetchOptions;
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initRecaptcha);
} else {
    initRecaptcha();
}
