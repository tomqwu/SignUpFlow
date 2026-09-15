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

    // Delete Organization
    //
    // Hard-delete the authenticated admin's organization and related data.
    //
    //Future deleteOrganization(String orgId) async
    test('test deleteOrganization', () async {
      // TODO
    });

    // Get Organization
    //
    // Read the authenticated member's organization only.
    //
    //Future<OrganizationResponse> getOrganization(String orgId) async
    test('test getOrganization', () async {
      // TODO
    });

    // List Organizations
    //
    // List only the caller's organization. Excludes cancelled by default.
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
    // Update the authenticated admin's organization and record the actor.
    //
    //Future<OrganizationResponse> updateOrganization(String orgId, OrganizationUpdate organizationUpdate) async
    test('test updateOrganization', () async {
      // TODO
    });

  });
}
