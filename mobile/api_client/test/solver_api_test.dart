import 'package:test/test.dart';
import 'package:signupflow_api/signupflow_api.dart';


/// tests for SolverApi
void main() {
  final instance = SignupflowApi().getSolverApi();

  group(SolverApi, () {
    // Solve Schedule
    //
    // Generate a schedule for the organization (admin only).  This endpoint: 1. Loads all org data from database 2. Runs the constraint solver 3. Saves the solution to database 4. Returns solution metrics and violations
    //
    //Future<SolveResponse> solveSchedule(SolveRequest solveRequest) async
    test('test solveSchedule', () async {
      // TODO
    });

  });
}
