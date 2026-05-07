import 'package:test/test.dart';
import 'package:signupflow_api/signupflow_api.dart';


/// tests for PeopleApi
void main() {
  final instance = SignupflowApi().getPeopleApi();

  group(PeopleApi, () {
    // Bulk Import People
    //
    // Admin-only bulk people import.  Strictly JSON-array body — no file upload (file uploads are Phase 2 scope). Validates each row, persists rows that don't already exist, and returns created/skipped counts plus a row-level error list.
    //
    //Future<BulkImportResponse> bulkImportPeople(String orgId, BuiltMap<String, JsonObject> requestBody) async
    test('test bulkImportPeople', () async {
      // TODO
    });

    // Create Person
    //
    // Create a new person (admin only).
    //
    //Future<PersonResponse> createPerson(PersonCreate personCreate) async
    test('test createPerson', () async {
      // TODO
    });

    // Delete Person
    //
    // Delete person (admin only).
    //
    //Future deletePerson(String personId) async
    test('test deletePerson', () async {
      // TODO
    });

    // Get Current Person
    //
    // Get the current authenticated user's profile.
    //
    //Future<PersonResponse> getCurrentPerson() async
    test('test getCurrentPerson', () async {
      // TODO
    });

    // Get Person
    //
    // Get person by ID. Users can only view people from their own organization.
    //
    //Future<PersonResponse> getPerson(String personId) async
    test('test getPerson', () async {
      // TODO
    });

    // List People
    //
    // List people. Users can only see people from their own organization.
    //
    //Future<ListResponsePersonResponse> listPeople({ String orgId, String role, String q, String status, int limit, int offset }) async
    test('test listPeople', () async {
      // TODO
    });

    // Update Current Person
    //
    // Update the current authenticated user's profile.
    //
    //Future<PersonResponse> updateCurrentPerson(PersonUpdate personUpdate) async
    test('test updateCurrentPerson', () async {
      // TODO
    });

    // Update Person
    //
    // Update person. Users can edit themselves, admins can edit anyone in their org.
    //
    //Future<PersonResponse> updatePerson(String personId, PersonUpdate personUpdate) async
    test('test updatePerson', () async {
      // TODO
    });

  });
}
