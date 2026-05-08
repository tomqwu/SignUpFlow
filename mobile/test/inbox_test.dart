// Inbox screen widget test — overrides inboxProvider with fake rows
// and asserts the empty + populated states render.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:signupflow_mobile/features/volunteer/inbox_provider.dart';
import 'package:signupflow_mobile/features/volunteer/inbox_screen.dart';
import 'package:signupflow_mobile/theme/theme.dart';

InboxData _withRows() => InboxData(
      unread: 1,
      rows: [
        InboxRow(
          id: 1,
          type: 'assignment',
          status: 'sent',
          createdAt: DateTime(2026, 5, 7, 9, 30),
        ),
        InboxRow(
          id: 2,
          type: 'reminder',
          status: 'opened',
          createdAt: DateTime(2026, 5, 6, 18, 0),
          openedAt: DateTime(2026, 5, 6, 18, 5),
        ),
      ],
    );

void main() {
  testWidgets('inbox renders empty state', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          inboxProvider.overrideWith(
            (ref) async => const InboxData(rows: [], unread: 0),
          ),
        ],
        child: MaterialApp(
          theme: buildBlockMonoTheme(),
          home: const InboxScreen(),
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.text('INBOX'), findsOneWidget);
    expect(find.textContaining('No notifications yet'), findsOneWidget);
  });

  testWidgets('inbox renders rows with subjects + read state', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          inboxProvider.overrideWith((ref) async => _withRows()),
        ],
        child: MaterialApp(
          theme: buildBlockMonoTheme(),
          home: const InboxScreen(),
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.text('You were assigned to an event'), findsOneWidget);
    expect(find.text('Reminder: upcoming event'), findsOneWidget);
    expect(find.text('ASSIGNMENT'), findsOneWidget);
    expect(find.text('REMINDER'), findsOneWidget);
  });

  test('isUnread mirrors backend predicate (opened_at AND clicked_at null)',
      () {
    final pristine = InboxRow(
      id: 1,
      type: 'assignment',
      status: 'sent',
      createdAt: DateTime(2026, 5, 7),
    );
    expect(pristine.isUnread, isTrue);

    final opened = InboxRow(
      id: 2,
      type: 'assignment',
      status: 'opened',
      createdAt: DateTime(2026, 5, 7),
      openedAt: DateTime(2026, 5, 7, 9),
    );
    expect(opened.isUnread, isFalse);

    // SendGrid can land a click webhook before an open webhook, so
    // clicked_at can be set while opened_at is still null. The backend
    // unread count excludes such rows; the row state must agree.
    final clickedNotOpened = InboxRow(
      id: 3,
      type: 'assignment',
      status: 'clicked',
      createdAt: DateTime(2026, 5, 7),
      clickedAt: DateTime(2026, 5, 7, 9, 5),
    );
    expect(clickedNotOpened.isUnread, isFalse);
  });
}
