// Solver mutation + last-solve memoization — Sprint 7.9.

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/api/api_client.dart';
import 'package:signupflow_mobile/auth/auth_provider.dart';
import 'package:signupflow_mobile/features/admin/dashboard_provider.dart';

class SolverState {
  const SolverState({
    this.busy = false,
    this.lastSolutionId,
    this.lastError,
  });
  final bool busy;
  final int? lastSolutionId;
  final String? lastError;

  SolverState copyWith({
    bool? busy,
    int? lastSolutionId,
    String? lastError,
  }) =>
      SolverState(
        busy: busy ?? this.busy,
        lastSolutionId: lastSolutionId ?? this.lastSolutionId,
        lastError: lastError ?? this.lastError,
      );
}

class SolverController extends Notifier<SolverState> {
  @override
  SolverState build() => const SolverState();

  Future<int?> run({
    required DateTime fromDate,
    required DateTime toDate,
    required bool changeMin,
    required String mode,
  }) async {
    final orgId = ref.read(authProvider).orgId;
    if (orgId == null) {
      state = state.copyWith(lastError: 'Not signed in');
      return null;
    }
    state = const SolverState(busy: true);
    try {
      final body = (api.SolveRequestBuilder()
            ..orgId = orgId
            ..fromDate = api.Date(fromDate.year, fromDate.month, fromDate.day)
            ..toDate = api.Date(toDate.year, toDate.month, toDate.day)
            ..mode = mode
            ..changeMin = changeMin)
          .build();
      final res = await ref
          .read(signupflowApiProvider)
          .getSolverApi()
          .solveSchedule(solveRequest: body);
      final solutionId = res.data?.solutionId;
      ref.invalidate(dashboardProvider);
      state = SolverState(busy: false, lastSolutionId: solutionId);
      return solutionId;
    } on Exception catch (e) {
      state = SolverState(busy: false, lastError: e.toString());
      return null;
    }
  }
}

final solverControllerProvider =
    NotifierProvider<SolverController, SolverState>(SolverController.new);

class SolutionDetailData {
  const SolutionDetailData({
    required this.solution,
    required this.stats,
  });
  final api.SolutionResponse solution;
  final api.SolutionStatsResponse? stats;
}

final solutionDetailProvider =
    FutureProvider.family<SolutionDetailData, int>((ref, id) async {
  final apiClient = ref.watch(signupflowApiProvider);
  final futures = await Future.wait([
    apiClient.getSolutionsApi().getSolution(solutionId: id),
    apiClient.getSolutionsApi().getSolutionStats(solutionId: id).then(
          (r) => r,
          onError: (Object _) => null,
        ),
  ]);
  final sol = (futures[0] as dynamic).data as api.SolutionResponse?;
  if (sol == null) {
    throw StateError('Empty /solutions/$id response');
  }
  final stats = (futures[1] as dynamic)?.data as api.SolutionStatsResponse?;
  return SolutionDetailData(solution: sol, stats: stats);
});
