// Admin dashboard data — Sprint 7.7.
//
// Combines:
//   AnalyticsApi.getVolunteerStats(org_id) → JsonObject (active volunteers + …)
//   AnalyticsApi.getScheduleHealth(org_id) → JsonObject (events, health, …)
//   SolutionsApi.listSolutions(org_id)     → list[SolutionResponse]
//
// The two analytics endpoints return JsonObject because the backend
// FastAPI handlers don't declare typed response models. We decode them
// manually with optional fields — missing keys fall back to safe defaults.

import 'dart:convert';

import 'package:built_value/json_object.dart' show JsonObject;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/api/api_client.dart';
import 'package:signupflow_mobile/auth/auth_provider.dart';

class DashboardData {
  const DashboardData({
    required this.activeVolunteers,
    required this.eventsThisWeek,
    required this.healthScore,
    required this.publishedSolution,
    required this.publishedAt,
    required this.recentSolutions,
  });

  final int activeVolunteers;
  final int eventsThisWeek;
  final num healthScore;
  final api.SolutionResponse? publishedSolution;
  final DateTime? publishedAt;
  final List<api.SolutionResponse> recentSolutions;
}

Map<String, dynamic>? _decodeJsonObject(JsonObject? obj) {
  if (obj == null) return null;
  final decoded = json.decode(obj.toString());
  return decoded is Map<String, dynamic> ? decoded : null;
}

final dashboardProvider = FutureProvider<DashboardData>((ref) async {
  final orgId = ref.watch(authProvider).orgId;
  if (orgId == null) {
    return const DashboardData(
      activeVolunteers: 0,
      eventsThisWeek: 0,
      healthScore: 0,
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
  final eventsThisWeek =
      (health['events_this_week'] as num?)?.toInt() ?? 0;
  final healthScore = (health['health_score'] as num?) ?? 0;

  api.SolutionResponse? published;
  for (final s in solList) {
    if (s.isPublished ?? false) {
      published = s;
      break;
    }
  }

  return DashboardData(
    activeVolunteers: activeVolunteers,
    eventsThisWeek: eventsThisWeek,
    healthScore: healthScore,
    publishedSolution: published,
    publishedAt: published?.publishedAt,
    recentSolutions: solList,
  );
});
