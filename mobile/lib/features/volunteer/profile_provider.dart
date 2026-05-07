// Profile flow — Sprint 7.6.
//
// Loads PersonMe (PeopleApi.getCurrentPerson) + CalendarSubscriptionResponse
// (CalendarApi.getSubscriptionUrl) in parallel. Reset-token mutation calls
// CalendarApi.resetCalendarToken (self-reset; admin-reset is a separate
// endpoint we don't surface in the volunteer profile).

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/api/api_client.dart';
import 'package:signupflow_mobile/auth/auth_provider.dart';

class ProfileData {
  const ProfileData({required this.person, this.subscription});
  final api.PersonResponse person;
  final api.CalendarSubscriptionResponse? subscription;
}

final profileProvider = FutureProvider<ProfileData>((ref) async {
  final personId = ref.watch(authProvider).personId;
  final apiClient = ref.watch(signupflowApiProvider);

  final personFuture = apiClient.getPeopleApi().getCurrentPerson();
  // Subscription URL is per-person; only fetchable if we know our id.
  final subFuture = personId == null
      ? Future<api.CalendarSubscriptionResponse?>.value(null)
      : apiClient
          .getCalendarApi()
          .getSubscriptionUrl(personId: personId)
          .then((r) => r.data);

  final results = await Future.wait([personFuture, subFuture]);
  final person = (results[0] as dynamic).data as api.PersonResponse?;
  if (person == null) {
    throw StateError('Empty /people/me response');
  }
  final sub = results[1] as api.CalendarSubscriptionResponse?;
  return ProfileData(person: person, subscription: sub);
});

class ProfileMutationsController extends Notifier<bool> {
  @override
  bool build() => false;

  /// Reset calendar token. Returns null on success or an error message.
  Future<String?> resetToken() async {
    final personId = ref.read(authProvider).personId;
    if (personId == null) return 'Not signed in';
    state = true;
    try {
      await ref
          .read(signupflowApiProvider)
          .getCalendarApi()
          .resetCalendarToken(personId: personId);
      ref.invalidate(profileProvider);
      state = false;
      return null;
    } on Exception catch (e) {
      state = false;
      return e.toString();
    }
  }
}

final profileMutationsProvider =
    NotifierProvider<ProfileMutationsController, bool>(
  ProfileMutationsController.new,
);
