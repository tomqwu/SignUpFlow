// Volunteer Availability — Sprint 7.5.
// Visual target: mobile/prototype/screenshots/v2/05-v-availability.png.
//
// Scope: ships TimeOff (multi-day vacation) management end-to-end against
// AvailabilityApi. Recurring rules (rrule) + single-date exceptions are
// in a "coming soon" panel — backend doesn't expose CRUD for them yet.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:signupflow_mobile/features/volunteer/availability_provider.dart';
import 'package:signupflow_mobile/theme/colors.dart';
import 'package:signupflow_mobile/theme/components.dart';
import 'package:signupflow_mobile/theme/typography.dart';

class AvailabilityScreen extends ConsumerWidget {
  const AvailabilityScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncData = ref.watch(availabilityProvider);

    return Scaffold(
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  TextButton(
                    onPressed: () => _openAddSheet(context, ref),
                    style: TextButton.styleFrom(
                      foregroundColor: BlockColors.accent,
                    ),
                    child: Text(
                      'ADD',
                      style: BlockType.monoLabel.copyWith(
                        color: BlockColors.accent,
                        fontSize: 13,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const PageTitle('Availability'),
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

  Future<void> _openAddSheet(BuildContext context, WidgetRef ref) async {
    DateTime? start;
    DateTime? end;
    final reasonCtrl = TextEditingController();

    final result = await showModalBottomSheet<bool>(
      context: context,
      isScrollControlled: true,
      backgroundColor: context.blockColor(
        light: BlockColors.bgCard,
        dark: BlockColors.bgCardDark,
      ),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (sheetCtx) {
        return StatefulBuilder(
          builder: (innerCtx, setState) => Padding(
            padding: EdgeInsets.fromLTRB(
              20,
              16,
              20,
              MediaQuery.of(innerCtx).viewInsets.bottom + 20,
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text('ADD TIME OFF', style: BlockType.monoLabel.copyWith(color: BlockColors.ink1)),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: _DateField(
                        label: 'From',
                        value: start,
                        onTap: () async {
                          final picked = await _pickDate(innerCtx, initial: start);
                          if (picked != null) setState(() => start = picked);
                        },
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: _DateField(
                        label: 'To',
                        value: end,
                        onTap: () async {
                          final picked = await _pickDate(innerCtx, initial: end ?? start);
                          if (picked != null) setState(() => end = picked);
                        },
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                TextField(
                  controller: reasonCtrl,
                  style: BlockType.body,
                  decoration: InputDecoration(
                    hintText: 'Reason (optional)',
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
                        onPressed: () => Navigator.of(sheetCtx).pop(false),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: BlockButton(
                        label: 'Save',
                        onPressed: () async {
                          if (start == null || end == null) return;
                          if (end!.isBefore(start!)) {
                            ScaffoldMessenger.of(innerCtx).showSnackBar(
                              const SnackBar(content: Text('End date must be on or after start')),
                            );
                            return;
                          }
                          final err = await ref
                              .read(availabilityMutationsProvider.notifier)
                              .addTimeoff(
                                start!,
                                end!,
                                reasonCtrl.text.trim().isEmpty
                                    ? null
                                    : reasonCtrl.text.trim(),
                              );
                          if (!innerCtx.mounted) return;
                          if (err != null) {
                            ScaffoldMessenger.of(innerCtx).showSnackBar(
                              SnackBar(content: Text('Failed: $err')),
                            );
                            return;
                          }
                          Navigator.of(sheetCtx).pop(true);
                        },
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );

    if ((result ?? false) && context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Time off saved')),
      );
    }
  }

  Future<DateTime?> _pickDate(BuildContext ctx, {DateTime? initial}) {
    final now = DateTime.now();
    return showDatePicker(
      context: ctx,
      initialDate: initial ?? now,
      firstDate: DateTime(now.year, now.month - 1),
      lastDate: DateTime(now.year + 2),
    );
  }
}

class _Body extends ConsumerWidget {
  const _Body({required this.data});
  final AvailabilityData data;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final today = DateTime.now();
    final monthStart = DateTime(today.year, today.month);
    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(16, 0, 16, 96),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          BlockCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  crossAxisAlignment: CrossAxisAlignment.baseline,
                  textBaseline: TextBaseline.alphabetic,
                  children: [
                    Text(
                      DateFormat('MMMM y').format(monthStart),
                      style: BlockType.subhead,
                    ),
                    Text(
                      '${data.blockedDays.length} BLOCKED',
                      style: BlockType.monoData.copyWith(fontSize: 10),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                _MonthGrid(monthStart: monthStart, blockedDays: data.blockedDays),
                const SizedBox(height: 12),
                const Row(
                  children: [
                    _LegendDot(color: BlockColors.ink1, label: 'Blocked'),
                    SizedBox(width: 14),
                    _LegendDot(color: BlockColors.accentSoft, label: 'Today'),
                  ],
                ),
              ],
            ),
          ),
          const MonoLabel('Time off · vacation periods'),
          if (data.entries.isEmpty)
            BlockCard(
              child: Text(
                'No time off scheduled. Tap ADD above to block dates.',
                style: BlockType.bodySm,
                textAlign: TextAlign.center,
              ),
            )
          else
            for (final e in data.entries) _TimeOffRow(entry: e),
          const MonoLabel('Recurring rules · weekly / biweekly'),
          const _RruleCard(),
          const MonoLabel('One-off blocked dates'),
          _ExceptionsCard(exceptions: data.exceptions),
        ],
      ),
    );
  }
}

class _MonthGrid extends StatelessWidget {
  const _MonthGrid({required this.monthStart, required this.blockedDays});
  final DateTime monthStart;
  final Set<DateTime> blockedDays;

  @override
  Widget build(BuildContext context) {
    final firstWeekday = monthStart.weekday; // Mon=1..Sun=7
    final daysInMonth = DateTime(monthStart.year, monthStart.month + 1, 0).day;
    final today = DateTime.now();
    const dow = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];

    final cells = <Widget>[];
    for (final d in dow) {
      cells.add(_GridCell(child: Text(d, style: BlockType.monoTiny.copyWith(fontSize: 9))));
    }
    for (var i = 1; i < firstWeekday; i++) {
      cells.add(const _GridCell());
    }
    for (var d = 1; d <= daysInMonth; d++) {
      final date = DateTime(monthStart.year, monthStart.month, d);
      final blocked = blockedDays.contains(date);
      final isToday = today.year == date.year && today.month == date.month && today.day == date.day;
      cells.add(_DayCell(day: d, blocked: blocked, isToday: isToday));
    }

    return GridView.count(
      crossAxisCount: 7,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      mainAxisSpacing: 4,
      crossAxisSpacing: 4,
      children: cells,
    );
  }
}

class _GridCell extends StatelessWidget {
  const _GridCell({this.child});
  final Widget? child;
  @override
  Widget build(BuildContext context) =>
      Center(child: child ?? const SizedBox.shrink());
}

class _DayCell extends StatelessWidget {
  const _DayCell({required this.day, required this.blocked, required this.isToday});
  final int day;
  final bool blocked;
  final bool isToday;

  @override
  Widget build(BuildContext context) {
    var bg = Colors.transparent;
    var fg = BlockColors.ink1;
    if (blocked) {
      bg = BlockColors.ink1;
      fg = Colors.white;
    } else if (isToday) {
      bg = BlockColors.accentSoft;
      fg = BlockColors.accentInk;
    }
    return Container(
      decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(8)),
      alignment: Alignment.center,
      child: Text(
        '$day',
        style: BlockType.body.copyWith(color: fg, fontSize: 14, fontWeight: FontWeight.w500),
      ),
    );
  }
}

class _LegendDot extends StatelessWidget {
  const _LegendDot({required this.color, required this.label});
  final Color color;
  final String label;
  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 10,
          height: 10,
          decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(3)),
        ),
        const SizedBox(width: 5),
        Text(label, style: BlockType.bodySm),
      ],
    );
  }
}

class _TimeOffRow extends ConsumerWidget {
  const _TimeOffRow({required this.entry});
  final TimeOffEntry entry;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final f = DateFormat('d MMM');
    final range = entry.startDate.isAtSameMomentAs(entry.endDate)
        ? f.format(entry.startDate)
        : '${f.format(entry.startDate)} – ${f.format(entry.endDate)}';
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: BlockCard(
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(range, style: BlockType.subhead),
                  if (entry.reason != null && entry.reason!.isNotEmpty)
                    Padding(
                      padding: const EdgeInsets.only(top: 2),
                      child: Text(entry.reason!, style: BlockType.bodySm),
                    ),
                ],
              ),
            ),
            IconButton(
              onPressed: () async {
                final err = await ref
                    .read(availabilityMutationsProvider.notifier)
                    .deleteTimeoff(entry.id);
                if (!context.mounted) return;
                if (err != null) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Failed: $err')),
                  );
                }
              },
              icon: const Icon(Icons.close, color: BlockColors.danger, size: 20),
            ),
          ],
        ),
      ),
    );
  }
}

class _RruleCard extends ConsumerWidget {
  const _RruleCard();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncRrule = ref.watch(availabilityRruleProvider);
    return BlockCard(
      child: asyncRrule.when(
        loading: () => const SizedBox(
          height: 40,
          child: Center(child: CircularProgressIndicator(strokeWidth: 2)),
        ),
        error: (e, _) => Text('Failed to load: $e', style: BlockType.bodySm),
        data: (rrule) {
          if (rrule == null || rrule.isEmpty) {
            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'No recurring rule yet.',
                  style: BlockType.bodySm.copyWith(color: BlockColors.ink2),
                ),
                const SizedBox(height: 10),
                BlockButton(
                  label: 'Set recurring rule',
                  onPressed: () => _openPresetSheet(context, ref, current: null),
                ),
              ],
            );
          }
          final presetLabel = kRrulePresets
              .firstWhere(
                (p) => p.rrule == rrule,
                orElse: () => RrulePreset(label: rrule, rrule: rrule),
              )
              .label;
          return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('CURRENT', style: BlockType.monoLabel.copyWith(fontSize: 10)),
              const SizedBox(height: 4),
              Text(presetLabel, style: BlockType.body),
              if (presetLabel != rrule) ...[
                const SizedBox(height: 4),
                Text(rrule, style: BlockType.bodySm.copyWith(color: BlockColors.ink2)),
              ],
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: BlockButton(
                      label: 'Change',
                      kind: BlockButtonKind.secondary,
                      onPressed: () =>
                          _openPresetSheet(context, ref, current: rrule),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: BlockButton(
                      label: 'Clear',
                      kind: BlockButtonKind.destructive,
                      onPressed: () async {
                        final err = await ref
                            .read(availabilityMutationsProvider.notifier)
                            .clearRrule();
                        if (!context.mounted) return;
                        if (err != null) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text('Failed: $err')),
                          );
                        }
                      },
                    ),
                  ),
                ],
              ),
            ],
          );
        },
      ),
    );
  }

  Future<void> _openPresetSheet(
    BuildContext context,
    WidgetRef ref, {
    required String? current,
  }) async {
    final customCtrl = TextEditingController(
      text: current != null &&
              !kRrulePresets.any((p) => p.rrule == current)
          ? current
          : '',
    );
    final picked = await showModalBottomSheet<String?>(
      context: context,
      isScrollControlled: true,
      backgroundColor: context.blockColor(
        light: BlockColors.bgCard,
        dark: BlockColors.bgCardDark,
      ),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (sheetCtx) => Padding(
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
            Text(
              'CHOOSE A RULE',
              style: BlockType.monoLabel.copyWith(color: BlockColors.ink1),
            ),
            const SizedBox(height: 10),
            for (final p in kRrulePresets)
              Padding(
                padding: const EdgeInsets.only(bottom: 6),
                child: BlockButton(
                  label: p.label,
                  kind: current == p.rrule
                      ? BlockButtonKind.primary
                      : BlockButtonKind.secondary,
                  onPressed: () => Navigator.of(sheetCtx).pop(p.rrule),
                ),
              ),
            const SizedBox(height: 10),
            Text(
              'OR CUSTOM RRULE',
              style: BlockType.monoLabel.copyWith(fontSize: 10),
            ),
            const SizedBox(height: 4),
            TextField(
              controller: customCtrl,
              style: BlockType.bodySm,
              decoration: InputDecoration(
                hintText: 'FREQ=WEEKLY;BYDAY=MO,WE',
                hintStyle: BlockType.bodySm.copyWith(color: BlockColors.ink3),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: const BorderSide(color: BlockColors.line1),
                ),
              ),
            ),
            const SizedBox(height: 10),
            BlockButton(
              label: 'Save custom',
              onPressed: () {
                final t = customCtrl.text.trim();
                if (t.isEmpty) return;
                Navigator.of(sheetCtx).pop(t);
              },
            ),
          ],
        ),
      ),
    );

    if (picked == null || !context.mounted) return;
    final err =
        await ref.read(availabilityMutationsProvider.notifier).setRrule(picked);
    if (!context.mounted) return;
    if (err != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed: $err')),
      );
    }
  }
}

class _ExceptionsCard extends ConsumerWidget {
  const _ExceptionsCard({required this.exceptions});
  final List<ExceptionEntry> exceptions;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (exceptions.isEmpty)
          BlockCard(
            child: Text(
              'No one-off blocked dates yet.',
              style: BlockType.bodySm.copyWith(color: BlockColors.ink2),
              textAlign: TextAlign.center,
            ),
          )
        else
          for (final e in exceptions)
            Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: BlockCard(
                child: Row(
                  children: [
                    Expanded(
                      child: Text(
                        DateFormat('EEEE, d MMM y').format(e.date),
                        style: BlockType.body,
                      ),
                    ),
                    IconButton(
                      onPressed: () async {
                        final err = await ref
                            .read(availabilityMutationsProvider.notifier)
                            .deleteException(e.id);
                        if (!context.mounted) return;
                        if (err != null) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text('Failed: $err')),
                          );
                        }
                      },
                      icon: const Icon(
                        Icons.close,
                        color: BlockColors.danger,
                        size: 20,
                      ),
                    ),
                  ],
                ),
              ),
            ),
        const SizedBox(height: 4),
        BlockButton(
          label: '+ Add date',
          kind: BlockButtonKind.secondary,
          onPressed: () => _openAddDate(context, ref),
        ),
      ],
    );
  }

  Future<void> _openAddDate(BuildContext context, WidgetRef ref) async {
    final now = DateTime.now();
    final picked = await showDatePicker(
      context: context,
      initialDate: now,
      firstDate: DateTime(now.year, now.month - 1),
      lastDate: DateTime(now.year + 2),
    );
    if (picked == null || !context.mounted) return;
    final err = await ref
        .read(availabilityMutationsProvider.notifier)
        .addException(picked);
    if (!context.mounted) return;
    if (err != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed: $err')),
      );
    }
  }
}

class _DateField extends StatelessWidget {
  const _DateField({required this.label, required this.value, required this.onTap});
  final String label;
  final DateTime? value;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        decoration: BoxDecoration(
          border: Border.all(color: BlockColors.line1),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              label.toUpperCase(),
              style: BlockType.monoLabel.copyWith(fontSize: 10),
            ),
            const SizedBox(height: 2),
            Text(
              value == null ? 'Pick a date' : DateFormat('d MMM y').format(value!),
              style: BlockType.body.copyWith(
                color: value == null ? BlockColors.ink3 : BlockColors.ink1,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
