# signupflow_api.api.AuditApi

## Load the API package
```dart
import 'package:signupflow_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**listAuditLogs**](AuditApi.md#listauditlogs) | **GET** /api/v1/audit-logs | List Audit Logs


# **listAuditLogs**
> ListResponseAuditLogResponse listAuditLogs(userId, action, resourceType, startDate, endDate, status, limit, offset)

List Audit Logs

Return audit log rows scoped to the caller's organization.  Admin-only. Each call is itself recorded as a `data.exported` audit event so reads of the audit log are themselves auditable.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getAuditApi();
final String userId = userId_example; // String | Filter by user_id
final String action = action_example; // String | Filter by action (e.g., auth.login.success)
final String resourceType = resourceType_example; // String | Filter by resource_type
final DateTime startDate = 2013-10-20T19:20:30+01:00; // DateTime | Inclusive lower bound on timestamp
final DateTime endDate = 2013-10-20T19:20:30+01:00; // DateTime | Inclusive upper bound on timestamp
final String status = status_example; // String | success / failure / denied
final int limit = 56; // int | Page size, max 200
final int offset = 56; // int | Number of rows to skip

try {
    final response = api.listAuditLogs(userId, action, resourceType, startDate, endDate, status, limit, offset);
    print(response);
} catch on DioException (e) {
    print('Exception when calling AuditApi->listAuditLogs: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **userId** | **String**| Filter by user_id | [optional] 
 **action** | **String**| Filter by action (e.g., auth.login.success) | [optional] 
 **resourceType** | **String**| Filter by resource_type | [optional] 
 **startDate** | **DateTime**| Inclusive lower bound on timestamp | [optional] 
 **endDate** | **DateTime**| Inclusive upper bound on timestamp | [optional] 
 **status** | **String**| success / failure / denied | [optional] 
 **limit** | **int**| Page size, max 200 | [optional] [default to 50]
 **offset** | **int**| Number of rows to skip | [optional] [default to 0]

### Return type

[**ListResponseAuditLogResponse**](ListResponseAuditLogResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

