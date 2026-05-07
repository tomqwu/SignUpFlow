import 'package:test/test.dart';
import 'package:signupflow_api/signupflow_api.dart';


/// tests for ResourcesApi
void main() {
  final instance = SignupflowApi().getResourcesApi();

  group(ResourcesApi, () {
    // Create Resource
    //
    // Create a new resource (admin only, scoped to admin's org).
    //
    //Future<ResourceResponse> createResource(ResourceCreate resourceCreate) async
    test('test createResource', () async {
      // TODO
    });

    // Delete Resource
    //
    // Delete a resource (admin only).  Refuses with 409 if any Event still references the resource — preserves referential integrity without forcing the admin to discover dangling FKs by surprise.
    //
    //Future deleteResource(String resourceId) async
    test('test deleteResource', () async {
      // TODO
    });

    // Get Resource
    //
    // Get a single resource by id; tenancy enforced via the row's org_id.
    //
    //Future<ResourceResponse> getResource(String resourceId) async
    test('test getResource', () async {
      // TODO
    });

    // List Resources
    //
    // List resources for one organization. Caller must be a member.
    //
    //Future<ListResponseResourceResponse> listResources(String orgId, { String type, int limit, int offset }) async
    test('test listResources', () async {
      // TODO
    });

    // Update Resource
    //
    // Update a resource (admin only). org_id is immutable.
    //
    //Future<ResourceResponse> updateResource(String resourceId, ResourceUpdate resourceUpdate) async
    test('test updateResource', () async {
      // TODO
    });

  });
}
