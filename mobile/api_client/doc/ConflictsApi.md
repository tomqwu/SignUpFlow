# signupflow_api.api.ConflictsApi

## Load the API package
```dart
import 'package:signupflow_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**checkConflicts**](ConflictsApi.md#checkconflicts) | **POST** /api/v1/conflicts/check | Check Conflicts
[**listConflicts**](ConflictsApi.md#listconflicts) | **GET** /api/v1/conflicts/ | List Conflicts


# **checkConflicts**
> ConflictCheckResponse checkConflicts(conflictCheckRequest)

Check Conflicts

Check for scheduling conflicts before assigning a person to an event.  Detects: - Already assigned to this event - Time-off periods overlapping with event - Double-booked (assigned to another event at the same time)

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getConflictsApi();
final ConflictCheckRequest conflictCheckRequest = ; // ConflictCheckRequest | 

try {
    final response = api.checkConflicts(conflictCheckRequest);
    print(response);
} catch on DioException (e) {
    print('Exception when calling ConflictsApi->checkConflicts: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **conflictCheckRequest** | [**ConflictCheckRequest**](ConflictCheckRequest.md)|  | 

### Return type

[**ConflictCheckResponse**](ConflictCheckResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listConflicts**
> ListResponseConflictType listConflicts(orgId, personId, limit, offset)

List Conflicts

List currently-detected conflicts across an org (admin-only).  Scans every Assignment in the org (or just the named person's) and surfaces `time_off` and `double_booked` conflicts. `already_assigned` is intentionally omitted because the assignment exists.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getConflictsApi();
final String orgId = orgId_example; // String | Organization ID
final String personId = personId_example; // String | Optional filter to a single person
final int limit = 56; // int | Page size, max 200
final int offset = 56; // int | Number of rows to skip

try {
    final response = api.listConflicts(orgId, personId, limit, offset);
    print(response);
} catch on DioException (e) {
    print('Exception when calling ConflictsApi->listConflicts: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**| Organization ID | 
 **personId** | **String**| Optional filter to a single person | [optional] 
 **limit** | **int**| Page size, max 200 | [optional] [default to 50]
 **offset** | **int**| Number of rows to skip | [optional] [default to 0]

### Return type

[**ListResponseConflictType**](ListResponseConflictType.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

