import 'package:test/test.dart';
import 'package:signupflow_api/signupflow_api.dart';


/// tests for AvailabilityApi
void main() {
  final instance = SignupflowApi().getAvailabilityApi();

  group(AvailabilityApi, () {
    // Add Timeoff
    //
    // Add a time-off period for a person.
    //
    //Future<JsonObject> addTimeoff(String personId, TimeOffCreate timeOffCreate) async
    test('test addTimeoff', () async {
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

    // Delete Timeoff
    //
    // Delete a time-off period.
    //
    //Future deleteTimeoff(String personId, int timeoffId) async
    test('test deleteTimeoff', () async {
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
