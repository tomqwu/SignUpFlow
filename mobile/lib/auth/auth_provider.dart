// Stub auth — Sprint 7.1 only. Real JWT/Keychain flow lands in 7.2.
// Provides `role` (volunteer | admin | unauth) so GoRouter can branch.

import 'package:flutter_riverpod/flutter_riverpod.dart';

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

  // Demo shortcuts that the prototype uses too. Real /auth/login lands in 7.2.
  void demoSignInVolunteer() =>
      state = state.copyWith(role: AuthRole.volunteer, token: 'demo-volunteer');

  void demoSignInAdmin() =>
      state = state.copyWith(role: AuthRole.admin, token: 'demo-admin');

  void signOut() => state = const AuthState();
}

final authProvider = NotifierProvider<AuthController, AuthState>(
  AuthController.new,
);
