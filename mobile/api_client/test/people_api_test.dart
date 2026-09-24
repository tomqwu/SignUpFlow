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

    // Deactivate Person
    //
    // Retire a departing member (admin only), keeping their history.  This is the departure path to prefer over ``DELETE``. A hard delete cascades through ``Person.assignments`` and erases completed work along with the future work, silently rewriting a published record. Deactivating keeps the row, so past assignments stay as history, while future live work is reopened exactly as a qualification removal would reopen it. ``get_current_user`` already rejects a non-active person, so their session and any further login stop working.
    //
    //Future<PersonResponse> deactivatePerson(String personId) async
    test('test deactivatePerson', () async {
      // TODO
    });

    // Delete Person
    //
    // Erase a person and all their work (admin only).  This removes completed history as well as future work, because ``Person.assignments`` cascades. Prefer ``POST /{person_id}/deactivate`` for someone who has simply left; keep this for genuine erasure requests.
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
