# signupflow_api.api.ConstraintsApi

## Load the API package
```dart
import 'package:signupflow_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**createConstraint**](ConstraintsApi.md#createconstraint) | **POST** /api/v1/constraints/ | Create Constraint
[**deleteConstraint**](ConstraintsApi.md#deleteconstraint) | **DELETE** /api/v1/constraints/{constraint_id} | Delete Constraint
[**getConstraint**](ConstraintsApi.md#getconstraint) | **GET** /api/v1/constraints/{constraint_id} | Get Constraint
[**listConstraints**](ConstraintsApi.md#listconstraints) | **GET** /api/v1/constraints/ | List Constraints
[**updateConstraint**](ConstraintsApi.md#updateconstraint) | **PUT** /api/v1/constraints/{constraint_id} | Update Constraint


# **createConstraint**
> ConstraintResponse createConstraint(constraintCreate)

Create Constraint

Create a new constraint (admin only, scoped to admin's org).

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getConstraintsApi();
final ConstraintCreate constraintCreate = ; // ConstraintCreate | 

try {
    final response = api.createConstraint(constraintCreate);
    print(response);
} catch on DioException (e) {
    print('Exception when calling ConstraintsApi->createConstraint: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **constraintCreate** | [**ConstraintCreate**](ConstraintCreate.md)|  | 

### Return type

[**ConstraintResponse**](ConstraintResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteConstraint**
> deleteConstraint(constraintId)

Delete Constraint

Delete constraint (admin only, scoped to admin's org).

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getConstraintsApi();
final int constraintId = 56; // int | 

try {
    api.deleteConstraint(constraintId);
} catch on DioException (e) {
    print('Exception when calling ConstraintsApi->deleteConstraint: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **constraintId** | **int**|  | 

### Return type

void (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getConstraint**
> ConstraintResponse getConstraint(constraintId)

Get Constraint

Get constraint by ID; org isolation enforced.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getConstraintsApi();
final int constraintId = 56; // int | 

try {
    final response = api.getConstraint(constraintId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling ConstraintsApi->getConstraint: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **constraintId** | **int**|  | 

### Return type

[**ConstraintResponse**](ConstraintResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listConstraints**
> ListResponseConstraintResponse listConstraints(orgId, constraintType, limit, offset)

List Constraints

List constraints. Always scoped to the caller's organization.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getConstraintsApi();
final String orgId = orgId_example; // String | Filter by organization ID
final String constraintType = constraintType_example; // String | Filter by type (hard/soft)
final int limit = 56; // int | Page size, max 200
final int offset = 56; // int | Number of rows to skip

try {
    final response = api.listConstraints(orgId, constraintType, limit, offset);
    print(response);
} catch on DioException (e) {
    print('Exception when calling ConstraintsApi->listConstraints: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**| Filter by organization ID | [optional] 
 **constraintType** | **String**| Filter by type (hard/soft) | [optional] 
 **limit** | **int**| Page size, max 200 | [optional] [default to 50]
 **offset** | **int**| Number of rows to skip | [optional] [default to 0]

### Return type

[**ListResponseConstraintResponse**](ListResponseConstraintResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateConstraint**
> ConstraintResponse updateConstraint(constraintId, constraintUpdate)

Update Constraint

Update constraint (admin only, scoped to admin's org).

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getConstraintsApi();
final int constraintId = 56; // int | 
final ConstraintUpdate constraintUpdate = ; // ConstraintUpdate | 

try {
    final response = api.updateConstraint(constraintId, constraintUpdate);
    print(response);
} catch on DioException (e) {
    print('Exception when calling ConstraintsApi->updateConstraint: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **constraintId** | **int**|  | 
 **constraintUpdate** | [**ConstraintUpdate**](ConstraintUpdate.md)|  | 

### Return type

[**ConstraintResponse**](ConstraintResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

