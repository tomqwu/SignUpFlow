// PasswordResetRepository — request a reset token and confirm a new
// password. The endpoint always returns the same generic message
// regardless of whether the email exists (anti-enumeration), so the
// "request" call has no failure-path branching.

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/api/api_client.dart';

class PasswordResetRepository {
  PasswordResetRepository(this._client);
  final api.SignupflowApi _client;

  /// Request a password-reset email. Always returns success, per spec.
  Future<void> requestReset(String email) async {
    try {
      final body = (api.PasswordResetRequestBuilder()..email = email).build();
      await _client.getAuthApi().requestPasswordReset(
            passwordResetRequest: body,
          );
    } on DioException catch (e) {
      throw PasswordResetFailure(
        'Network error: ${e.message ?? e.response?.statusCode}',
      );
    }
  }

  /// Confirm a reset token + new password.
  Future<void> confirmReset({
    required String token,
    required String newPassword,
  }) async {
    try {
      final body = (api.PasswordResetConfirmBuilder()
            ..token = token
            ..newPassword = newPassword)
          .build();
      await _client.getAuthApi().resetPassword(passwordResetConfirm: body);
    } on DioException catch (e) {
      final code = e.response?.statusCode;
      if (code == 400 || code == 404 || code == 410) {
        throw const PasswordResetFailure(
          'This reset link is invalid or has expired.',
        );
      }
      if (code == 422) {
        throw const PasswordResetFailure(
          'Password did not pass validation.',
        );
      }
      throw PasswordResetFailure('Network error: ${e.message ?? code}');
    }
  }
}

class PasswordResetFailure implements Exception {
  const PasswordResetFailure(this.message);
  final String message;
  @override
  String toString() => message;
}

final passwordResetRepositoryProvider =
    Provider<PasswordResetRepository>((ref) {
  return PasswordResetRepository(ref.watch(signupflowApiProvider));
});
