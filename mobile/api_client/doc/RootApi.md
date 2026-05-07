# signupflow_api.api.RootApi

## Load the API package
```dart
import 'package:signupflow_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**apiInfo**](RootApi.md#apiinfo) | **GET** /api/v1 | Api Info


# **apiInfo**
> JsonObject apiInfo()

Api Info

API information endpoint.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getRootApi();

try {
    final response = api.apiInfo();
    print(response);
} catch on DioException (e) {
    print('Exception when calling RootApi->apiInfo: $e\n');
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

