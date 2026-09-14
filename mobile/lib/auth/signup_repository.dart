// SignupRepository — atomically creates an organization and its first admin
// through POST /auth/signup (see api/routers/auth.py).

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/api/api_client.dart';
import 'package:signupflow_mobile/auth/auth_provider.dart';
import 'package:signupflow_mobile/auth/login_repository.dart';
import 'package:signupflow_mobile/auth/secure_token_storage.dart';

class SignupRepository {
  SignupRepository(this._client, this._storage);
  final api.SignupflowApi _client;
  final SecureTokenStorage _storage;

  /// Atomically create a fresh organization and its first admin account.
  /// Returns the resulting auth state on success; throws [SignupFailure].
  Future<AuthState> createOrgAndSignUp({
    required String orgId,
    required String orgName,
    required String adminName,
    required String email,
    required String password,
  }) async {
    try {
      final signupReq = (api.SignupRequestBuilder()
            ..orgId = orgId
            ..orgName = orgName
            ..name = adminName
            ..email = email
            ..password = password)
          .build();
      final res = await _client.getAuthApi().signup(signupRequest: signupReq);
      final body = res.data;
      if (body == null || body.token.isEmpty) {
        throw const SignupFailure('Server returned an empty token.');
      }
      await _storage.writeToken(body.token);
      // Mirror login_repository: clear any prior refresh token if the server
      // didn't issue one, so a brand-new account can't inherit the previous
      // user's refresh credential.
      final refreshToken = body.refreshToken;
      if (refreshToken != null && refreshToken.isNotEmpty) {
        await _storage.writeRefreshToken(refreshToken);
      } else {
        await _storage.clearRefreshToken();
      }
      return AuthState(
        role: LoginRepository.resolveRole(body.roles.toList()),
        token: body.token,
        personId: body.personId,
        email: body.email,
        orgId: body.orgId,
        name: body.name,
      );
    } on DioException catch (e) {
      final code = e.response?.statusCode;
      if (code == 409) {
        throw const SignupFailure(
          'That organization ID or email is already in use.',
        );
      }
      if (code == 422) {
        throw const SignupFailure('Organization or account details are invalid.');
      }
      throw SignupFailure('Network error: ${e.message ?? code}');
    }
  }
}

class SignupFailure implements Exception {
  const SignupFailure(this.message);
  final String message;
  @override
  String toString() => message;
}

final signupRepositoryProvider = Provider<SignupRepository>((ref) {
  return SignupRepository(
    ref.watch(signupflowApiProvider),
    ref.watch(secureTokenStorageProvider),
  );
});
