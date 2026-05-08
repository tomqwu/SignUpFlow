# signupflow_api.api.AuthApi

## Load the API package
```dart
import 'package:signupflow_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**checkEmail**](AuthApi.md#checkemail) | **POST** /api/v1/auth/check-email | Check Email
[**login**](AuthApi.md#login) | **POST** /api/v1/auth/login | Login
[**refresh**](AuthApi.md#refresh) | **POST** /api/v1/auth/refresh | Refresh
[**requestPasswordReset**](AuthApi.md#requestpasswordreset) | **POST** /api/v1/auth/forgot-password | Request Password Reset
[**resetPassword**](AuthApi.md#resetpassword) | **POST** /api/v1/auth/reset-password | Reset Password
[**signup**](AuthApi.md#signup) | **POST** /api/v1/auth/signup | Signup


# **checkEmail**
> JsonObject checkEmail(email)

Check Email

Check if email is already registered.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getAuthApi();
final String email = email_example; // String | 

try {
    final response = api.checkEmail(email);
    print(response);
} catch on DioException (e) {
    print('Exception when calling AuthApi->checkEmail: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **email** | **String**|  | 

### Return type

[**JsonObject**](JsonObject.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **login**
> AuthResponse login(loginRequest)

Login

Login with email and password. Rate limited to 5 requests per 5 minutes per IP.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getAuthApi();
final LoginRequest loginRequest = ; // LoginRequest | 

try {
    final response = api.login(loginRequest);
    print(response);
} catch on DioException (e) {
    print('Exception when calling AuthApi->login: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **loginRequest** | [**LoginRequest**](LoginRequest.md)|  | 

### Return type

[**AuthResponse**](AuthResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **refresh**
> RefreshResponse refresh(refreshRequest)

Refresh

Exchange a refresh token for a new access+refresh pair.  On every successful refresh: - Both tokens are rotated and returned. - ``Person.refresh_token_version`` is incremented and persisted. - The new refresh JWT carries the post-increment ``rtv``. - **The prior refresh JWT becomes unusable** because its ``rtv`` is   now older than the user's current ``refresh_token_version``.  Validates: - JWT signature + non-expired - ``type == \"refresh\"`` (rejects access tokens) - ``sub`` (person_id) AND ``org_id`` claims present and match a   live user (multi-tenant filter on the DB lookup; project rule:   every Person query filters by ``org_id``). - ``pwd_iat`` matches current ``password_changed_at`` (refresh   issued before a password change is rejected). - ``rtv`` matches current ``refresh_token_version`` (replay of a   prior refresh JWT is rejected).

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getAuthApi();
final RefreshRequest refreshRequest = ; // RefreshRequest | 

try {
    final response = api.refresh(refreshRequest);
    print(response);
} catch on DioException (e) {
    print('Exception when calling AuthApi->refresh: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **refreshRequest** | [**RefreshRequest**](RefreshRequest.md)|  | 

### Return type

[**RefreshResponse**](RefreshResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **requestPasswordReset**
> JsonObject requestPasswordReset(passwordResetRequest)

Request Password Reset

Request a password reset token.  Always returns the same generic message regardless of whether the email exists. Audits every request. The reset token is held in-memory and is NEVER returned in the response in production. Set `DEBUG_RETURN_RESET_TOKEN=true` in dev/test environments to opt into receiving the token in the JSON body for E2E exercise.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getAuthApi();
final PasswordResetRequest passwordResetRequest = ; // PasswordResetRequest | 

try {
    final response = api.requestPasswordReset(passwordResetRequest);
    print(response);
} catch on DioException (e) {
    print('Exception when calling AuthApi->requestPasswordReset: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **passwordResetRequest** | [**PasswordResetRequest**](PasswordResetRequest.md)|  | 

### Return type

[**JsonObject**](JsonObject.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **resetPassword**
> JsonObject resetPassword(passwordResetConfirm)

Reset Password

Reset password using token.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getAuthApi();
final PasswordResetConfirm passwordResetConfirm = ; // PasswordResetConfirm | 

try {
    final response = api.resetPassword(passwordResetConfirm);
    print(response);
} catch on DioException (e) {
    print('Exception when calling AuthApi->resetPassword: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **passwordResetConfirm** | [**PasswordResetConfirm**](PasswordResetConfirm.md)|  | 

### Return type

[**JsonObject**](JsonObject.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **signup**
> AuthResponse signup(signupRequest)

Signup

Create a new user account. Rate limited to 3 requests per hour per IP.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getAuthApi();
final SignupRequest signupRequest = ; // SignupRequest | 

try {
    final response = api.signup(signupRequest);
    print(response);
} catch on DioException (e) {
    print('Exception when calling AuthApi->signup: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **signupRequest** | [**SignupRequest**](SignupRequest.md)|  | 

### Return type

[**AuthResponse**](AuthResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

