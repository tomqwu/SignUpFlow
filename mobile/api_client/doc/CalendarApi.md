# signupflow_api.api.CalendarApi

## Load the API package
```dart
import 'package:signupflow_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**adminResetCalendarToken**](CalendarApi.md#adminresetcalendartoken) | **POST** /api/v1/calendar/{person_id}/admin-reset | Admin Reset Calendar Token
[**calendarFeed**](CalendarApi.md#calendarfeed) | **GET** /api/v1/calendar/feed/{token} | Calendar Feed
[**exportOrganizationEvents**](CalendarApi.md#exportorganizationevents) | **GET** /api/v1/calendar/org/export | Export Organization Events
[**exportPersonalSchedule**](CalendarApi.md#exportpersonalschedule) | **GET** /api/v1/calendar/export | Export Personal Schedule
[**getSubscriptionUrl**](CalendarApi.md#getsubscriptionurl) | **GET** /api/v1/calendar/subscribe | Get Subscription Url
[**resetCalendarToken**](CalendarApi.md#resetcalendartoken) | **POST** /api/v1/calendar/reset-token | Reset Calendar Token


# **adminResetCalendarToken**
> CalendarTokenResetResponse adminResetCalendarToken(personId)

Admin Reset Calendar Token

Admin-only force-reset of another user's calendar token.  Same as `/calendar/reset-token` but explicitly an admin override of a target user's token. Always audited as `calendar.token.admin_reset`.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getCalendarApi();
final String personId = personId_example; // String | 

try {
    final response = api.adminResetCalendarToken(personId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling CalendarApi->adminResetCalendarToken: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **personId** | **String**|  | 

### Return type

[**CalendarTokenResetResponse**](CalendarTokenResetResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **calendarFeed**
> JsonObject calendarFeed(token)

Calendar Feed

Public calendar feed endpoint for subscriptions.  This endpoint is accessed by calendar applications using the subscription URL. It returns an ICS file that is automatically refreshed by the calendar app.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getCalendarApi();
final String token = token_example; // String | 

try {
    final response = api.calendarFeed(token);
    print(response);
} catch on DioException (e) {
    print('Exception when calling CalendarApi->calendarFeed: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **String**|  | 

### Return type

[**JsonObject**](JsonObject.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **exportOrganizationEvents**
> JsonObject exportOrganizationEvents(orgId, personId, includeAssignments)

Export Organization Events

Export all organization events as ICS file (admin only).  This endpoint is for administrators to export all events in the organization.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getCalendarApi();
final String orgId = orgId_example; // String | 
final String personId = personId_example; // String | 
final bool includeAssignments = true; // bool | 

try {
    final response = api.exportOrganizationEvents(orgId, personId, includeAssignments);
    print(response);
} catch on DioException (e) {
    print('Exception when calling CalendarApi->exportOrganizationEvents: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**|  | 
 **personId** | **String**|  | 
 **includeAssignments** | **bool**|  | [optional] [default to true]

### Return type

[**JsonObject**](JsonObject.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **exportPersonalSchedule**
> JsonObject exportPersonalSchedule(personId)

Export Personal Schedule

Export personal schedule as ICS file.  This endpoint downloads an ICS file with all assigned events for a person.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getCalendarApi();
final String personId = personId_example; // String | 

try {
    final response = api.exportPersonalSchedule(personId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling CalendarApi->exportPersonalSchedule: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **personId** | **String**|  | 

### Return type

[**JsonObject**](JsonObject.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getSubscriptionUrl**
> CalendarSubscriptionResponse getSubscriptionUrl(personId)

Get Subscription Url

Get calendar subscription URL for a person.  Returns a webcal:// URL that can be used to subscribe to the calendar in Google Calendar, Apple Calendar, Outlook, etc. Caller must be the target person or an admin in the same organization.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getCalendarApi();
final String personId = personId_example; // String | 

try {
    final response = api.getSubscriptionUrl(personId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling CalendarApi->getSubscriptionUrl: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **personId** | **String**|  | 

### Return type

[**CalendarSubscriptionResponse**](CalendarSubscriptionResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **resetCalendarToken**
> CalendarTokenResetResponse resetCalendarToken(personId)

Reset Calendar Token

Reset calendar subscription token for a person.  This invalidates the old subscription URL and generates a new one. Caller must be the target person or an admin in the same organization. Use `/calendar/{person_id}/admin-reset` for the admin-only flow.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getCalendarApi();
final String personId = personId_example; // String | 

try {
    final response = api.resetCalendarToken(personId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling CalendarApi->resetCalendarToken: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **personId** | **String**|  | 

### Return type

[**CalendarTokenResetResponse**](CalendarTokenResetResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

