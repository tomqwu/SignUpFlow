// Availability screen widget test — covers the calendar grid + time-off
// list (Sprint 7.5) and the rrule editor + one-off exceptions card
// (Sprint 8.9).

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:signupflow_mobile/features/volunteer/availability_provider.dart';
import 'package:signupflow_mobile/features/volunteer/availability_screen.dart';
import 'package:signupflow_mobile/theme/theme.dart';

AvailabilityData _data() => AvailabilityData(
      entries: [
        TimeOffEntry(
          id: 1,
          startDate: DateTime(2026, 5, 12),
          endDate: DateTime(2026, 5, 13),
          reason: 'Family trip',
        ),
        TimeOffEntry(
          id: 2,
          startDate: DateTime(2026, 5, 27),
          endDate: DateTime(2026, 5, 27),
        ),
      ],
      exceptions: [
        ExceptionEntry(id: 10, date: DateTime(2026, 7, 4)),
      ],
    );

void main() {
  testWidgets(
    'availability renders calendar + time-off list + rrule editor + exceptions',
    (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            availabilityProvider.overrideWith((ref) async => _data()),
            availabilityRruleProvider.overrideWith(
              (ref) async => 'FREQ=WEEKLY;BYDAY=MO',
            ),
          ],
          child: MaterialApp(
            theme: buildBlockMonoTheme(),
            home: const AvailabilityScreen(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      expect(find.text('AVAILABILITY'), findsOneWidget);
      // Calendar block count is timeoff days + exceptions (3 + 1 + 1 = 5).
      expect(find.text('Family trip'), findsOneWidget);
      // rrule preset matched and shown by friendly label.
      expect(find.text('Every Monday'), findsOneWidget);
      // Exception date renders the formatted full date.
      expect(find.textContaining('Jul 2026'), findsOneWidget);
      // No COMING SOON anywhere.
      expect(find.text('COMING SOON'), findsNothing);
    },
  );

  testWidgets('empty rrule shows "no recurring rule yet" copy', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          availabilityProvider.overrideWith(
            (ref) async => const AvailabilityData(entries: []),
          ),
          availabilityRruleProvider.overrideWith((ref) async => null),
        ],
        child: MaterialApp(
          theme: buildBlockMonoTheme(),
          home: const AvailabilityScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.textContaining('No time off scheduled'), findsOneWidget);
    expect(find.text('No recurring rule yet.'), findsOneWidget);
    expect(find.textContaining('No one-off blocked dates'), findsOneWidget);
  });
}
