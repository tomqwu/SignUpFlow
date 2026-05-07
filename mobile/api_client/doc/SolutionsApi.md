# signupflow_api.api.SolutionsApi

## Load the API package
```dart
import 'package:signupflow_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**compareSolutions**](SolutionsApi.md#comparesolutions) | **GET** /api/v1/solutions/{solution_a_id}/compare/{solution_b_id} | Compare Solutions
[**createManualSolution**](SolutionsApi.md#createmanualsolution) | **POST** /api/v1/solutions/ | Create Manual Solution
[**deleteSolution**](SolutionsApi.md#deletesolution) | **DELETE** /api/v1/solutions/{solution_id} | Delete Solution
[**exportSolution**](SolutionsApi.md#exportsolution) | **POST** /api/v1/solutions/{solution_id}/export | Export Solution
[**getSolution**](SolutionsApi.md#getsolution) | **GET** /api/v1/solutions/{solution_id} | Get Solution
[**getSolutionAssignments**](SolutionsApi.md#getsolutionassignments) | **GET** /api/v1/solutions/{solution_id}/assignments | Get Solution Assignments
[**getSolutionStats**](SolutionsApi.md#getsolutionstats) | **GET** /api/v1/solutions/{solution_id}/stats | Get Solution Stats
[**listSolutions**](SolutionsApi.md#listsolutions) | **GET** /api/v1/solutions/ | List Solutions
[**publishSolution**](SolutionsApi.md#publishsolution) | **POST** /api/v1/solutions/{solution_id}/publish | Publish Solution
[**rollbackSolution**](SolutionsApi.md#rollbacksolution) | **POST** /api/v1/solutions/{solution_id}/rollback | Rollback Solution
[**unpublishSolution**](SolutionsApi.md#unpublishsolution) | **POST** /api/v1/solutions/{solution_id}/unpublish | Unpublish Solution


# **compareSolutions**
> SolutionDiffResponse compareSolutions(solutionAId, solutionBId)

Compare Solutions

Diff two solutions (admin only). Both must belong to the same org as the caller.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getSolutionsApi();
final int solutionAId = 56; // int | 
final int solutionBId = 56; // int | 

try {
    final response = api.compareSolutions(solutionAId, solutionBId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling SolutionsApi->compareSolutions: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **solutionAId** | **int**|  | 
 **solutionBId** | **int**|  | 

### Return type

[**SolutionDiffResponse**](SolutionDiffResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createManualSolution**
> SolutionResponse createManualSolution(requestBody)

Create Manual Solution

Create a manual solution record (for testing or external import). Note: This does not create assignments, just the solution metadata.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getSolutionsApi();
final BuiltMap<String, JsonObject> requestBody = Object; // BuiltMap<String, JsonObject> | 

try {
    final response = api.createManualSolution(requestBody);
    print(response);
} catch on DioException (e) {
    print('Exception when calling SolutionsApi->createManualSolution: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **requestBody** | [**BuiltMap&lt;String, JsonObject&gt;**](JsonObject.md)|  | 

### Return type

[**SolutionResponse**](SolutionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteSolution**
> deleteSolution(solutionId)

Delete Solution

Delete solution and all assignments.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getSolutionsApi();
final int solutionId = 56; // int | 

try {
    api.deleteSolution(solutionId);
} catch on DioException (e) {
    print('Exception when calling SolutionsApi->deleteSolution: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **solutionId** | **int**|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **exportSolution**
> JsonObject exportSolution(solutionId, exportFormat)

Export Solution

Export solution in various formats (CSV, ICS, JSON).

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getSolutionsApi();
final int solutionId = 56; // int | 
final ExportFormat exportFormat = ; // ExportFormat | 

try {
    final response = api.exportSolution(solutionId, exportFormat);
    print(response);
} catch on DioException (e) {
    print('Exception when calling SolutionsApi->exportSolution: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **solutionId** | **int**|  | 
 **exportFormat** | [**ExportFormat**](ExportFormat.md)|  | 

### Return type

[**JsonObject**](JsonObject.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getSolution**
> SolutionResponse getSolution(solutionId)

Get Solution

Get solution by ID.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getSolutionsApi();
final int solutionId = 56; // int | 

try {
    final response = api.getSolution(solutionId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling SolutionsApi->getSolution: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **solutionId** | **int**|  | 

### Return type

[**SolutionResponse**](SolutionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getSolutionAssignments**
> JsonObject getSolutionAssignments(solutionId)

Get Solution Assignments

Get all assignments for a solution.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getSolutionsApi();
final int solutionId = 56; // int | 

try {
    final response = api.getSolutionAssignments(solutionId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling SolutionsApi->getSolutionAssignments: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **solutionId** | **int**|  | 

### Return type

[**JsonObject**](JsonObject.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getSolutionStats**
> SolutionStatsResponse getSolutionStats(solutionId)

Get Solution Stats

Stats endpoint (admin only): fairness histogram + stability + workload distribution.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getSolutionsApi();
final int solutionId = 56; // int | 

try {
    final response = api.getSolutionStats(solutionId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling SolutionsApi->getSolutionStats: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **solutionId** | **int**|  | 

### Return type

[**SolutionStatsResponse**](SolutionStatsResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listSolutions**
> ListResponseSolutionResponse listSolutions(orgId, limit, offset)

List Solutions

List solutions with optional filters.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getSolutionsApi();
final String orgId = orgId_example; // String | Filter by organization ID
final int limit = 56; // int | Page size, max 200
final int offset = 56; // int | Number of rows to skip

try {
    final response = api.listSolutions(orgId, limit, offset);
    print(response);
} catch on DioException (e) {
    print('Exception when calling SolutionsApi->listSolutions: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**| Filter by organization ID | [optional] 
 **limit** | **int**| Page size, max 200 | [optional] [default to 50]
 **offset** | **int**| Number of rows to skip | [optional] [default to 0]

### Return type

[**ListResponseSolutionResponse**](ListResponseSolutionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **publishSolution**
> SolutionResponse publishSolution(solutionId)

Publish Solution

Publish a solution (admin only). Unpublishes any prior published in the same org.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getSolutionsApi();
final int solutionId = 56; // int | 

try {
    final response = api.publishSolution(solutionId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling SolutionsApi->publishSolution: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **solutionId** | **int**|  | 

### Return type

[**SolutionResponse**](SolutionResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **rollbackSolution**
> SolutionResponse rollbackSolution(solutionId)

Rollback Solution

Rollback to a previously-published solution (admin only).  Republishes the target and unpublishes whatever is currently published in the same org. The target must have been published at some point before (i.e. an audit row recording its publish/rollback exists); otherwise 400.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getSolutionsApi();
final int solutionId = 56; // int | 

try {
    final response = api.rollbackSolution(solutionId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling SolutionsApi->rollbackSolution: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **solutionId** | **int**|  | 

### Return type

[**SolutionResponse**](SolutionResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **unpublishSolution**
> SolutionResponse unpublishSolution(solutionId)

Unpublish Solution

Unpublish a solution (admin only).

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getSolutionsApi();
final int solutionId = 56; // int | 

try {
    final response = api.unpublishSolution(solutionId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling SolutionsApi->unpublishSolution: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **solutionId** | **int**|  | 

### Return type

[**SolutionResponse**](SolutionResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

