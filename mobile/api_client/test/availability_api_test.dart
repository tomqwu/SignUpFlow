import 'package:test/test.dart';
import 'package:signupflow_api/signupflow_api.dart';


/// tests for AvailabilityApi
void main() {
  final instance = SignupflowApi().getAvailabilityApi();

  group(AvailabilityApi, () {
    // Add Exception
    //
    // Add a single-date exception. Idempotent on (availability_id, date).
    //
    //Future<AvailabilityExceptionResponse> addException(String personId, AvailabilityExceptionCreate availabilityExceptionCreate) async
    test('test addException', () async {
      // TODO
    });

    // Add Timeoff
    //
    // Add a time-off period for a person.
    //
    //Future<JsonObject> addTimeoff(String personId, TimeOffCreate timeOffCreate) async
    test('test addTimeoff', () async {
      // TODO
    });

    // Clear Rrule
    //
    // Clear the rrule string for a person.  Idempotent — succeeds with 204 even if the row never had an rrule, or even if the Availability row doesn't exist yet.
    //
    //Future clearRrule(String personId) async
    test('test clearRrule', () async {
      // TODO
    });

    // Create Availability
    //
    // Create availability record for a person.
    //
    //Future<JsonObject> createAvailability(String personId) async
    test('test createAvailability', () async {
      // TODO
    });

    // Delete Exception
    //
    // Delete a single-date exception by id.
    //
    //Future deleteException(String personId, int exceptionId) async
    test('test deleteException', () async {
      // TODO
    });

    // Delete Timeoff
    //
    // Delete a time-off period.
    //
    //Future deleteTimeoff(String personId, int timeoffId) async
    test('test deleteTimeoff', () async {
      // TODO
    });

    // Get Rrule
    //
    // Return the single recurring-availability rrule for a person.  Returns ``rrule: null`` when the person has no Availability row or has not set an rrule. Mobile renders this as \"no recurring rule yet.\"
    //
    //Future<AvailabilityRruleResponse> getRrule(String personId) async
    test('test getRrule', () async {
      // TODO
    });

    // Get Timeoff
    //
    // Get all time-off periods for a person.
    //
    //Future<JsonObject> getTimeoff(String personId) async
    test('test getTimeoff', () async {
      // TODO
    });

    // List Exceptions
    //
    // List single-date availability exceptions for a person.
    //
    //Future<BuiltList<AvailabilityExceptionResponse>> listExceptions(String personId) async
    test('test listExceptions', () async {
      // TODO
    });

    // Set Rrule
    //
    // Set (or replace) the rrule string for a person.
    //
    //Future<AvailabilityRruleResponse> setRrule(String personId, AvailabilityRruleUpdate availabilityRruleUpdate) async
    test('test setRrule', () async {
      // TODO
    });

    // Update Timeoff
    //
    // Update a time-off period.
    //
    //Future<JsonObject> updateTimeoff(String personId, int timeoffId, TimeOffCreate timeOffCreate) async
    test('test updateTimeoff', () async {
      // TODO
    });

  });
}
