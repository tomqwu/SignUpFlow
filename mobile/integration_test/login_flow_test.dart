// Sprint 10 PR 10.2 — first integration test (on-device end-to-end).
//
// Drives the app from cold launch through the login screen to the
// authenticated landing. Uses InMemoryTokenStorage (from
// mobile/lib/auth/secure_token_storage.dart) and a fake LoginRepository
// (same pattern as mobile/test/auth_test.dart) so the test doesn't need
// a live backend.
//
// Run via:
//   flutter test integration_test/login_flow_test.dart
//   ... or use mobile/scripts/run_integration_tests.sh to pick a
//   simulator / emulator automatically.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:signupflow_mobile/app.dart';
import 'package:signupflow_mobile/auth/auth_provider.dart';
import 'package:signupflow_mobile/auth/login_repository.dart';
import 'package:signupflow_mobile/auth/secure_token_storage.dart';

class _FakeLoginRepo implements LoginRepository {
  _FakeLoginRepo({this.role = AuthRole.volunteer});
  AuthRole role;

  @override
  Future<AuthState> signIn(String email, String password) async {
    // Echo a token shaped like the real backend's so any consumer that
    // checks length / structure doesn't trip.
    return AuthState(
      role: role,
      token: 'integration-test-access-$email',
      email: email,
      name: 'Test User',
    );
  }

  @override
  Future<void> signOut() async {
    // No-op for the integration test — the storage override handles state.
  }
}

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('Cold launch → /login → enter creds → land authenticated',
      (tester) async {
    final storage = InMemoryTokenStorage();
    final repo = _FakeLoginRepo();

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          loginRepositoryProvider.overrideWithValue(repo),
          secureTokenStorageProvider.overrideWithValue(storage),
        ],
        child: const SignUpFlowApp(),
      ),
    );
    await tester.pumpAndSettle();

    // The unauthenticated app lands on /login. We expect at least the
    // email + password fields to be visible.
    expect(find.byType(TextField), findsAtLeastNWidgets(2));

    // Find the email and password inputs by their decoration label (the
    // login screen labels them; if those labels change this test fails
    // fast, which is the point of an end-to-end smoke).
    final emailField = find.widgetWithText(TextField, 'Email');
    final passwordField = find.widgetWithText(TextField, 'Password');
    expect(emailField, findsOneWidget);
    expect(passwordField, findsOneWidget);

    await tester.enterText(emailField, 'volunteer@example.com');
    await tester.enterText(passwordField, 'irrelevant-fake-pw');
    await tester.pumpAndSettle();

    // Tap the primary login button. The label is the same in both
    // light and dark themes; if the label changes update this string.
    final loginButton = find.widgetWithText(ElevatedButton, 'Log in');
    expect(loginButton, findsOneWidget);
    await tester.tap(loginButton);
    await tester.pumpAndSettle();

    // After successful sign-in, the auth state's token must be set.
    // We don't assert exact landing screen here because the volunteer's
    // home screen depends on backend data we're not stubbing; the auth
    // state mutation is the smoke.
    final ctx = tester.element(find.byType(SignUpFlowApp));
    final container = ProviderScope.containerOf(ctx);
    final auth = container.read(authProvider);
    expect(auth.role, AuthRole.volunteer);
    expect(auth.token, 'integration-test-access-volunteer@example.com');
  });
}
