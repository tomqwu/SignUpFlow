import 'package:test/test.dart';
import 'package:signupflow_api/signupflow_api.dart';


/// tests for ConstraintsApi
void main() {
  final instance = SignupflowApi().getConstraintsApi();

  group(ConstraintsApi, () {
    // Create Constraint
    //
    // Create a new constraint (admin only, scoped to admin's org).
    //
    //Future<ConstraintResponse> createConstraint(ConstraintCreate constraintCreate) async
    test('test createConstraint', () async {
      // TODO
    });

    // Delete Constraint
    //
    // Delete constraint (admin only, scoped to admin's org).
    //
    //Future deleteConstraint(int constraintId) async
    test('test deleteConstraint', () async {
      // TODO
    });

    // Get Constraint
    //
    // Get constraint by ID; org isolation enforced.
    //
    //Future<ConstraintResponse> getConstraint(int constraintId) async
    test('test getConstraint', () async {
      // TODO
    });

    // List Constraints
    //
    // List constraints. Always scoped to the caller's organization.
    //
    //Future<ListResponseConstraintResponse> listConstraints({ String orgId, String constraintType, int limit, int offset }) async
    test('test listConstraints', () async {
      // TODO
    });

    // Update Constraint
    //
    // Update constraint (admin only, scoped to admin's org).
    //
    //Future<ConstraintResponse> updateConstraint(int constraintId, ConstraintUpdate constraintUpdate) async
    test('test updateConstraint', () async {
      // TODO
    });

  });
}
