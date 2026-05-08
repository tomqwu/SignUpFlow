// Inbox feed for volunteers — wraps NotificationsApi.

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/api/api_client.dart';
import 'package:signupflow_mobile/auth/auth_provider.dart';

class InboxRow {
  const InboxRow({
    required this.id,
    required this.type,
    required this.status,
    required this.createdAt,
    this.openedAt,
    this.eventId,
  });
  final int id;
  final String type;
  final String status;
  final DateTime createdAt;
  final DateTime? openedAt;
  final String? eventId;

  bool get isUnread => openedAt == null;

  /// Human-readable subject. The backend stores no rendered subject yet
  /// (templates are rendered on send), so we synthesise one from the type.
  String get subject {
    switch (type) {
      case 'assignment':
        return 'You were assigned to an event';
      case 'reminder':
        return 'Reminder: upcoming event';
      case 'update':
        return 'Event details updated';
      case 'cancellation':
        return 'Event was cancelled';
      case 'digest_daily':
        return 'Daily schedule digest';
      case 'digest_weekly':
        return 'Weekly schedule digest';
      case 'admin_summary':
        return 'Weekly stats summary';
      default:
        return type;
    }
  }
}

class InboxData {
  const InboxData({required this.rows, required this.unread});
  final List<InboxRow> rows;
  final int unread;
}

final inboxProvider = FutureProvider<InboxData>((ref) async {
  final auth = ref.watch(authProvider);
  final orgId = auth.orgId;
  if (orgId == null) {
    return const InboxData(rows: [], unread: 0);
  }
  final client = ref.watch(signupflowApiProvider);

  final listRes = await client.getNotificationsApi().listNotifications(orgId: orgId);
  final body = listRes.data;
  final rows = <InboxRow>[];
  if (body != null) {
    for (final n in body.notifications) {
      rows.add(_fromApi(n));
    }
  }

  final countRes = await client.getNotificationsApi().getUnreadCount();
  var unread = 0;
  final raw = countRes.data;
  if (raw != null) {
    final asMap = raw.asMap;
    final v = asMap['unread'];
    if (v is num) unread = v.toInt();
  }

  return InboxData(rows: rows, unread: unread);
});

InboxRow _fromApi(api.NotificationResponse n) => InboxRow(
      id: n.id,
      type: n.type,
      status: n.status,
      createdAt: n.createdAt,
      openedAt: n.openedAt,
      eventId: n.eventId,
    );

class InboxMutationsController extends Notifier<bool> {
  @override
  bool build() => false; // busy flag

  Future<String?> markRead(int notificationId) async {
    state = true;
    try {
      await ref
          .read(signupflowApiProvider)
          .getNotificationsApi()
          .markNotificationRead(notificationId: notificationId);
      ref.invalidate(inboxProvider);
      state = false;
      return null;
    } on Exception catch (e) {
      state = false;
      return e.toString();
    }
  }
}

final inboxMutationsProvider =
    NotifierProvider<InboxMutationsController, bool>(
  InboxMutationsController.new,
);
