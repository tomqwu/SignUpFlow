# signupflow_api.api.HealthApi

## Load the API package
```dart
import 'package:signupflow_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**healthCheck**](HealthApi.md#healthcheck) | **GET** /health | Health Check


# **healthCheck**
> JsonObject healthCheck()

Health Check

Health check endpoint with database connectivity check.  Returns:     200 OK: Service and database are healthy     503 Service Unavailable: Database connection failed

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getHealthApi();

try {
    final response = api.healthCheck();
    print(response);
} catch on DioException (e) {
    print('Exception when calling HealthApi->healthCheck: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**JsonObject**](JsonObject.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

