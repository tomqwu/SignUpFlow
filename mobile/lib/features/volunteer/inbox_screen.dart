// Volunteer Inbox — Sprint 8.10.
// Replaces the StubScreen with a real list against /notifications.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:signupflow_mobile/features/volunteer/inbox_provider.dart';
import 'package:signupflow_mobile/theme/colors.dart';
import 'package:signupflow_mobile/theme/components.dart';
import 'package:signupflow_mobile/theme/typography.dart';

class InboxScreen extends ConsumerWidget {
  const InboxScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncData = ref.watch(inboxProvider);
    return Scaffold(
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const PageTitle('Inbox'),
            Expanded(
              child: asyncData.when(
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (e, _) => Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Text(
                      'Failed to load: $e',
                      style: BlockType.bodySm,
                      textAlign: TextAlign.center,
                    ),
                  ),
                ),
                data: (data) => _Body(data: data),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _Body extends ConsumerWidget {
  const _Body({required this.data});
  final InboxData data;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (data.rows.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Text(
            'No notifications yet.\n\nWhen you get assigned to an event, '
            'or when a schedule changes, a row will appear here.',
            style: BlockType.bodySm.copyWith(color: BlockColors.ink2),
            textAlign: TextAlign.center,
          ),
        ),
      );
    }
    return RefreshIndicator(
      onRefresh: () async {
        ref.invalidate(inboxProvider);
        await ref.read(inboxProvider.future);
      },
      child: ListView.builder(
        padding: const EdgeInsets.fromLTRB(16, 0, 16, 96),
        itemCount: data.rows.length,
        itemBuilder: (_, i) => _Row(row: data.rows[i]),
      ),
    );
  }
}

class _Row extends ConsumerWidget {
  const _Row({required this.row});
  final InboxRow row;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final unreadDot = row.isUnread
        ? Container(
            width: 8,
            height: 8,
            margin: const EdgeInsets.only(right: 8, top: 6),
            decoration: const BoxDecoration(
              color: BlockColors.accent,
              shape: BoxShape.circle,
            ),
          )
        : const SizedBox(width: 16);

    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: BlockCard(
        child: InkWell(
          onTap: () async {
            if (row.isUnread) {
              await ref.read(inboxMutationsProvider.notifier).markRead(row.id);
            }
            if (!context.mounted) return;
            if (row.eventId != null) {
              // The only detail route mobile has today is /v/assignment/:id,
              // and notifications carry an event_id (not assignment_id).
              // Bouncing to the schedule tab is the most useful destination
              // for v1 — the user can find the event there.
              context.go('/v/schedule');
            }
          },
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              unreadDot,
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      row.subject,
                      style: BlockType.body.copyWith(
                        fontWeight:
                            row.isUnread ? FontWeight.w600 : FontWeight.w400,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      DateFormat('d MMM y · HH:mm').format(row.createdAt),
                      style:
                          BlockType.bodySm.copyWith(color: BlockColors.ink2),
                    ),
                  ],
                ),
              ),
              Text(
                row.type.toUpperCase(),
                style: BlockType.monoLabel.copyWith(fontSize: 9),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
