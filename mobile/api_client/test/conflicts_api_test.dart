import 'package:test/test.dart';
import 'package:signupflow_api/signupflow_api.dart';


/// tests for ConflictsApi
void main() {
  final instance = SignupflowApi().getConflictsApi();

  group(ConflictsApi, () {
    // Check Conflicts
    //
    // Check for scheduling conflicts before assigning a person to an event.  Detects: - Already assigned to this event - Time-off periods overlapping with event - Double-booked (assigned to another event at the same time)
    //
    //Future<ConflictCheckResponse> checkConflicts(ConflictCheckRequest conflictCheckRequest) async
    test('test checkConflicts', () async {
      // TODO
    });

    // List Conflicts
    //
    // List currently-detected conflicts across an org (admin-only).  Scans every Assignment in the org (or just the named person's) and surfaces `time_off` and `double_booked` conflicts. `already_assigned` is intentionally omitted because the assignment exists.
    //
    //Future<ListResponseConflictType> listConflicts(String orgId, { String personId, int limit, int offset }) async
    test('test listConflicts', () async {
      // TODO
    });

  });
}
