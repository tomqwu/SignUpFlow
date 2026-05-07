import 'package:test/test.dart';
import 'package:signupflow_api/signupflow_api.dart';


/// tests for AssignmentsApi
void main() {
  final instance = SignupflowApi().getAssignmentsApi();

  group(AssignmentsApi, () {
    // Accept Assignment
    //
    // Mark the caller's assignment as confirmed.
    //
    //Future<AssignmentResponse> acceptAssignment(int assignmentId) async
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
    // Flag the caller's assignment for swap; admin follows up out of band.
    //
    //Future<AssignmentResponse> requestSwap(int assignmentId, AssignmentSwapRequest assignmentSwapRequest) async
    test('test requestSwap', () async {
      // TODO
    });

  });
}
