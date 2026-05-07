// Admin Publish + Rollback — Sprint 7.10.
// Visual target: mobile/prototype/screenshots/v2/14-a-publish.png.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/features/admin/publish_provider.dart';
import 'package:signupflow_mobile/theme/colors.dart';
import 'package:signupflow_mobile/theme/components.dart';
import 'package:signupflow_mobile/theme/typography.dart';

class PublishScreen extends ConsumerWidget {
  const PublishScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncRecent = ref.watch(recentSolutionsProvider);
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
                    'PUBLISH',
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
              child: asyncRecent.when(
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (e, _) => Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Text('Failed: $e', style: BlockType.bodySm),
                  ),
                ),
                data: (solutions) => _Body(solutions: solutions),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _Body extends ConsumerWidget {
  const _Body({required this.solutions});
  final List<api.SolutionResponse> solutions;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    api.SolutionResponse? published;
    for (final s in solutions) {
      if (s.isPublished ?? false) {
        published = s;
        break;
      }
    }
    final pending = solutions.where((s) => !(s.isPublished ?? false)).toList();
    final everPublished = solutions
        .where((s) => s.publishedAt != null && !(s.isPublished ?? false))
        .take(5)
        .toList();
    final busy = ref.watch(publishMutationsProvider);

    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const MonoLabel('Currently published'),
          if (published != null)
            _PublishedCard(published: published, busy: busy)
          else
            BlockCard(
              child: Text(
                'No solution is published yet.',
                style: BlockType.bodySm,
              ),
            ),
          const MonoLabel('Publish a draft'),
          if (pending.isEmpty)
            BlockCard(
              child: Text(
                'No draft solutions to publish.',
                style: BlockType.bodySm,
              ),
            )
          else
            for (final s in pending) _PublishRow(solution: s),
          const MonoLabel('Rollback history'),
          if (everPublished.isEmpty)
            BlockCard(
              child: Text(
                'No prior published solutions yet.',
                style: BlockType.bodySm,
              ),
            )
          else
            for (final s in everPublished) _RollbackRow(solution: s),
        ],
      ),
    );
  }
}

class _PublishedCard extends ConsumerWidget {
  const _PublishedCard({required this.published, required this.busy});
  final api.SolutionResponse published;
  final bool busy;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return BlockCard(
      color: BlockColors.accentSoft,
      borderColor: BlockColors.accent,
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Solution #${published.id}', style: BlockType.subhead),
                const SizedBox(height: 4),
                const StatusText(kind: StatusKind.confirmed, label: 'LIVE'),
                const SizedBox(height: 2),
                Text(
                  'HEALTH ${published.healthScore.toInt()} · ${published.assignmentCount ?? 0} ASSIGNMENTS',
                  style: BlockType.monoTiny.copyWith(fontSize: 10),
                ),
              ],
            ),
          ),
          SizedBox(
            width: 132,
            child: BlockButton(
              label: busy ? 'Working…' : 'Unpublish',
              kind: BlockButtonKind.destructive,
              onPressed: busy
                  ? null
                  : () async {
                      final err = await ref
                          .read(publishMutationsProvider.notifier)
                          .unpublish(published.id);
                      if (!context.mounted) return;
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text(err ?? 'Unpublished')),
                      );
                    },
            ),
          ),
        ],
      ),
    );
  }
}

class _PublishRow extends ConsumerWidget {
  const _PublishRow({required this.solution});
  final api.SolutionResponse solution;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final busy = ref.watch(publishMutationsProvider);
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: BlockCard(
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Solution #${solution.id}', style: BlockType.subhead),
                  const SizedBox(height: 2),
                  Text(
                    'DRAFT · HEALTH ${solution.healthScore.toInt()}',
                    style: BlockType.monoTiny.copyWith(fontSize: 10),
                  ),
                ],
              ),
            ),
            SizedBox(
              width: 110,
              child: BlockButton(
                label: busy ? '…' : 'Publish',
                kind: BlockButtonKind.go,
                onPressed: busy
                    ? null
                    : () async {
                        final err = await ref
                            .read(publishMutationsProvider.notifier)
                            .publish(solution.id);
                        if (!context.mounted) return;
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text(err ?? 'Published')),
                        );
                      },
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _RollbackRow extends ConsumerWidget {
  const _RollbackRow({required this.solution});
  final api.SolutionResponse solution;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final busy = ref.watch(publishMutationsProvider);
    final when = solution.publishedAt != null
        ? DateFormat('d MMM y').format(solution.publishedAt!.toLocal())
        : '—';
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: BlockCard(
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Solution #${solution.id}', style: BlockType.subhead),
                  const SizedBox(height: 2),
                  Text(
                    'PUBLISHED $when · HEALTH ${solution.healthScore.toInt()}',
                    style: BlockType.monoTiny.copyWith(fontSize: 10),
                  ),
                ],
              ),
            ),
            SizedBox(
              width: 120,
              child: BlockButton(
                label: busy ? '…' : 'Rollback',
                kind: BlockButtonKind.secondary,
                onPressed: busy
                    ? null
                    : () async {
                        final err = await ref
                            .read(publishMutationsProvider.notifier)
                            .rollback(solution.id);
                        if (!context.mounted) return;
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text(err ?? 'Rolled back')),
                        );
                      },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
