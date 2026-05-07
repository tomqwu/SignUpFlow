// Availability screen widget test — overrides availabilityProvider with
// fake data, asserts the calendar grid + time-off list + the
// "coming soon" recurring-rules panel render.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:signupflow_mobile/features/volunteer/availability_provider.dart';
import 'package:signupflow_mobile/features/volunteer/availability_screen.dart';
import 'package:signupflow_mobile/theme/theme.dart';

AvailabilityData _data() => AvailabilityData(entries: [
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
    ]);

void main() {
  testWidgets('availability renders calendar + time-off list + rrule callout',
      (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          availabilityProvider.overrideWith((ref) async => _data()),
        ],
        child: MaterialApp(
          theme: buildBlockMonoTheme(),
          home: const AvailabilityScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('AVAILABILITY'), findsOneWidget);
    expect(find.text('2 BLOCKED'), findsOneWidget);
    expect(find.text('Family trip'), findsOneWidget);
    expect(find.text('COMING SOON'), findsOneWidget);
  });

  testWidgets('empty time-off shows the empty state copy', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          availabilityProvider.overrideWith(
            (ref) async => const AvailabilityData(entries: []),
          ),
        ],
        child: MaterialApp(
          theme: buildBlockMonoTheme(),
          home: const AvailabilityScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.textContaining('No time off scheduled'), findsOneWidget);
    expect(find.text('0 BLOCKED'), findsOneWidget);
  });
}
