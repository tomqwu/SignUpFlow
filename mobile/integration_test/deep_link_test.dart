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
import 'package:signupflow_mobile/auth/auth_provider.dart';
import 'package:signupflow_mobile/auth/invitation_repository.dart';
import 'package:signupflow_mobile/auth/secure_token_storage.dart';
import 'package:signupflow_mobile/features/auth/login_screen.dart';

/// Stub repo so InvitationScreen.initState's verify() call returns a
/// canned preview instead of hitting the real API. Without this the
/// test would hang/flake on a Dio connect timeout.
class FakeInvitationRepo implements InvitationRepository {
  @override
  Future<InvitationPreview> verify(String token) async {
    return InvitationPreview(
      token: token,
      orgId: 'integration_test_org',
      invitedName: 'Integration Tester',
      invitedEmail: 'integration@example.com',
      invitedBy: 'Test Admin',
      roles: const ['volunteer'],
    );
  }

  @override
  Future<AuthState> accept({
    required String token,
    required String password,
    String? timezone,
  }) async {
    // Routing-only tests don't reach this — return a minimal state.
    return const AuthState(role: AuthRole.volunteer, token: 'fake');
  }
}

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  Future<void> launchApp(WidgetTester tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          secureTokenStorageProvider.overrideWithValue(InMemoryTokenStorage()),
          invitationRepositoryProvider.overrideWithValue(FakeInvitationRepo()),
        ],
        child: const SignUpFlowApp(),
      ),
    );
    await tester.pumpAndSettle();
  }

  GoRouter routerOf(WidgetTester tester) {
    // GoRouter.of walks up the InheritedGoRouter inheritance chain.
    // The InheritedGoRouter is installed by MaterialApp.router AROUND
    // the Navigator, so we need a context strictly inside that
    // subtree. Initial route is /login → LoginScreen is in the tree;
    // its context is below the Navigator, below InheritedGoRouter.
    final ctx = tester.element(find.byType(LoginScreen));
    return GoRouter.of(ctx);
  }

  String currentLocation(GoRouter router) {
    return router.routeInformationProvider.value.uri.toString();
  }

  testWidgets('signupflow://invitation?token=... routes to /invitation',
      (tester) async {
    await launchApp(tester);
    final router = routerOf(tester);

    // Host-form URL — the OLD production format (pre-10.3). The
    // _hostRouteRemap in router.dart handles warm-start remap so any
    // email in flight with the host-form URL still routes.
    router.go('signupflow://invitation?token=integration_test_token');
    await tester.pumpAndSettle();

    final current = currentLocation(router);
    expect(
      current.contains('/invitation'),
      isTrue,
      reason: 'Expected to land on /invitation, got: $current',
    );
    expect(current.contains('token=integration_test_token'), isTrue);
  });

  testWidgets('signupflow:///invitation?token=... (path form) routes to /invitation',
      (tester) async {
    await launchApp(tester);
    final router = routerOf(tester);

    // Triple-slash form — the NEW production format (10.3+). Empty
    // authority, path="/invitation". This is what cold-start emails
    // use; routes via go_router's standard path matching.
    router.go('signupflow:///invitation?token=integration_test_token');
    await tester.pumpAndSettle();

    final current = currentLocation(router);
    expect(current.contains('/invitation'), isTrue);
    expect(current.contains('token=integration_test_token'), isTrue);
  });

  testWidgets('signupflow://reset-password?token=... routes to /reset-password',
      (tester) async {
    await launchApp(tester);
    final router = routerOf(tester);

    router.go('signupflow://reset-password?token=integration_test_token');
    await tester.pumpAndSettle();

    final current = currentLocation(router);
    expect(current.contains('/reset-password'), isTrue);
    expect(current.contains('token=integration_test_token'), isTrue);
  });
}
