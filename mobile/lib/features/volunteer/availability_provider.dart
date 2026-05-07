// Availability flow — Sprint 7.5.
//
// The OpenAPI snapshot only exposes TimeOff endpoints (multi-day vacation
// periods). The Sprint 5 backend work that added single-date exceptions +
// rrule rules is consumed by the solver but doesn't have CRUD routes yet —
// so the recurring-rules section in mobile/prototype/screenshots/v2/05-…
// stays in a "coming soon" state until the backend exposes those endpoints.

import 'dart:convert';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/api/api_client.dart';
import 'package:signupflow_mobile/auth/auth_provider.dart';

class TimeOffEntry {
  const TimeOffEntry({
    required this.id,
    required this.startDate,
    required this.endDate,
    this.reason,
  });
  final int id;
  final DateTime startDate; // local date (parsed from "YYYY-MM-DD")
  final DateTime endDate;
  final String? reason;

  /// All days in the inclusive range — used to mark the calendar grid.
  Iterable<DateTime> daysCovered() sync* {
    var d = startDate;
    while (!d.isAfter(endDate)) {
      yield d;
      d = d.add(const Duration(days: 1));
    }
  }
}

class AvailabilityData {
  const AvailabilityData({required this.entries});
  final List<TimeOffEntry> entries;

  Set<DateTime> get blockedDays {
    final s = <DateTime>{};
    for (final e in entries) {
      s.addAll(e.daysCovered());
    }
    return s;
  }
}

DateTime _parseDate(String iso) {
  // FastAPI returns "YYYY-MM-DD" (no timezone). Parse as a calendar date
  // anchored at local midnight so calendar grid math is straightforward.
  final parts = iso.split('-').map(int.parse).toList();
  return DateTime(parts[0], parts[1], parts[2]);
}

final availabilityProvider = FutureProvider<AvailabilityData>((ref) async {
  final personId = ref.watch(authProvider).personId;
  if (personId == null) return const AvailabilityData(entries: []);

  final apiClient = ref.watch(signupflowApiProvider);
  final res = await apiClient.getAvailabilityApi().getTimeoff(personId: personId);
  final body = res.data;
  if (body == null) return const AvailabilityData(entries: []);

  // body is JsonObject — re-encode + decode to plain Dart types.
  final decoded = json.decode(body.toString());
  if (decoded is! Map<String, dynamic>) {
    return const AvailabilityData(entries: []);
  }
  final raw = decoded['timeoff'];
  if (raw is! List) return const AvailabilityData(entries: []);

  final entries = <TimeOffEntry>[];
  for (final e in raw) {
    if (e is! Map<String, dynamic>) continue;
    entries.add(TimeOffEntry(
      id: (e['id'] as num).toInt(),
      startDate: _parseDate(e['start_date'] as String),
      endDate: _parseDate(e['end_date'] as String),
      reason: e['reason'] as String?,
    ));
  }
  entries.sort((a, b) => a.startDate.compareTo(b.startDate));
  return AvailabilityData(entries: entries);
});

class AvailabilityMutationsController extends Notifier<bool> {
  @override
  bool build() => false; // busy flag

  Future<String?> addTimeoff(DateTime start, DateTime end, String? reason) async {
    final personId = ref.read(authProvider).personId;
    if (personId == null) return 'Not signed in';
    state = true;
    try {
      final body = (api.TimeOffCreateBuilder()
            ..startDate = api.Date(start.year, start.month, start.day)
            ..endDate = api.Date(end.year, end.month, end.day)
            ..reason = reason)
          .build();
      await ref.read(signupflowApiProvider).getAvailabilityApi().addTimeoff(
            personId: personId,
            timeOffCreate: body,
          );
      ref.invalidate(availabilityProvider);
      state = false;
      return null;
    } on Exception catch (e) {
      state = false;
      return e.toString();
    }
  }

  Future<String?> deleteTimeoff(int timeoffId) async {
    final personId = ref.read(authProvider).personId;
    if (personId == null) return 'Not signed in';
    state = true;
    try {
      await ref.read(signupflowApiProvider).getAvailabilityApi().deleteTimeoff(
            personId: personId,
            timeoffId: timeoffId,
          );
      ref.invalidate(availabilityProvider);
      state = false;
      return null;
    } on Exception catch (e) {
      state = false;
      return e.toString();
    }
  }
}

final availabilityMutationsProvider =
    NotifierProvider<AvailabilityMutationsController, bool>(
  AvailabilityMutationsController.new,
);
