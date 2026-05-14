// Sprint 10 PR 10.4c — dark-mode regression test for segment toggles.
//
// Pins the contract: when the app is rendered under
// `themeMode: ThemeMode.dark`, the active segment pill in both
// SolutionReview and Solver must NOT be `Colors.white` — that's the
// bypass pattern Codex flagged and 10.4c is fixing. If anyone
// reintroduces the hardcode, these tests fail.

import 'package:built_collection/built_collection.dart';
import 'package:built_value/json_object.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/features/admin/solution_assignments_provider.dart';
import 'package:signupflow_mobile/features/admin/solution_review_screen.dart';
import 'package:signupflow_mobile/features/admin/solver_provider.dart';
import 'package:signupflow_mobile/features/admin/solver_screen.dart';
import 'package:signupflow_mobile/theme/colors.dart';
import 'package:signupflow_mobile/theme/theme.dart';

api.SolutionAssignmentsResponse _emptyAssignments(int id) {
  return (api.SolutionAssignmentsResponseBuilder()
        ..solutionId = id
        ..events = ListBuilder<api.SolutionAssignmentEntry>()
        ..totalAssignments = 0)
      .build();
}

api.SolutionResponse _solution() {
  return (api.SolutionResponseBuilder()
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
}

api.SolutionStatsResponse _stats() {
  return (api.SolutionStatsResponseBuilder()
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
}

Color? _activePillColor(WidgetTester tester, String label) {
  // Each segment renders the label inside a GestureDetector > Container.
  // Walk up from the label Text to find the Container with the active
  // pill color (the closest enclosing decorated Container).
  final container = tester
      .widgetList<Container>(
        find.ancestor(
          of: find.text(label),
          matching: find.byType(Container),
        ),
      )
      .firstWhere(
        (c) => c.decoration is BoxDecoration,
        orElse: Container.new,
      );
  final deco = container.decoration as BoxDecoration?;
  return deco?.color;
}

void main() {
  testWidgets(
    'SolutionReview active segment pill is not Colors.white in dark mode',
    (tester) async {
      final data = SolutionDetailData(solution: _solution(), stats: _stats());

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            solutionDetailProvider(142).overrideWith((ref) async => data),
            solutionAssignmentsProvider(142)
                .overrideWith((ref) async => _emptyAssignments(142)),
          ],
          child: MaterialApp(
            theme: buildBlockMonoTheme(),
            darkTheme: buildBlockMonoDarkTheme(),
            themeMode: ThemeMode.dark,
            home: const SolutionReviewScreen(solutionId: '142'),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Default segment is "assignments" — the ASSIGNMENTS label is the
      // active pill.
      final activeColor = _activePillColor(tester, 'ASSIGNMENTS');
      expect(activeColor, isNot(Colors.white),
          reason: '10.4c regression: active segment pill must follow theme');
      expect(activeColor, BlockColors.bgCardDark);
    },
  );

  testWidgets(
    'Solver active mode pill is not Colors.white in dark mode',
    (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            theme: buildBlockMonoTheme(),
            darkTheme: buildBlockMonoDarkTheme(),
            themeMode: ThemeMode.dark,
            home: const SolverScreen(),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Default mode is 'strict' — STRICT is the active pill.
      final activeColor = _activePillColor(tester, 'STRICT');
      expect(activeColor, isNot(Colors.white),
          reason: '10.4c regression: active mode pill must follow theme');
      expect(activeColor, BlockColors.bgCardDark);
    },
  );

  testWidgets(
    'SolutionReview active segment pill IS Colors.white in light mode',
    (tester) async {
      final data = SolutionDetailData(solution: _solution(), stats: _stats());

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            solutionDetailProvider(142).overrideWith((ref) async => data),
            solutionAssignmentsProvider(142)
                .overrideWith((ref) async => _emptyAssignments(142)),
          ],
          child: MaterialApp(
            theme: buildBlockMonoTheme(),
            home: const SolutionReviewScreen(solutionId: '142'),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Sanity check that the light-mode look is unchanged.
      expect(_activePillColor(tester, 'ASSIGNMENTS'), Colors.white);
    },
  );
}
