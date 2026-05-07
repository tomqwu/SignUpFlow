// Admin Compare — Sprint 7.10.
// Visual target: mobile/prototype/screenshots/v2/13-a-compare.png.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/features/admin/compare_provider.dart';
import 'package:signupflow_mobile/features/admin/publish_provider.dart';
import 'package:signupflow_mobile/theme/colors.dart';
import 'package:signupflow_mobile/theme/components.dart';
import 'package:signupflow_mobile/theme/typography.dart';

class CompareScreen extends ConsumerStatefulWidget {
  const CompareScreen({super.key});

  @override
  ConsumerState<CompareScreen> createState() => _CompareScreenState();
}

class _CompareScreenState extends ConsumerState<CompareScreen> {
  int? _aId;
  int? _bId;

  @override
  Widget build(BuildContext context) {
    final recent = ref.watch(recentSolutionsProvider);
    final canCompare = _aId != null && _bId != null && _aId != _bId;
    final diffAsync = canCompare
        ? ref.watch(compareDiffProvider(CompareIds(a: _aId!, b: _bId!)))
        : null;

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
                    onPressed: () => GoRouter.of(context).pop(),
                    style: TextButton.styleFrom(foregroundColor: BlockColors.accent),
                    child: Text(
                      '‹ BACK',
                      style: BlockType.monoLabel.copyWith(
                        color: BlockColors.accent,
                        fontSize: 13,
                      ),
                    ),
                  ),
                  Text(
                    'COMPARE',
                    style: BlockType.monoLabel.copyWith(
                      color: BlockColors.ink1,
                      fontSize: 13,
                    ),
                  ),
                  const SizedBox(width: 60),
                ],
              ),
            ),
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 96),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    recent.when(
                      loading: () => const Padding(
                        padding: EdgeInsets.all(24),
                        child: Center(child: CircularProgressIndicator()),
                      ),
                      error: (e, _) => Text('Failed to load solutions: $e', style: BlockType.bodySm),
                      data: (solutions) {
                        if (solutions.length < 2) {
                          return BlockCard(
                            child: Text(
                              'You need at least 2 solutions to compare.',
                              style: BlockType.bodySm,
                            ),
                          );
                        }
                        return Row(
                          children: [
                            Expanded(
                              child: _SolutionDropdown(
                                label: 'Solution A',
                                solutions: solutions,
                                value: _aId,
                                onChanged: (v) => setState(() => _aId = v),
                              ),
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: _SolutionDropdown(
                                label: 'Solution B',
                                solutions: solutions,
                                value: _bId,
                                onChanged: (v) => setState(() => _bId = v),
                              ),
                            ),
                          ],
                        );
                      },
                    ),
                    if (diffAsync != null) ...[
                      const MonoLabel('Diff summary'),
                      diffAsync.when(
                        loading: () => const Padding(
                          padding: EdgeInsets.all(24),
                          child: Center(child: CircularProgressIndicator()),
                        ),
                        error: (e, _) => BlockCard(
                          child: Text('Failed: $e', style: BlockType.bodySm),
                        ),
                        data: _DiffView.new,
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SolutionDropdown extends StatelessWidget {
  const _SolutionDropdown({
    required this.label,
    required this.solutions,
    required this.value,
    required this.onChanged,
  });
  final String label;
  final List<api.SolutionResponse> solutions;
  final int? value;
  final ValueChanged<int?> onChanged;

  @override
  Widget build(BuildContext context) {
    return BlockCard(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label.toUpperCase(), style: BlockType.monoLabel.copyWith(fontSize: 10)),
          const SizedBox(height: 2),
          DropdownButtonHideUnderline(
            child: DropdownButton<int>(
              value: value,
              hint: Text('Pick…', style: BlockType.body.copyWith(color: BlockColors.ink3)),
              isExpanded: true,
              items: [
                for (final s in solutions)
                  DropdownMenuItem(
                    value: s.id,
                    child: Text(
                      '#${s.id} · ${(s.isPublished ?? false) ? "live" : "draft"}',
                      style: BlockType.body,
                    ),
                  ),
              ],
              onChanged: onChanged,
            ),
          ),
        ],
      ),
    );
  }
}

class _DiffView extends StatelessWidget {
  const _DiffView(this.diff);
  final api.SolutionDiffResponse diff;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        BlockCard(
          child: Row(
            children: [
              _DiffStat(label: 'ADDED', value: '+${diff.added.length}', color: BlockColors.success),
              _DiffStat(label: 'REMOVED', value: '−${diff.removed.length}', color: BlockColors.danger),
              _DiffStat(label: 'UNCHANGED', value: '${diff.unchangedCount}', color: BlockColors.ink1),
              _DiffStat(label: 'AFFECTED', value: '${diff.affectedPersons.length}', color: BlockColors.accent),
            ],
          ),
        ),
        if (diff.removed.isNotEmpty) ...[
          MonoLabel('Removed · ${diff.removed.length}'),
          for (final c in diff.removed) _ChangeRow(change: c, sign: '−', color: BlockColors.danger),
        ],
        if (diff.added.isNotEmpty) ...[
          MonoLabel('Added · ${diff.added.length}'),
          for (final c in diff.added) _ChangeRow(change: c, sign: '+', color: BlockColors.success),
        ],
        if (diff.added.isEmpty && diff.removed.isEmpty)
          BlockCard(
            child: Text(
              'These two solutions are identical.',
              style: BlockType.bodySm,
            ),
          ),
      ],
    );
  }
}

class _DiffStat extends StatelessWidget {
  const _DiffStat({required this.label, required this.value, required this.color});
  final String label;
  final String value;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: BlockType.monoLabel.copyWith(fontSize: 9)),
          const SizedBox(height: 2),
          Text(
            value,
            style: BlockType.subhead.copyWith(fontSize: 20, color: color),
          ),
        ],
      ),
    );
  }
}

class _ChangeRow extends StatelessWidget {
  const _ChangeRow({required this.change, required this.sign, required this.color});
  final api.AssignmentChange change;
  final String sign;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: BlockCard(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        child: Row(
          children: [
            SizedBox(
              width: 16,
              child: Text(
                sign,
                style: BlockType.subhead.copyWith(color: color, fontSize: 18),
                textAlign: TextAlign.center,
              ),
            ),
            const SizedBox(width: 6),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(change.personId, style: BlockType.body.copyWith(fontSize: 14)),
                  const SizedBox(height: 2),
                  Text(
                    '${(change.role ?? "—").toUpperCase()} · EVENT ${change.eventId.toUpperCase()}',
                    style: BlockType.monoTiny.copyWith(fontSize: 10),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
