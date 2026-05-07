# signupflow_api.api.ResourcesApi

## Load the API package
```dart
import 'package:signupflow_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**createResource**](ResourcesApi.md#createresource) | **POST** /api/v1/resources/ | Create Resource
[**deleteResource**](ResourcesApi.md#deleteresource) | **DELETE** /api/v1/resources/{resource_id} | Delete Resource
[**getResource**](ResourcesApi.md#getresource) | **GET** /api/v1/resources/{resource_id} | Get Resource
[**listResources**](ResourcesApi.md#listresources) | **GET** /api/v1/resources/ | List Resources
[**updateResource**](ResourcesApi.md#updateresource) | **PUT** /api/v1/resources/{resource_id} | Update Resource


# **createResource**
> ResourceResponse createResource(resourceCreate)

Create Resource

Create a new resource (admin only, scoped to admin's org).

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getResourcesApi();
final ResourceCreate resourceCreate = ; // ResourceCreate | 

try {
    final response = api.createResource(resourceCreate);
    print(response);
} catch on DioException (e) {
    print('Exception when calling ResourcesApi->createResource: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resourceCreate** | [**ResourceCreate**](ResourceCreate.md)|  | 

### Return type

[**ResourceResponse**](ResourceResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteResource**
> deleteResource(resourceId)

Delete Resource

Delete a resource (admin only).  Refuses with 409 if any Event still references the resource — preserves referential integrity without forcing the admin to discover dangling FKs by surprise.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getResourcesApi();
final String resourceId = resourceId_example; // String | 

try {
    api.deleteResource(resourceId);
} catch on DioException (e) {
    print('Exception when calling ResourcesApi->deleteResource: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resourceId** | **String**|  | 

### Return type

void (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getResource**
> ResourceResponse getResource(resourceId)

Get Resource

Get a single resource by id; tenancy enforced via the row's org_id.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getResourcesApi();
final String resourceId = resourceId_example; // String | 

try {
    final response = api.getResource(resourceId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling ResourcesApi->getResource: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resourceId** | **String**|  | 

### Return type

[**ResourceResponse**](ResourceResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listResources**
> ListResponseResourceResponse listResources(orgId, type, limit, offset)

List Resources

List resources for one organization. Caller must be a member.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getResourcesApi();
final String orgId = orgId_example; // String | Organization ID — required (single-tenant scope)
final String type = type_example; // String | Filter by resource type
final int limit = 56; // int | Page size, max 200
final int offset = 56; // int | Number of rows to skip

try {
    final response = api.listResources(orgId, type, limit, offset);
    print(response);
} catch on DioException (e) {
    print('Exception when calling ResourcesApi->listResources: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**| Organization ID — required (single-tenant scope) | 
 **type** | **String**| Filter by resource type | [optional] 
 **limit** | **int**| Page size, max 200 | [optional] [default to 50]
 **offset** | **int**| Number of rows to skip | [optional] [default to 0]

### Return type

[**ListResponseResourceResponse**](ListResponseResourceResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateResource**
> ResourceResponse updateResource(resourceId, resourceUpdate)

Update Resource

Update a resource (admin only). org_id is immutable.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getResourcesApi();
final String resourceId = resourceId_example; // String | 
final ResourceUpdate resourceUpdate = ; // ResourceUpdate | 

try {
    final response = api.updateResource(resourceId, resourceUpdate);
    print(response);
} catch on DioException (e) {
    print('Exception when calling ResourcesApi->updateResource: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resourceId** | **String**|  | 
 **resourceUpdate** | [**ResourceUpdate**](ResourceUpdate.md)|  | 

### Return type

[**ResourceResponse**](ResourceResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

