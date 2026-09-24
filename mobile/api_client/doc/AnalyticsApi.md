# signupflow_api.api.AnalyticsApi

## Load the API package
```dart
import 'package:signupflow_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**getBurnoutRisk**](AnalyticsApi.md#getburnoutrisk) | **GET** /api/v1/analytics/{org_id}/burnout-risk | Get Burnout Risk
[**getScheduleHealth**](AnalyticsApi.md#getschedulehealth) | **GET** /api/v1/analytics/{org_id}/schedule-health | Get Schedule Health
[**getVolunteerStats**](AnalyticsApi.md#getvolunteerstats) | **GET** /api/v1/analytics/{org_id}/volunteer-stats | Get Volunteer Stats


# **getBurnoutRisk**
> JsonObject getBurnoutRisk(orgId, threshold)

Get Burnout Risk

Identify volunteers at risk of burnout (serving too frequently).  Counts assignments on events that started in the last 30 days; upcoming assignments do not count.  Admin-only within `org_id`. This endpoint returns other volunteers' names and emails, so peer volunteers can never read it.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getAnalyticsApi();
final String orgId = orgId_example; // String |
final int threshold = 56; // int | Assignments in the last 30 days (upcoming excluded) that flag risk

try {
    final response = api.getBurnoutRisk(orgId, threshold);
    print(response);
} catch on DioException (e) {
    print('Exception when calling AnalyticsApi->getBurnoutRisk: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**|  |
 **threshold** | **int**| Assignments in the last 30 days (upcoming excluded) that flag risk | [optional] [default to 4]

### Return type

[**JsonObject**](JsonObject.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getScheduleHealth**
> JsonObject getScheduleHealth(orgId)

Get Schedule Health

Get schedule health metrics for upcoming events (start time now or later).  Admin-only within `org_id`.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getAnalyticsApi();
final String orgId = orgId_example; // String |

try {
    final response = api.getScheduleHealth(orgId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling AnalyticsApi->getScheduleHealth: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**|  |

### Return type

[**JsonObject**](JsonObject.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getVolunteerStats**
> JsonObject getVolunteerStats(orgId, days)

Get Volunteer Stats

Get volunteer participation statistics for events in the last `days` days.  Counts only events that started between now - `days` and now; a published future schedule is not participation yet.  Admin-only within `org_id`. The caller must be an authenticated admin whose own org matches the requested one.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getAnalyticsApi();
final String orgId = orgId_example; // String |
final int days = 56; // int | Number of past days to analyze; the window ends now and excludes upcoming events

try {
    final response = api.getVolunteerStats(orgId, days);
    print(response);
} catch on DioException (e) {
    print('Exception when calling AnalyticsApi->getVolunteerStats: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**|  |
 **days** | **int**| Number of past days to analyze; the window ends now and excludes upcoming events | [optional] [default to 30]

### Return type

[**JsonObject**](JsonObject.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
