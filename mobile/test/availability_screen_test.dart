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
      // BLOCKED header counts every day in blockedDays — 3 days from the
      // 2-day timeoff range (May 12-13) + 1 day from the single-day timeoff
      // (May 27) + 1 exception (Jul 4) = 4 distinct blocked days.
      expect(find.text('4 BLOCKED'), findsOneWidget);
      expect(find.text('Family trip'), findsOneWidget);
      // rrule preset matched and shown by friendly label.
      expect(find.text('Every Monday'), findsOneWidget);
      // Exception date renders the formatted full date.
      expect(find.textContaining('Jul 2026'), findsOneWidget);
      // No COMING SOON anywhere.
      expect(find.text('COMING SOON'), findsNothing);
    },
  );

  testWidgets(
    'BLOCKED header counts exception-only days (no time-off)',
    (tester) async {
      // Regression for Codex review on PR 8.9: header used to bind to
      // `entries.length`, which would say "0 BLOCKED" for a volunteer with
      // only single-date exceptions even though the calendar shaded those
      // days. Header must derive from blockedDays.
      final exceptionsOnly = AvailabilityData(
        entries: const [],
        exceptions: [
          ExceptionEntry(id: 1, date: DateTime(2026, 7, 4)),
          ExceptionEntry(id: 2, date: DateTime(2026, 7, 11)),
          ExceptionEntry(id: 3, date: DateTime(2026, 7, 18)),
        ],
      );
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            availabilityProvider.overrideWith((ref) async => exceptionsOnly),
            availabilityRruleProvider.overrideWith((ref) async => null),
          ],
          child: MaterialApp(
            theme: buildBlockMonoTheme(),
            home: const AvailabilityScreen(),
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.text('3 BLOCKED'), findsOneWidget);
      expect(find.text('0 BLOCKED'), findsNothing);
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
