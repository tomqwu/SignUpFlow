// Volunteer Schedule — Sprint 7.3.
// Visual target: mobile/prototype/screenshots/v2/03-v-schedule.png.
// Data: scheduleProvider (FutureProvider) joins listMyAssignments +
//        listEvents client-side.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:signupflow_mobile/features/volunteer/schedule_provider.dart';
import 'package:signupflow_mobile/theme/colors.dart';
import 'package:signupflow_mobile/theme/components.dart';
import 'package:signupflow_mobile/theme/typography.dart';

class VolunteerScheduleScreen extends ConsumerWidget {
  const VolunteerScheduleScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncData = ref.watch(scheduleProvider);

    return Scaffold(
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Top action — calendar export sheet (lands in PR 7.6).
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  TextButton(
                    style: TextButton.styleFrom(
                      foregroundColor: BlockColors.accent,
                      textStyle: BlockType.monoLabel.copyWith(
                        color: BlockColors.accent,
                        fontSize: 13,
                      ),
                    ),
                    onPressed: () => ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Calendar export lands in 7.6')),
                    ),
                    child: const Text('EXPORT'),
                  ),
                ],
              ),
            ),
            const PageTitle('Schedule'),
            Expanded(
              child: asyncData.when(
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (e, _) => _ErrorState(
                  message: e.toString(),
                  onRetry: () => ref.invalidate(scheduleProvider),
                ),
                data: (data) => data.isEmpty
                    ? const _EmptyState()
                    : _ScheduleList(data: data),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ScheduleList extends StatelessWidget {
  const _ScheduleList({required this.data});
  final ScheduleData data;

  @override
  Widget build(BuildContext context) {
    final today = DateTime.now();
    final thisMonday = today.subtract(Duration(days: today.weekday - 1));
    final nextMonday = thisMonday.add(const Duration(days: 7));

    // Pull-to-refresh comes in a follow-up; simple ListView is fine for now.
    return ListView.builder(
      padding: const EdgeInsets.fromLTRB(16, 0, 16, 96),
      itemCount: data.groups.length,
      itemBuilder: (ctx, idx) {
        final g = data.groups[idx];
        // Tag the first group of "this week" / "next week" for context.
        String? weekTag;
        if (g.date.isAfter(thisMonday.subtract(const Duration(days: 1))) &&
            g.date.isBefore(nextMonday)) {
          final firstThisWeek = data.groups.indexWhere(
            (x) => x.date.isAfter(thisMonday.subtract(const Duration(days: 1))),
          );
          if (idx == firstThisWeek) weekTag = 'THIS WEEK';
        } else if (g.date.isAfter(nextMonday.subtract(const Duration(days: 1))) &&
            g.date.isBefore(nextMonday.add(const Duration(days: 7)))) {
          final firstNextWeek = data.groups.indexWhere(
            (x) => x.date.isAfter(nextMonday.subtract(const Duration(days: 1))),
          );
          if (idx == firstNextWeek) weekTag = 'NEXT WEEK';
        }
        return _DateGroup(group: g, weekTag: weekTag);
      },
    );
  }
}

class _DateGroup extends StatelessWidget {
  const _DateGroup({required this.group, this.weekTag});
  final ScheduleGroup group;
  final String? weekTag;

  @override
  Widget build(BuildContext context) {
    final dateLabel = DateFormat('EEE d MMM').format(group.date).toUpperCase();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        MonoLabel(
          dateLabel,
          trailing: weekTag != null
              ? Text(weekTag!, style: BlockType.monoLabel.copyWith(color: BlockColors.accent))
              : null,
        ),
        ...group.rows.map((r) => _AssignmentRow(row: r)),
      ],
    );
  }
}

class _AssignmentRow extends StatelessWidget {
  const _AssignmentRow({required this.row});
  final ScheduleRow row;

  String _timeChipText() {
    final f = DateFormat('HH:mm');
    return '${f.format(row.start)}–${f.format(row.end)}';
  }

  StatusKind _status() => switch (row.assignment.status.toLowerCase()) {
        'confirmed' || 'accepted' => StatusKind.confirmed,
        'pending' => StatusKind.pending,
        'declined' => StatusKind.declined,
        _ => StatusKind.neutral,
      };

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Material(
        color: BlockColors.bgCard,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(14),
          side: const BorderSide(color: BlockColors.line1),
        ),
        child: InkWell(
          borderRadius: BorderRadius.circular(14),
          onTap: () => context.go('/v/assignment/${row.assignment.id}'),
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Wrap(
                        spacing: 8,
                        crossAxisAlignment: WrapCrossAlignment.center,
                        children: [
                          TimeChip(_timeChipText()),
                          if (row.assignment.role != null)
                            RoleChip(row.assignment.role!),
                        ],
                      ),
                      const SizedBox(height: 6),
                      Text(
                        row.event.type,
                        style: BlockType.subhead,
                      ),
                      const SizedBox(height: 4),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          // Location not present on EventResponse v1 — we
                          // surface event id as a faint slug to keep the row
                          // grounded; future schema can swap in a real
                          // location field.
                          Text(
                            'Event ${row.event.id}',
                            style: BlockType.bodySm.copyWith(color: BlockColors.ink2),
                          ),
                          StatusText(kind: _status(), label: row.assignment.status),
                        ],
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 4),
                const Icon(Icons.chevron_right, color: BlockColors.ink3, size: 20),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _EmptyState extends StatelessWidget {
  const _EmptyState();
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('NO UPCOMING ASSIGNMENTS', style: BlockType.monoLabel),
            const SizedBox(height: 8),
            Text(
              "When the next schedule is published you'll see your roster here.",
              style: BlockType.bodySm,
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

class _ErrorState extends StatelessWidget {
  const _ErrorState({required this.message, required this.onRetry});
  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('FAILED TO LOAD', style: BlockType.monoLabel.copyWith(color: BlockColors.danger)),
            const SizedBox(height: 8),
            Text(
              message,
              style: BlockType.bodySm,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            BlockButton(
              label: 'Retry',
              kind: BlockButtonKind.secondary,
              onPressed: onRetry,
            ),
          ],
        ),
      ),
    );
  }
}
