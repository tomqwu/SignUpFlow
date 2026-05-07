import 'package:test/test.dart';
import 'package:signupflow_api/signupflow_api.dart';


/// tests for EventsApi
void main() {
  final instance = SignupflowApi().getEventsApi();

  group(EventsApi, () {
    // Create Event
    //
    // Create a new event (admin only).
    //
    //Future<EventResponse> createEvent(EventCreate eventCreate) async
    test('test createEvent', () async {
      // TODO
    });

    // Delete Event
    //
    // Delete event (admin only).
    //
    //Future deleteEvent(String eventId) async
    test('test deleteEvent', () async {
      // TODO
    });

    // Get All Assignments
    //
    // Get all assignments for an organization (both from solutions and manual).
    //
    //Future<JsonObject> getAllAssignments(String orgId) async
    test('test getAllAssignments', () async {
      // TODO
    });

    // Get Available People
    //
    // Get people available for this event based on roles.  Returns list of people who have matching roles, with flags indicating if they're already assigned or have blocked the event date.
    //
    //Future<BuiltList<AvailablePerson>> getAvailablePeople(String eventId) async
    test('test getAvailablePeople', () async {
      // TODO
    });

    // Get Event
    //
    // Get event by ID.
    //
    //Future<EventResponse> getEvent(String eventId) async
    test('test getEvent', () async {
      // TODO
    });

    // List Events
    //
    // List events with optional filters.
    //
    //Future<ListResponseEventResponse> listEvents({ String orgId, String eventType, DateTime startAfter, DateTime startBefore, String q, String status, int limit, int offset }) async
    test('test listEvents', () async {
      // TODO
    });

    // Manage Assignment
    //
    // Assign or unassign a person to/from an event (admin only).
    //
    //Future<JsonObject> manageAssignment(String eventId, AssignmentRequest assignmentRequest) async
    test('test manageAssignment', () async {
      // TODO
    });

    // Update Event
    //
    // Update event (admin only).
    //
    //Future<EventResponse> updateEvent(String eventId, EventUpdate eventUpdate) async
    test('test updateEvent', () async {
      // TODO
    });

    // Validate Event
    //
    // Validate if event has proper configuration and enough people.  Checks: 1. Event has role requirements configured 2. Enough people available for each role 3. No assigned people are blocked on the event date  Returns:     Dictionary with is_valid flag and list of validation warnings
    //
    //Future<BuiltMap<String, JsonObject>> validateEvent(String eventId) async
    test('test validateEvent', () async {
      // TODO
    });

  });
}
