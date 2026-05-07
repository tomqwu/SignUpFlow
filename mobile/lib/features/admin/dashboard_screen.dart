// Admin Dashboard — Sprint 7.7.
// Visual target: mobile/prototype/screenshots/v2/08-a-dashboard.png.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/features/admin/dashboard_provider.dart';
import 'package:signupflow_mobile/theme/colors.dart';
import 'package:signupflow_mobile/theme/components.dart';
import 'package:signupflow_mobile/theme/typography.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncData = ref.watch(dashboardProvider);
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
                    onPressed: () => ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Org settings drawer comes in 7.10+'),
                      ),
                    ),
                    style: TextButton.styleFrom(foregroundColor: BlockColors.accent),
                    child: Text(
                      'SETTINGS',
                      style: BlockType.monoLabel.copyWith(
                        color: BlockColors.accent,
                        fontSize: 13,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const PageTitle('Dashboard'),
            Expanded(
              child: asyncData.when(
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (e, _) => Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Text(
                      'Failed to load dashboard: $e',
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

class _Body extends StatelessWidget {
  const _Body({required this.data});
  final DashboardData data;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(16, 0, 16, 96),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          GridView.count(
            crossAxisCount: 2,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            mainAxisSpacing: 8,
            crossAxisSpacing: 8,
            childAspectRatio: 1.7,
            children: [
              KpiCell(
                value: '${data.activeVolunteers}',
                label: 'Active volunteers',
              ),
              KpiCell(
                value: '${data.eventsThisWeek}',
                label: 'Events this week',
              ),
              KpiCell(
                value: '${data.healthScore.toInt()}',
                unit: '/100',
                label: 'Health score',
                accent: true,
              ),
              _PublishedKpi(
                published: data.publishedSolution,
                publishedAt: data.publishedAt,
              ),
            ],
          ),
          const MonoLabel('Recent solutions'),
          if (data.recentSolutions.isEmpty)
            BlockCard(
              child: Text(
                'No solutions yet. Run the solver to generate the first one.',
                style: BlockType.bodySm,
              ),
            )
          else
            for (final s in data.recentSolutions.take(5))
              _SolutionRow(solution: s),
          const MonoLabel('Quick actions'),
          Row(
            children: [
              Expanded(
                child: BlockButton(
                  label: 'Run solver',
                  kind: BlockButtonKind.go,
                  onPressed: () => GoRouter.of(context).go('/a/solver'),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: BlockButton(
                  label: 'Invite people',
                  kind: BlockButtonKind.secondary,
                  onPressed: () => GoRouter.of(context).go('/a/people'),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _PublishedKpi extends StatelessWidget {
  const _PublishedKpi({required this.published, required this.publishedAt});
  final api.SolutionResponse? published;
  final DateTime? publishedAt;

  @override
  Widget build(BuildContext context) {
    if (published == null) {
      return BlockCard(
        padding: const EdgeInsets.fromLTRB(14, 16, 14, 16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const StatusText(kind: StatusKind.neutral, label: 'NONE LIVE'),
            const SizedBox(height: 6),
            Text('Publish a solution to start.', style: BlockType.bodySm),
            const Spacer(),
            Text('No published solution', style: BlockType.monoTiny),
          ],
        ),
      );
    }
    final ago = publishedAt != null
        ? _relativeAgo(publishedAt!)
        : '—';
    return BlockCard(
      padding: const EdgeInsets.fromLTRB(14, 16, 14, 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const StatusText(kind: StatusKind.confirmed, label: 'PUBLISHED'),
          const SizedBox(height: 4),
          Text(
            ago,
            style: BlockType.body.copyWith(fontSize: 13, fontWeight: FontWeight.w500),
          ),
          const Spacer(),
          Text(
            'Solution #${published!.id}',
            style: BlockType.monoTiny.copyWith(color: BlockColors.ink2),
          ),
        ],
      ),
    );
  }

  static String _relativeAgo(DateTime when) {
    final delta = DateTime.now().difference(when);
    if (delta.inMinutes < 60) return '${delta.inMinutes}m ago';
    if (delta.inHours < 24) return '${delta.inHours}h ago';
    if (delta.inDays < 30) return '${delta.inDays}d ago';
    return DateFormat('d MMM').format(when);
  }
}

class _SolutionRow extends StatelessWidget {
  const _SolutionRow({required this.solution});
  final api.SolutionResponse solution;

  @override
  Widget build(BuildContext context) {
    final isLive = solution.isPublished ?? false;
    final created = DateFormat('d MMM · h:mm a').format(solution.createdAt.toLocal());
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
          onTap: () => GoRouter.of(context).go('/a/solution/${solution.id}'),
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Text('Solution #${solution.id}', style: BlockType.subhead),
                          const SizedBox(width: 8),
                          if (isLive)
                            const StatusText(kind: StatusKind.confirmed, label: 'LIVE')
                          else
                            const StatusText(kind: StatusKind.pending, label: 'DRAFT'),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'HEALTH ${solution.healthScore.toInt()} · ${created.toUpperCase()}',
                        style: BlockType.monoTiny.copyWith(fontSize: 10),
                      ),
                    ],
                  ),
                ),
                const Icon(Icons.chevron_right, color: BlockColors.ink3, size: 20),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
