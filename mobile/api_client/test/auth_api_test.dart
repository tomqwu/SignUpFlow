import 'package:test/test.dart';
import 'package:signupflow_api/signupflow_api.dart';


/// tests for AuthApi
void main() {
  final instance = SignupflowApi().getAuthApi();

  group(AuthApi, () {
    // Check Email
    //
    // Check if email is already registered.
    //
    //Future<JsonObject> checkEmail(String email) async
    test('test checkEmail', () async {
      // TODO
    });

    // Login
    //
    // Login with email and password. Rate limited to 5 requests per 5 minutes per IP.
    //
    //Future<AuthResponse> login(LoginRequest loginRequest) async
    test('test login', () async {
      // TODO
    });

    // Request Password Reset
    //
    // Request a password reset token.  Always returns the same generic message regardless of whether the email exists. Audits every request. The reset token is held in-memory and is NEVER returned in the response in production. Set `DEBUG_RETURN_RESET_TOKEN=true` in dev/test environments to opt into receiving the token in the JSON body for E2E exercise.
    //
    //Future<JsonObject> requestPasswordReset(PasswordResetRequest passwordResetRequest) async
    test('test requestPasswordReset', () async {
      // TODO
    });

    // Reset Password
    //
    // Reset password using token.
    //
    //Future<JsonObject> resetPassword(PasswordResetConfirm passwordResetConfirm) async
    test('test resetPassword', () async {
      // TODO
    });

    // Signup
    //
    // Create a new user account. Rate limited to 3 requests per hour per IP.
    //
    //Future<AuthResponse> signup(SignupRequest signupRequest) async
    test('test signup', () async {
      // TODO
    });

  });
}
