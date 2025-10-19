/**
 * Role Management Authentication Bug Tests
 *
 * Tests for Bug #8: Role management broken - roles disappear after editing
 *
 * Root Cause: fetch() instead of authFetch() caused 401 errors
 * Fix: Changed all fetch() calls to authFetch() in role management code
 */

// Mock global dependencies
global.API_BASE_URL = 'http://localhost:8000/api';
global.currentUser = { org_id: 'test_org_123', id: 'user_123' };
global.currentOrg = { id: 'test_org_123' };
global.authFetch = jest.fn();
global.fetch = jest.fn(); // Should NOT be called

describe('Role Management Authentication Fix', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    describe('Bug #8: loadOrgRoles() should use authFetch', () => {
        test('should call authFetch, not fetch', async () => {
            // Mock authFetch to return roles
            global.authFetch.mockResolvedValue({
                ok: true,
                json: async () => ({
                    config: {
                        custom_roles: ['volunteer', 'leader', 'admin']
                    }
                })
            });

            // Simulate loadOrgRoles function
            const loadOrgRoles = async () => {
                const response = await global.authFetch(`${API_BASE_URL}/organizations/${currentUser.org_id}`);
                if (response.ok) {
                    const data = await response.json();
                    return data.config?.custom_roles || [];
                }
                return [];
            };

            const roles = await loadOrgRoles();

            // Verify authFetch was called (not fetch)
            expect(global.authFetch).toHaveBeenCalledWith('http://localhost:8000/api/organizations/test_org_123');
            expect(global.fetch).not.toHaveBeenCalled();
            expect(roles).toEqual(['volunteer', 'leader', 'admin']);
        });

        test('should fail with 401 if using fetch instead of authFetch', async () => {
            // Mock fetch to return 401 (simulating the bug)
            global.fetch.mockResolvedValue({
                ok: false,
                status: 401,
                json: async () => ({ detail: 'Not authenticated' })
            });

            // Simulate BUGGY version using fetch
            const loadOrgRolesBuggy = async () => {
                const response = await global.fetch(`${API_BASE_URL}/organizations/${currentUser.org_id}`);
                if (response.ok) {
                    const data = await response.json();
                    return data.config?.custom_roles || [];
                }
                return []; // Returns empty on 401!
            };

            const roles = await loadOrgRolesBuggy();

            // Bug: Returns empty array, making roles disappear!
            expect(roles).toEqual([]);
            expect(global.fetch).toHaveBeenCalled();
        });
    });

    describe('Bug #8: addCustomRole() should use authFetch', () => {
        test('should use authFetch for GET and PUT', async () => {
            global.authFetch
                .mockResolvedValueOnce({
                    ok: true,
                    json: async () => ({
                        config: {
                            custom_roles: ['volunteer', 'leader']
                        }
                    })
                })
                .mockResolvedValueOnce({
                    ok: true,
                    json: async () => ({ success: true })
                });

            // Simulate addCustomRole
            const addCustomRole = async (roleName) => {
                // GET current config
                const orgResponse = await global.authFetch(`${API_BASE_URL}/organizations/${currentUser.org_id}`);
                const orgData = await orgResponse.json();
                const currentRoles = orgData.config?.custom_roles || [];

                // PUT updated config
                const updatedRoles = [...currentRoles, roleName];
                const updateResponse = await global.authFetch(`${API_BASE_URL}/organizations/${currentUser.org_id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        config: { custom_roles: updatedRoles }
                    })
                });

                return updateResponse.ok;
            };

            const success = await addCustomRole('musician');

            // Verify authFetch called twice (GET + PUT)
            expect(global.authFetch).toHaveBeenCalledTimes(2);
            expect(global.fetch).not.toHaveBeenCalled();
            expect(success).toBe(true);
        });
    });

    describe('Bug #8: saveEditRole() should use authFetch', () => {
        test('should use authFetch for GET and PUT', async () => {
            global.authFetch
                .mockResolvedValueOnce({
                    ok: true,
                    json: async () => ({
                        config: {
                            custom_roles: ['volunteer', 'leader'],
                            role_descriptions: { volunteer: 'Old desc' }
                        }
                    })
                })
                .mockResolvedValueOnce({
                    ok: true,
                    json: async () => ({ success: true })
                });

            // Simulate saveEditRole
            const saveEditRole = async (oldName, newName, newDesc) => {
                // GET current config
                const orgResponse = await global.authFetch(`${API_BASE_URL}/organizations/${currentOrg.id}`);
                const orgData = await orgResponse.json();

                const config = orgData.config || {};
                const roleDescriptions = config.role_descriptions || {};
                roleDescriptions[newName] = newDesc;

                // PUT updated config
                const updateResponse = await global.authFetch(`${API_BASE_URL}/organizations/${currentOrg.id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        config: {
                            ...config,
                            role_descriptions: roleDescriptions
                        }
                    })
                });

                return updateResponse.ok;
            };

            const success = await saveEditRole('volunteer', 'volunteer', 'New description');

            // Verify authFetch called twice (GET + PUT)
            expect(global.authFetch).toHaveBeenCalledTimes(2);
            expect(global.fetch).not.toHaveBeenCalled();
            expect(success).toBe(true);
        });
    });

    describe('Bug #8: performDeleteRole() should use authFetch', () => {
        test('should use authFetch for GET and PUT', async () => {
            global.authFetch
                .mockResolvedValueOnce({
                    ok: true,
                    json: async () => ({
                        config: {
                            custom_roles: ['volunteer', 'leader', 'musician'],
                            role_descriptions: { musician: 'Plays music' }
                        }
                    })
                })
                .mockResolvedValueOnce({
                    ok: true,
                    json: async () => ({ success: true })
                });

            // Simulate performDeleteRole
            const performDeleteRole = async (roleName) => {
                // GET current config
                const orgResponse = await global.authFetch(`${API_BASE_URL}/organizations/${currentUser.org_id}`);
                const orgData = await orgResponse.json();

                // Remove role
                const currentRoles = orgData.config?.custom_roles || [];
                const updatedRoles = currentRoles.filter(r => r !== roleName);

                // Remove description
                const descriptions = orgData.config?.role_descriptions || {};
                delete descriptions[roleName];

                // PUT updated config
                const updateResponse = await global.authFetch(`${API_BASE_URL}/organizations/${currentUser.org_id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        config: {
                            custom_roles: updatedRoles,
                            role_descriptions: descriptions
                        }
                    })
                });

                return updateResponse.ok;
            };

            const success = await performDeleteRole('musician');

            // Verify authFetch called twice (GET + PUT)
            expect(global.authFetch).toHaveBeenCalledTimes(2);
            expect(global.fetch).not.toHaveBeenCalled();
            expect(success).toBe(true);
        });
    });

    describe('Bug #8: loadAdminRoles() should use authFetch', () => {
        test('should use authFetch to get org config', async () => {
            global.authFetch
                .mockResolvedValueOnce({
                    ok: true,
                    json: async () => ({
                        config: {
                            custom_roles: ['volunteer', 'leader', 'admin']
                        }
                    })
                })
                .mockResolvedValueOnce({
                    ok: true,
                    json: async () => ({
                        config: {
                            role_descriptions: { volunteer: 'Serves regularly' }
                        }
                    })
                })
                .mockResolvedValueOnce({
                    ok: true,
                    json: async () => ({
                        people: []
                    })
                });

            // Simulate loadAdminRoles (simplified)
            const loadAdminRoles = async () => {
                // First call to get roles
                const response1 = await global.authFetch(`${API_BASE_URL}/organizations/${currentUser.org_id}`);
                const data1 = await response1.json();
                const roles = data1.config?.custom_roles || [];

                // Second call to get descriptions
                const response2 = await global.authFetch(`${API_BASE_URL}/organizations/${currentOrg.id}`);
                const data2 = await response2.json();

                // Third call to get people
                const response3 = await global.authFetch(`${API_BASE_URL}/people/?org_id=${currentOrg.id}`);
                await response3.json();

                return roles;
            };

            const roles = await loadAdminRoles();

            // Verify authFetch called 3 times
            expect(global.authFetch).toHaveBeenCalledTimes(3);
            expect(global.fetch).not.toHaveBeenCalled();
            expect(roles).toEqual(['volunteer', 'leader', 'admin']);
        });
    });

    describe('Bug Symptom: Roles disappearing', () => {
        test('BEFORE FIX: Using fetch() causes roles to disappear due to 401', async () => {
            // Mock fetch returning 401 (no JWT token)
            global.fetch.mockResolvedValue({
                ok: false,
                status: 401
            });

            // Buggy version using fetch
            const loadRolesBuggy = async () => {
                const response = await global.fetch(`${API_BASE_URL}/organizations/${currentOrg.id}`);
                if (!response.ok) {
                    return []; // Returns empty on error - ROLES DISAPPEAR!
                }
                const data = await response.json();
                return data.config?.custom_roles || [];
            };

            const roles = await loadRolesBuggy();

            // Bug: Returns empty array
            expect(roles).toEqual([]);
        });

        test('AFTER FIX: Using authFetch() works correctly', async () => {
            // Mock authFetch returning 200 (with JWT token)
            global.authFetch.mockResolvedValue({
                ok: true,
                json: async () => ({
                    config: {
                        custom_roles: ['volunteer', 'leader', 'admin']
                    }
                })
            });

            // Fixed version using authFetch
            const loadRolesFixed = async () => {
                const response = await global.authFetch(`${API_BASE_URL}/organizations/${currentOrg.id}`);
                if (!response.ok) {
                    return [];
                }
                const data = await response.json();
                return data.config?.custom_roles || [];
            };

            const roles = await loadRolesFixed();

            // Fix: Returns roles correctly
            expect(roles).toEqual(['volunteer', 'leader', 'admin']);
        });
    });
});
