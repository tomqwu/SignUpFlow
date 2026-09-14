# signupflow_api.api.AuthApi

## Load the API package
```dart
import 'package:signupflow_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**changePassword**](AuthApi.md#changepassword) | **POST** /api/v1/auth/change-password | Change Password
[**checkEmail**](AuthApi.md#checkemail) | **POST** /api/v1/auth/check-email | Check Email
[**login**](AuthApi.md#login) | **POST** /api/v1/auth/login | Login
[**refresh**](AuthApi.md#refresh) | **POST** /api/v1/auth/refresh | Refresh
[**requestPasswordReset**](AuthApi.md#requestpasswordreset) | **POST** /api/v1/auth/forgot-password | Request Password Reset
[**resetPassword**](AuthApi.md#resetpassword) | **POST** /api/v1/auth/reset-password | Reset Password
[**signup**](AuthApi.md#signup) | **POST** /api/v1/auth/signup | Signup


# **changePassword**
> AuthResponse changePassword(changePasswordRequest)

Change Password

Change the authenticated user's password. Verifies the current password, then rotates the hash and stamps password_changed_at so previously-issued access tokens are invalidated (same revocation mechanism as password reset). Returns a fresh token pair so the caller stays signed in.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getAuthApi();
final ChangePasswordRequest changePasswordRequest = ; // ChangePasswordRequest |

try {
    final response = api.changePassword(changePasswordRequest);
    print(response);
} catch on DioException (e) {
    print('Exception when calling AuthApi->changePassword: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **changePasswordRequest** | [**ChangePasswordRequest**](ChangePasswordRequest.md)|  |

### Return type

[**AuthResponse**](AuthResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

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

Request a password reset token.  Always returns the same generic message regardless of whether the email exists. Audits every request. The reset token is persisted in the ``password_reset_tokens`` table (see model in ``api/models.py``) so it survives multi-worker deployments — the legacy in-memory dict broke under the documented default ``WORKERS=4`` because the worker handling ``POST /reset-password`` may differ from the one that issued the token. The token is NEVER returned in the response in production. Set ``DEBUG_RETURN_RESET_TOKEN=true`` in dev/test environments to opt into receiving the token in the JSON body for E2E exercise.  Email send is queued via ``BackgroundTasks`` so the HTTP response timing is independent of email backend latency — both for anti- enumeration and to prevent slow-SMTP DoS. The reset token is issued synchronously; email delivery is best-effort.

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

Reset password using token.  The token row is *claimed* with a single conditional UPDATE rather than a SELECT-then-update sequence. Two concurrent /reset-password submissions of the same emailed link otherwise both pass a SELECT (``used_at IS NULL``) before either can stamp it, and both proceed to change the password — last-write-wins semantics, not the one-time-use guarantee the endpoint advertises. The atomic UPDATE closes that race: at most one row transitions from NULL to a timestamp, ``rowcount == 0`` for the loser.

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

Create one organization and its first admin in a single transaction.

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

