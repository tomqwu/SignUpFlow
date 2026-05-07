// Solver + Solution Review widget tests.

import 'package:built_collection/built_collection.dart';
import 'package:built_value/json_object.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/features/admin/solution_review_screen.dart';
import 'package:signupflow_mobile/features/admin/solver_provider.dart';
import 'package:signupflow_mobile/features/admin/solver_screen.dart';
import 'package:signupflow_mobile/theme/theme.dart';

void main() {
  testWidgets('solver screen renders date range + mode + run button',
      (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(theme: buildBlockMonoTheme(), home: const SolverScreen()),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('RUN SOLVER'), findsOneWidget);
    expect(find.text('DATE RANGE'), findsOneWidget);
    expect(find.text('STRICT'), findsAtLeastNWidgets(1));
    expect(find.text('Minimize moves from published'), findsOneWidget);
    expect(find.text('RUN SOLVER →'), findsOneWidget);
  });

  testWidgets('solution review renders segmented control + assignments default',
      (tester) async {
    final solution = (api.SolutionResponseBuilder()
          ..id = 142
          ..orgId = 'hcc'
          ..solveMs = 274
          ..hardViolations = 0
          ..softScore = 1.5
          ..healthScore = 98
          ..isPublished = false
          ..assignmentCount = 24
          ..createdAt = DateTime(2026, 5, 7, 14, 14).toUtc()
          ..metrics = MapBuilder<String, JsonObject?>())
        .build();
    final stats = (api.SolutionStatsResponseBuilder()
          ..solutionId = 142
          ..fairness = (api.FairnessStatsBuilder()
            ..stdev = 0.42
            ..perPersonCounts = MapBuilder<String, int>({'p1': 1, 'p2': 2})
            ..histogram = MapBuilder<String, int>({'1': 1, '2': 1}))
          ..stability = (api.StabilityMetricsBuilder()
            ..movesFromPublished = 4
            ..affectedPersons = 2)
          ..workload = (api.WorkloadStatsBuilder()
            ..maxEventsPerPerson = 3
            ..minEventsPerPerson = 1
            ..medianEventsPerPerson = 2.0
            ..totalEventsAssigned = 8
            ..distinctPersonsAssigned = 4))
        .build();
    final data = SolutionDetailData(solution: solution, stats: stats);

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          solutionDetailProvider(142).overrideWith((ref) async => data),
        ],
        child: MaterialApp(
          theme: buildBlockMonoTheme(),
          home: const SolutionReviewScreen(solutionId: '142'),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('SOLUTION #142'), findsOneWidget);
    expect(find.text('ASSIGNMENTS'), findsOneWidget);
    expect(find.text('STATS'), findsOneWidget);
    expect(find.text('CONFLICTS'), findsOneWidget);
    expect(find.text('Solution #142'), findsOneWidget);
    expect(find.text('PUBLISH'), findsOneWidget);
    expect(find.text('COMPARE WITH ANOTHER SOLUTION'), findsOneWidget);
  });

  testWidgets('solution review STATS segment shows stability KPIs', (tester) async {
    final solution = (api.SolutionResponseBuilder()
          ..id = 142
          ..orgId = 'hcc'
          ..solveMs = 274
          ..hardViolations = 0
          ..softScore = 1.5
          ..healthScore = 98
          ..isPublished = false
          ..assignmentCount = 24
          ..createdAt = DateTime(2026, 5, 7, 14, 14).toUtc()
          ..metrics = MapBuilder<String, JsonObject?>())
        .build();
    final stats = (api.SolutionStatsResponseBuilder()
          ..solutionId = 142
          ..fairness = (api.FairnessStatsBuilder()
            ..stdev = 0.42
            ..perPersonCounts = MapBuilder<String, int>()
            ..histogram = MapBuilder<String, int>())
          ..stability = (api.StabilityMetricsBuilder()
            ..movesFromPublished = 4
            ..affectedPersons = 2)
          ..workload = (api.WorkloadStatsBuilder()
            ..maxEventsPerPerson = 3
            ..minEventsPerPerson = 1
            ..medianEventsPerPerson = 2.0
            ..totalEventsAssigned = 8
            ..distinctPersonsAssigned = 4))
        .build();
    final data = SolutionDetailData(solution: solution, stats: stats);

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          solutionDetailProvider(142).overrideWith((ref) async => data),
        ],
        child: MaterialApp(
          theme: buildBlockMonoTheme(),
          home: const SolutionReviewScreen(solutionId: '142'),
        ),
      ),
    );
    await tester.pumpAndSettle();

    // Tap STATS segment
    await tester.tap(find.text('STATS'));
    await tester.pumpAndSettle();

    expect(find.text('4'), findsOneWidget);     // movesFromPublished KPI
    expect(find.text('3'), findsOneWidget);     // max/person KPI
    expect(find.text('0.42'), findsOneWidget);  // stdev
  });
}
