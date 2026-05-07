// Smoke test for the 7.1 skeleton: app boots, login screen renders,
// "demo · volunteer" shortcut routes into the volunteer schedule tab.

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:signupflow_mobile/app.dart';

void main() {
  testWidgets('app boots into login and demo-volunteer routes to schedule',
      (tester) async {
    await tester.pumpWidget(const ProviderScope(child: SignUpFlowApp()));
    await tester.pumpAndSettle();

    // Login screen renders the sign-in button + demo shortcut copy.
    // (Wordmark uses RichText so individual segments aren't findable
    // by `find.text` — assert via the demo shortcut label instead.)
    expect(find.text('SIGN IN'), findsOneWidget);
    expect(find.text('DEMO SHORTCUT'), findsOneWidget);

    // Demo shortcut → Volunteer.
    await tester.tap(find.text('VOLUNTEER'));
    await tester.pumpAndSettle();

    // Lands on the schedule tab — page title + bottom nav label visible.
    expect(find.text('SCHEDULE'), findsWidgets);
  });
}
