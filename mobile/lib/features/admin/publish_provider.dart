// Publish / unpublish / rollback flow — Sprint 7.10.

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/api/api_client.dart';
import 'package:signupflow_mobile/features/admin/dashboard_provider.dart';
import 'package:signupflow_mobile/features/admin/solver_provider.dart';

class PublishMutationsController extends Notifier<bool> {
  @override
  bool build() => false;

  Future<String?> publish(int solutionId) async => _wrap(() async {
        await ref
            .read(signupflowApiProvider)
            .getSolutionsApi()
            .publishSolution(solutionId: solutionId);
      }, solutionId);

  Future<String?> unpublish(int solutionId) async => _wrap(() async {
        await ref
            .read(signupflowApiProvider)
            .getSolutionsApi()
            .unpublishSolution(solutionId: solutionId);
      }, solutionId);

  Future<String?> rollback(int solutionId) async => _wrap(() async {
        await ref
            .read(signupflowApiProvider)
            .getSolutionsApi()
            .rollbackSolution(solutionId: solutionId);
      }, solutionId);

  Future<String?> _wrap(Future<void> Function() body, int solutionId) async {
    state = true;
    try {
      await body();
      ref
        ..invalidate(dashboardProvider)
        ..invalidate(solutionDetailProvider(solutionId));
      state = false;
      return null;
    } on Exception catch (e) {
      state = false;
      return e.toString();
    }
  }
}

final publishMutationsProvider =
    NotifierProvider<PublishMutationsController, bool>(
  PublishMutationsController.new,
);

/// Light-weight provider for the most-recent few solutions (used by both
/// the publish picker and the rollback history list). Reuses the same
/// listSolutions call the dashboard does, but here scoped to the publish
/// screen so refresh is local.
final recentSolutionsProvider =
    FutureProvider<List<api.SolutionResponse>>((ref) async {
  final dashboard = await ref.watch(dashboardProvider.future);
  return dashboard.recentSolutions;
});
