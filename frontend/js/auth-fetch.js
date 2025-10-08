/**
 * Authenticated fetch wrapper for API calls with Bearer token.
 *
 * This module provides a fetch wrapper that automatically includes
 * JWT Bearer tokens in the Authorization header.
 */

const API_BASE_URL = '/api';

/**
 * Make an authenticated API request with Bearer token.
 *
 * @param {string} url - API endpoint URL
 * @param {object} options - Fetch options (method, headers, body, etc.)
 * @returns {Promise<Response>} Fetch response
 */
async function authFetch(url, options = {}) {
    // Get token from localStorage
    const token = localStorage.getItem('authToken');

    // Build headers
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    // Add Authorization header if token exists
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    // Make request
    const response = await fetch(url, {
        ...options,
        headers
    });

    // Handle 401 Unauthorized (token expired or invalid)
    if (response.status === 401) {
        console.warn('🔐 Authentication failed - token invalid or expired');

        // Clear invalid token
        localStorage.removeItem('authToken');
        localStorage.removeItem('currentUser');
        localStorage.removeItem('currentOrg');

        // Redirect to login if not already there
        if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/join')) {
            console.log('🔐 Redirecting to login...');
            if (window.router) {
                window.router.navigate('/login');
            } else {
                window.location.href = '/';
            }
        }

        throw new Error('Authentication required');
    }

    return response;
}

/**
 * Make an authenticated GET request.
 *
 * @param {string} url - API endpoint URL
 * @returns {Promise<any>} Parsed JSON response
 */
async function authGet(url) {
    const response = await authFetch(url, { method: 'GET' });
    if (!response.ok) {
        throw new Error(`GET ${url} failed: ${response.statusText}`);
    }
    return await response.json();
}

/**
 * Make an authenticated POST request.
 *
 * @param {string} url - API endpoint URL
 * @param {object} data - Request body data
 * @returns {Promise<any>} Parsed JSON response
 */
async function authPost(url, data) {
    const response = await authFetch(url, {
        method: 'POST',
        body: JSON.stringify(data)
    });
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(error.detail || `POST ${url} failed`);
    }
    return await response.json();
}

/**
 * Make an authenticated PUT request.
 *
 * @param {string} url - API endpoint URL
 * @param {object} data - Request body data
 * @returns {Promise<any>} Parsed JSON response
 */
async function authPut(url, data) {
    const response = await authFetch(url, {
        method: 'PUT',
        body: JSON.stringify(data)
    });
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(error.detail || `PUT ${url} failed`);
    }
    return await response.json();
}

/**
 * Make an authenticated DELETE request.
 *
 * @param {string} url - API endpoint URL
 * @returns {Promise<any>} Parsed JSON response or null
 */
async function authDelete(url) {
    const response = await authFetch(url, { method: 'DELETE' });
    if (!response.ok) {
        throw new Error(`DELETE ${url} failed: ${response.statusText}`);
    }
    // DELETE may return empty response
    const text = await response.text();
    return text ? JSON.parse(text) : null;
}

// Export functions
window.authFetch = authFetch;
window.authGet = authGet;
window.authPost = authPost;
window.authPut = authPut;
window.authDelete = authDelete;
