# signupflow_api.api.AvailabilityApi

## Load the API package
```dart
import 'package:signupflow_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**addException**](AvailabilityApi.md#addexception) | **POST** /api/v1/availability/{person_id}/exceptions | Add Exception
[**addTimeoff**](AvailabilityApi.md#addtimeoff) | **POST** /api/v1/availability/{person_id}/timeoff | Add Timeoff
[**clearRrule**](AvailabilityApi.md#clearrrule) | **DELETE** /api/v1/availability/{person_id}/rrule | Clear Rrule
[**createAvailability**](AvailabilityApi.md#createavailability) | **POST** /api/v1/availability/ | Create Availability
[**deleteException**](AvailabilityApi.md#deleteexception) | **DELETE** /api/v1/availability/{person_id}/exceptions/{exception_id} | Delete Exception
[**deleteTimeoff**](AvailabilityApi.md#deletetimeoff) | **DELETE** /api/v1/availability/{person_id}/timeoff/{timeoff_id} | Delete Timeoff
[**getRrule**](AvailabilityApi.md#getrrule) | **GET** /api/v1/availability/{person_id}/rrule | Get Rrule
[**getTimeoff**](AvailabilityApi.md#gettimeoff) | **GET** /api/v1/availability/{person_id}/timeoff | Get Timeoff
[**listExceptions**](AvailabilityApi.md#listexceptions) | **GET** /api/v1/availability/{person_id}/exceptions | List Exceptions
[**setRrule**](AvailabilityApi.md#setrrule) | **PUT** /api/v1/availability/{person_id}/rrule | Set Rrule
[**updateTimeoff**](AvailabilityApi.md#updatetimeoff) | **PATCH** /api/v1/availability/{person_id}/timeoff/{timeoff_id} | Update Timeoff


# **addException**
> AvailabilityExceptionResponse addException(personId, availabilityExceptionCreate)

Add Exception

Add a single-date exception. Idempotent on (availability_id, date).

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getAvailabilityApi();
final String personId = personId_example; // String | 
final AvailabilityExceptionCreate availabilityExceptionCreate = ; // AvailabilityExceptionCreate | 

try {
    final response = api.addException(personId, availabilityExceptionCreate);
    print(response);
} catch on DioException (e) {
    print('Exception when calling AvailabilityApi->addException: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **personId** | **String**|  | 
 **availabilityExceptionCreate** | [**AvailabilityExceptionCreate**](AvailabilityExceptionCreate.md)|  | 

### Return type

[**AvailabilityExceptionResponse**](AvailabilityExceptionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

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

# **clearRrule**
> clearRrule(personId)

Clear Rrule

Clear the rrule string for a person.  Idempotent — succeeds with 204 even if the row never had an rrule, or even if the Availability row doesn't exist yet.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getAvailabilityApi();
final String personId = personId_example; // String | 

try {
    api.clearRrule(personId);
} catch on DioException (e) {
    print('Exception when calling AvailabilityApi->clearRrule: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **personId** | **String**|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
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

# **deleteException**
> deleteException(personId, exceptionId)

Delete Exception

Delete a single-date exception by id.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getAvailabilityApi();
final String personId = personId_example; // String | 
final int exceptionId = 56; // int | 

try {
    api.deleteException(personId, exceptionId);
} catch on DioException (e) {
    print('Exception when calling AvailabilityApi->deleteException: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **personId** | **String**|  | 
 **exceptionId** | **int**|  | 

### Return type

void (empty response body)

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

# **getRrule**
> AvailabilityRruleResponse getRrule(personId)

Get Rrule

Return the single recurring-availability rrule for a person.  Returns ``rrule: null`` when the person has no Availability row or has not set an rrule. Mobile renders this as \"no recurring rule yet.\"

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getAvailabilityApi();
final String personId = personId_example; // String | 

try {
    final response = api.getRrule(personId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling AvailabilityApi->getRrule: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **personId** | **String**|  | 

### Return type

[**AvailabilityRruleResponse**](AvailabilityRruleResponse.md)

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

# **listExceptions**
> BuiltList<AvailabilityExceptionResponse> listExceptions(personId)

List Exceptions

List single-date availability exceptions for a person.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getAvailabilityApi();
final String personId = personId_example; // String | 

try {
    final response = api.listExceptions(personId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling AvailabilityApi->listExceptions: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **personId** | **String**|  | 

### Return type

[**BuiltList&lt;AvailabilityExceptionResponse&gt;**](AvailabilityExceptionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **setRrule**
> AvailabilityRruleResponse setRrule(personId, availabilityRruleUpdate)

Set Rrule

Set (or replace) the rrule string for a person.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getAvailabilityApi();
final String personId = personId_example; // String | 
final AvailabilityRruleUpdate availabilityRruleUpdate = ; // AvailabilityRruleUpdate | 

try {
    final response = api.setRrule(personId, availabilityRruleUpdate);
    print(response);
} catch on DioException (e) {
    print('Exception when calling AvailabilityApi->setRrule: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **personId** | **String**|  | 
 **availabilityRruleUpdate** | [**AvailabilityRruleUpdate**](AvailabilityRruleUpdate.md)|  | 

### Return type

[**AvailabilityRruleResponse**](AvailabilityRruleResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
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

