# signupflow_api.api.AssignmentsApi

## Load the API package
```dart
import 'package:signupflow_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**acceptAssignment**](AssignmentsApi.md#acceptassignment) | **POST** /api/v1/assignments/{assignment_id}/accept | Accept Assignment
[**declineAssignment**](AssignmentsApi.md#declineassignment) | **POST** /api/v1/assignments/{assignment_id}/decline | Decline Assignment
[**listMyAssignments**](AssignmentsApi.md#listmyassignments) | **GET** /api/v1/assignments/me | List My Assignments
[**requestSwap**](AssignmentsApi.md#requestswap) | **POST** /api/v1/assignments/{assignment_id}/swap-request | Request Swap


# **acceptAssignment**
> AssignmentResponse acceptAssignment(assignmentId)

Accept Assignment

Mark the caller's assignment as confirmed.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getAssignmentsApi();
final int assignmentId = 56; // int | 

try {
    final response = api.acceptAssignment(assignmentId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling AssignmentsApi->acceptAssignment: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **assignmentId** | **int**|  | 

### Return type

[**AssignmentResponse**](AssignmentResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **declineAssignment**
> AssignmentResponse declineAssignment(assignmentId, assignmentDeclineRequest)

Decline Assignment

Decline the caller's assignment with a reason.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getAssignmentsApi();
final int assignmentId = 56; // int | 
final AssignmentDeclineRequest assignmentDeclineRequest = ; // AssignmentDeclineRequest | 

try {
    final response = api.declineAssignment(assignmentId, assignmentDeclineRequest);
    print(response);
} catch on DioException (e) {
    print('Exception when calling AssignmentsApi->declineAssignment: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **assignmentId** | **int**|  | 
 **assignmentDeclineRequest** | [**AssignmentDeclineRequest**](AssignmentDeclineRequest.md)|  | 

### Return type

[**AssignmentResponse**](AssignmentResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listMyAssignments**
> ListResponseAssignmentResponse listMyAssignments(limit, offset)

List My Assignments

Return assignments belonging to the caller, scoped to their org via the join.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getAssignmentsApi();
final int limit = 56; // int | Page size, max 200
final int offset = 56; // int | Number of rows to skip

try {
    final response = api.listMyAssignments(limit, offset);
    print(response);
} catch on DioException (e) {
    print('Exception when calling AssignmentsApi->listMyAssignments: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| Page size, max 200 | [optional] [default to 50]
 **offset** | **int**| Number of rows to skip | [optional] [default to 0]

### Return type

[**ListResponseAssignmentResponse**](ListResponseAssignmentResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **requestSwap**
> AssignmentResponse requestSwap(assignmentId, assignmentSwapRequest)

Request Swap

Flag the caller's assignment for swap; admin follows up out of band.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getAssignmentsApi();
final int assignmentId = 56; // int | 
final AssignmentSwapRequest assignmentSwapRequest = ; // AssignmentSwapRequest | 

try {
    final response = api.requestSwap(assignmentId, assignmentSwapRequest);
    print(response);
} catch on DioException (e) {
    print('Exception when calling AssignmentsApi->requestSwap: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **assignmentId** | **int**|  | 
 **assignmentSwapRequest** | [**AssignmentSwapRequest**](AssignmentSwapRequest.md)|  | 

### Return type

[**AssignmentResponse**](AssignmentResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

