// People list + invite — Sprint 7.8.

import 'package:built_collection/built_collection.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/api/api_client.dart';
import 'package:signupflow_mobile/auth/auth_provider.dart';

final peopleProvider = FutureProvider<List<api.PersonResponse>>((ref) async {
  final orgId = ref.watch(authProvider).orgId;
  if (orgId == null) return const [];
  final res = await ref
      .watch(signupflowApiProvider)
      .getPeopleApi()
      .listPeople(orgId: orgId, limit: 200);
  return res.data?.items.toList() ?? const [];
});

class InviteController extends Notifier<bool> {
  @override
  bool build() => false;

  Future<String?> invite({
    required String name,
    required String email,
    required List<String> roles,
  }) async {
    final orgId = ref.read(authProvider).orgId;
    if (orgId == null) return 'Not signed in';
    state = true;
    try {
      final body = (api.InvitationCreateBuilder()
            ..name = name
            ..email = email
            ..roles = ListBuilder<String>(roles))
          .build();
      await ref
          .read(signupflowApiProvider)
          .getInvitationsApi()
          .createInvitation(orgId: orgId, invitationCreate: body);
      ref.invalidate(peopleProvider);
      state = false;
      return null;
    } on Exception catch (e) {
      state = false;
      return e.toString();
    }
  }
}

final inviteControllerProvider =
    NotifierProvider<InviteController, bool>(InviteController.new);
