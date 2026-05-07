// AuthController — Riverpod state for token + role.
// Real signIn lands in PR 7.2 (this file). Demo shortcuts retained for
// offline dev and the widget smoke test.

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:signupflow_mobile/auth/login_repository.dart';
import 'package:signupflow_mobile/auth/secure_token_storage.dart';

enum AuthRole { unauth, volunteer, admin }

class AuthState {
  const AuthState({this.role = AuthRole.unauth, this.token});
  final AuthRole role;
  final String? token;

  AuthState copyWith({AuthRole? role, String? token}) =>
      AuthState(role: role ?? this.role, token: token ?? this.token);
}

class AuthController extends Notifier<AuthState> {
  @override
  AuthState build() => const AuthState();

  /// Real /auth/login + secure storage. Returns null on success;
  /// returns a user-facing error message on failure.
  Future<String?> signIn(String email, String password) async {
    try {
      final next = await ref
          .read(loginRepositoryProvider)
          .signIn(email.trim(), password);
      state = next;
      return null;
    } on LoginFailure catch (e) {
      return e.message;
    } on Exception catch (e) {
      return 'Unexpected error: $e';
    }
  }

  // Demo shortcuts — bypass /auth/login. Useful for design review and the
  // smoke widget test (no network). NOT included in production builds via
  // a const guard once we add release flavours; for now they're always on.
  void demoSignInVolunteer() =>
      state = state.copyWith(role: AuthRole.volunteer, token: 'demo-volunteer');

  void demoSignInAdmin() =>
      state = state.copyWith(role: AuthRole.admin, token: 'demo-admin');

  Future<void> signOut() async {
    await ref.read(secureTokenStorageProvider).clearToken();
    state = const AuthState();
  }
}

final authProvider = NotifierProvider<AuthController, AuthState>(
  AuthController.new,
);
