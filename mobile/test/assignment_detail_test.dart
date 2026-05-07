// Assignment detail screen widget test — overrides scheduleProvider with
// fake data and confirms the detail screen finds the row by id and shows
// the action buttons.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/features/volunteer/assignment_detail_screen.dart';
import 'package:signupflow_mobile/features/volunteer/schedule_provider.dart';
import 'package:signupflow_mobile/theme/theme.dart';

api.AssignmentResponse _assn({
  required int id,
  required String eventId,
  required String role,
  required String status,
}) {
  return (api.AssignmentResponseBuilder()
        ..id = id
        ..eventId = eventId
        ..personId = 'me'
        ..role = role
        ..status = status
        ..assignedAt = DateTime(2026, 5, 1).toUtc())
      .build();
}

api.EventResponse _event({
  required String id,
  required String type,
  required DateTime start,
  required DateTime end,
}) {
  return (api.EventResponseBuilder()
        ..id = id
        ..orgId = 'hcc'
        ..type = type
        ..startTime = start.toUtc()
        ..endTime = end.toUtc()
        ..createdAt = DateTime(2026, 5, 1).toUtc()
        ..updatedAt = DateTime(2026, 5, 1).toUtc())
      .build();
}

ScheduleData _scheduleWithOneRow() {
  final row = ScheduleRow(
    assignment: _assn(id: 142, eventId: 'e1', role: 'usher', status: 'pending'),
    event: _event(
      id: 'e1',
      type: 'Sunday Service',
      start: DateTime(2026, 5, 25, 10),
      end: DateTime(2026, 5, 25, 11, 30),
    ),
  );
  return ScheduleData(
    groups: [ScheduleGroup(date: DateTime(2026, 5, 25), rows: [row])],
  );
}

void main() {
  testWidgets('detail finds row by id and renders actions', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          scheduleProvider.overrideWith((ref) async => _scheduleWithOneRow()),
        ],
        child: MaterialApp(
          theme: buildBlockMonoTheme(),
          home: const AssignmentDetailScreen(assignmentId: '142'),
        ),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('ASSIGNMENT'), findsOneWidget);
    expect(find.text('Sunday Service'), findsOneWidget);
    expect(find.text('USHER'), findsOneWidget);
    expect(find.text('PENDING'), findsOneWidget);
    expect(find.text('ACCEPT'), findsOneWidget);
    expect(find.text('SWAP'), findsOneWidget);
    expect(find.text('DECLINE'), findsOneWidget);
  });

  testWidgets('detail shows not-found when id is unknown', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          scheduleProvider.overrideWith((ref) async => _scheduleWithOneRow()),
        ],
        child: MaterialApp(
          theme: buildBlockMonoTheme(),
          home: const AssignmentDetailScreen(assignmentId: '999'),
        ),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('NOT FOUND'), findsOneWidget);
  });

  testWidgets('detail rejects non-numeric id', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          theme: buildBlockMonoTheme(),
          home: const AssignmentDetailScreen(assignmentId: 'banana'),
        ),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('Invalid assignment id'), findsOneWidget);
  });
}
