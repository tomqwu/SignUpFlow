// People + Events screen widget tests.

import 'package:built_collection/built_collection.dart';
import 'package:built_value/json_object.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/features/admin/events_provider.dart';
import 'package:signupflow_mobile/features/admin/events_screen.dart';
import 'package:signupflow_mobile/features/admin/people_provider.dart';
import 'package:signupflow_mobile/features/admin/people_screen.dart';
import 'package:signupflow_mobile/theme/theme.dart';

api.PersonResponse _person({
  required String id,
  required String name,
  required String email,
  required List<String> roles,
}) =>
    (api.PersonResponseBuilder()
          ..id = id
          ..name = name
          ..email = email
          ..orgId = 'hcc'
          ..language = 'en'
          ..timezone = 'UTC'
          ..roles = ListBuilder<String>(roles)
          ..createdAt = DateTime(2026, 5, 1).toUtc()
          ..updatedAt = DateTime(2026, 5, 1).toUtc()
          ..extraData = MapBuilder<String, JsonObject?>())
        .build();

api.EventResponse _event({
  required String id,
  required String type,
  required DateTime start,
}) =>
    (api.EventResponseBuilder()
          ..id = id
          ..orgId = 'hcc'
          ..type = type
          ..startTime = start.toUtc()
          ..endTime = start.add(const Duration(hours: 1)).toUtc()
          ..createdAt = DateTime(2026, 5, 1).toUtc()
          ..updatedAt = DateTime(2026, 5, 1).toUtc()
          ..extraData = MapBuilder<String, JsonObject?>())
        .build();

void main() {
  testWidgets('people screen renders search + person rows', (tester) async {
    final people = [
      _person(id: 'p1', name: 'Sarah Kowalski', email: 's@hcc.org', roles: ['volunteer']),
      _person(id: 'p2', name: 'James Park', email: 'j@hcc.org', roles: ['volunteer', 'admin']),
    ];
    await tester.pumpWidget(
      ProviderScope(
        overrides: [peopleProvider.overrideWith((ref) async => people)],
        child: MaterialApp(theme: buildBlockMonoTheme(), home: const PeopleScreen()),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('PEOPLE'), findsOneWidget);
    expect(find.textContaining('Search by name'), findsOneWidget);
    expect(find.text('Sarah Kowalski'), findsOneWidget);
    expect(find.text('James Park'), findsOneWidget);
    expect(find.text('VOLUNTEER'), findsAtLeastNWidgets(2));
    expect(find.text('ADMIN'), findsOneWidget);
  });

  testWidgets('events screen renders upcoming + recurring sections', (tester) async {
    final tomorrow = DateTime.now().add(const Duration(days: 1));
    final data = EventsData(
      events: [_event(id: 'e1', type: 'Sunday Service', start: tomorrow)],
      series: const [],
    );
    await tester.pumpWidget(
      ProviderScope(
        overrides: [eventsProvider.overrideWith((ref) async => data)],
        child: MaterialApp(theme: buildBlockMonoTheme(), home: const EventsScreen()),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('EVENTS'), findsOneWidget);
    // MonoLabel uppercases whatever is passed in, so the rendered text
    // is "UPCOMING · 1" / "RECURRING SERIES · 0".
    expect(find.textContaining('UPCOMING · 1'), findsOneWidget);
    expect(find.text('Sunday Service'), findsOneWidget);
    expect(find.textContaining('RECURRING SERIES · 0'), findsOneWidget);
  });
}
