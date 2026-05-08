# signupflow_api.model.AuthResponse

## Load the model package
```dart
import 'package:signupflow_api/api.dart';
```

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email** | **String** |  | 
**language** | **String** |  | 
**name** | **String** |  | 
**orgId** | **String** |  | 
**personId** | **String** |  | 
**refreshToken** | **String** | Refresh token (long-lived). Use POST /auth/refresh to exchange for a fresh access+refresh token pair. | [optional] [default to '']
**roles** | **BuiltList&lt;String&gt;** |  | 
**timezone** | **String** |  | 
**token** | **String** |  | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


