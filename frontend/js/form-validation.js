/**
 * Form Validation System
 * Provides inline error messages and visual feedback
 */

// Validation rules
const validators = {
    required: (value) => value && value.trim() !== '',
    email: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
    minLength: (min) => (value) => value && value.length >= min,
    maxLength: (max) => (value) => value && value.length <= max,
    dateAfter: (startDate) => (endDate) => new Date(endDate) >= new Date(startDate),
    futureDate: (value) => new Date(value) >= new Date(),
    pattern: (regex) => (value) => regex.test(value),
};

// Error messages
const errorMessages = {
    required: 'This field is required',
    email: 'Please enter a valid email address',
    minLength: (min) => `Must be at least ${min} characters`,
    maxLength: (max) => `Must be no more than ${max} characters`,
    dateAfter: 'End date must be after start date',
    futureDate: 'Date must be in the future',
    pattern: 'Invalid format',
};

// Show error message below field
function showFieldError(fieldId, message) {
    const field = document.getElementById(fieldId);
    if (!field) return;

    // Remove existing error
    hideFieldError(fieldId);

    // Add error class to field
    field.classList.add('field-error');

    // Create error message element
    const errorEl = document.createElement('div');
    errorEl.className = 'error-message';
    errorEl.id = `${fieldId}-error`;
    errorEl.textContent = message;
    errorEl.style.cssText = `
        color: #ef4444;
        font-size: 12px;
        margin-top: 4px;
        display: block;
    `;

    // Insert after field
    field.parentNode.insertBefore(errorEl, field.nextSibling);
}

// Hide error message
function hideFieldError(fieldId) {
    const field = document.getElementById(fieldId);
    if (!field) return;

    field.classList.remove('field-error');

    const errorEl = document.getElementById(`${fieldId}-error`);
    if (errorEl) {
        errorEl.remove();
    }
}

// Validate single field
function validateField(fieldId, rules) {
    const field = document.getElementById(fieldId);
    if (!field) return true;

    const value = field.value;

    for (const rule of rules) {
        const { type, param, message } = rule;
        const validator = typeof type === 'function' ? type : validators[type];

        if (!validator) continue;

        const isValid = param !== undefined
            ? validator(param)(value)
            : validator(value);

        if (!isValid) {
            const errorMsg = message ||
                (typeof errorMessages[type] === 'function'
                    ? errorMessages[type](param)
                    : errorMessages[type]);
            showFieldError(fieldId, errorMsg);
            return false;
        }
    }

    hideFieldError(fieldId);
    return true;
}

// Validate entire form
function validateForm(formId, fieldRules) {
    let isValid = true;

    for (const [fieldId, rules] of Object.entries(fieldRules)) {
        if (!validateField(fieldId, rules)) {
            isValid = false;
        }
    }

    return isValid;
}

// Add real-time validation to field
function addRealTimeValidation(fieldId, rules) {
    const field = document.getElementById(fieldId);
    if (!field) return;

    // Validate on blur
    field.addEventListener('blur', () => {
        validateField(fieldId, rules);
    });

    // Clear error on input
    field.addEventListener('input', () => {
        if (field.classList.contains('field-error')) {
            hideFieldError(fieldId);
        }
    });
}

// Setup form with validation
function setupFormValidation(formId, fieldRules, onSubmit) {
    const form = document.getElementById(formId);
    if (!form) return;

    // Add real-time validation to all fields
    for (const [fieldId, rules] of Object.entries(fieldRules)) {
        addRealTimeValidation(fieldId, rules);
    }

    // Handle form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (!validateForm(formId, fieldRules)) {
            showToast('Please fix the errors in the form', 'error');
            return;
        }

        if (onSubmit) {
            await onSubmit(e);
        }
    });
}

// Add CSS for error states
if (!document.getElementById('validation-styles')) {
    const style = document.createElement('style');
    style.id = 'validation-styles';
    style.textContent = `
        .field-error {
            border-color: #ef4444 !important;
            background-color: #fef2f2 !important;
        }

        .field-error:focus {
            outline-color: #ef4444 !important;
            box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1) !important;
        }

        .error-message {
            animation: fadeIn 0.2s ease-in;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-4px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .loading-spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid #f3f4f6;
            border-top-color: #3b82f6;
            border-radius: 50%;
            animation: spin 0.6s linear infinite;
            margin-left: 8px;
            vertical-align: middle;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
    `;
    document.head.appendChild(style);
}

// Show loading state on button
function setButtonLoading(buttonId, loading = true, originalText = null) {
    const button = document.getElementById(buttonId);
    if (!button) return;

    if (loading) {
        button.dataset.originalText = button.innerHTML;
        button.disabled = true;
        button.innerHTML = `${button.dataset.originalText || 'Loading...'}<span class="loading-spinner"></span>`;
    } else {
        button.disabled = false;
        button.innerHTML = button.dataset.originalText || originalText || 'Submit';
        delete button.dataset.originalText;
    }
}

// Helper: validate date range
function validateDateRange(startFieldId, endFieldId) {
    const startField = document.getElementById(startFieldId);
    const endField = document.getElementById(endFieldId);

    if (!startField || !endField) return true;

    const startDate = new Date(startField.value);
    const endDate = new Date(endField.value);

    if (endDate < startDate) {
        showFieldError(endFieldId, 'End date must be after start date');
        return false;
    }

    hideFieldError(endFieldId);
    return true;
}

// Export functions for use in other scripts
window.formValidation = {
    validateField,
    validateForm,
    showFieldError,
    hideFieldError,
    setupFormValidation,
    addRealTimeValidation,
    setButtonLoading,
    validateDateRange,
    validators,
};
