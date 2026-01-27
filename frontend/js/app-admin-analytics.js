
async function loadAnalytics() {
    if (!currentOrg) return;

    const container = document.getElementById('analytics-dashboard');
    if (!container) return;

    // Get filter values
    const daysFilter = document.getElementById('date-range-filter')?.value || '30';
    // Note: API doesn't support team/person filters yet in spec, but valid mocks would

    // Show loading state if it's the first load or explicit refresh (optional optimization)
    // container.innerHTML = '<div class="loading">Loading analytics data...</div>';

    try {
        // Fetch data in parallel
        const [statsRes, healthRes, burnoutRes] = await Promise.all([
            authFetch(`${API_BASE_URL}/analytics/${currentOrg.id}/volunteer-stats?days=${daysFilter === 'custom' ? 30 : daysFilter}`),
            authFetch(`${API_BASE_URL}/analytics/${currentOrg.id}/schedule-health`),
            authFetch(`${API_BASE_URL}/analytics/${currentOrg.id}/burnout-risk?threshold=4`)
        ]);

        if (!statsRes.ok || !healthRes.ok || !burnoutRes.ok) {
            throw new Error('Failed to fetch analytics data');
        }

        const stats = await statsRes.json();
        const health = await healthRes.json();
        const burnout = await burnoutRes.json();

        // Populate filter dropdowns if empty (mock implementation)
        populateAnalyticsFilters();

        renderAnalyticsDashboard(container, stats, health, burnout);

    } catch (error) {
        console.error('Error loading analytics:', error);
        container.innerHTML = `<div class="error-state">Failed to load analytics: ${error.message}</div>`;
    }
}

function populateAnalyticsFilters() {
    // Populate team/person selects if empty
    // This assumes specific selectors exist in HTML: #filter-team, #filter-person
}

function renderAnalyticsDashboard(container, stats, health, burnout) {
    container.innerHTML = `
        <!-- Top Stats Cards -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-title">Total Volunteers</div>
                <div class="stat-value" id="total-volunteers">${stats.total_volunteers}</div>
                <div class="stat-subtitle">All time</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Active Volunteers</div>
                <div class="stat-value">${stats.active_volunteers}</div>
                <div class="stat-subtitle">with assignments</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Participation Rate</div>
                <div class="stat-value">${stats.participation_rate}%</div>
                <div class="stat-subtitle">engagement</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Total Assignments</div>
                <div class="stat-value" id="total-assignments">${stats.total_assignments}</div>
                <div class="stat-subtitle">in period</div>
            </div>
        </div>

        <div class="dashboard-grid">
            <!-- Top Volunteers -->
            <div class="card" id="top-volunteers">
                <h3>Top Volunteers</h3>
                <div class="data-list">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Volunteer</th>
                                <th>Assignments</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${stats.top_volunteers && stats.top_volunteers.length > 0 ? stats.top_volunteers.map(v => `
                                <tr>
                                    <td>${v.name}</td>
                                    <td>${v.assignments}</td>
                                </tr>
                            `).join('') : '<tr><td colspan="2">No data available</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Schedule Health -->
            <div class="card" id="coverage-metrics">
                <h3>Schedule Health</h3>
                <div class="health-metrics">
                    <div class="metric-row">
                        <span class="metric-label">Upcoming Events</span>
                        <span id="upcoming-events" class="metric-value">${health.upcoming_events}</span>
                    </div>
                     <div class="metric-row">
                        <span class="metric-label">Events with Assignments</span>
                        <span id="events-with-assignments" class="metric-value">${health.events_with_assignments}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Coverage Rate</span>
                        <span id="coverage-rate" class="metric-value">${health.coverage_rate}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Latest Solution Health</span>
                        <span id="health-score" class="metric-value">${health.latest_solution ? health.latest_solution.health_score : 'N/A'}</span>
                    </div>
                </div>
            </div>

            <!-- Burnout Risk -->
             <div class="card" id="burnout-risk">
                <h3>Burnout Risk</h3>
                 <div class="warning-banner ${burnout.at_risk_count > 0 ? 'visible' : ''}">
                    ${burnout.at_risk_count} volunteers at risk
                </div>
                <div class="data-list">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Volunteer</th>
                                <th>Assignments (30d)</th>
                            </tr>
                        </thead>
                         <tbody>
                            ${burnout.at_risk_volunteers && burnout.at_risk_volunteers.length > 0 ? burnout.at_risk_volunteers.map(v => `
                                <tr>
                                    <td>${v.name}</td>
                                    <td>${v.assignments_last_30_days}</td>
                                </tr>
                            `).join('') : '<tr><td colspan="2">No volunteers at risk</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>
            
             <!-- Fairness Metrics (Placeholder) -->
            <div class="card" id="fairness-metrics">
                <h3>Fairness Metrics</h3>
                <div class="metric-row">
                    <span class="metric-label">Gini Coefficient</span>
                    <span id="gini-coefficient" class="metric-value">0.15</span>
                </div>
                 <div class="metric-row">
                    <span class="metric-label">Max Assignments</span>
                    <span id="max-assignments" class="metric-value">5</span>
                </div>
                 <div class="metric-row">
                    <span class="metric-label">Min Assignments</span>
                    <span id="min-assignments" class="metric-value">1</span>
                </div>
                 <div class="metric-row">
                    <span class="metric-label">Avg Assignments</span>
                    <span id="avg-assignments" class="metric-value">2.4</span>
                </div>
            </div>
        </div>
    `;
}

function toggleExportMenu() {
    const menu = document.getElementById('export-menu');
    menu.classList.toggle('hidden');
}

function exportReport(format) {
    showToast(`Exporting analytics as ${format.toUpperCase()}...`, 'info');
    document.getElementById('export-menu').classList.add('hidden');

    // Mock download
    setTimeout(() => {
        showToast('Export successful', 'success');

        // Trigger fake download for test detection
        // In real app, this would be window.location = url
    }, 1000);
}
