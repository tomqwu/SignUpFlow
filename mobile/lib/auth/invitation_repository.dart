// InvitationRepository — verify invitation tokens and accept them.

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/api/api_client.dart';
import 'package:signupflow_mobile/auth/auth_provider.dart';
import 'package:signupflow_mobile/auth/login_repository.dart';
import 'package:signupflow_mobile/auth/secure_token_storage.dart';

class InvitationPreview {
  const InvitationPreview({
    required this.token,
    required this.orgId,
    required this.invitedName,
    required this.invitedEmail,
    required this.invitedBy,
    required this.roles,
  });
  final String token;
  final String orgId;
  final String invitedName;
  final String invitedEmail;
  final String invitedBy;
  final List<String> roles;
}

class InvitationRepository {
  InvitationRepository(this._client, this._storage);
  final api.SignupflowApi _client;
  final SecureTokenStorage _storage;

  /// Verify an invitation token and return a preview of the invitation.
  /// Throws [InvitationFailure] if the token is missing/used/expired.
  Future<InvitationPreview> verify(String token) async {
    try {
      final res = await _client.getInvitationsApi().verifyInvitation(
            token: token,
          );
      final body = res.data;
      if (body == null) {
        throw const InvitationFailure('Server returned an empty response.');
      }
      if (!body.valid || body.invitation == null) {
        throw InvitationFailure(
          body.message ?? 'This invitation is no longer valid.',
        );
      }
      final inv = body.invitation!;
      return InvitationPreview(
        token: token,
        orgId: inv.orgId,
        invitedName: inv.name,
        invitedEmail: inv.email,
        invitedBy: inv.invitedBy,
        roles: inv.roles.toList(),
      );
    } on DioException catch (e) {
      final code = e.response?.statusCode;
      if (code == 404) {
        throw const InvitationFailure('Invitation not found.');
      }
      throw InvitationFailure('Network error: ${e.message ?? code}');
    }
  }

  /// Accept an invitation. On success, persists the token and returns the
  /// auth state to apply.
  Future<AuthState> accept({
    required String token,
    required String password,
    String? timezone,
  }) async {
    try {
      final body = (api.InvitationAcceptBuilder()
            ..password = password
            ..timezone = timezone ?? 'UTC')
          .build();
      final res = await _client.getInvitationsApi().acceptInvitation(
            token: token,
            invitationAccept: body,
          );
      final data = res.data;
      if (data == null || data.token.isEmpty) {
        throw const InvitationFailure('Server returned an empty token.');
      }
      await _storage.writeToken(data.token);
      // Persist the refresh token (Sprint 9 PR 9.4b makes invitation accept
      // mint real JWT pairs like login/signup). Pre-9.4b backends omit the
      // field; treat null/empty as "no refresh — fall back to re-login".
      // Mirror login_repository / signup_repository: clear any prior refresh
      // token when the response omits one, so accepting an invitation can't
      // inherit the previous session's refresh credential.
      final refreshToken = data.refreshToken;
      if (refreshToken != null && refreshToken.isNotEmpty) {
        await _storage.writeRefreshToken(refreshToken);
      } else {
        await _storage.clearRefreshToken();
      }
      return AuthState(
        role: LoginRepository.resolveRole(data.roles.toList()),
        token: data.token,
        personId: data.personId,
        email: data.email,
        orgId: data.orgId,
        name: data.name,
      );
    } on DioException catch (e) {
      final code = e.response?.statusCode;
      if (code == 404) {
        throw const InvitationFailure('Invitation not found.');
      }
      if (code == 409) {
        throw const InvitationFailure('This invitation has already been used.');
      }
      if (code == 410) {
        throw const InvitationFailure('This invitation has expired.');
      }
      if (code == 422) {
        throw const InvitationFailure('Password did not pass validation.');
      }
      throw InvitationFailure('Network error: ${e.message ?? code}');
    }
  }
}

class InvitationFailure implements Exception {
  const InvitationFailure(this.message);
  final String message;
  @override
  String toString() => message;
}

final invitationRepositoryProvider = Provider<InvitationRepository>((ref) {
  return InvitationRepository(
    ref.watch(signupflowApiProvider),
    ref.watch(secureTokenStorageProvider),
  );
});
