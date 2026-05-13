// Sprint 10 PR 10.3 — deep-link routing verification.
//
// Codex flagged across #87/#88 + earlier reviews that the backend's
// emitted `signupflow://invitation?token=...` URL puts "invitation" in
// the URI host with an empty path, while go_router matches by path —
// so without remapping, the link lands on "/" instead of /invitation.
//
// This test exercises both URL forms via the router directly so the
// test fails fast if the remap (`router.dart:_hostRouteRemap`) regresses,
// and operator-side smoke against a real device can pick the same
// failures up via `flutter test integration_test/deep_link_test.dart`.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:integration_test/integration_test.dart';
import 'package:signupflow_mobile/app.dart';
import 'package:signupflow_mobile/auth/secure_token_storage.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  Future<void> _launch(WidgetTester tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          secureTokenStorageProvider.overrideWithValue(InMemoryTokenStorage()),
        ],
        child: const SignUpFlowApp(),
      ),
    );
    await tester.pumpAndSettle();
  }

  GoRouter _routerOf(WidgetTester tester) {
    // SignUpFlowApp is the ancestor that installs MaterialApp.router;
    // the InheritedGoRouter lives BELOW MaterialApp's Navigator. Find
    // any Material widget (the login screen renders one) and pull the
    // router from that context.
    final ctx = tester.element(find.byType(MaterialApp));
    return GoRouter.of(ctx);
  }

  String _currentLocation(GoRouter router) {
    return router.routeInformationProvider.value.uri.toString();
  }

  testWidgets('signupflow://invitation?token=... routes to /invitation',
      (tester) async {
    await _launch(tester);
    final router = _routerOf(tester);

    // Host-form URL — the backend's current production format
    // (api/services/email_service.py emits this for password-reset
    // and the matching create_invitation path).
    router.go('signupflow://invitation?token=integration_test_token');
    await tester.pumpAndSettle();

    final current = _currentLocation(router);
    expect(
      current.contains('/invitation'),
      isTrue,
      reason: 'Expected to land on /invitation, got: $current',
    );
    expect(current.contains('token=integration_test_token'), isTrue);
  });

  testWidgets('signupflow:///invitation?token=... (path form) routes to /invitation',
      (tester) async {
    await _launch(tester);
    final router = _routerOf(tester);

    router.go('signupflow:///invitation?token=integration_test_token');
    await tester.pumpAndSettle();

    final current = _currentLocation(router);
    expect(current.contains('/invitation'), isTrue);
    expect(current.contains('token=integration_test_token'), isTrue);
  });

  testWidgets('signupflow://reset-password?token=... routes to /reset-password',
      (tester) async {
    await _launch(tester);
    final router = _routerOf(tester);

    router.go('signupflow://reset-password?token=integration_test_token');
    await tester.pumpAndSettle();

    final current = _currentLocation(router);
    expect(current.contains('/reset-password'), isTrue);
    expect(current.contains('token=integration_test_token'), isTrue);
  });
}
