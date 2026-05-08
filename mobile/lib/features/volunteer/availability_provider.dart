// Availability flow — Sprint 7.5 + Sprint 8.9.
//
// Wraps three groups of endpoints:
// - TimeOff (multi-day vacation periods): listed since 7.5.
// - Recurring rrule (single string per person): added Sprint 8.3, wired here.
// - Single-date exceptions: added Sprint 8.2, wired here.

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

class ExceptionEntry {
  const ExceptionEntry({required this.id, required this.date});
  final int id;
  final DateTime date;
}

class AvailabilityData {
  const AvailabilityData({
    required this.entries,
    this.exceptions = const [],
  });
  final List<TimeOffEntry> entries;
  final List<ExceptionEntry> exceptions;

  Set<DateTime> get blockedDays {
    final s = <DateTime>{};
    for (final e in entries) {
      s.addAll(e.daysCovered());
    }
    for (final e in exceptions) {
      s.add(e.date);
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

DateTime _dateOnly(api.Date d) => DateTime(d.year, d.month, d.day);

final availabilityProvider = FutureProvider<AvailabilityData>((ref) async {
  final personId = ref.watch(authProvider).personId;
  if (personId == null) return const AvailabilityData(entries: []);

  final apiClient = ref.watch(signupflowApiProvider);

  // Time-off (existing pre-Sprint-8 endpoint — still returns JsonObject).
  final res = await apiClient.getAvailabilityApi().getTimeoff(personId: personId);
  final body = res.data;
  final entries = <TimeOffEntry>[];
  if (body != null) {
    final decoded = json.decode(body.toString());
    if (decoded is Map<String, dynamic>) {
      final raw = decoded['timeoff'];
      if (raw is List) {
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
      }
    }
  }

  // Single-date exceptions (Sprint 8.2). Typed list response.
  final excRes = await apiClient
      .getAvailabilityApi()
      .listExceptions(personId: personId);
  final exceptions = <ExceptionEntry>[];
  for (final row in excRes.data ?? const <api.AvailabilityExceptionResponse>[]) {
    exceptions.add(ExceptionEntry(id: row.id, date: _dateOnly(row.exceptionDate)));
  }
  exceptions.sort((a, b) => a.date.compareTo(b.date));

  return AvailabilityData(entries: entries, exceptions: exceptions);
});

/// Single rrule string per person (null when unset).
final availabilityRruleProvider = FutureProvider<String?>((ref) async {
  final personId = ref.watch(authProvider).personId;
  if (personId == null) return null;
  final apiClient = ref.watch(signupflowApiProvider);
  final res = await apiClient.getAvailabilityApi().getRrule(personId: personId);
  return res.data?.rrule;
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

  Future<String?> addException(DateTime date) async {
    final personId = ref.read(authProvider).personId;
    if (personId == null) return 'Not signed in';
    state = true;
    try {
      final body = (api.AvailabilityExceptionCreateBuilder()
            ..exceptionDate = api.Date(date.year, date.month, date.day))
          .build();
      await ref.read(signupflowApiProvider).getAvailabilityApi().addException(
            personId: personId,
            availabilityExceptionCreate: body,
          );
      ref.invalidate(availabilityProvider);
      state = false;
      return null;
    } on Exception catch (e) {
      state = false;
      return e.toString();
    }
  }

  Future<String?> deleteException(int exceptionId) async {
    final personId = ref.read(authProvider).personId;
    if (personId == null) return 'Not signed in';
    state = true;
    try {
      await ref
          .read(signupflowApiProvider)
          .getAvailabilityApi()
          .deleteException(personId: personId, exceptionId: exceptionId);
      ref.invalidate(availabilityProvider);
      state = false;
      return null;
    } on Exception catch (e) {
      state = false;
      return e.toString();
    }
  }

  Future<String?> setRrule(String rrule) async {
    final personId = ref.read(authProvider).personId;
    if (personId == null) return 'Not signed in';
    state = true;
    try {
      final body = (api.AvailabilityRruleUpdateBuilder()..rrule = rrule).build();
      await ref.read(signupflowApiProvider).getAvailabilityApi().setRrule(
            personId: personId,
            availabilityRruleUpdate: body,
          );
      ref.invalidate(availabilityRruleProvider);
      state = false;
      return null;
    } on Exception catch (e) {
      state = false;
      return e.toString();
    }
  }

  Future<String?> clearRrule() async {
    final personId = ref.read(authProvider).personId;
    if (personId == null) return 'Not signed in';
    state = true;
    try {
      await ref
          .read(signupflowApiProvider)
          .getAvailabilityApi()
          .clearRrule(personId: personId);
      ref.invalidate(availabilityRruleProvider);
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

/// Friendly preset → raw RRULE string. Used by the rrule editor card.
class RrulePreset {
  const RrulePreset({required this.label, required this.rrule});
  final String label;
  final String rrule;
}

const List<RrulePreset> kRrulePresets = [
  RrulePreset(label: 'Every Monday', rrule: 'FREQ=WEEKLY;BYDAY=MO'),
  RrulePreset(label: 'Every Friday', rrule: 'FREQ=WEEKLY;BYDAY=FR'),
  RrulePreset(label: 'Every weekend', rrule: 'FREQ=WEEKLY;BYDAY=SA,SU'),
  RrulePreset(label: 'Every other Friday', rrule: 'FREQ=WEEKLY;INTERVAL=2;BYDAY=FR'),
  RrulePreset(label: 'First Sunday of month', rrule: 'FREQ=MONTHLY;BYDAY=1SU'),
];
