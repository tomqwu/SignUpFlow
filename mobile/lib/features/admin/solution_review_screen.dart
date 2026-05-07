// Admin Solution Review — Sprint 7.9.
// Visual target: mobile/prototype/screenshots/v2/12-a-solution.png.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:signupflow_mobile/features/admin/solver_provider.dart';
import 'package:signupflow_mobile/theme/colors.dart';
import 'package:signupflow_mobile/theme/components.dart';
import 'package:signupflow_mobile/theme/typography.dart';

class SolutionReviewScreen extends ConsumerStatefulWidget {
  const SolutionReviewScreen({required this.solutionId, super.key});
  final String solutionId;

  @override
  ConsumerState<SolutionReviewScreen> createState() => _SolutionReviewScreenState();
}

class _SolutionReviewScreenState extends ConsumerState<SolutionReviewScreen> {
  String _segment = 'assignments';

  int? get _id => int.tryParse(widget.solutionId);

  @override
  Widget build(BuildContext context) {
    final id = _id;
    if (id == null) {
      return _frame(
        const Center(child: Text('Invalid solution id')),
      );
    }
    final asyncData = ref.watch(solutionDetailProvider(id));
    return _frame(
      asyncData.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Text('Failed to load solution: $e', style: BlockType.bodySm),
          ),
        ),
        data: (data) => _Body(
          data: data,
          segment: _segment,
          onSegmentChanged: (v) => setState(() => _segment = v),
          onPublish: () => GoRouter.of(context).go('/a/publish'),
          onCompare: () => GoRouter.of(context).go('/a/compare'),
        ),
      ),
      id: id,
    );
  }

  Widget _frame(Widget body, {int? id}) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  TextButton(
                    onPressed: () => GoRouter.of(context).go('/a/solver'),
                    style: TextButton.styleFrom(foregroundColor: BlockColors.accent),
                    child: Text(
                      '‹ SOLVER',
                      style: BlockType.monoLabel.copyWith(
                        color: BlockColors.accent,
                        fontSize: 13,
                      ),
                    ),
                  ),
                  Text(
                    id == null ? 'SOLUTION' : 'SOLUTION #$id',
                    style: BlockType.monoLabel.copyWith(
                      color: BlockColors.ink1,
                      fontSize: 13,
                    ),
                  ),
                  TextButton(
                    onPressed: id == null ? null : () => GoRouter.of(context).go('/a/publish'),
                    style: TextButton.styleFrom(foregroundColor: BlockColors.accent),
                    child: Text(
                      'PUBLISH',
                      style: BlockType.monoLabel.copyWith(
                        color: BlockColors.accent,
                        fontSize: 13,
                      ),
                    ),
                  ),
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

class _Body extends StatelessWidget {
  const _Body({
    required this.data,
    required this.segment,
    required this.onSegmentChanged,
    required this.onPublish,
    required this.onCompare,
  });
  final SolutionDetailData data;
  final String segment;
  final ValueChanged<String> onSegmentChanged;
  final VoidCallback onPublish;
  final VoidCallback onCompare;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _Segment(value: segment, onChanged: onSegmentChanged),
          const SizedBox(height: 14),
          if (segment == 'assignments') _AssignmentsView(data: data),
          if (segment == 'stats') _StatsView(data: data),
          if (segment == 'conflicts') _ConflictsView(data: data),
          const SizedBox(height: 18),
          BlockButton(
            label: 'Compare with another solution',
            kind: BlockButtonKind.secondary,
            onPressed: onCompare,
          ),
        ],
      ),
    );
  }
}

class _Segment extends StatelessWidget {
  const _Segment({required this.value, required this.onChanged});
  final String value;
  final ValueChanged<String> onChanged;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(3),
      decoration: BoxDecoration(
        color: BlockColors.line2,
        borderRadius: BorderRadius.circular(999),
      ),
      child: Row(
        children: [
          Expanded(child: _seg('ASSIGNMENTS', 'assignments')),
          Expanded(child: _seg('STATS', 'stats')),
          Expanded(child: _seg('CONFLICTS', 'conflicts')),
        ],
      ),
    );
  }

  Widget _seg(String label, String key) {
    final active = value == key;
    return GestureDetector(
      onTap: () => onChanged(key),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 7),
        decoration: BoxDecoration(
          color: active ? Colors.white : Colors.transparent,
          borderRadius: BorderRadius.circular(999),
        ),
        alignment: Alignment.center,
        child: Text(
          label,
          style: BlockType.monoLabel.copyWith(
            fontSize: 11,
            color: active ? BlockColors.ink1 : BlockColors.ink2,
          ),
        ),
      ),
    );
  }
}

class _AssignmentsView extends StatelessWidget {
  const _AssignmentsView({required this.data});
  final SolutionDetailData data;

  @override
  Widget build(BuildContext context) {
    final created = DateFormat('EEE d MMM y · h:mm a')
        .format(data.solution.createdAt.toLocal())
        .toUpperCase();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        BlockCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Solution #${data.solution.id}', style: BlockType.subhead),
              const SizedBox(height: 4),
              Text(created, style: BlockType.monoTiny.copyWith(fontSize: 10)),
              const SizedBox(height: 10),
              Wrap(
                spacing: 14,
                runSpacing: 6,
                children: [
                  StatusText(
                    kind: data.solution.hardViolations == 0
                        ? StatusKind.confirmed
                        : StatusKind.declined,
                    label: '${data.solution.hardViolations} hard',
                  ),
                  StatusText(
                    kind: StatusKind.pending,
                    label: '${data.solution.softScore.toStringAsFixed(1)} soft',
                  ),
                  Text(
                    'HEALTH ${data.solution.healthScore.toInt()}',
                    style: BlockType.monoData.copyWith(fontSize: 11),
                  ),
                ],
              ),
            ],
          ),
        ),
        const MonoLabel('Per-event breakdown — coming in 7.10'),
        BlockCard(
          color: const Color(0xFFFFF7ED),
          borderColor: const Color(0xFFFED7AA),
          child: Text(
            'Listing assignments grouped by event needs an enriched API '
            'response (event title + assignees in one call). The current '
            'getSolutionAssignments returns a JsonObject; rendering it '
            'cleanly will land alongside Compare in 7.10.',
            style: BlockType.bodySm,
          ),
        ),
      ],
    );
  }
}

class _StatsView extends StatelessWidget {
  const _StatsView({required this.data});
  final SolutionDetailData data;

  @override
  Widget build(BuildContext context) {
    final stats = data.stats;
    if (stats == null) {
      return BlockCard(
        child: Text('Stats unavailable for this solution.', style: BlockType.bodySm),
      );
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const MonoLabel('Stability vs published'),
        Row(
          children: [
            Expanded(
              child: KpiCell(
                value: '${stats.stability.movesFromPublished}',
                label: 'Moves',
                accent: true,
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: KpiCell(
                value: '${stats.stability.affectedPersons}',
                label: 'People affected',
              ),
            ),
          ],
        ),
        const MonoLabel('Workload'),
        Row(
          children: [
            Expanded(
              child: KpiCell(
                value: '${stats.workload.maxEventsPerPerson}',
                label: 'Max / person',
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: KpiCell(
                value: stats.workload.medianEventsPerPerson.toStringAsFixed(1),
                label: 'Median / person',
              ),
            ),
          ],
        ),
        const MonoLabel('Fairness'),
        BlockCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Stdev', style: BlockType.monoLabel),
              Text(
                stats.fairness.stdev.toStringAsFixed(2),
                style: BlockType.subhead.copyWith(fontSize: 22),
              ),
              const SizedBox(height: 6),
              Text(
                'Lower stdev means assignments are more evenly distributed across people.',
                style: BlockType.bodySm,
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _ConflictsView extends StatelessWidget {
  const _ConflictsView({required this.data});
  final SolutionDetailData data;

  @override
  Widget build(BuildContext context) {
    final hard = data.solution.hardViolations;
    if (hard == 0) {
      return BlockCard(
        padding: const EdgeInsets.all(28),
        child: Column(
          children: [
            const Icon(Icons.check_circle_outline, color: BlockColors.success, size: 28),
            const SizedBox(height: 8),
            Text('NO HARD CONFLICTS', style: BlockType.monoLabel.copyWith(color: BlockColors.success)),
            const SizedBox(height: 4),
            Text(
              'Soft violations (if any) appear under STATS.',
              style: BlockType.bodySm,
            ),
          ],
        ),
      );
    }
    return BlockCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          StatusText(kind: StatusKind.declined, label: '$hard hard violations'),
          const SizedBox(height: 6),
          Text(
            'A breakdown of which constraint each violation traces to '
            'comes alongside the Assignments view in 7.10.',
            style: BlockType.bodySm,
          ),
        ],
      ),
    );
  }
}
