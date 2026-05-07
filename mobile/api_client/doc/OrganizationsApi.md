# signupflow_api.api.OrganizationsApi

## Load the API package
```dart
import 'package:signupflow_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**cancelOrganization**](OrganizationsApi.md#cancelorganization) | **POST** /api/v1/organizations/{org_id}/cancel | Cancel Organization
[**createOrganization**](OrganizationsApi.md#createorganization) | **POST** /api/v1/organizations/ | Create Organization
[**deleteOrganization**](OrganizationsApi.md#deleteorganization) | **DELETE** /api/v1/organizations/{org_id} | Delete Organization
[**getOrganization**](OrganizationsApi.md#getorganization) | **GET** /api/v1/organizations/{org_id} | Get Organization
[**listOrganizations**](OrganizationsApi.md#listorganizations) | **GET** /api/v1/organizations/ | List Organizations
[**restoreOrganization**](OrganizationsApi.md#restoreorganization) | **POST** /api/v1/organizations/{org_id}/restore | Restore Organization
[**updateOrganization**](OrganizationsApi.md#updateorganization) | **PUT** /api/v1/organizations/{org_id} | Update Organization


# **cancelOrganization**
> OrganizationResponse cancelOrganization(orgId)

Cancel Organization

Soft-cancel the organization (admin only).  Sets `cancelled_at` to now and schedules a 30-day data-retention window via `data_retention_until`. The org is excluded from the default list until restored.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getOrganizationsApi();
final String orgId = orgId_example; // String | 

try {
    final response = api.cancelOrganization(orgId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling OrganizationsApi->cancelOrganization: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**|  | 

### Return type

[**OrganizationResponse**](OrganizationResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createOrganization**
> OrganizationResponse createOrganization(organizationCreate)

Create Organization

Create a new organization. Rate limited to 2 requests per hour per IP.  Automatically creates Free plan subscription with 10 volunteer limit.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getOrganizationsApi();
final OrganizationCreate organizationCreate = ; // OrganizationCreate | 

try {
    final response = api.createOrganization(organizationCreate);
    print(response);
} catch on DioException (e) {
    print('Exception when calling OrganizationsApi->createOrganization: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organizationCreate** | [**OrganizationCreate**](OrganizationCreate.md)|  | 

### Return type

[**OrganizationResponse**](OrganizationResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteOrganization**
> deleteOrganization(orgId)

Delete Organization

Delete organization and all related data.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getOrganizationsApi();
final String orgId = orgId_example; // String | 

try {
    api.deleteOrganization(orgId);
} catch on DioException (e) {
    print('Exception when calling OrganizationsApi->deleteOrganization: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getOrganization**
> OrganizationResponse getOrganization(orgId)

Get Organization

Get organization by ID.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getOrganizationsApi();
final String orgId = orgId_example; // String | 

try {
    final response = api.getOrganization(orgId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling OrganizationsApi->getOrganization: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**|  | 

### Return type

[**OrganizationResponse**](OrganizationResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listOrganizations**
> ListResponseOrganizationResponse listOrganizations(includeCancelled, q, limit, offset)

List Organizations

List all organizations. Excludes cancelled by default.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getOrganizationsApi();
final bool includeCancelled = true; // bool | Include organizations that have been cancelled (admin view)
final String q = q_example; // String | Case-insensitive search on organization name
final int limit = 56; // int | Page size, max 200
final int offset = 56; // int | Number of rows to skip

try {
    final response = api.listOrganizations(includeCancelled, q, limit, offset);
    print(response);
} catch on DioException (e) {
    print('Exception when calling OrganizationsApi->listOrganizations: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **includeCancelled** | **bool**| Include organizations that have been cancelled (admin view) | [optional] [default to false]
 **q** | **String**| Case-insensitive search on organization name | [optional] 
 **limit** | **int**| Page size, max 200 | [optional] [default to 50]
 **offset** | **int**| Number of rows to skip | [optional] [default to 0]

### Return type

[**ListResponseOrganizationResponse**](ListResponseOrganizationResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **restoreOrganization**
> OrganizationResponse restoreOrganization(orgId)

Restore Organization

Restore a cancelled organization (admin only). Clears cancellation fields.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getOrganizationsApi();
final String orgId = orgId_example; // String | 

try {
    final response = api.restoreOrganization(orgId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling OrganizationsApi->restoreOrganization: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**|  | 

### Return type

[**OrganizationResponse**](OrganizationResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateOrganization**
> OrganizationResponse updateOrganization(orgId, organizationUpdate)

Update Organization

Update organization.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getOrganizationsApi();
final String orgId = orgId_example; // String | 
final OrganizationUpdate organizationUpdate = ; // OrganizationUpdate | 

try {
    final response = api.updateOrganization(orgId, organizationUpdate);
    print(response);
} catch on DioException (e) {
    print('Exception when calling OrganizationsApi->updateOrganization: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**|  | 
 **organizationUpdate** | [**OrganizationUpdate**](OrganizationUpdate.md)|  | 

### Return type

[**OrganizationResponse**](OrganizationResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

