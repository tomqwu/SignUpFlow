/**
 * Billing Portal - Subscription management and upgrade interface
 *
 * Features:
 * - Display current subscription plan and usage
 * - Show pricing plans comparison
 * - Handle upgrade flow with Stripe Checkout
 * - Display billing history
 */

import { API_BASE_URL, authFetch } from './auth.js';
import i18n from './i18n.js';

/**
 * Initialize billing portal
 */
export async function initBillingPortal() {
    console.log('Initializing billing portal...');

    const currentUser = JSON.parse(localStorage.getItem('currentUser'));
    if (!currentUser) {
        console.error('No current user found');
        return;
    }

    // Check if user is admin
    const isAdmin = currentUser.roles && currentUser.roles.includes('admin');
    if (!isAdmin) {
        showError(i18n.t('billing.error_messages.admin_required'));
        return;
    }

    await loadCurrentSubscription();
    await loadPricingPlans();

    setupEventListeners();
    handleCheckoutReturn();
}

/**
 * Load current subscription details
 */
async function loadCurrentSubscription() {
    try {
        const currentUser = JSON.parse(localStorage.getItem('currentUser'));
        const response = await authFetch(
            `${API_BASE_URL}/billing/subscription?org_id=${currentUser.org_id}`
        );

        if (!response.ok) {
            throw new Error('Failed to load subscription');
        }

        const data = await response.json();
        displayCurrentSubscription(data);
    } catch (error) {
        console.error('Error loading subscription:', error);
        showError(i18n.t('billing.error_messages.load_failed'));
    }
}

/**
 * Display current subscription information
 */
function displayCurrentSubscription(data) {
    const container = document.getElementById('current-subscription');
    if (!container) return;

    const subscription = data.subscription;
    const usage = data.usage;

    // Display plan tier
    const planName = i18n.t(`billing.plan_names.${subscription.plan_tier}`);
    const statusBadge = getStatusBadge(subscription.status);

    // Format billing cycle and next renewal date
    const billingCycleDisplay = subscription.billing_cycle ?
        i18n.t(`billing.billing_cycles.${subscription.billing_cycle}`) : '';

    const nextRenewalDate = subscription.current_period_end ?
        new Date(subscription.current_period_end).toLocaleDateString() : '';

    container.innerHTML = `
        <div class="subscription-header">
            <h2 data-i18n="billing.billing_portal.current_plan">${i18n.t('billing.billing_portal.current_plan')}</h2>
            <div class="plan-info">
                <span class="plan-name">${planName}</span>
                ${statusBadge}
            </div>
        </div>

        ${subscription.billing_cycle && subscription.plan_tier !== 'free' ? `
            <div class="subscription-details" style="margin: 1.5rem 0; padding: 1rem; background-color: #f9fafb; border-radius: 0.5rem;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div>
                        <p style="font-size: 0.875rem; color: #6b7280; margin-bottom: 0.25rem;">
                            ${i18n.t('billing.billing_portal.billing_cycle')}
                        </p>
                        <p style="font-weight: 500; color: #1f2937;">
                            ${billingCycleDisplay}
                        </p>
                    </div>
                    ${nextRenewalDate ? `
                        <div>
                            <p style="font-size: 0.875rem; color: #6b7280; margin-bottom: 0.25rem;">
                                ${i18n.t('billing.billing_portal.next_renewal')}
                            </p>
                            <p style="font-weight: 500; color: #1f2937;">
                                ${nextRenewalDate}
                            </p>
                        </div>
                    ` : ''}
                </div>
            </div>
        ` : ''}

        ${subscription.status === 'trialing' ? `
            <div class="trial-notice">
                <strong data-i18n="billing.status.trialing">${i18n.t('billing.status.trialing')}</strong>
                <p>${i18n.t('billing.messages.trial_ends', {
                    date: new Date(subscription.trial_end_date).toLocaleDateString()
                })}</p>
                <button
                    class="btn-primary add-payment-btn"
                    data-i18n="billing.buttons.add_payment_method"
                    style="margin-top: 1rem;">
                    ${i18n.t('billing.buttons.add_payment_method')}
                </button>
                <p style="margin-top: 0.5rem; font-size: 0.875rem; color: #6b7280;">
                    ${i18n.t('billing.upgrade_prompts.trial_ending_soon', {
                        days: Math.ceil((new Date(subscription.trial_end_date) - new Date()) / (1000 * 60 * 60 * 24)),
                        plan: i18n.t(`billing.plan_names.${subscription.plan_tier}`)
                    })}
                </p>
            </div>
        ` : ''}

        ${subscription.pending_downgrade ? `
            <div class="downgrade-notice" style="margin: 1.5rem 0; padding: 1rem; background-color: #fef3c7; border-left: 4px solid #f59e0b; border-radius: 0.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <strong style="color: #92400e; display: block; margin-bottom: 0.5rem;">
                            ⏳ Downgrade Scheduled
                        </strong>
                        <p style="color: #78350f; margin-bottom: 0.5rem;">
                            Your plan will downgrade to <strong>${i18n.t(`billing.plan_names.${subscription.pending_downgrade.new_plan_tier}`)}</strong>
                            on <strong>${new Date(subscription.pending_downgrade.effective_date).toLocaleDateString()}</strong>
                        </p>
                        ${subscription.pending_downgrade.credit_amount_cents > 0 ? `
                            <p style="color: #78350f; font-size: 0.875rem;">
                                💰 Account credit: $${(subscription.pending_downgrade.credit_amount_cents / 100).toFixed(2)}
                            </p>
                        ` : ''}
                        ${subscription.pending_downgrade.reason ? `
                            <p style="color: #78350f; font-size: 0.875rem; margin-top: 0.5rem;">
                                Reason: ${subscription.pending_downgrade.reason}
                            </p>
                        ` : ''}
                    </div>
                    <button
                        class="btn-secondary cancel-downgrade-btn"
                        style="margin-left: 1rem; white-space: nowrap;"
                        onclick="cancelDowngrade()">
                        Cancel Downgrade
                    </button>
                </div>
            </div>
        ` : ''}

        <div class="usage-summary">
            <h3 data-i18n="billing.usage_tracking.current_usage">${i18n.t('billing.usage_tracking.current_usage')}</h3>
            ${renderUsageMetrics(usage)}
        </div>

        ${data.next_invoice ? `
            <div class="next-invoice">
                <h3 data-i18n="billing.billing_portal.next_invoice">${i18n.t('billing.billing_portal.next_invoice')}</h3>
                <p>${i18n.t('common.date')}: ${new Date(data.next_invoice.due_date).toLocaleDateString()}</p>
                <p>${i18n.t('billing.billing_portal.amount')}: ${data.next_invoice.amount}</p>
            </div>
        ` : ''}
    `;
}

/**
 * Render usage metrics
 */
function renderUsageMetrics(usage) {
    if (!usage || !usage.usage) return '<p>No usage data available</p>';

    let html = '<div class="usage-metrics">';

    for (const [metricType, metrics] of Object.entries(usage.usage)) {
        const percentage = metrics.percentage || 0;
        const isApproachingLimit = percentage >= 80;
        const isOverLimit = percentage >= 100;

        const progressClass = isOverLimit ? 'over-limit' :
                             isApproachingLimit ? 'approaching-limit' : '';

        html += `
            <div class="usage-metric">
                <div class="metric-header">
                    <span class="metric-label">${i18n.t(`billing.usage_tracking.${metricType}`)}</span>
                    <span class="metric-value">${metrics.current}/${metrics.limit || '∞'}</span>
                </div>
                <div class="progress-bar ${progressClass}">
                    <div class="progress-fill" style="width: ${Math.min(percentage, 100)}%"></div>
                </div>
                <div class="metric-percentage">${percentage.toFixed(1)}% ${i18n.t('billing.usage_tracking.used')}</div>
            </div>
        `;
    }

    html += '</div>';
    return html;
}

/**
 * Get status badge HTML
 */
function getStatusBadge(status) {
    const statusClass = `status-${status}`;
    const statusText = i18n.t(`billing.status.${status}`);
    return `<span class="status-badge ${statusClass}">${statusText}</span>`;
}

/**
 * Load pricing plans
 */
async function loadPricingPlans() {
    const container = document.getElementById('pricing-plans');
    if (!container) return;

    const plans = [
        {
            tier: 'free',
            name: i18n.t('billing.plan_names.free'),
            price: i18n.t('billing.pricing.free_price'),
            features: [
                i18n.t('billing.features.volunteers_limit', { count: 10 }),
                i18n.t('billing.features.events_limit', { count: 50 }),
                i18n.t('billing.features.storage_limit', { count: 100 }),
                i18n.t('billing.features.email_support')
            ],
            current: false
        },
        {
            tier: 'starter',
            name: i18n.t('billing.plan_names.starter'),
            monthlyPrice: i18n.t('billing.pricing.starter_monthly'),
            annualPrice: i18n.t('billing.pricing.starter_annual'),
            features: [
                i18n.t('billing.features.volunteers_limit', { count: 50 }),
                i18n.t('billing.features.events_limit', { count: 200 }),
                i18n.t('billing.features.storage_limit', { count: 1000 }),
                i18n.t('billing.features.priority_support')
            ],
            popular: true,
            current: false
        },
        {
            tier: 'pro',
            name: i18n.t('billing.plan_names.pro'),
            monthlyPrice: i18n.t('billing.pricing.pro_monthly'),
            annualPrice: i18n.t('billing.pricing.pro_annual'),
            features: [
                i18n.t('billing.features.volunteers_limit', { count: 200 }),
                i18n.t('billing.features.events_unlimited'),
                i18n.t('billing.features.storage_unlimited'),
                i18n.t('billing.features.phone_support')
            ],
            current: false
        },
        {
            tier: 'enterprise',
            name: i18n.t('billing.plan_names.enterprise'),
            price: i18n.t('billing.pricing.enterprise_price'),
            features: [
                i18n.t('billing.features.volunteers_unlimited'),
                i18n.t('billing.features.events_unlimited'),
                i18n.t('billing.features.storage_unlimited'),
                i18n.t('billing.features.dedicated_account_manager')
            ],
            current: false
        }
    ];

    container.innerHTML = '<div class="pricing-grid">' +
        plans.map(plan => renderPricingCard(plan)).join('') +
        '</div>';
}

/**
 * Render pricing card
 */
function renderPricingCard(plan) {
    const isCurrentPlan = plan.current;
    const popularBadge = plan.popular ?
        `<span class="popular-badge">${i18n.t('common.popular')}</span>` : '';

    let priceHtml;
    if (plan.tier === 'free' || plan.tier === 'enterprise') {
        priceHtml = `<div class="price">${plan.price}</div>`;
    } else {
        // Get savings for annual billing
        const savingsKey = `billing.pricing.${plan.tier}_annual_savings`;
        const savingsBadge = i18n.t(savingsKey);

        priceHtml = `
            <div class="price">
                <span class="monthly-price">${plan.monthlyPrice}</span>
                <span class="annual-price">${plan.annualPrice}</span>
            </div>
            <p class="billing-cycle-note monthly-note" data-i18n="billing.pricing.trial_period">
                ${i18n.t('billing.pricing.trial_period')}
            </p>
            <p class="billing-cycle-note annual-note savings-badge" style="display: none;">
                <strong style="color: #059669;">${savingsBadge}</strong>
            </p>
        `;
    }

    return `
        <div class="pricing-card ${isCurrentPlan ? 'current' : ''} ${plan.popular ? 'popular' : ''}">
            ${popularBadge}
            <h3>${plan.name}</h3>
            ${priceHtml}
            <ul class="features">
                ${plan.features.map(f => `<li>${f}</li>`).join('')}
            </ul>
            ${renderPlanButton(plan, isCurrentPlan)}
        </div>
    `;
}

/**
 * Render plan action button
 */
function renderPlanButton(plan, isCurrentPlan) {
    if (isCurrentPlan) {
        return `
            <button class="btn-current" disabled data-i18n="billing.status.current_plan">
                ${i18n.t('billing.billing_portal.current_plan')}
            </button>
        `;
    }

    if (plan.tier === 'free') {
        return ''; // No action for free plan
    }

    if (plan.tier === 'enterprise') {
        return `
            <button
                class="btn-primary"
                onclick="window.open('mailto:sales@signupflow.io', '_blank')"
                data-i18n="billing.buttons.contact_sales">
                ${i18n.t('billing.buttons.contact_sales')}
            </button>
        `;
    }

    // For paid plans, show both "Start Trial" and "Upgrade" options
    return `
        <button
            class="btn-primary start-trial-btn"
            data-plan="${plan.tier}"
            data-i18n="billing.buttons.start_trial"
            style="margin-bottom: 0.5rem;">
            ${i18n.t('billing.buttons.start_trial')}
        </button>
        <button
            class="btn-secondary upgrade-btn"
            data-plan="${plan.tier}"
            data-i18n="billing.buttons.upgrade">
            ${i18n.t('billing.buttons.upgrade')}
        </button>
    `;
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Upgrade button clicks
    document.addEventListener('click', async (e) => {
        if (e.target.classList.contains('upgrade-btn')) {
            const plan = e.target.dataset.plan;
            await handleUpgrade(plan);
        }

        // Start trial button clicks
        if (e.target.classList.contains('start-trial-btn')) {
            const plan = e.target.dataset.plan;
            await handleStartTrial(plan);
        }

        // Add payment method button clicks
        if (e.target.classList.contains('add-payment-btn')) {
            await handleAddPayment();
        }
    });

    // Billing cycle toggle
    const cycleToggle = document.getElementById('billing-cycle-toggle');
    if (cycleToggle) {
        cycleToggle.addEventListener('change', (e) => {
            toggleBillingCycle(e.target.value);
        });
    }
}

/**
 * Handle plan upgrade
 */
async function handleUpgrade(planTier) {
    try {
        const currentUser = JSON.parse(localStorage.getItem('currentUser'));

        // Show confirmation dialog
        const confirmed = confirm(
            i18n.t('billing.confirmation.upgrade_message', {
                plan: i18n.t(`billing.plan_names.${planTier}`),
                price: i18n.t(`billing.pricing.${planTier}_monthly`)
            })
        );

        if (!confirmed) return;

        // Show loading state
        showLoading(i18n.t('common.loading'));

        // Create upgrade request
        const response = await authFetch(
            `${API_BASE_URL}/billing/subscription/upgrade`,
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    org_id: currentUser.org_id,
                    plan_tier: planTier,
                    billing_cycle: 'monthly', // Default to monthly
                    trial_days: 14
                })
            }
        );

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upgrade failed');
        }

        const result = await response.json();

        if (result.success && result.checkout_url) {
            // Redirect to Stripe Checkout
            window.location.href = result.checkout_url;
        } else {
            throw new Error(result.message || 'Failed to create checkout session');
        }

    } catch (error) {
        console.error('Upgrade error:', error);
        hideLoading();
        showError(error.message || i18n.t('billing.error_messages.upgrade_failed'));
    }
}

/**
 * Handle start trial
 */
async function handleStartTrial(planTier) {
    try {
        const currentUser = JSON.parse(localStorage.getItem('currentUser'));

        // Show confirmation dialog
        const confirmed = confirm(
            i18n.t('billing.confirmation.start_trial_message', {
                plan: i18n.t(`billing.plan_names.${planTier}`),
                days: 14
            }) || `Start 14-day free trial of ${i18n.t(`billing.plan_names.${planTier}`)} plan? No payment required.`
        );

        if (!confirmed) return;

        // Show loading state
        showLoading(i18n.t('common.loading'));

        // Create trial request
        const response = await authFetch(
            `${API_BASE_URL}/billing/subscription/trial`,
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    org_id: currentUser.org_id,
                    plan_tier: planTier,
                    trial_days: 14
                })
            }
        );

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to start trial');
        }

        const result = await response.json();

        hideLoading();

        if (result.success) {
            showSuccess(i18n.t('billing.messages.trial_started'));
            // Reload subscription to show trial status
            setTimeout(() => {
                loadCurrentSubscription();
                loadPricingPlans(); // Refresh pricing cards to show updated state
            }, 1000);
        } else {
            throw new Error(result.message || 'Failed to start trial');
        }

    } catch (error) {
        console.error('Start trial error:', error);
        hideLoading();
        showError(error.message || i18n.t('billing.error_messages.trial_failed'));
    }
}

/**
 * Handle add payment method
 */
async function handleAddPayment() {
    try {
        // TODO: Implement Stripe Billing Portal integration
        // For now, redirect to upgrade flow (which includes payment)

        showInfo(
            'To add a payment method, please upgrade your subscription. ' +
            'The trial will automatically convert to a paid subscription when you add payment.'
        );

        // Alternative: Could implement Stripe Customer Portal session
        // const response = await authFetch(`${API_BASE_URL}/billing/portal-session`);
        // window.location.href = result.portal_url;

    } catch (error) {
        console.error('Add payment error:', error);
        showError('Failed to open payment method manager');
    }
}

/**
 * Handle return from Stripe Checkout
 */
function handleCheckoutReturn() {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');
    const cancelled = urlParams.get('cancelled');

    if (sessionId) {
        showSuccess(i18n.t('billing.messages.upgrade_success'));
        // Reload subscription to show updated plan
        setTimeout(() => {
            loadCurrentSubscription();
        }, 1000);
    } else if (cancelled) {
        showInfo(i18n.t('billing.messages.upgrade_cancelled'));
    }
}

/**
 * Toggle billing cycle display
 */
function toggleBillingCycle(cycle) {
    const cards = document.querySelectorAll('.pricing-card');
    cards.forEach(card => {
        const monthlyPrice = card.querySelector('.monthly-price');
        const annualPrice = card.querySelector('.annual-price');

        if (monthlyPrice && annualPrice) {
            if (cycle === 'annual') {
                monthlyPrice.style.display = 'none';
                annualPrice.style.display = 'block';
            } else {
                monthlyPrice.style.display = 'block';
                annualPrice.style.display = 'none';
            }
        }
    });
}

/**
 * Show loading overlay
 */
function showLoading(message) {
    const overlay = document.createElement('div');
    overlay.id = 'billing-loading';
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
        <div class="loading-spinner"></div>
        <p>${message}</p>
    `;
    document.body.appendChild(overlay);
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    const overlay = document.getElementById('billing-loading');
    if (overlay) {
        overlay.remove();
    }
}

/**
 * Show success message
 */
function showSuccess(message) {
    showToast(message, 'success');
}

/**
 * Show error message
 */
function showError(message) {
    showToast(message, 'error');
}

/**
 * Show info message
 */
function showInfo(message) {
    showToast(message, 'info');
}

/**
 * Cancel scheduled downgrade
 */
async function cancelDowngrade() {
    const currentUser = JSON.parse(localStorage.getItem('currentUser') || 'null');
    const currentOrg = JSON.parse(localStorage.getItem('currentOrg') || 'null');

    if (!currentUser || !currentOrg) {
        showError('Please log in to cancel downgrade');
        return;
    }

    if (!confirm('Are you sure you want to cancel the scheduled downgrade?')) {
        return;
    }

    showLoading('Cancelling downgrade...');

    try {
        const response = await authFetch(`${API_BASE_URL}/billing/subscription/cancel-downgrade?org_id=${currentOrg.id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to cancel downgrade');
        }

        const result = await response.json();

        hideLoading();
        showSuccess('Downgrade cancelled successfully!');

        // Reload subscription data to refresh UI
        setTimeout(() => {
            loadSubscriptionData();
        }, 1000);

    } catch (error) {
        hideLoading();
        showError(error.message || 'Failed to cancel downgrade. Please try again.');
        console.error('Error cancelling downgrade:', error);
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('show');
    }, 100);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
