# signupflow_api.api.SolverApi

## Load the API package
```dart
import 'package:signupflow_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**solveSchedule**](SolverApi.md#solveschedule) | **POST** /api/v1/solver/solve | Solve Schedule


# **solveSchedule**
> SolveResponse solveSchedule(solveRequest)

Solve Schedule

Generate a schedule for the organization (admin only).  This endpoint: 1. Loads all org data from database 2. Runs the constraint solver 3. Saves the solution to database 4. Returns solution metrics and violations

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getSolverApi();
final SolveRequest solveRequest = ; // SolveRequest | 

try {
    final response = api.solveSchedule(solveRequest);
    print(response);
} catch on DioException (e) {
    print('Exception when calling SolverApi->solveSchedule: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **solveRequest** | [**SolveRequest**](SolveRequest.md)|  | 

### Return type

[**SolveResponse**](SolveResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

