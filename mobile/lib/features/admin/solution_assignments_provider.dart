// Per-event assignments for a solution. Sprint 8.11.
//
// Wraps SolutionsApi.getSolutionAssignments (now typed as
// SolutionAssignmentsResponse thanks to Sprint 8.1 / #68).

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/api/api_client.dart';

final solutionAssignmentsProvider =
    FutureProvider.family<api.SolutionAssignmentsResponse, int>(
  (ref, solutionId) async {
    final apiClient = ref.watch(signupflowApiProvider);
    final res = await apiClient.getSolutionsApi().getSolutionAssignments(
          solutionId: solutionId,
        );
    final body = res.data;
    if (body == null) {
      throw StateError('Empty /solutions/$solutionId/assignments response');
    }
    return body;
  },
);
