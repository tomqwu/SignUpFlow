# signupflow_api.api.PeopleApi

## Load the API package
```dart
import 'package:signupflow_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**bulkImportPeople**](PeopleApi.md#bulkimportpeople) | **POST** /api/v1/people/bulk | Bulk Import People
[**createPerson**](PeopleApi.md#createperson) | **POST** /api/v1/people/ | Create Person
[**deletePerson**](PeopleApi.md#deleteperson) | **DELETE** /api/v1/people/{person_id} | Delete Person
[**getCurrentPerson**](PeopleApi.md#getcurrentperson) | **GET** /api/v1/people/me | Get Current Person
[**getPerson**](PeopleApi.md#getperson) | **GET** /api/v1/people/{person_id} | Get Person
[**listPeople**](PeopleApi.md#listpeople) | **GET** /api/v1/people/ | List People
[**updateCurrentPerson**](PeopleApi.md#updatecurrentperson) | **PUT** /api/v1/people/me | Update Current Person
[**updatePerson**](PeopleApi.md#updateperson) | **PUT** /api/v1/people/{person_id} | Update Person


# **bulkImportPeople**
> BulkImportResponse bulkImportPeople(orgId, requestBody)

Bulk Import People

Admin-only bulk people import.  Strictly JSON-array body — no file upload (file uploads are Phase 2 scope). Validates each row, persists rows that don't already exist, and returns created/skipped counts plus a row-level error list.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getPeopleApi();
final String orgId = orgId_example; // String | Organization to import people into
final BuiltMap<String, JsonObject> requestBody = Object; // BuiltMap<String, JsonObject> | 

try {
    final response = api.bulkImportPeople(orgId, requestBody);
    print(response);
} catch on DioException (e) {
    print('Exception when calling PeopleApi->bulkImportPeople: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**| Organization to import people into | 
 **requestBody** | [**BuiltMap&lt;String, JsonObject&gt;**](JsonObject.md)|  | 

### Return type

[**BulkImportResponse**](BulkImportResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createPerson**
> PersonResponse createPerson(personCreate)

Create Person

Create a new person (admin only).

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getPeopleApi();
final PersonCreate personCreate = ; // PersonCreate | 

try {
    final response = api.createPerson(personCreate);
    print(response);
} catch on DioException (e) {
    print('Exception when calling PeopleApi->createPerson: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **personCreate** | [**PersonCreate**](PersonCreate.md)|  | 

### Return type

[**PersonResponse**](PersonResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deletePerson**
> deletePerson(personId)

Delete Person

Delete person (admin only).

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getPeopleApi();
final String personId = personId_example; // String | 

try {
    api.deletePerson(personId);
} catch on DioException (e) {
    print('Exception when calling PeopleApi->deletePerson: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **personId** | **String**|  | 

### Return type

void (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getCurrentPerson**
> PersonResponse getCurrentPerson()

Get Current Person

Get the current authenticated user's profile.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getPeopleApi();

try {
    final response = api.getCurrentPerson();
    print(response);
} catch on DioException (e) {
    print('Exception when calling PeopleApi->getCurrentPerson: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**PersonResponse**](PersonResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getPerson**
> PersonResponse getPerson(personId)

Get Person

Get person by ID. Users can only view people from their own organization.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getPeopleApi();
final String personId = personId_example; // String | 

try {
    final response = api.getPerson(personId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling PeopleApi->getPerson: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **personId** | **String**|  | 

### Return type

[**PersonResponse**](PersonResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listPeople**
> ListResponsePersonResponse listPeople(orgId, role, q, status, limit, offset)

List People

List people. Users can only see people from their own organization.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getPeopleApi();
final String orgId = orgId_example; // String | Filter by organization ID
final String role = role_example; // String | Filter by role
final String q = q_example; // String | Case-insensitive search across name and email
final String status = status_example; // String | Filter by Person.status (active/inactive/invited)
final int limit = 56; // int | Page size, max 200
final int offset = 56; // int | Number of rows to skip

try {
    final response = api.listPeople(orgId, role, q, status, limit, offset);
    print(response);
} catch on DioException (e) {
    print('Exception when calling PeopleApi->listPeople: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**| Filter by organization ID | [optional] 
 **role** | **String**| Filter by role | [optional] 
 **q** | **String**| Case-insensitive search across name and email | [optional] 
 **status** | **String**| Filter by Person.status (active/inactive/invited) | [optional] 
 **limit** | **int**| Page size, max 200 | [optional] [default to 50]
 **offset** | **int**| Number of rows to skip | [optional] [default to 0]

### Return type

[**ListResponsePersonResponse**](ListResponsePersonResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateCurrentPerson**
> PersonResponse updateCurrentPerson(personUpdate)

Update Current Person

Update the current authenticated user's profile.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getPeopleApi();
final PersonUpdate personUpdate = ; // PersonUpdate | 

try {
    final response = api.updateCurrentPerson(personUpdate);
    print(response);
} catch on DioException (e) {
    print('Exception when calling PeopleApi->updateCurrentPerson: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **personUpdate** | [**PersonUpdate**](PersonUpdate.md)|  | 

### Return type

[**PersonResponse**](PersonResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updatePerson**
> PersonResponse updatePerson(personId, personUpdate)

Update Person

Update person. Users can edit themselves, admins can edit anyone in their org.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getPeopleApi();
final String personId = personId_example; // String | 
final PersonUpdate personUpdate = ; // PersonUpdate | 

try {
    final response = api.updatePerson(personId, personUpdate);
    print(response);
} catch on DioException (e) {
    print('Exception when calling PeopleApi->updatePerson: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **personId** | **String**|  | 
 **personUpdate** | [**PersonUpdate**](PersonUpdate.md)|  | 

### Return type

[**PersonResponse**](PersonResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

