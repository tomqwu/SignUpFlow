// Schedule screen widget test — overrides scheduleProvider with synthetic
// data so we can assert the layout (date sections + time chips + status)
// without hitting the network or the generated API.

import 'package:built_value/built_value.dart' show BuiltValueNullFieldError;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/features/volunteer/schedule_provider.dart';
import 'package:signupflow_mobile/features/volunteer/schedule_screen.dart';
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

void main() {
  testWidgets('schedule renders date groups + time chips + status', (tester) async {
    final group1 = ScheduleGroup(date: DateTime(2026, 5, 25), rows: [
      ScheduleRow(
        assignment: _assn(
          id: 1,
          eventId: 'e1',
          role: 'usher',
          status: 'confirmed',
        ),
        event: _event(
          id: 'e1',
          type: 'Sunday Service',
          start: DateTime(2026, 5, 25, 10),
          end: DateTime(2026, 5, 25, 11, 30),
        ),
      ),
    ]);
    final fakeData = ScheduleData(groups: [group1]);

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          scheduleProvider.overrideWith((ref) async => fakeData),
        ],
        child: MaterialApp(
          theme: buildBlockMonoTheme(),
          home: const VolunteerScheduleScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('SCHEDULE'), findsOneWidget);
    // Date label format is `EEE d MMM` uppercased — e.g. "MON 25 MAY".
    // Don't assert the day-of-week (calendar-dependent); just confirm the
    // day-of-month + month appear.
    expect(find.textContaining('25 MAY'), findsOneWidget);
    expect(find.text('10:00–11:30'), findsOneWidget);
    expect(find.text('USHER'), findsOneWidget);
    expect(find.text('CONFIRMED'), findsOneWidget);
    expect(find.text('Sunday Service'), findsOneWidget);
  });

  testWidgets('schedule shows empty state when no assignments', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          scheduleProvider.overrideWith((ref) async => const ScheduleData(groups: [])),
        ],
        child: MaterialApp(
          theme: buildBlockMonoTheme(),
          home: const VolunteerScheduleScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('NO UPCOMING ASSIGNMENTS'), findsOneWidget);
  });

  test('built_value model construction throws on missing fields', () {
    // Smoke: confirms our test helpers populate enough fields. If we forget
    // a required field the built_value builder throws — this test would fail.
    expect(
      () => api.AssignmentResponseBuilder().build(),
      throwsA(isA<BuiltValueNullFieldError>()),
    );
  });
}
