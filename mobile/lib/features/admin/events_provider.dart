// Events list + recurring series — Sprint 7.8.

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/api/api_client.dart';
import 'package:signupflow_mobile/auth/auth_provider.dart';

class EventsData {
  const EventsData({required this.events, required this.series});
  final List<api.EventResponse> events;
  final List<api.RecurringSeriesResponse> series;
}

final eventsProvider = FutureProvider<EventsData>((ref) async {
  final orgId = ref.watch(authProvider).orgId;
  if (orgId == null) return const EventsData(events: [], series: []);

  final apiClient = ref.watch(signupflowApiProvider);
  final futures = await Future.wait([
    apiClient.getEventsApi().listEvents(orgId: orgId, limit: 100),
    apiClient.getRecurringEventsApi().listRecurringSeries(orgId: orgId),
  ]);

  final events = ((futures[0] as dynamic).data
              as api.ListResponseEventResponse?)
          ?.items
          .toList() ??
      const <api.EventResponse>[];
  final series = ((futures[1] as dynamic).data
              as api.ListResponseRecurringSeriesResponse?)
          ?.items
          .toList() ??
      const <api.RecurringSeriesResponse>[];

  events.sort((a, b) => a.startTime.compareTo(b.startTime));
  return EventsData(events: events, series: series);
});
