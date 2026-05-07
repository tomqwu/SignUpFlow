# signupflow_api.api.AvailabilityApi

## Load the API package
```dart
import 'package:signupflow_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**addTimeoff**](AvailabilityApi.md#addtimeoff) | **POST** /api/v1/availability/{person_id}/timeoff | Add Timeoff
[**createAvailability**](AvailabilityApi.md#createavailability) | **POST** /api/v1/availability/ | Create Availability
[**deleteTimeoff**](AvailabilityApi.md#deletetimeoff) | **DELETE** /api/v1/availability/{person_id}/timeoff/{timeoff_id} | Delete Timeoff
[**getTimeoff**](AvailabilityApi.md#gettimeoff) | **GET** /api/v1/availability/{person_id}/timeoff | Get Timeoff
[**updateTimeoff**](AvailabilityApi.md#updatetimeoff) | **PATCH** /api/v1/availability/{person_id}/timeoff/{timeoff_id} | Update Timeoff


# **addTimeoff**
> JsonObject addTimeoff(personId, timeOffCreate)

Add Timeoff

Add a time-off period for a person.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getAvailabilityApi();
final String personId = personId_example; // String | 
final TimeOffCreate timeOffCreate = ; // TimeOffCreate | 

try {
    final response = api.addTimeoff(personId, timeOffCreate);
    print(response);
} catch on DioException (e) {
    print('Exception when calling AvailabilityApi->addTimeoff: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **personId** | **String**|  | 
 **timeOffCreate** | [**TimeOffCreate**](TimeOffCreate.md)|  | 

### Return type

[**JsonObject**](JsonObject.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createAvailability**
> JsonObject createAvailability(personId)

Create Availability

Create availability record for a person.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getAvailabilityApi();
final String personId = personId_example; // String | 

try {
    final response = api.createAvailability(personId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling AvailabilityApi->createAvailability: $e\n');
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

# **deleteTimeoff**
> deleteTimeoff(personId, timeoffId)

Delete Timeoff

Delete a time-off period.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getAvailabilityApi();
final String personId = personId_example; // String | 
final int timeoffId = 56; // int | 

try {
    api.deleteTimeoff(personId, timeoffId);
} catch on DioException (e) {
    print('Exception when calling AvailabilityApi->deleteTimeoff: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **personId** | **String**|  | 
 **timeoffId** | **int**|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getTimeoff**
> JsonObject getTimeoff(personId)

Get Timeoff

Get all time-off periods for a person.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getAvailabilityApi();
final String personId = personId_example; // String | 

try {
    final response = api.getTimeoff(personId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling AvailabilityApi->getTimeoff: $e\n');
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

# **updateTimeoff**
> JsonObject updateTimeoff(personId, timeoffId, timeOffCreate)

Update Timeoff

Update a time-off period.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getAvailabilityApi();
final String personId = personId_example; // String | 
final int timeoffId = 56; // int | 
final TimeOffCreate timeOffCreate = ; // TimeOffCreate | 

try {
    final response = api.updateTimeoff(personId, timeoffId, timeOffCreate);
    print(response);
} catch on DioException (e) {
    print('Exception when calling AvailabilityApi->updateTimeoff: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **personId** | **String**|  | 
 **timeoffId** | **int**|  | 
 **timeOffCreate** | [**TimeOffCreate**](TimeOffCreate.md)|  | 

### Return type

[**JsonObject**](JsonObject.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

