// LoginRepository — wraps AuthApi + secure storage. Returns the resolved
// AuthState (or throws) so AuthController stays declarative.

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:signupflow_mobile/api/auth_api.dart';
import 'package:signupflow_mobile/api/models.dart';
import 'package:signupflow_mobile/auth/auth_provider.dart';
import 'package:signupflow_mobile/auth/secure_token_storage.dart';

class LoginRepository {
  LoginRepository(this._authApi, this._storage);
  final AuthApi _authApi;
  final SecureTokenStorage _storage;

  /// Sign in. On success, persists the token in secure storage and returns
  /// the auth state to apply. Throws [LoginFailure] on bad creds / network.
  Future<AuthState> signIn(String email, String password) async {
    try {
      final res = await _authApi.login(
        LoginRequest(email: email, password: password),
      );
      if (res.token.isEmpty) {
        throw const LoginFailure('Server returned an empty token');
      }
      await _storage.writeToken(res.token);
      return AuthState(role: _resolveRole(res.roles), token: res.token);
    } on DioException catch (e) {
      final code = e.response?.statusCode;
      if (code == 401 || code == 403) {
        throw const LoginFailure('Wrong email or password');
      }
      throw LoginFailure('Network error: ${e.message ?? code}');
    }
  }

  Future<void> signOut() => _storage.clearToken();

  static AuthRole _resolveRole(List<String> roles) {
    final lower = roles.map((r) => r.toLowerCase()).toSet();
    if (lower.contains('admin')) return AuthRole.admin;
    if (lower.contains('volunteer')) return AuthRole.volunteer;
    return AuthRole.unauth;
  }
}

class LoginFailure implements Exception {
  const LoginFailure(this.message);
  final String message;
  @override
  String toString() => message;
}

final loginRepositoryProvider = Provider<LoginRepository>((ref) {
  return LoginRepository(
    ref.watch(authApiProvider),
    ref.watch(secureTokenStorageProvider),
  );
});
