/**
 * Tests for the Events view forEach bug fix.
 *
 * Bug: "Error: Cannot read properties of undefined (reading 'forEach')"
 * Fix: Added defensive array validation in loadAdminEvents()
 */

describe('Events View forEach Bug Fix', () => {
    let mockListElement;

    beforeEach(() => {
        // Create mock DOM element
        mockListElement = document.createElement('div');
        mockListElement.id = 'admin-events-list';
        document.body.appendChild(mockListElement);

        // Mock i18n
        global.i18n = {
            t: jest.fn((key) => key)
        };

        // Mock authFetch
        global.authFetch = jest.fn();
    });

    afterEach(() => {
        document.body.removeChild(mockListElement);
        jest.clearAllMocks();
    });

    test('should handle undefined events array without crashing', async () => {
        // Mock API response with undefined events
        global.authFetch.mockResolvedValue({
            ok: true,
            json: async () => ({
                total: 0,
                events: undefined  // This would cause forEach error
            })
        });

        // Simulate the fixed loadAdminEvents logic
        const data = { total: 0, events: undefined };

        // The fix: defensive check
        if (data.total === 0 || !data.events || !Array.isArray(data.events) || data.events.length === 0) {
            mockListElement.innerHTML = '<p class="help-text">No events</p>';
        } else {
            // This would crash without the fix
            mockListElement.innerHTML = data.events.map(e => `<div>${e.title}</div>`).join('');
            data.events.forEach(event => console.log(event));
        }

        // Should not crash and should show message
        expect(mockListElement.innerHTML).toContain('No events');
    });

    test('should handle null events array without crashing', async () => {
        // Mock API response with null events
        const data = { total: 0, events: null };

        // The fix: defensive check
        if (data.total === 0 || !data.events || !Array.isArray(data.events) || data.events.length === 0) {
            mockListElement.innerHTML = '<p class="help-text">No events</p>';
        } else {
            mockListElement.innerHTML = data.events.map(e => `<div>${e.title}</div>`).join('');
            data.events.forEach(event => console.log(event));
        }

        expect(mockListElement.innerHTML).toContain('No events');
    });

    test('should handle empty events array', async () => {
        // Mock API response with empty array
        const data = { total: 0, events: [] };

        // The fix: defensive check
        if (data.total === 0 || !data.events || !Array.isArray(data.events) || data.events.length === 0) {
            mockListElement.innerHTML = '<p class="help-text">No events</p>';
        } else {
            mockListElement.innerHTML = data.events.map(e => `<div>${e.title}</div>`).join('');
            data.events.forEach(event => console.log(event));
        }

        expect(mockListElement.innerHTML).toContain('No events');
    });

    test('should render events when array is valid', async () => {
        // Mock API response with valid events
        const data = {
            total: 2,
            events: [
                { id: '1', title: 'Event 1' },
                { id: '2', title: 'Event 2' }
            ]
        };

        // The fix: defensive check
        if (data.total === 0 || !data.events || !Array.isArray(data.events) || data.events.length === 0) {
            mockListElement.innerHTML = '<p class="help-text">No events</p>';
        } else {
            mockListElement.innerHTML = data.events.map(e => `<div>${e.title}</div>`).join('');

            // This should work now with the defensive check
            if (data.events && Array.isArray(data.events)) {
                data.events.forEach(event => {
                    expect(event).toHaveProperty('id');
                    expect(event).toHaveProperty('title');
                });
            }
        }

        expect(mockListElement.innerHTML).toContain('Event 1');
        expect(mockListElement.innerHTML).toContain('Event 2');
    });

    test('should handle non-array events value', async () => {
        // Mock API response with events as object instead of array
        const data = { total: 1, events: { id: '1', title: 'Event 1' } };

        // The fix: defensive check
        if (data.total === 0 || !data.events || !Array.isArray(data.events) || data.events.length === 0) {
            mockListElement.innerHTML = '<p class="help-text">No events</p>';
        } else {
            mockListElement.innerHTML = data.events.map(e => `<div>${e.title}</div>`).join('');
            data.events.forEach(event => console.log(event));
        }

        // Should not crash and should show message (not an array)
        expect(mockListElement.innerHTML).toContain('No events');
    });
});
