import 'package:test/test.dart';
import 'package:signupflow_api/signupflow_api.dart';


/// tests for AssignmentsApi
void main() {
  final instance = SignupflowApi().getAssignmentsApi();

  group(AssignmentsApi, () {
    // Accept Assignment
    //
    // Record the caller's explicit acceptance of the current commitment.
    //
    //Future<AssignmentResponse> acceptAssignment(int assignmentId, { int expectedRevision }) async
    test('test acceptAssignment', () async {
      // TODO
    });

    // Decline Assignment
    //
    // Decline the caller's assignment with a reason.
    //
    //Future<AssignmentResponse> declineAssignment(int assignmentId, AssignmentDeclineRequest assignmentDeclineRequest) async
    test('test declineAssignment', () async {
      // TODO
    });

    // List My Assignments
    //
    // Return assignments belonging to the caller, scoped to their org via the join.
    //
    //Future<ListResponseAssignmentResponse> listMyAssignments({ int limit, int offset }) async
    test('test listMyAssignments', () async {
      // TODO
    });

    // Request Swap
    //
    // Record that the caller needs a replacement for the current commitment.
    //
    //Future<AssignmentResponse> requestSwap(int assignmentId, AssignmentSwapRequest assignmentSwapRequest) async
    test('test requestSwap', () async {
      // TODO
    });

  });
}
