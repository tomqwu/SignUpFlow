// Auth controller test — exercises signIn / signOut without hitting the
// network. Uses Riverpod overrides to swap in a fake LoginRepository +
// in-memory secure storage.

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:signupflow_mobile/auth/auth_provider.dart';
import 'package:signupflow_mobile/auth/login_repository.dart';
import 'package:signupflow_mobile/auth/secure_token_storage.dart';

class _FakeLoginRepo implements LoginRepository {
  _FakeLoginRepo({this.shouldSucceed = true, this.role = AuthRole.volunteer});
  bool shouldSucceed;
  AuthRole role;
  bool signedOut = false;

  @override
  Future<AuthState> signIn(String email, String password) async {
    if (!shouldSucceed) throw const LoginFailure('Wrong email or password');
    return AuthState(role: role, token: 'fake-jwt-$email');
  }

  @override
  Future<void> signOut() async {
    signedOut = true;
  }
}

void main() {
  test('signIn success → role + token applied', () async {
    final repo = _FakeLoginRepo(role: AuthRole.admin);
    final storage = InMemoryTokenStorage();
    final container = ProviderContainer(
      overrides: [
        loginRepositoryProvider.overrideWithValue(repo),
        secureTokenStorageProvider.overrideWithValue(storage),
      ],
    );
    addTearDown(container.dispose);

    expect(container.read(authProvider).role, AuthRole.unauth);

    final err = await container.read(authProvider.notifier).signIn(
          'admin@hcc.org',
          'pw',
        );
    expect(err, isNull);
    final state = container.read(authProvider);
    expect(state.role, AuthRole.admin);
    expect(state.token, 'fake-jwt-admin@hcc.org');
  });

  test('signIn failure surfaces user-facing message', () async {
    final repo = _FakeLoginRepo(shouldSucceed: false);
    final container = ProviderContainer(
      overrides: [
        loginRepositoryProvider.overrideWithValue(repo),
        secureTokenStorageProvider.overrideWithValue(InMemoryTokenStorage()),
      ],
    );
    addTearDown(container.dispose);

    final err = await container
        .read(authProvider.notifier)
        .signIn('a@b.org', 'wrong');
    expect(err, 'Wrong email or password');
    expect(container.read(authProvider).role, AuthRole.unauth);
  });

  test('signOut wipes state and storage', () async {
    final repo = _FakeLoginRepo();
    final storage = InMemoryTokenStorage();
    await storage.writeToken('tok');
    final container = ProviderContainer(
      overrides: [
        loginRepositoryProvider.overrideWithValue(repo),
        secureTokenStorageProvider.overrideWithValue(storage),
      ],
    );
    addTearDown(container.dispose);

    container.read(authProvider.notifier).demoSignInVolunteer();
    expect(container.read(authProvider).role, AuthRole.volunteer);

    await container.read(authProvider.notifier).signOut();
    expect(container.read(authProvider).role, AuthRole.unauth);
    expect(await storage.readToken(), isNull);
  });
}
