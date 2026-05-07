// AssignmentDetail flow — Sprint 7.4.
//
// `assignmentDetailProvider.family(int)` derives the row from
// `scheduleProvider`'s already-loaded data instead of re-fetching. The
// schedule is the canonical source — opening a detail page from a
// notification (which we don't have a path for in MVP1) would require a
// dedicated /assignments/{id} GET, which doesn't exist on the backend yet.
//
// Mutation actions (accept/decline/swap) live on
// `AssignmentMutationsController` so callsites don't have to hold a Dio /
// AuthState themselves. Successful mutations invalidate the schedule.

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/api/api_client.dart';
import 'package:signupflow_mobile/features/volunteer/schedule_provider.dart';

/// Returns the schedule row for the given assignment id if it's already present in
/// the loaded schedule, otherwise null. Wraps the schedule's loading/error
/// state so the screen can show the same spinners as the list.
final assignmentDetailProvider =
    Provider.family<AsyncValue<ScheduleRow?>, int>((ref, assignmentId) {
  final schedule = ref.watch(scheduleProvider);
  return schedule.whenData((data) {
    for (final g in data.groups) {
      for (final r in g.rows) {
        if (r.assignment.id == assignmentId) return r;
      }
    }
    return null;
  });
});

enum MutationStatus { idle, busy, error }

class MutationState {
  const MutationState({this.status = MutationStatus.idle, this.error});
  final MutationStatus status;
  final String? error;

  MutationState busy() => const MutationState(status: MutationStatus.busy);
  MutationState fail(String msg) =>
      MutationState(status: MutationStatus.error, error: msg);
  MutationState idle() => const MutationState();
}

class AssignmentMutationsController extends Notifier<MutationState> {
  @override
  MutationState build() => const MutationState();

  /// Accept. Returns null on success or error message on failure.
  Future<String?> accept(int assignmentId) async {
    state = state.busy();
    try {
      await ref
          .read(signupflowApiProvider)
          .getAssignmentsApi()
          .acceptAssignment(assignmentId: assignmentId);
      ref.invalidate(scheduleProvider);
      state = state.idle();
      return null;
    } on Exception catch (e) {
      final msg = _readableError(e);
      state = state.fail(msg);
      return msg;
    }
  }

  /// Decline. `reason` is required on the backend even when blank-ish.
  Future<String?> decline(int assignmentId, String reason) async {
    state = state.busy();
    try {
      final body = (api.AssignmentDeclineRequestBuilder()
            ..declineReason = reason.trim().isEmpty
                ? 'No reason provided'
                : reason.trim())
          .build();
      await ref.read(signupflowApiProvider).getAssignmentsApi().declineAssignment(
            assignmentId: assignmentId,
            assignmentDeclineRequest: body,
          );
      ref.invalidate(scheduleProvider);
      state = state.idle();
      return null;
    } on Exception catch (e) {
      final msg = _readableError(e);
      state = state.fail(msg);
      return msg;
    }
  }

  /// Request a swap. `note` is optional.
  Future<String?> requestSwap(int assignmentId, String? note) async {
    state = state.busy();
    try {
      final builder = api.AssignmentSwapRequestBuilder();
      if (note != null && note.trim().isNotEmpty) builder.note = note.trim();
      await ref.read(signupflowApiProvider).getAssignmentsApi().requestSwap(
            assignmentId: assignmentId,
            assignmentSwapRequest: builder.build(),
          );
      ref.invalidate(scheduleProvider);
      state = state.idle();
      return null;
    } on Exception catch (e) {
      final msg = _readableError(e);
      state = state.fail(msg);
      return msg;
    }
  }

  static String _readableError(Object e) {
    final raw = e.toString();
    return raw.length > 160 ? '${raw.substring(0, 160)}…' : raw;
  }
}

final assignmentMutationsProvider =
    NotifierProvider<AssignmentMutationsController, MutationState>(
  AssignmentMutationsController.new,
);
