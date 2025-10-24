/**
 * SMS Preferences Management Module
 *
 * Handles:
 * - Phone verification flow
 * - SMS notification preferences
 * - Opt-in/opt-out management
 * - Rate limit display
 */

// Assumes authFetch, showToast, and i18n are loaded globally
const API_BASE_URL = window.location.origin;

/**
 * Initialize SMS preferences UI
 */
export async function initSmsPreferences() {
    const currentUser = JSON.parse(localStorage.getItem('currentUser') || 'null');
    if (!currentUser) return;

    // Load SMS preferences
    await loadSmsPreferences(currentUser.id);

    // Attach event listeners
    attachSmsEventListeners();
}

/**
 * Load SMS preferences from backend
 */
async function loadSmsPreferences(personId) {
    try {
        const response = await authFetch(`${API_BASE_URL}/api/people/${personId}`);
        if (!response.ok) {
            throw new Error('Failed to load SMS preferences');
        }

        const person = await response.json();

        // Check if SMS preferences exist
        if (person.sms_preferences) {
            renderSmsPreferences(person.sms_preferences);
        } else {
            renderPhoneVerificationForm();
        }
    } catch (error) {
        console.error('Error loading SMS preferences:', error);
        showToast(i18n.t('messages.error.load_failed'), 'error');
    }
}

/**
 * Render SMS preferences UI
 */
function renderSmsPreferences(smsPrefs) {
    const container = document.getElementById('sms-preferences-container');
    if (!container) return;

    const isVerified = smsPrefs.verified;
    const isOptedOut = smsPrefs.opt_out_date !== null;

    container.innerHTML = `
        <div class="sms-preferences-section">
            <h3 data-i18n="settings.sms.title">SMS Notifications</h3>

            <!-- Phone Number Display -->
            <div class="phone-number-display">
                <label data-i18n="settings.sms.phone_number">Phone Number:</label>
                <div class="phone-info">
                    <span class="phone-number">${smsPrefs.phone_number || 'Not set'}</span>
                    ${isVerified ?
                        '<span class="badge badge-success" data-i18n="settings.sms.verified">Verified ✓</span>' :
                        '<span class="badge badge-warning" data-i18n="settings.sms.not_verified">Not Verified</span>'
                    }
                </div>
                ${isVerified ?
                    '<button id="change-phone-btn" class="btn btn-secondary btn-sm" data-i18n="settings.sms.change_phone">Change Phone</button>' :
                    ''
                }
            </div>

            <!-- Verification Status -->
            ${!isVerified ? `
                <div class="alert alert-warning">
                    <p data-i18n="settings.sms.verify_required">
                        Please verify your phone number to receive SMS notifications.
                    </p>
                    <button id="verify-phone-btn" class="btn btn-primary" data-i18n="settings.sms.verify_now">
                        Verify Now
                    </button>
                </div>
            ` : ''}

            <!-- Opt-Out Status -->
            ${isOptedOut ? `
                <div class="alert alert-info">
                    <p data-i18n="settings.sms.opted_out">
                        You have opted out of SMS notifications. Reply START to re-enable.
                    </p>
                    <p class="text-muted">
                        <small data-i18n="settings.sms.opt_out_date">
                            Opted out on: ${new Date(smsPrefs.opt_out_date).toLocaleDateString()}
                        </small>
                    </p>
                </div>
            ` : ''}

            <!-- Notification Preferences -->
            ${isVerified && !isOptedOut ? `
                <div class="notification-preferences">
                    <h4 data-i18n="settings.sms.notification_types">Notification Types</h4>
                    <p class="text-muted" data-i18n="settings.sms.notification_desc">
                        Choose which notifications you want to receive via SMS
                    </p>

                    <div class="checkbox-group">
                        <label class="checkbox-label">
                            <input type="checkbox" id="notify-assignment"
                                ${smsPrefs.notification_types?.includes('assignment') ? 'checked' : ''}>
                            <span data-i18n="settings.sms.notify_assignment">Assignment Notifications</span>
                            <small class="text-muted" data-i18n="settings.sms.notify_assignment_desc">
                                When you're assigned to an event
                            </small>
                        </label>

                        <label class="checkbox-label">
                            <input type="checkbox" id="notify-reminder"
                                ${smsPrefs.notification_types?.includes('reminder') ? 'checked' : ''}>
                            <span data-i18n="settings.sms.notify_reminder">Event Reminders</span>
                            <small class="text-muted" data-i18n="settings.sms.notify_reminder_desc">
                                24-hour reminder before events
                            </small>
                        </label>

                        <label class="checkbox-label">
                            <input type="checkbox" id="notify-change"
                                ${smsPrefs.notification_types?.includes('change') ? 'checked' : ''}>
                            <span data-i18n="settings.sms.notify_change">Schedule Changes</span>
                            <small class="text-muted" data-i18n="settings.sms.notify_change_desc">
                                When event details change
                            </small>
                        </label>

                        <label class="checkbox-label">
                            <input type="checkbox" id="notify-cancellation"
                                ${smsPrefs.notification_types?.includes('cancellation') ? 'checked' : ''}>
                            <span data-i18n="settings.sms.notify_cancellation">Cancellations</span>
                            <small class="text-muted" data-i18n="settings.sms.notify_cancellation_desc">
                                When events are cancelled
                            </small>
                        </label>
                    </div>

                    <button id="save-sms-prefs-btn" class="btn btn-primary" data-i18n="common.buttons.save">
                        Save Preferences
                    </button>
                </div>

                <!-- Language Preference -->
                <div class="language-preference">
                    <h4 data-i18n="settings.sms.language">SMS Language</h4>
                    <select id="sms-language" class="form-control">
                        <option value="en" ${smsPrefs.language === 'en' ? 'selected' : ''}>English</option>
                        <option value="es" ${smsPrefs.language === 'es' ? 'selected' : ''}>Español (Spanish)</option>
                        <option value="pt" ${smsPrefs.language === 'pt' ? 'selected' : ''}>Português (Portuguese)</option>
                        <option value="zh-CN" ${smsPrefs.language === 'zh-CN' ? 'selected' : ''}>简体中文 (Simplified Chinese)</option>
                        <option value="zh-TW" ${smsPrefs.language === 'zh-TW' ? 'selected' : ''}>繁體中文 (Traditional Chinese)</option>
                        <option value="fr" ${smsPrefs.language === 'fr' ? 'selected' : ''}>Français (French)</option>
                    </select>
                </div>

                <!-- Rate Limit Display -->
                <div class="rate-limit-info">
                    <p class="text-muted">
                        <small data-i18n="settings.sms.rate_limit">
                            Rate limit: 3 SMS per day (resets at midnight)
                        </small>
                    </p>
                </div>
            ` : ''}
        </div>
    `;

    // Re-translate
    if (window.translatePage) {
        window.translatePage();
    }
}

/**
 * Render phone verification form
 */
function renderPhoneVerificationForm() {
    const container = document.getElementById('sms-preferences-container');
    if (!container) return;

    container.innerHTML = `
        <div class="phone-verification-form">
            <h3 data-i18n="settings.sms.verify_phone">Verify Phone Number</h3>
            <p class="text-muted" data-i18n="settings.sms.verify_desc">
                Enter your phone number to receive SMS notifications. We'll send you a verification code.
            </p>

            <!-- Phone Number Input -->
            <div class="form-group">
                <label for="phone-input" data-i18n="settings.sms.phone_number">Phone Number</label>
                <input
                    type="tel"
                    id="phone-input"
                    class="form-control"
                    placeholder="+1234567890"
                    data-i18n-placeholder="settings.sms.phone_placeholder">
                <small class="form-text text-muted" data-i18n="settings.sms.e164_format">
                    Use E.164 format (e.g., +12345678900 for US numbers)
                </small>
            </div>

            <!-- Verify Button -->
            <button id="send-verification-btn" class="btn btn-primary" data-i18n="settings.sms.send_code">
                Send Verification Code
            </button>

            <!-- Verification Code Input (hidden initially) -->
            <div id="verification-code-section" class="verification-code-section" style="display: none;">
                <h4 data-i18n="settings.sms.enter_code">Enter Verification Code</h4>
                <p class="text-muted" data-i18n="settings.sms.code_sent">
                    We've sent a 6-digit code to your phone. Enter it below:
                </p>

                <div class="form-group">
                    <input
                        type="text"
                        id="verification-code-input"
                        class="form-control verification-code-input"
                        placeholder="123456"
                        maxlength="6"
                        pattern="[0-9]{6}">
                    <small class="form-text text-muted" data-i18n="settings.sms.code_expires">
                        Code expires in 10 minutes. Max 3 attempts.
                    </small>
                </div>

                <button id="verify-code-btn" class="btn btn-primary" data-i18n="settings.sms.verify_code">
                    Verify Code
                </button>
                <button id="resend-code-btn" class="btn btn-secondary" data-i18n="settings.sms.resend_code">
                    Resend Code
                </button>
            </div>
        </div>
    `;

    // Re-translate
    if (window.translatePage) {
        window.translatePage();
    }
}

/**
 * Attach event listeners for SMS preferences
 */
function attachSmsEventListeners() {
    // Send verification code
    document.addEventListener('click', async (e) => {
        if (e.target.id === 'send-verification-btn') {
            await sendVerificationCode();
        }
    });

    // Verify code
    document.addEventListener('click', async (e) => {
        if (e.target.id === 'verify-code-btn') {
            await verifyCode();
        }
    });

    // Resend code
    document.addEventListener('click', async (e) => {
        if (e.target.id === 'resend-code-btn') {
            await sendVerificationCode();
        }
    });

    // Save SMS preferences
    document.addEventListener('click', async (e) => {
        if (e.target.id === 'save-sms-prefs-btn') {
            await saveSmsPreferences();
        }
    });

    // Change phone number
    document.addEventListener('click', (e) => {
        if (e.target.id === 'change-phone-btn') {
            renderPhoneVerificationForm();
        }
    });

    // Verify phone button (from warning alert)
    document.addEventListener('click', (e) => {
        if (e.target.id === 'verify-phone-btn') {
            renderPhoneVerificationForm();
        }
    });
}

/**
 * Send verification code to phone number
 */
async function sendVerificationCode() {
    const phoneInput = document.getElementById('phone-input');
    if (!phoneInput) return;

    const phoneNumber = phoneInput.value.trim();
    if (!phoneNumber) {
        showToast(i18n.t('messages.error.phone_required'), 'error');
        return;
    }

    // Validate E.164 format
    const e164Pattern = /^\+[1-9]\d{1,14}$/;
    if (!e164Pattern.test(phoneNumber)) {
        showToast(i18n.t('messages.error.invalid_phone_format'), 'error');
        return;
    }

    const currentUser = JSON.parse(localStorage.getItem('currentUser') || 'null');
    if (!currentUser) return;

    const personId = parseInt(currentUser.id.split('_').pop());

    try {
        // First, verify phone number format with Twilio
        const verifyResponse = await authFetch(`${API_BASE_URL}/api/sms/verify-phone`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone_number: phoneNumber })
        });

        if (!verifyResponse.ok) {
            throw new Error('Phone verification failed');
        }

        const verifyResult = await verifyResponse.json();

        if (!verifyResult.valid || !verifyResult.deliverable) {
            showToast(
                i18n.t('messages.error.phone_not_deliverable') ||
                'This phone number cannot receive SMS messages',
                'error'
            );
            return;
        }

        // Send verification code
        const codeResponse = await authFetch(`${API_BASE_URL}/api/sms/send-verification-code`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                person_id: personId,
                phone_number: phoneNumber
            })
        });

        if (!codeResponse.ok) {
            throw new Error('Failed to send verification code');
        }

        // Show verification code input section
        const codeSection = document.getElementById('verification-code-section');
        if (codeSection) {
            codeSection.style.display = 'block';
        }

        // Disable phone input
        phoneInput.disabled = true;

        showToast(
            i18n.t('messages.success.verification_code_sent') ||
            'Verification code sent! Check your phone.',
            'success'
        );

        // Focus on code input
        const codeInput = document.getElementById('verification-code-input');
        if (codeInput) {
            codeInput.focus();
        }

    } catch (error) {
        console.error('Error sending verification code:', error);
        showToast(i18n.t('messages.error.send_code_failed'), 'error');
    }
}

/**
 * Verify SMS code
 */
async function verifyCode() {
    const codeInput = document.getElementById('verification-code-input');
    if (!codeInput) return;

    const code = codeInput.value.trim();
    if (!code || code.length !== 6) {
        showToast(i18n.t('messages.error.invalid_code'), 'error');
        return;
    }

    const currentUser = JSON.parse(localStorage.getItem('currentUser') || 'null');
    if (!currentUser) return;

    const personId = parseInt(currentUser.id.split('_').pop());

    try {
        const response = await authFetch(`${API_BASE_URL}/api/sms/verify-code`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                person_id: personId,
                code: parseInt(code)
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Verification failed');
        }

        const result = await response.json();

        showToast(
            i18n.t('messages.success.phone_verified') ||
            'Phone verified successfully! You can now receive SMS notifications.',
            'success'
        );

        // Reload SMS preferences to show verified state
        await loadSmsPreferences(currentUser.id);

    } catch (error) {
        console.error('Error verifying code:', error);
        showToast(error.message || i18n.t('messages.error.verification_failed'), 'error');
    }
}

/**
 * Save SMS preferences
 */
async function saveSmsPreferences() {
    const notificationTypes = [];

    if (document.getElementById('notify-assignment')?.checked) {
        notificationTypes.push('assignment');
    }
    if (document.getElementById('notify-reminder')?.checked) {
        notificationTypes.push('reminder');
    }
    if (document.getElementById('notify-change')?.checked) {
        notificationTypes.push('change');
    }
    if (document.getElementById('notify-cancellation')?.checked) {
        notificationTypes.push('cancellation');
    }

    const language = document.getElementById('sms-language')?.value || 'en';

    const currentUser = JSON.parse(localStorage.getItem('currentUser') || 'null');
    if (!currentUser) return;

    try {
        const response = await authFetch(`${API_BASE_URL}/api/people/${currentUser.id}/sms-preferences`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                notification_types: notificationTypes,
                language: language
            })
        });

        if (!response.ok) {
            throw new Error('Failed to save SMS preferences');
        }

        showToast(
            i18n.t('messages.success.sms_prefs_saved') ||
            'SMS preferences saved successfully',
            'success'
        );

    } catch (error) {
        console.error('Error saving SMS preferences:', error);
        showToast(i18n.t('messages.error.save_failed'), 'error');
    }
}

// Expose functions globally for non-module scripts
window.initSmsPreferences = initSmsPreferences;
window.loadSmsPreferences = loadSmsPreferences;
window.sendVerificationCode = sendVerificationCode;
window.verifyCode = verifyCode;
window.saveSmsPreferences = saveSmsPreferences;
