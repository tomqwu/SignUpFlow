// Admin dashboard widget test — overrides dashboardProvider with synthetic
// data and asserts KPI grid + recent solutions list + quick action row.

import 'package:built_collection/built_collection.dart';
import 'package:built_value/json_object.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/features/admin/dashboard_provider.dart';
import 'package:signupflow_mobile/features/admin/dashboard_screen.dart';
import 'package:signupflow_mobile/theme/theme.dart';

api.SolutionResponse _solution({
  required int id,
  required bool isPublished,
  required int health,
}) {
  return (api.SolutionResponseBuilder()
        ..id = id
        ..orgId = 'hcc'
        ..solveMs = 274
        ..hardViolations = 0
        ..softScore = 1
        ..healthScore = health
        ..createdAt = DateTime(2026, 5, 7, 14, 14).toUtc()
        ..isPublished = isPublished
        ..publishedAt = isPublished ? DateTime(2026, 5, 4).toUtc() : null
        ..assignmentCount = 24
        ..metrics = MapBuilder<String, JsonObject?>())
      .build();
}

void main() {
  testWidgets('dashboard renders KPI grid + recent solutions', (tester) async {
    final data = DashboardData(
      activeVolunteers: 47,
      eventsThisWeek: 12,
      healthScore: 98,
      publishedSolution: _solution(id: 141, isPublished: true, health: 96),
      publishedAt: DateTime(2026, 5, 4),
      recentSolutions: [
        _solution(id: 142, isPublished: false, health: 98),
        _solution(id: 141, isPublished: true, health: 96),
      ],
    );
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          dashboardProvider.overrideWith((ref) async => data),
        ],
        child: MaterialApp(
          theme: buildBlockMonoTheme(),
          home: const DashboardScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('DASHBOARD'), findsOneWidget);
    expect(find.text('47'), findsOneWidget);
    expect(find.text('12'), findsOneWidget);
    expect(find.text('98'), findsOneWidget);
    expect(find.text('Solution #142'), findsOneWidget);
    expect(find.text('DRAFT'), findsOneWidget);
    // Solution #141 appears twice: in the KPI card subtitle + in the
    // recent solutions list row.
    expect(find.text('Solution #141'), findsNWidgets(2));
    expect(find.text('LIVE'), findsAtLeastNWidgets(1));
    expect(find.text('RUN SOLVER'), findsOneWidget);
  });

  testWidgets('dashboard with no solutions shows empty copy', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          dashboardProvider.overrideWith((ref) async => const DashboardData(
                activeVolunteers: 0,
                eventsThisWeek: 0,
                healthScore: 0,
                publishedSolution: null,
                publishedAt: null,
                recentSolutions: [],
              )),
        ],
        child: MaterialApp(
          theme: buildBlockMonoTheme(),
          home: const DashboardScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('NONE LIVE'), findsOneWidget);
    expect(find.textContaining('No solutions yet'), findsOneWidget);
  });
}
