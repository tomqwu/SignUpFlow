// Password reset tests — request + confirm flows with a fake repo.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:signupflow_mobile/auth/password_reset_repository.dart';
import 'package:signupflow_mobile/features/auth/forgot_password_screen.dart';
import 'package:signupflow_mobile/features/auth/reset_password_screen.dart';

class _FakeResetRepo implements PasswordResetRepository {
  _FakeResetRepo({this.confirmOk = true});
  bool confirmOk;
  String? lastEmail;
  String? lastToken;
  String? lastNewPassword;

  @override
  Future<void> requestReset(String email) async {
    lastEmail = email;
  }

  @override
  Future<void> confirmReset({
    required String token,
    required String newPassword,
  }) async {
    lastToken = token;
    lastNewPassword = newPassword;
    if (!confirmOk) {
      throw const PasswordResetFailure(
        'This reset link is invalid or has expired.',
      );
    }
  }
}

void main() {
  group('ForgotPasswordScreen', () {
    Widget wrap(ProviderContainer container) {
      return UncontrolledProviderScope(
        container: container,
        child: const MaterialApp(home: ForgotPasswordScreen()),
      );
    }

    testWidgets('submitting email shows confirmation card', (tester) async {
      final repo = _FakeResetRepo();
      final container = ProviderContainer(
        overrides: [
          passwordResetRepositoryProvider.overrideWithValue(repo),
        ],
      );
      addTearDown(container.dispose);
      await tester.pumpWidget(wrap(container));

      await tester.enterText(
        find.widgetWithText(TextField, 'you@church.org'),
        'sarah@hope.org',
      );
      await tester.tap(find.text('SEND RESET LINK'));
      await tester.pump();

      expect(find.text('CHECK YOUR EMAIL'), findsOneWidget);
      expect(repo.lastEmail, 'sarah@hope.org');
    });

    testWidgets('blocks submit when email empty', (tester) async {
      final container = ProviderContainer(
        overrides: [
          passwordResetRepositoryProvider.overrideWithValue(_FakeResetRepo()),
        ],
      );
      addTearDown(container.dispose);
      await tester.pumpWidget(wrap(container));
      await tester.tap(find.text('SEND RESET LINK'));
      await tester.pump();
      expect(find.text('Email required.'), findsOneWidget);
    });
  });

  group('ResetPasswordScreen', () {
    Widget wrap(ProviderContainer container, String token) {
      return UncontrolledProviderScope(
        container: container,
        child: MaterialApp(home: ResetPasswordScreen(token: token)),
      );
    }

    testWidgets('happy path with deep-link token shows done card',
        (tester) async {
      final repo = _FakeResetRepo();
      final container = ProviderContainer(
        overrides: [
          passwordResetRepositoryProvider.overrideWithValue(repo),
        ],
      );
      addTearDown(container.dispose);
      await tester.pumpWidget(wrap(container, 'rst_xyz'));

      await tester.enterText(
        find.widgetWithText(TextField, 'min 6 characters'),
        'newpw1',
      );
      await tester.enterText(
        find.widgetWithText(TextField, 'retype password'),
        'newpw1',
      );
      await tester.tap(find.text('RESET PASSWORD'));
      await tester.pump();

      expect(find.text('PASSWORD RESET'), findsOneWidget);
      expect(repo.lastToken, 'rst_xyz');
      expect(repo.lastNewPassword, 'newpw1');
    });

    testWidgets('mismatched passwords block submit', (tester) async {
      final container = ProviderContainer(
        overrides: [
          passwordResetRepositoryProvider.overrideWithValue(_FakeResetRepo()),
        ],
      );
      addTearDown(container.dispose);
      await tester.pumpWidget(wrap(container, 'rst_xyz'));

      await tester.enterText(
        find.widgetWithText(TextField, 'min 6 characters'),
        'newpw1',
      );
      await tester.enterText(
        find.widgetWithText(TextField, 'retype password'),
        'different',
      );
      await tester.tap(find.text('RESET PASSWORD'));
      await tester.pump();
      expect(find.text("Passwords don't match."), findsOneWidget);
    });

    testWidgets('expired token surfaces server message', (tester) async {
      final container = ProviderContainer(
        overrides: [
          passwordResetRepositoryProvider.overrideWithValue(
            _FakeResetRepo(confirmOk: false),
          ),
        ],
      );
      addTearDown(container.dispose);
      await tester.pumpWidget(wrap(container, 'rst_old'));

      await tester.enterText(
        find.widgetWithText(TextField, 'min 6 characters'),
        'newpw1',
      );
      await tester.enterText(
        find.widgetWithText(TextField, 'retype password'),
        'newpw1',
      );
      await tester.tap(find.text('RESET PASSWORD'));
      await tester.pump();
      expect(
        find.text('This reset link is invalid or has expired.'),
        findsOneWidget,
      );
    });
  });
}
