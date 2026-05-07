// Invitation accept test — controller success/failure + widget tests for
// the verify → accept flow with a fake repository.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:signupflow_mobile/auth/auth_provider.dart';
import 'package:signupflow_mobile/auth/invitation_repository.dart';
import 'package:signupflow_mobile/auth/secure_token_storage.dart';
import 'package:signupflow_mobile/features/auth/invitation_screen.dart';

class _FakeInvitationRepo implements InvitationRepository {
  _FakeInvitationRepo({this.verifyOk = true, this.acceptOk = true});
  bool verifyOk;
  bool acceptOk;
  String? lastAcceptedToken;

  @override
  Future<InvitationPreview> verify(String token) async {
    if (!verifyOk) {
      throw const InvitationFailure('This invitation is no longer valid.');
    }
    return InvitationPreview(
      token: token,
      orgId: 'hope',
      invitedName: 'New Volunteer',
      invitedEmail: 'new@hope.org',
      invitedBy: 'admin@hope.org',
      roles: const ['volunteer'],
    );
  }

  @override
  Future<AuthState> accept({
    required String token,
    required String password,
    String? timezone,
  }) async {
    lastAcceptedToken = token;
    if (!acceptOk) {
      throw const InvitationFailure('This invitation has already been used.');
    }
    return AuthState(
      role: AuthRole.volunteer,
      token: 'fake-jwt-$token',
      orgId: 'hope',
      email: 'new@hope.org',
      name: 'New Volunteer',
    );
  }
}

void main() {
  group('AuthController.acceptInvitation', () {
    test('success applies volunteer role + token', () async {
      final repo = _FakeInvitationRepo();
      final container = ProviderContainer(
        overrides: [
          invitationRepositoryProvider.overrideWithValue(repo),
          secureTokenStorageProvider.overrideWithValue(InMemoryTokenStorage()),
        ],
      );
      addTearDown(container.dispose);

      final err = await container.read(authProvider.notifier).acceptInvitation(
            token: 'inv_abc',
            password: 'pw1234',
          );
      expect(err, isNull);
      expect(container.read(authProvider).role, AuthRole.volunteer);
      expect(repo.lastAcceptedToken, 'inv_abc');
    });

    test('failure surfaces server message', () async {
      final repo = _FakeInvitationRepo(acceptOk: false);
      final container = ProviderContainer(
        overrides: [
          invitationRepositoryProvider.overrideWithValue(repo),
          secureTokenStorageProvider.overrideWithValue(InMemoryTokenStorage()),
        ],
      );
      addTearDown(container.dispose);

      final err = await container.read(authProvider.notifier).acceptInvitation(
            token: 'inv_abc',
            password: 'pw1234',
          );
      expect(err, 'This invitation has already been used.');
      expect(container.read(authProvider).role, AuthRole.unauth);
    });
  });

  group('InvitationScreen', () {
    Widget wrap(ProviderContainer container, String token) {
      return UncontrolledProviderScope(
        container: container,
        child: MaterialApp(home: InvitationScreen(token: token)),
      );
    }

    testWidgets('with no token shows paste form', (tester) async {
      final container = ProviderContainer(
        overrides: [
          invitationRepositoryProvider.overrideWithValue(_FakeInvitationRepo()),
          secureTokenStorageProvider.overrideWithValue(InMemoryTokenStorage()),
        ],
      );
      addTearDown(container.dispose);
      await tester.pumpWidget(wrap(container, ''));
      await tester.pump();

      expect(find.text('NO TOKEN IN LINK'), findsOneWidget);
      expect(find.text('CONTINUE'), findsOneWidget);
    });

    testWidgets('with valid token shows preview card', (tester) async {
      final container = ProviderContainer(
        overrides: [
          invitationRepositoryProvider.overrideWithValue(_FakeInvitationRepo()),
          secureTokenStorageProvider.overrideWithValue(InMemoryTokenStorage()),
        ],
      );
      addTearDown(container.dispose);
      await tester.pumpWidget(wrap(container, 'inv_abc'));
      // FutureBuilder resolves on next pump.
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 50));

      expect(find.text('YOU ARE INVITED'), findsOneWidget);
      expect(find.text('New Volunteer'), findsOneWidget);
      expect(find.text('new@hope.org'), findsOneWidget);
      expect(find.text('hope'), findsOneWidget);
      expect(find.text('volunteer'), findsOneWidget);
    });

    testWidgets('invalid token shows error card', (tester) async {
      final container = ProviderContainer(
        overrides: [
          invitationRepositoryProvider.overrideWithValue(
            _FakeInvitationRepo(verifyOk: false),
          ),
          secureTokenStorageProvider.overrideWithValue(InMemoryTokenStorage()),
        ],
      );
      addTearDown(container.dispose);
      await tester.pumpWidget(wrap(container, 'inv_bad'));
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 50));

      expect(find.text('INVITATION ERROR'), findsOneWidget);
      expect(
        find.text('This invitation is no longer valid.'),
        findsOneWidget,
      );
    });
  });
}
