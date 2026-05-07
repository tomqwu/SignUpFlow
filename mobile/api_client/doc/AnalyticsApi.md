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

Identify volunteers at risk of burnout (serving too frequently).

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getAnalyticsApi();
final String orgId = orgId_example; // String | 
final int threshold = 56; // int | Assignments per month threshold

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
 **threshold** | **int**| Assignments per month threshold | [optional] [default to 4]

### Return type

[**JsonObject**](JsonObject.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getScheduleHealth**
> JsonObject getScheduleHealth(orgId)

Get Schedule Health

Get schedule health metrics.

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

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getVolunteerStats**
> JsonObject getVolunteerStats(orgId, days)

Get Volunteer Stats

Get volunteer participation statistics.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getAnalyticsApi();
final String orgId = orgId_example; // String | 
final int days = 56; // int | Number of days to analyze

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
 **days** | **int**| Number of days to analyze | [optional] [default to 30]

### Return type

[**JsonObject**](JsonObject.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

