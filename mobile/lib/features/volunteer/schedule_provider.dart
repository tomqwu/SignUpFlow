// Schedule provider — fetches the volunteer's upcoming assignments and
// joins them with their events client-side. Returns a ScheduleData VM
// grouped by date.
//
// API surface used:
//   AssignmentsApi.listMyAssignments() — paginated assignments for the
//                                         currently-authenticated person.
//   EventsApi.listEvents(orgId: …)     — paginated events for the org;
//                                         joined client-side by event_id.
//
// Why client-side join: the FastAPI shapes don't return event metadata
// embedded in the assignment list. Doing the join here keeps the backend
// thin. Two HTTP calls is fine for MVP scale (a typical volunteer has
// <20 upcoming assignments + <100 events in a 90-day window).

import 'package:dio/dio.dart' show Response;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/api/api_client.dart';
import 'package:signupflow_mobile/auth/auth_provider.dart';

/// One row in the schedule — assignment + the event it points to.
class ScheduleRow {
  const ScheduleRow({required this.assignment, required this.event});
  final api.AssignmentResponse assignment;
  final api.EventResponse event;

  DateTime get start => event.startTime.toLocal();
  DateTime get end => event.endTime.toLocal();
  DateTime get dateKey => DateTime(start.year, start.month, start.day);
}

/// Group of rows on a single calendar day.
class ScheduleGroup {
  const ScheduleGroup({required this.date, required this.rows});
  final DateTime date;
  final List<ScheduleRow> rows;
}

/// Top-level schedule VM consumed by ScheduleScreen.
class ScheduleData {
  const ScheduleData({required this.groups});
  final List<ScheduleGroup> groups;
  bool get isEmpty => groups.isEmpty;
}

final scheduleProvider = FutureProvider<ScheduleData>((ref) async {
  final auth = ref.watch(authProvider);
  final orgId = auth.orgId;
  if (orgId == null) {
    // Demo shortcuts skip the auth response, so we may not have an org_id.
    // Empty data is the right behaviour — the screen renders an empty state.
    return const ScheduleData(groups: []);
  }

  final apiClient = ref.watch(signupflowApiProvider);

  // Fire both requests in parallel.
  final futures = await Future.wait([
    apiClient.getAssignmentsApi().listMyAssignments(),
    apiClient.getEventsApi().listEvents(orgId: orgId),
  ]);

  final assignmentsBody = (futures[0] as Response<api.ListResponseAssignmentResponse>).data;
  final eventsBody = (futures[1] as Response<api.ListResponseEventResponse>).data;

  if (assignmentsBody == null || eventsBody == null) {
    return const ScheduleData(groups: []);
  }

  final eventsById = <String, api.EventResponse>{
    for (final e in eventsBody.items) e.id: e,
  };

  final rows = <ScheduleRow>[];
  for (final a in assignmentsBody.items) {
    final ev = eventsById[a.eventId];
    if (ev == null) continue; // assignment for an event the user can't see; skip
    rows.add(ScheduleRow(assignment: a, event: ev));
  }

  rows.sort((x, y) => x.start.compareTo(y.start));

  // Group consecutive rows with the same dateKey.
  final groups = <ScheduleGroup>[];
  for (final r in rows) {
    if (groups.isNotEmpty && groups.last.date == r.dateKey) {
      groups.last.rows.add(r);
    } else {
      groups.add(ScheduleGroup(date: r.dateKey, rows: [r]));
    }
  }

  return ScheduleData(groups: groups);
});
