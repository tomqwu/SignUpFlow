# signupflow_api.api.NotificationsApi

## Load the API package
```dart
import 'package:signupflow_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**getMyEmailPreferences**](NotificationsApi.md#getmyemailpreferences) | **GET** /api/v1/notifications/preferences/me | Get My Email Preferences
[**getNotification**](NotificationsApi.md#getnotification) | **GET** /api/v1/notifications/{notification_id} | Get Notification
[**getOrganizationNotificationStats**](NotificationsApi.md#getorganizationnotificationstats) | **GET** /api/v1/notifications/stats/organization | Get Organization Notification Stats
[**getUnreadCount**](NotificationsApi.md#getunreadcount) | **GET** /api/v1/notifications/unread/count | Get Unread Count
[**listNotifications**](NotificationsApi.md#listnotifications) | **GET** /api/v1/notifications/ | List Notifications
[**markNotificationRead**](NotificationsApi.md#marknotificationread) | **POST** /api/v1/notifications/{notification_id}/read | Mark Notification Read
[**sendTestNotification**](NotificationsApi.md#sendtestnotification) | **POST** /api/v1/notifications/test/send | Send Test Notification
[**updateMyEmailPreferences**](NotificationsApi.md#updatemyemailpreferences) | **PUT** /api/v1/notifications/preferences/me | Update My Email Preferences


# **getMyEmailPreferences**
> EmailPreferenceResponse getMyEmailPreferences()

Get My Email Preferences

Get current user's email notification preferences.  Returns default preferences if none exist yet.  **RBAC**: Authenticated user

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getNotificationsApi();

try {
    final response = api.getMyEmailPreferences();
    print(response);
} catch on DioException (e) {
    print('Exception when calling NotificationsApi->getMyEmailPreferences: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**EmailPreferenceResponse**](EmailPreferenceResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getNotification**
> NotificationResponse getNotification(notificationId)

Get Notification

Get single notification details.  Users can only view their own notifications.  **RBAC**: Authenticated user (must be notification recipient) **Multi-tenant**: Verified by recipient_id

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getNotificationsApi();
final int notificationId = 56; // int | 

try {
    final response = api.getNotification(notificationId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling NotificationsApi->getNotification: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **notificationId** | **int**|  | 

### Return type

[**NotificationResponse**](NotificationResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getOrganizationNotificationStats**
> NotificationStatsResponse getOrganizationNotificationStats(orgId, days)

Get Organization Notification Stats

Get organization-wide notification statistics.  Provides metrics for admins: - Total notifications sent by type - Delivery success rate - Open/click rates - Recent failures  **RBAC**: Admin only **Multi-tenant**: Filtered by org_id

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getNotificationsApi();
final String orgId = orgId_example; // String | Organization ID
final int days = 56; // int | Number of days to analyze

try {
    final response = api.getOrganizationNotificationStats(orgId, days);
    print(response);
} catch on DioException (e) {
    print('Exception when calling NotificationsApi->getOrganizationNotificationStats: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**| Organization ID | 
 **days** | **int**| Number of days to analyze | [optional] [default to 7]

### Return type

[**NotificationStatsResponse**](NotificationStatsResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getUnreadCount**
> JsonObject getUnreadCount()

Get Unread Count

Return the number of unread notifications for the current user.  Mobile Inbox uses this for the unread-dot badge on the tab bar. A notification is \"unread\" when neither ``opened_at`` nor ``clicked_at`` is set yet.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getNotificationsApi();

try {
    final response = api.getUnreadCount();
    print(response);
} catch on DioException (e) {
    print('Exception when calling NotificationsApi->getUnreadCount: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**JsonObject**](JsonObject.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listNotifications**
> NotificationListResponse listNotifications(orgId, status, type, limit, offset)

List Notifications

List notifications for current user.  Volunteers see only their own notifications. Admins see all organization notifications.  **RBAC**: Authenticated user (volunteer or admin) **Multi-tenant**: Filtered by org_id (and recipient_id for volunteers)

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getNotificationsApi();
final String orgId = orgId_example; // String | Organization ID
final String status = status_example; // String | Filter by status (pending, sent, delivered, etc.)
final String type = type_example; // String | Filter by type (assignment, reminder, update, cancellation)
final int limit = 56; // int | Number of notifications to return
final int offset = 56; // int | Pagination offset

try {
    final response = api.listNotifications(orgId, status, type, limit, offset);
    print(response);
} catch on DioException (e) {
    print('Exception when calling NotificationsApi->listNotifications: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**| Organization ID | 
 **status** | **String**| Filter by status (pending, sent, delivered, etc.) | [optional] 
 **type** | **String**| Filter by type (assignment, reminder, update, cancellation) | [optional] 
 **limit** | **int**| Number of notifications to return | [optional] [default to 50]
 **offset** | **int**| Pagination offset | [optional] [default to 0]

### Return type

[**NotificationListResponse**](NotificationListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **markNotificationRead**
> NotificationResponse markNotificationRead(notificationId)

Mark Notification Read

Mark a notification as read by the recipient.  Sets ``opened_at`` to now (idempotent — does nothing if already set). The mobile Inbox calls this when the user taps a row.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getNotificationsApi();
final int notificationId = 56; // int | 

try {
    final response = api.markNotificationRead(notificationId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling NotificationsApi->markNotificationRead: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **notificationId** | **int**|  | 

### Return type

[**NotificationResponse**](NotificationResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **sendTestNotification**
> JsonObject sendTestNotification(recipientEmail, orgId)

Send Test Notification

Send a test email notification to verify email configuration.  Sends a test assignment notification to the specified email address. Useful for testing SendGrid configuration, SMTP settings, and template rendering.  **RBAC**: Admin only **Multi-tenant**: Verified by admin's org_id

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getNotificationsApi();
final String recipientEmail = recipientEmail_example; // String | Email address to send test notification
final String orgId = orgId_example; // String | Organization ID

try {
    final response = api.sendTestNotification(recipientEmail, orgId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling NotificationsApi->sendTestNotification: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **recipientEmail** | **String**| Email address to send test notification | 
 **orgId** | **String**| Organization ID | 

### Return type

[**JsonObject**](JsonObject.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateMyEmailPreferences**
> EmailPreferenceResponse updateMyEmailPreferences(emailPreferenceUpdate)

Update My Email Preferences

Update current user's email notification preferences.  Allows users to: - Change notification frequency (immediate, daily, weekly, disabled) - Enable/disable specific notification types - Set language and timezone for emails - Set preferred digest delivery hour  **RBAC**: Authenticated user

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getNotificationsApi();
final EmailPreferenceUpdate emailPreferenceUpdate = ; // EmailPreferenceUpdate | 

try {
    final response = api.updateMyEmailPreferences(emailPreferenceUpdate);
    print(response);
} catch on DioException (e) {
    print('Exception when calling NotificationsApi->updateMyEmailPreferences: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **emailPreferenceUpdate** | [**EmailPreferenceUpdate**](EmailPreferenceUpdate.md)|  | 

### Return type

[**EmailPreferenceResponse**](EmailPreferenceResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

