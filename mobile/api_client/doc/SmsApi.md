# signupflow_api.api.SmsApi

## Load the API package
```dart
import 'package:signupflow_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**getSmsUsageStats**](SmsApi.md#getsmsusagestats) | **GET** /api/sms/organizations/{org_id}/sms-usage | Get Sms Usage Stats
[**sendAssignmentNotificationApi**](SmsApi.md#sendassignmentnotificationapi) | **POST** /api/sms/send-assignment-notification | Send Assignment Notification Api
[**sendBroadcastApi**](SmsApi.md#sendbroadcastapi) | **POST** /api/sms/send-broadcast | Send Broadcast Api
[**sendEventReminderApi**](SmsApi.md#sendeventreminderapi) | **POST** /api/sms/send-event-reminder | Send Event Reminder Api
[**sendVerificationCode**](SmsApi.md#sendverificationcode) | **POST** /api/sms/send-verification-code | Send Verification Code
[**twilioDeliveryStatusWebhook**](SmsApi.md#twiliodeliverystatuswebhook) | **POST** /api/sms/webhook/delivery-status | Twilio Delivery Status Webhook
[**twilioIncomingSmsWebhook**](SmsApi.md#twilioincomingsmswebhook) | **POST** /api/sms/webhook/incoming-sms | Twilio Incoming Sms Webhook
[**updateSmsPreferences**](SmsApi.md#updatesmspreferences) | **PUT** /api/sms/people/{person_id}/sms-preferences | Update Sms Preferences
[**verifyCode**](SmsApi.md#verifycode) | **POST** /api/sms/verify-code | Verify Code
[**verifyPhoneNumber**](SmsApi.md#verifyphonenumber) | **POST** /api/sms/verify-phone | Verify Phone Number


# **getSmsUsageStats**
> SmsUsageStatsResponse getSmsUsageStats(orgId)

Get Sms Usage Stats

Get SMS usage statistics for organization (admin only).  Returns current month usage with budget tracking.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getSmsApi();
final int orgId = 56; // int |

try {
    final response = api.getSmsUsageStats(orgId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling SmsApi->getSmsUsageStats: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **int**|  |

### Return type

[**SmsUsageStatsResponse**](SmsUsageStatsResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **sendAssignmentNotificationApi**
> JsonObject sendAssignmentNotificationApi(sendAssignmentNotificationRequest)

Send Assignment Notification Api

Send assignment notification SMS to volunteer (admin only).  Queues background task for async delivery.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getSmsApi();
final SendAssignmentNotificationRequest sendAssignmentNotificationRequest = ; // SendAssignmentNotificationRequest |

try {
    final response = api.sendAssignmentNotificationApi(sendAssignmentNotificationRequest);
    print(response);
} catch on DioException (e) {
    print('Exception when calling SmsApi->sendAssignmentNotificationApi: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sendAssignmentNotificationRequest** | [**SendAssignmentNotificationRequest**](SendAssignmentNotificationRequest.md)|  |

### Return type

[**JsonObject**](JsonObject.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **sendBroadcastApi**
> BroadcastResponse sendBroadcastApi(sendBroadcastRequest)

Send Broadcast Api

Send broadcast SMS to multiple volunteers (admin only).  Max 200 recipients per broadcast. Respects rate limits, quiet hours, and opt-outs.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getSmsApi();
final SendBroadcastRequest sendBroadcastRequest = ; // SendBroadcastRequest |

try {
    final response = api.sendBroadcastApi(sendBroadcastRequest);
    print(response);
} catch on DioException (e) {
    print('Exception when calling SmsApi->sendBroadcastApi: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sendBroadcastRequest** | [**SendBroadcastRequest**](SendBroadcastRequest.md)|  |

### Return type

[**BroadcastResponse**](BroadcastResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **sendEventReminderApi**
> JsonObject sendEventReminderApi(sendEventReminderRequest)

Send Event Reminder Api

Send reminder SMS to all assigned volunteers for event (admin only).  Queues background task for async delivery.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getSmsApi();
final SendEventReminderRequest sendEventReminderRequest = ; // SendEventReminderRequest |

try {
    final response = api.sendEventReminderApi(sendEventReminderRequest);
    print(response);
} catch on DioException (e) {
    print('Exception when calling SmsApi->sendEventReminderApi: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sendEventReminderRequest** | [**SendEventReminderRequest**](SendEventReminderRequest.md)|  |

### Return type

[**JsonObject**](JsonObject.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **sendVerificationCode**
> VerificationCodeResponse sendVerificationCode(verificationCodeRequest)

Send Verification Code

Generate and send 6-digit verification code via SMS.  Code expires in 10 minutes, max 3 verification attempts.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getSmsApi();
final VerificationCodeRequest verificationCodeRequest = ; // VerificationCodeRequest |

try {
    final response = api.sendVerificationCode(verificationCodeRequest);
    print(response);
} catch on DioException (e) {
    print('Exception when calling SmsApi->sendVerificationCode: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **verificationCodeRequest** | [**VerificationCodeRequest**](VerificationCodeRequest.md)|  |

### Return type

[**VerificationCodeResponse**](VerificationCodeResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **twilioDeliveryStatusWebhook**
> JsonObject twilioDeliveryStatusWebhook()

Twilio Delivery Status Webhook

Handle SMS delivery status updates from Twilio webhook.  Updates message status (delivered, failed, undelivered).

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getSmsApi();

try {
    final response = api.twilioDeliveryStatusWebhook();
    print(response);
} catch on DioException (e) {
    print('Exception when calling SmsApi->twilioDeliveryStatusWebhook: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**JsonObject**](JsonObject.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **twilioIncomingSmsWebhook**
> JsonObject twilioIncomingSmsWebhook()

Twilio Incoming Sms Webhook

Handle incoming SMS from Twilio webhook.  Processes YES/NO/STOP/START/HELP replies from volunteers.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getSmsApi();

try {
    final response = api.twilioIncomingSmsWebhook();
    print(response);
} catch on DioException (e) {
    print('Exception when calling SmsApi->twilioIncomingSmsWebhook: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**JsonObject**](JsonObject.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateSmsPreferences**
> JsonObject updateSmsPreferences(personId, updateSmsPreferencesRequest)

Update Sms Preferences

Update SMS notification preferences for a user.  Users can update their own preferences, admins can update any user.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getSmsApi();
final String personId = personId_example; // String |
final UpdateSmsPreferencesRequest updateSmsPreferencesRequest = ; // UpdateSmsPreferencesRequest |

try {
    final response = api.updateSmsPreferences(personId, updateSmsPreferencesRequest);
    print(response);
} catch on DioException (e) {
    print('Exception when calling SmsApi->updateSmsPreferences: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **personId** | **String**|  |
 **updateSmsPreferencesRequest** | [**UpdateSmsPreferencesRequest**](UpdateSmsPreferencesRequest.md)|  |

### Return type

[**JsonObject**](JsonObject.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **verifyCode**
> VerifyCodeResponse verifyCode(verifyCodeRequest)

Verify Code

Verify SMS verification code and activate phone for notifications.  Marks phone as verified and enables SMS notifications.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getSmsApi();
final VerifyCodeRequest verifyCodeRequest = ; // VerifyCodeRequest |

try {
    final response = api.verifyCode(verifyCodeRequest);
    print(response);
} catch on DioException (e) {
    print('Exception when calling SmsApi->verifyCode: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **verifyCodeRequest** | [**VerifyCodeRequest**](VerifyCodeRequest.md)|  |

### Return type

[**VerifyCodeResponse**](VerifyCodeResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **verifyPhoneNumber**
> PhoneVerificationResponse verifyPhoneNumber(phoneVerificationRequest)

Verify Phone Number

Verify phone number format and deliverability using Twilio Lookup API.  Checks: - E.164 format validation - Carrier type (mobile vs landline) - Deliverability status

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getSmsApi();
final PhoneVerificationRequest phoneVerificationRequest = ; // PhoneVerificationRequest |

try {
    final response = api.verifyPhoneNumber(phoneVerificationRequest);
    print(response);
} catch on DioException (e) {
    print('Exception when calling SmsApi->verifyPhoneNumber: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **phoneVerificationRequest** | [**PhoneVerificationRequest**](PhoneVerificationRequest.md)|  |

### Return type

[**PhoneVerificationResponse**](PhoneVerificationResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

