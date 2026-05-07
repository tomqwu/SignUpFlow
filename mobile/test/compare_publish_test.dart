// Compare + Publish widget tests.

import 'package:built_collection/built_collection.dart';
import 'package:built_value/json_object.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/features/admin/compare_screen.dart';
import 'package:signupflow_mobile/features/admin/publish_provider.dart';
import 'package:signupflow_mobile/features/admin/publish_screen.dart';
import 'package:signupflow_mobile/theme/theme.dart';

api.SolutionResponse _solution({
  required int id,
  required bool isPublished,
  DateTime? publishedAt,
  int health = 96,
}) =>
    (api.SolutionResponseBuilder()
          ..id = id
          ..orgId = 'hcc'
          ..solveMs = 274
          ..hardViolations = 0
          ..softScore = 1
          ..healthScore = health
          ..isPublished = isPublished
          ..publishedAt = publishedAt
          ..assignmentCount = 24
          ..createdAt = DateTime(2026, 5, 1).toUtc()
          ..metrics = MapBuilder<String, JsonObject?>())
        .build();

void main() {
  testWidgets('compare screen shows pickers when 2+ solutions exist',
      (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          recentSolutionsProvider.overrideWith((ref) async => [
                _solution(id: 142, isPublished: false),
                _solution(id: 141, isPublished: true, publishedAt: DateTime(2026, 5, 4)),
              ]),
        ],
        child: MaterialApp(theme: buildBlockMonoTheme(), home: const CompareScreen()),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('COMPARE'), findsOneWidget);
    expect(find.text('SOLUTION A'), findsOneWidget);
    expect(find.text('SOLUTION B'), findsOneWidget);
  });

  testWidgets('compare requires 2+ solutions, falls back gracefully',
      (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          recentSolutionsProvider.overrideWith(
            (ref) async => [_solution(id: 1, isPublished: false)],
          ),
        ],
        child: MaterialApp(theme: buildBlockMonoTheme(), home: const CompareScreen()),
      ),
    );
    await tester.pumpAndSettle();

    expect(
      find.textContaining('You need at least 2 solutions'),
      findsOneWidget,
    );
  });

  testWidgets('publish screen renders currently-published + drafts',
      (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          recentSolutionsProvider.overrideWith((ref) async => [
                _solution(id: 142, isPublished: false, health: 98),
                _solution(
                  id: 141,
                  isPublished: true,
                  publishedAt: DateTime(2026, 5, 4),
                  health: 96,
                ),
              ]),
        ],
        child: MaterialApp(theme: buildBlockMonoTheme(), home: const PublishScreen()),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('PUBLISH'), findsAtLeastNWidgets(1));
    expect(find.text('CURRENTLY PUBLISHED'), findsOneWidget);
    expect(find.text('Solution #141'), findsOneWidget);
    expect(find.text('Solution #142'), findsOneWidget);
    expect(find.text('UNPUBLISH'), findsOneWidget);
  });

  testWidgets('publish screen handles no published solution', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          recentSolutionsProvider.overrideWith(
            (ref) async => [_solution(id: 1, isPublished: false)],
          ),
        ],
        child: MaterialApp(theme: buildBlockMonoTheme(), home: const PublishScreen()),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.textContaining('No solution is published'), findsOneWidget);
  });
}
