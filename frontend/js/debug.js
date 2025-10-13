/**
 * Debug utility for conditional console logging
 *
 * Usage:
 *   debug.log('User loaded:', user);
 *   debug.warn('Deprecated API');
 *   debug.error('Failed to fetch');
 *
 * Set DEBUG flag in environment or via URL parameter:
 *   ?debug=true
 */

// Check if debug mode is enabled
const DEBUG = (() => {
    // Check URL parameter first
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('debug')) {
        return urlParams.get('debug') !== 'false';
    }

    // Check localStorage
    const stored = localStorage.getItem('debug');
    if (stored !== null) {
        return stored === 'true';
    }

    // Default: debug mode OFF (must be explicitly enabled)
    return false;
})();

// Debug object with conditional logging
const debug = {
    enabled: DEBUG,

    log: (...args) => {
        if (DEBUG) {
            console.log('[DEBUG]', ...args);
        }
    },

    warn: (...args) => {
        if (DEBUG) {
            console.warn('[DEBUG]', ...args);
        }
    },

    error: (...args) => {
        // Always log errors, even in production
        console.error('[ERROR]', ...args);
    },

    info: (...args) => {
        if (DEBUG) {
            console.info('[DEBUG]', ...args);
        }
    },

    table: (...args) => {
        if (DEBUG && console.table) {
            console.table(...args);
        }
    },

    group: (label) => {
        if (DEBUG && console.group) {
            console.group(label);
        }
    },

    groupEnd: () => {
        if (DEBUG && console.groupEnd) {
            console.groupEnd();
        }
    },

    // Enable/disable debug mode programmatically
    enable: () => {
        localStorage.setItem('debug', 'true');
        window.location.reload();
    },

    disable: () => {
        localStorage.setItem('debug', 'false');
        window.location.reload();
    }
};

// Expose to window for easy access in console
window.debug = debug;

// Log debug status on load
if (DEBUG) {
    console.log('%c🐛 Debug mode enabled', 'color: #22c55e; font-weight: bold; font-size: 14px;');
    console.log('%cTo disable: debug.disable() or use ?debug=false', 'color: #64748b; font-size: 12px;');
}
