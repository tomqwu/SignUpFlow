import 'package:test/test.dart';
import 'package:signupflow_api/signupflow_api.dart';


/// tests for OrganizationsApi
void main() {
  final instance = SignupflowApi().getOrganizationsApi();

  group(OrganizationsApi, () {
    // Cancel Organization
    //
    // Soft-cancel the organization (admin only).  Sets `cancelled_at` to now and schedules a 30-day data-retention window via `data_retention_until`. The org is excluded from the default list until restored.
    //
    //Future<OrganizationResponse> cancelOrganization(String orgId) async
    test('test cancelOrganization', () async {
      // TODO
    });

    // Create Organization
    //
    // Create a new organization. Rate limited to 2 requests per hour per IP.  Automatically creates Free plan subscription with 10 volunteer limit.
    //
    //Future<OrganizationResponse> createOrganization(OrganizationCreate organizationCreate) async
    test('test createOrganization', () async {
      // TODO
    });

    // Delete Organization
    //
    // Delete organization and all related data.
    //
    //Future deleteOrganization(String orgId) async
    test('test deleteOrganization', () async {
      // TODO
    });

    // Get Organization
    //
    // Get organization by ID.
    //
    //Future<OrganizationResponse> getOrganization(String orgId) async
    test('test getOrganization', () async {
      // TODO
    });

    // List Organizations
    //
    // List all organizations. Excludes cancelled by default.
    //
    //Future<ListResponseOrganizationResponse> listOrganizations({ bool includeCancelled, String q, int limit, int offset }) async
    test('test listOrganizations', () async {
      // TODO
    });

    // Restore Organization
    //
    // Restore a cancelled organization (admin only). Clears cancellation fields.
    //
    //Future<OrganizationResponse> restoreOrganization(String orgId) async
    test('test restoreOrganization', () async {
      // TODO
    });

    // Update Organization
    //
    // Update organization.
    //
    //Future<OrganizationResponse> updateOrganization(String orgId, OrganizationUpdate organizationUpdate) async
    test('test updateOrganization', () async {
      // TODO
    });

  });
}
