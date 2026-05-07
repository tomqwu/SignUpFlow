// Volunteer Assignment Detail — Sprint 7.4.
// Visual target: mobile/prototype/screenshots/v2/04-v-assignment.png.
//
// Reads the schedule row from `assignmentDetailProvider`. Mutations route
// through `assignmentMutationsProvider`, which invalidates the schedule
// on success and pops back. Decline opens a bottom sheet for an optional
// reason.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:signupflow_mobile/features/volunteer/assignment_detail_provider.dart';
import 'package:signupflow_mobile/features/volunteer/schedule_provider.dart';
import 'package:signupflow_mobile/theme/colors.dart';
import 'package:signupflow_mobile/theme/components.dart';
import 'package:signupflow_mobile/theme/typography.dart';

class AssignmentDetailScreen extends ConsumerWidget {
  const AssignmentDetailScreen({required this.assignmentId, super.key});
  final String assignmentId;

  int? get _id => int.tryParse(assignmentId);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final id = _id;
    if (id == null) {
      return const _DetailFrame(
        body: Center(
          child: Text('Invalid assignment id'),
        ),
      );
    }

    final asyncRow = ref.watch(assignmentDetailProvider(id));
    final mutation = ref.watch(assignmentMutationsProvider);

    return _DetailFrame(
      onBack: () => context.go('/v/schedule'),
      body: asyncRow.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Padding(
          padding: const EdgeInsets.all(24),
          child: Center(
            child: Text(
              'Failed to load assignment: $e',
              style: BlockType.bodySm,
              textAlign: TextAlign.center,
            ),
          ),
        ),
        data: (row) => row == null
            ? const _NotFound()
            : _Body(row: row, busy: mutation.status == MutationStatus.busy, error: mutation.error),
      ),
    );
  }
}

class _DetailFrame extends StatelessWidget {
  const _DetailFrame({required this.body, this.onBack});
  final Widget body;
  final VoidCallback? onBack;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  if (onBack != null)
                    TextButton(
                      onPressed: onBack,
                      style: TextButton.styleFrom(foregroundColor: BlockColors.accent),
                      child: Text(
                        '‹ SCHEDULE',
                        style: BlockType.monoLabel.copyWith(
                          color: BlockColors.accent,
                          fontSize: 13,
                        ),
                      ),
                    )
                  else
                    const SizedBox(width: 80),
                  Text(
                    'ASSIGNMENT',
                    style: BlockType.monoLabel.copyWith(
                      color: BlockColors.ink1,
                      fontSize: 13,
                    ),
                  ),
                  const SizedBox(width: 80),
                ],
              ),
            ),
            Expanded(child: body),
          ],
        ),
      ),
    );
  }
}

class _NotFound extends StatelessWidget {
  const _NotFound();
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('NOT FOUND', style: BlockType.monoLabel),
            const SizedBox(height: 8),
            Text(
              "This assignment isn't in your current schedule. It may have been "
              'reassigned or the schedule republished.',
              style: BlockType.bodySm,
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

class _Body extends ConsumerWidget {
  const _Body({required this.row, required this.busy, this.error});
  final ScheduleRow row;
  final bool busy;
  final String? error;

  StatusKind _status() => switch (row.assignment.status.toLowerCase()) {
        'confirmed' || 'accepted' => StatusKind.confirmed,
        'pending' => StatusKind.pending,
        'declined' => StatusKind.declined,
        _ => StatusKind.neutral,
      };

  String _timeRange() {
    final f = DateFormat('HH:mm');
    return '${f.format(row.start)}–${f.format(row.end)}';
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          BlockCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Wrap(
                  spacing: 8,
                  crossAxisAlignment: WrapCrossAlignment.center,
                  children: [
                    TimeChip(_timeRange()),
                    if (row.assignment.role != null) RoleChip(row.assignment.role!),
                    StatusText(kind: _status(), label: row.assignment.status),
                  ],
                ),
                const SizedBox(height: 10),
                Text(
                  row.event.type,
                  style: BlockType.displayUpper(22).copyWith(
                    fontSize: 22,
                    height: 1.15,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  DateFormat('EEE d MMM y · h:mm a').format(row.start).toUpperCase(),
                  style: BlockType.monoData.copyWith(fontSize: 11),
                ),
                const SizedBox(height: 12),
                Text(
                  'Tap a button below to update your response. The schedule '
                  'will refresh once the change reaches the server.',
                  style: BlockType.bodySm,
                ),
              ],
            ),
          ),
          if (error != null) ...[
            const SizedBox(height: 12),
            Text(
              error!,
              style: BlockType.bodySm.copyWith(color: BlockColors.danger),
              textAlign: TextAlign.center,
            ),
          ],
          const MonoLabel('Your response'),
          Row(
            children: [
              Expanded(
                child: BlockButton(
                  label: busy ? 'Working…' : 'Accept',
                  kind: BlockButtonKind.go,
                  onPressed: busy ? null : () => _doAccept(context, ref),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: BlockButton(
                  label: 'Swap',
                  kind: BlockButtonKind.secondary,
                  onPressed: busy ? null : () => _doSwap(context, ref),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          BlockButton(
            label: 'Decline',
            kind: BlockButtonKind.destructive,
            onPressed: busy ? null : () => _doDecline(context, ref),
          ),
        ],
      ),
    );
  }

  Future<void> _doAccept(BuildContext context, WidgetRef ref) async {
    final err = await ref
        .read(assignmentMutationsProvider.notifier)
        .accept(row.assignment.id);
    if (!context.mounted) return;
    if (err == null) context.go('/v/schedule');
  }

  Future<void> _doSwap(BuildContext context, WidgetRef ref) async {
    final note = await _promptForText(
      context,
      title: 'REQUEST SWAP',
      hint: 'Optional note to your team lead',
      submitLabel: 'Send swap request',
    );
    if (note == null || !context.mounted) return; // user cancelled
    final err = await ref
        .read(assignmentMutationsProvider.notifier)
        .requestSwap(row.assignment.id, note);
    if (!context.mounted) return;
    if (err == null) context.go('/v/schedule');
  }

  Future<void> _doDecline(BuildContext context, WidgetRef ref) async {
    final reason = await _promptForText(
      context,
      title: 'DECLINE',
      hint: 'Reason (visible to your admin)',
      submitLabel: 'Decline',
      requireNonEmpty: true,
    );
    if (reason == null || !context.mounted) return;
    final err = await ref
        .read(assignmentMutationsProvider.notifier)
        .decline(row.assignment.id, reason);
    if (!context.mounted) return;
    if (err == null) context.go('/v/schedule');
  }

  Future<String?> _promptForText(
    BuildContext context, {
    required String title,
    required String hint,
    required String submitLabel,
    bool requireNonEmpty = false,
  }) {
    final ctrl = TextEditingController();
    return showModalBottomSheet<String?>(
      context: context,
      backgroundColor: BlockColors.bgCard,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (sheetCtx) {
        return Padding(
          padding: EdgeInsets.fromLTRB(
            20,
            16,
            20,
            MediaQuery.of(sheetCtx).viewInsets.bottom + 20,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(title, style: BlockType.monoLabel.copyWith(color: BlockColors.ink1)),
              const SizedBox(height: 8),
              TextField(
                controller: ctrl,
                autofocus: true,
                maxLines: 3,
                style: BlockType.body,
                decoration: InputDecoration(
                  hintText: hint,
                  hintStyle: BlockType.bodySm.copyWith(color: BlockColors.ink3),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: BlockColors.line1),
                  ),
                ),
              ),
              const SizedBox(height: 14),
              Row(
                children: [
                  Expanded(
                    child: BlockButton(
                      label: 'Cancel',
                      kind: BlockButtonKind.secondary,
                      onPressed: () => Navigator.of(sheetCtx).pop(null),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: BlockButton(
                      label: submitLabel,
                      onPressed: () {
                        final value = ctrl.text.trim();
                        if (requireNonEmpty && value.isEmpty) return;
                        Navigator.of(sheetCtx).pop(value);
                      },
                    ),
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }
}
