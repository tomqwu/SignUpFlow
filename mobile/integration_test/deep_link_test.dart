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

import 'package:flutter/widgets.dart';
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
    addTearDown(() async {
      await tester.pumpWidget(const SizedBox.shrink());
      await tester.pump();
    });
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          secureTokenStorageProvider.overrideWithValue(InMemoryTokenStorage()),
          invitationRepositoryProvider.overrideWithValue(FakeInvitationRepo()),
        ],
        child: const SignUpFlowApp(),
      ),
    );
    await tester.pump();
    await tester.pump();
    expect(find.byType(LoginScreen), findsOneWidget);
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

  Future<void> pumpRoute(WidgetTester tester) async {
    await tester.pump();
    await tester.pump();
  }

  Future<void> expectRoute(
    WidgetTester tester,
    GoRouter router,
    String uri,
    String expectedPath,
  ) async {
    router.go(uri);
    await pumpRoute(tester);
    final current = currentLocation(router);
    expect(
      current.contains(expectedPath),
      isTrue,
      reason: 'Expected to land on $expectedPath, got: $current',
    );
    expect(current.contains('token=integration_test_token'), isTrue);
  }

  testWidgets(
    'custom-scheme invitation and reset links route in one app lifecycle',
    (tester) async {
      await launchApp(tester);
      final router = routerOf(tester);

      // Preserve old host-form invitation links already in circulation.
      await expectRoute(
        tester,
        router,
        'signupflow://invitation?token=integration_test_token',
        '/invitation',
      );
      // Current path-form links use an empty authority and standard route path.
      await expectRoute(
        tester,
        router,
        'signupflow:///invitation?token=integration_test_token',
        '/invitation',
      );
      await expectRoute(
        tester,
        router,
        'signupflow://reset-password?token=integration_test_token',
        '/reset-password',
      );
    },
  );
}
