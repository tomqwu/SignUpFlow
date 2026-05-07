// Admin Events — Sprint 7.8.
// Visual target: mobile/prototype/screenshots/v2/10-a-events.png.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/features/admin/events_provider.dart';
import 'package:signupflow_mobile/theme/colors.dart';
import 'package:signupflow_mobile/theme/components.dart';
import 'package:signupflow_mobile/theme/typography.dart';

class EventsScreen extends ConsumerWidget {
  const EventsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncData = ref.watch(eventsProvider);
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
                      const SnackBar(content: Text('Create event lands in 7.10+')),
                    ),
                    style: TextButton.styleFrom(foregroundColor: BlockColors.accent),
                    child: Text(
                      '+ NEW',
                      style: BlockType.monoLabel.copyWith(
                        color: BlockColors.accent,
                        fontSize: 13,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const PageTitle('Events'),
            Expanded(
              child: asyncData.when(
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (e, _) => Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Text('Failed to load: $e', style: BlockType.bodySm),
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
  final EventsData data;

  @override
  Widget build(BuildContext context) {
    final upcoming = data.events
        .where((e) => e.startTime.toLocal().isAfter(DateTime.now().subtract(const Duration(hours: 1))))
        .take(20)
        .toList();
    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(16, 0, 16, 96),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          MonoLabel('Upcoming · ${upcoming.length}'),
          if (upcoming.isEmpty)
            BlockCard(
              child: Text(
                'No upcoming events. Add one with + NEW above.',
                style: BlockType.bodySm,
              ),
            )
          else
            for (final e in upcoming) _EventRow(event: e),
          MonoLabel('Recurring series · ${data.series.length}'),
          if (data.series.isEmpty)
            BlockCard(
              child: Text(
                'No recurring series defined yet.',
                style: BlockType.bodySm,
              ),
            )
          else
            for (final s in data.series) _SeriesRow(series: s),
        ],
      ),
    );
  }
}

class _EventRow extends StatelessWidget {
  const _EventRow({required this.event});
  final api.EventResponse event;

  @override
  Widget build(BuildContext context) {
    final start = event.startTime.toLocal();
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: BlockCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              DateFormat('EEE d MMM · HH:mm').format(start).toUpperCase(),
              style: BlockType.monoTiny.copyWith(fontSize: 10),
            ),
            const SizedBox(height: 4),
            Text(event.type, style: BlockType.subhead),
            const SizedBox(height: 4),
            Text('Event ${event.id}', style: BlockType.bodySm),
          ],
        ),
      ),
    );
  }
}

class _SeriesRow extends StatelessWidget {
  const _SeriesRow({required this.series});
  final api.RecurringSeriesResponse series;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: BlockCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(series.title, style: BlockType.subhead),
            const SizedBox(height: 4),
            Text(
              '${series.patternType.toUpperCase()} · '
              'EVERY ${series.frequencyInterval} ${series.weekdayName ?? ""}',
              style: BlockType.monoTiny.copyWith(fontSize: 10),
            ),
          ],
        ),
      ),
    );
  }
}
