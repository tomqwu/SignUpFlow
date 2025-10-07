/**
 * Search and Filter System
 * Real-time filtering for people, events, and schedules
 */

// Debounce function for search performance
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Filter people list
function filterPeople(searchTerm, filterRole = null) {
    const listEl = document.getElementById('admin-people-list');
    if (!listEl) return;

    const items = listEl.querySelectorAll('.admin-item');
    let visibleCount = 0;

    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        const matchesSearch = searchTerm === '' || text.includes(searchTerm.toLowerCase());

        // Get roles from item (if displayed)
        const rolesText = item.querySelector('.admin-item-meta')?.textContent || '';
        const matchesRole = !filterRole || rolesText.toLowerCase().includes(filterRole.toLowerCase());

        if (matchesSearch && matchesRole) {
            item.style.display = '';
            visibleCount++;
        } else {
            item.style.display = 'none';
        }
    });

    // Show "no results" message
    updateNoResultsMessage(listEl, visibleCount, 'people');
}

// Filter events list
function filterEvents(searchTerm, filterType = null, filterDateRange = null) {
    const listEl = document.getElementById('admin-events-list');
    if (!listEl) return;

    const items = listEl.querySelectorAll('.admin-item, .event-item');
    let visibleCount = 0;

    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        const matchesSearch = searchTerm === '' || text.includes(searchTerm.toLowerCase());

        // Type filter (if event type is displayed)
        const matchesType = !filterType || text.includes(filterType.toLowerCase());

        // Date range filter (if needed)
        let matchesDate = true;
        if (filterDateRange) {
            const dateText = item.querySelector('.admin-item-meta, .event-date')?.textContent || '';
            // Simple date matching - can be enhanced
            matchesDate = dateText !== '';
        }

        if (matchesSearch && matchesType && matchesDate) {
            item.style.display = '';
            visibleCount++;
        } else {
            item.style.display = 'none';
        }
    });

    updateNoResultsMessage(listEl, visibleCount, 'events');
}

// Filter schedules/solutions list
function filterSchedules(searchTerm) {
    const listEl = document.getElementById('admin-solutions-list');
    if (!listEl) return;

    const items = listEl.querySelectorAll('.admin-item, .schedule-item');
    let visibleCount = 0;

    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        const matchesSearch = searchTerm === '' || text.includes(searchTerm.toLowerCase());

        if (matchesSearch) {
            item.style.display = '';
            visibleCount++;
        } else {
            item.style.display = 'none';
        }
    });

    updateNoResultsMessage(listEl, visibleCount, 'schedules');
}

// Update "no results" message
function updateNoResultsMessage(container, visibleCount, itemType) {
    // Remove existing message
    const existingMsg = container.querySelector('.no-results-message');
    if (existingMsg) {
        existingMsg.remove();
    }

    // Add message if no results
    if (visibleCount === 0) {
        const msg = document.createElement('div');
        msg.className = 'no-results-message';
        msg.style.cssText = `
            padding: 40px 20px;
            text-align: center;
            color: #6b7280;
            font-size: 14px;
        `;
        msg.innerHTML = `
            <div style="font-size: 48px; margin-bottom: 16px;">🔍</div>
            <div style="font-size: 16px; font-weight: 500; margin-bottom: 8px;">No ${itemType} found</div>
            <div>Try adjusting your search terms</div>
        `;
        container.appendChild(msg);
    }
}

// Create search bar component
function createSearchBar(containerId, onSearchCallback, placeholder = 'Search...') {
    const container = document.getElementById(containerId);
    if (!container) return null;

    // Check if search bar already exists
    let searchBar = container.querySelector('.search-bar');
    if (searchBar) return searchBar.querySelector('input');

    // Create search bar
    searchBar = document.createElement('div');
    searchBar.className = 'search-bar';
    searchBar.style.cssText = `
        margin-bottom: 16px;
        position: relative;
    `;

    const input = document.createElement('input');
    input.type = 'text';
    input.placeholder = placeholder;
    input.className = 'search-input';
    input.style.cssText = `
        width: 100%;
        padding: 10px 40px 10px 12px;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        font-size: 14px;
        box-sizing: border-box;
    `;

    const icon = document.createElement('span');
    icon.innerHTML = '🔍';
    icon.style.cssText = `
        position: absolute;
        right: 12px;
        top: 50%;
        transform: translateY(-50%);
        pointer-events: none;
        opacity: 0.5;
    `;

    searchBar.appendChild(input);
    searchBar.appendChild(icon);

    // Add to container at the top
    container.insertBefore(searchBar, container.firstChild);

    // Add debounced search listener
    const debouncedSearch = debounce((value) => {
        onSearchCallback(value);
    }, 300);

    input.addEventListener('input', (e) => {
        debouncedSearch(e.target.value);
    });

    return input;
}

// Create filter dropdown
function createFilterDropdown(containerId, options, onFilterCallback, label = 'Filter:') {
    const container = document.getElementById(containerId);
    if (!container) return null;

    // Check if filter already exists
    let filterBar = container.querySelector('.filter-bar');
    if (filterBar) return filterBar.querySelector('select');

    filterBar = document.createElement('div');
    filterBar.className = 'filter-bar';
    filterBar.style.cssText = `
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    `;

    const labelEl = document.createElement('label');
    labelEl.textContent = label;
    labelEl.style.cssText = `
        font-size: 14px;
        font-weight: 500;
        color: #374151;
    `;

    const select = document.createElement('select');
    select.className = 'filter-select';
    select.style.cssText = `
        padding: 8px 12px;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        font-size: 14px;
        cursor: pointer;
    `;

    // Add options
    const allOption = document.createElement('option');
    allOption.value = '';
    allOption.textContent = i18n ? i18n.t('common.labels.all') : 'All';
    select.appendChild(allOption);

    options.forEach(opt => {
        const option = document.createElement('option');
        option.value = opt.value || opt;
        option.textContent = opt.label || opt;
        select.appendChild(option);
    });

    filterBar.appendChild(labelEl);
    filterBar.appendChild(select);

    // Add to container
    const searchBar = container.querySelector('.search-bar');
    if (searchBar) {
        container.insertBefore(filterBar, searchBar.nextSibling);
    } else {
        container.insertBefore(filterBar, container.firstChild);
    }

    select.addEventListener('change', (e) => {
        onFilterCallback(e.target.value);
    });

    return select;
}

// Setup search and filter for admin people list
function setupPeopleSearchFilter() {
    createSearchBar('admin-people-list', (searchTerm) => {
        filterPeople(searchTerm);
    }, 'Search people by name or email...');

    createFilterDropdown('admin-people-list', [
        'volunteer', 'leader', 'musician', 'tech', 'admin'
    ], (role) => {
        const searchInput = document.querySelector('#admin-people-list .search-input');
        const searchTerm = searchInput ? searchInput.value : '';
        filterPeople(searchTerm, role);
    }, 'Role:');
}

// Setup search and filter for admin events list
function setupEventsSearchFilter() {
    createSearchBar('admin-events-list', (searchTerm) => {
        filterEvents(searchTerm);
    }, 'Search events by type or date...');

    createFilterDropdown('admin-events-list', [
        'Sunday Service', 'Worship Service', 'Bible Study', 'Prayer Meeting'
    ], (type) => {
        const searchInput = document.querySelector('#admin-events-list .search-input');
        const searchTerm = searchInput ? searchInput.value : '';
        filterEvents(searchTerm, type);
    }, 'Type:');
}

// Setup search for schedules
function setupSchedulesSearchFilter() {
    createSearchBar('admin-solutions-list', (searchTerm) => {
        filterSchedules(searchTerm);
    }, 'Search schedules...');
}

// Export functions
window.searchFilter = {
    filterPeople,
    filterEvents,
    filterSchedules,
    createSearchBar,
    createFilterDropdown,
    setupPeopleSearchFilter,
    setupEventsSearchFilter,
    setupSchedulesSearchFilter,
};
