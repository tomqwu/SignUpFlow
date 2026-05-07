// Profile screen widget test — overrides profileProvider with synthetic
// PersonResponse + CalendarSubscriptionResponse and asserts the avatar,
// settings rows, ICS card, and log-out button render.

import 'package:built_collection/built_collection.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/features/volunteer/profile_provider.dart';
import 'package:signupflow_mobile/features/volunteer/profile_screen.dart';
import 'package:signupflow_mobile/theme/theme.dart';

api.PersonResponse _person() => (api.PersonResponseBuilder()
      ..id = 'p-sk'
      ..name = 'Sarah Kowalski'
      ..email = 'sarah.k@gmail.com'
      ..orgId = 'hcc'
      ..language = 'en'
      ..timezone = 'America/Los_Angeles'
      ..roles = ListBuilder<String>(['volunteer'])
      ..createdAt = DateTime(2026, 5, 1).toUtc()
      ..updatedAt = DateTime(2026, 5, 1).toUtc())
    .build();

api.CalendarSubscriptionResponse _sub() => (api.CalendarSubscriptionResponseBuilder()
      ..httpsUrl = 'https://api.signupflow.app/calendar/abc-123/ics'
      ..webcalUrl = 'webcal://api.signupflow.app/calendar/abc-123/ics'
      ..token = 'abc-123'
      ..message = 'OK')
    .build();

void main() {
  testWidgets('profile renders person + ICS card + settings', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          profileProvider.overrideWith(
            (ref) async => ProfileData(person: _person(), subscription: _sub()),
          ),
        ],
        child: MaterialApp(
          theme: buildBlockMonoTheme(),
          home: const VolunteerProfileScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('PROFILE'), findsOneWidget);
    expect(find.text('Sarah Kowalski'), findsOneWidget);
    expect(find.text('SARAH.K@GMAIL.COM'), findsOneWidget);
    expect(find.text('HCC'), findsOneWidget);
    expect(find.text('Copy URL'.toUpperCase()), findsOneWidget);
    expect(find.text('Reset token'.toUpperCase()), findsOneWidget);
    expect(find.text('English'), findsOneWidget);
    expect(find.text('LOG OUT'), findsOneWidget);
  });

  testWidgets('profile without subscription falls back gracefully', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          profileProvider.overrideWith(
            (ref) async => ProfileData(person: _person()),
          ),
        ],
        child: MaterialApp(
          theme: buildBlockMonoTheme(),
          home: const VolunteerProfileScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.textContaining('Calendar export unavailable'), findsOneWidget);
    expect(find.text('LOG OUT'), findsOneWidget);
  });
}
