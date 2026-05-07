// Create-org signup test — exercises AuthController.createOrgAndSignUp
// + the CreateOrgScreen form using a fake SignupRepository.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:signupflow_mobile/auth/auth_provider.dart';
import 'package:signupflow_mobile/auth/secure_token_storage.dart';
import 'package:signupflow_mobile/auth/signup_repository.dart';
import 'package:signupflow_mobile/features/auth/create_org_screen.dart';

class _FakeSignupRepo implements SignupRepository {
  _FakeSignupRepo({this.shouldSucceed = true});
  bool shouldSucceed;
  String? lastOrgId;

  @override
  Future<AuthState> createOrgAndSignUp({
    required String orgId,
    required String orgName,
    required String adminName,
    required String email,
    required String password,
  }) async {
    lastOrgId = orgId;
    if (!shouldSucceed) {
      throw const SignupFailure('That organization ID is already taken.');
    }
    return AuthState(
      role: AuthRole.admin,
      token: 'fake-jwt-$email',
      orgId: orgId,
      email: email,
      name: adminName,
    );
  }
}

void main() {
  group('AuthController.createOrgAndSignUp', () {
    test('success applies admin role + token', () async {
      final repo = _FakeSignupRepo();
      final container = ProviderContainer(
        overrides: [
          signupRepositoryProvider.overrideWithValue(repo),
          secureTokenStorageProvider.overrideWithValue(InMemoryTokenStorage()),
        ],
      );
      addTearDown(container.dispose);

      final err = await container.read(authProvider.notifier).createOrgAndSignUp(
            orgId: 'hope',
            orgName: 'Hope Community Church',
            adminName: 'Pastor Sarah',
            email: 'sarah@hope.org',
            password: 'sec!ret',
          );

      expect(err, isNull);
      final state = container.read(authProvider);
      expect(state.role, AuthRole.admin);
      expect(state.token, 'fake-jwt-sarah@hope.org');
      expect(state.orgId, 'hope');
      expect(repo.lastOrgId, 'hope');
    });

    test('failure surfaces server message', () async {
      final repo = _FakeSignupRepo(shouldSucceed: false);
      final container = ProviderContainer(
        overrides: [
          signupRepositoryProvider.overrideWithValue(repo),
          secureTokenStorageProvider.overrideWithValue(InMemoryTokenStorage()),
        ],
      );
      addTearDown(container.dispose);

      final err =
          await container.read(authProvider.notifier).createOrgAndSignUp(
                orgId: 'hope',
                orgName: 'Hope',
                adminName: 'S',
                email: 's@h.org',
                password: 'pw1234',
              );
      expect(err, 'That organization ID is already taken.');
      expect(container.read(authProvider).role, AuthRole.unauth);
    });
  });

  group('CreateOrgScreen', () {
    Widget wrap(ProviderContainer container) {
      return UncontrolledProviderScope(
        container: container,
        child: const MaterialApp(home: CreateOrgScreen()),
      );
    }

    testWidgets('autofills org id slug from org name', (tester) async {
      final container = ProviderContainer(
        overrides: [
          signupRepositoryProvider.overrideWithValue(_FakeSignupRepo()),
          secureTokenStorageProvider.overrideWithValue(InMemoryTokenStorage()),
        ],
      );
      addTearDown(container.dispose);
      await tester.pumpWidget(wrap(container));

      await tester.enterText(
        find.widgetWithText(TextField, 'Hope Community Church'),
        'Grace Sports League!',
      );
      await tester.pump();

      final orgIdField = find.widgetWithText(TextField, 'hope-community');
      expect(orgIdField, findsOneWidget);
      expect(
        (tester.widget<TextField>(orgIdField).controller!).text,
        'grace-sports-league',
      );
    });

    testWidgets('blocks submit when fields empty', (tester) async {
      final container = ProviderContainer(
        overrides: [
          signupRepositoryProvider.overrideWithValue(_FakeSignupRepo()),
          secureTokenStorageProvider.overrideWithValue(InMemoryTokenStorage()),
        ],
      );
      addTearDown(container.dispose);
      await tester.pumpWidget(wrap(container));

      await tester.tap(find.text('CREATE ORGANIZATION'));
      await tester.pump();

      expect(find.text('All fields are required.'), findsOneWidget);
    });
  });
}
