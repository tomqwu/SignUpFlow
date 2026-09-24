// Admin dashboard data — Sprint 7.7.
//
// Combines:
//   AnalyticsApi.getVolunteerStats(org_id) → JsonObject (active volunteers + …)
//   AnalyticsApi.getScheduleHealth(org_id) → JsonObject (upcoming_events,
//                                            latest_solution.health_score, …)
//   SolutionsApi.listSolutions(org_id)     → list[SolutionResponse]
//
// The two analytics endpoints return JsonObject because the backend
// FastAPI handlers don't declare typed response models. We decode them
// manually with optional fields — missing keys fall back to safe defaults.

import 'package:built_value/json_object.dart' show JsonObject;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/api/api_client.dart';
import 'package:signupflow_mobile/auth/auth_provider.dart';

class DashboardData {
  const DashboardData({
    required this.activeVolunteers,
    required this.upcomingEvents,
    required this.healthScore,
    required this.publishedSolution,
    required this.publishedAt,
    required this.recentSolutions,
  });

  final int activeVolunteers;
  final int upcomingEvents;

  /// Health score of the org's most recent solution; null until the solver
  /// has produced one.
  final num? healthScore;
  final api.SolutionResponse? publishedSolution;
  final DateTime? publishedAt;
  final List<api.SolutionResponse> recentSolutions;
}

// The generated client wraps the already-decoded body in a MapJsonObject;
// its toString() is Dart map syntax, not JSON, so read the value directly.
Map<String, dynamic>? _decodeJsonObject(JsonObject? obj) {
  final value = obj?.value;
  return value is Map ? Map<String, dynamic>.from(value) : null;
}

final dashboardProvider = FutureProvider<DashboardData>((ref) async {
  final orgId = ref.watch(authProvider).orgId;
  if (orgId == null) {
    return const DashboardData(
      activeVolunteers: 0,
      upcomingEvents: 0,
      healthScore: null,
      publishedSolution: null,
      publishedAt: null,
      recentSolutions: [],
    );
  }

  final apiClient = ref.watch(signupflowApiProvider);

  final futures = await Future.wait([
    apiClient.getAnalyticsApi().getVolunteerStats(orgId: orgId),
    apiClient.getAnalyticsApi().getScheduleHealth(orgId: orgId),
    apiClient.getSolutionsApi().listSolutions(orgId: orgId, limit: 10),
  ]);

  final volStats =
      _decodeJsonObject((futures[0] as dynamic).data as JsonObject?) ?? {};
  final health =
      _decodeJsonObject((futures[1] as dynamic).data as JsonObject?) ?? {};
  final solList =
      ((futures[2] as dynamic).data as api.ListResponseSolutionResponse?)
          ?.items
          .toList() ??
          const <api.SolutionResponse>[];

  final activeVolunteers = (volStats['active_volunteers'] as num?)?.toInt() ??
      (volStats['total'] as num?)?.toInt() ??
      0;
  final upcomingEvents = (health['upcoming_events'] as num?)?.toInt() ?? 0;
  final latestSolution = health['latest_solution'];
  final healthScore = latestSolution is Map
      ? latestSolution['health_score'] as num?
      : null;

  api.SolutionResponse? published;
  for (final s in solList) {
    if (s.isPublished ?? false) {
      published = s;
      break;
    }
  }

  return DashboardData(
    activeVolunteers: activeVolunteers,
    upcomingEvents: upcomingEvents,
    healthScore: healthScore,
    publishedSolution: published,
    publishedAt: published?.publishedAt,
    recentSolutions: solList,
  );
});
