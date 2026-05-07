# signupflow_api.model.PersonCreate

## Load the model package
```dart
import 'package:signupflow_api/api.dart';
```

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email** | **String** |  | [optional] 
**extraData** | [**BuiltMap&lt;String, JsonObject&gt;**](JsonObject.md) |  | [optional] 
**id** | **String** | Unique person ID | 
**language** | **String** | User's language preference (ISO 639-1 code) | [optional] [default to 'en']
**name** | **String** | Person's full name | 
**orgId** | **String** | Organization ID | 
**roles** | **BuiltList&lt;String&gt;** |  | [optional] 
**timezone** | **String** | User's timezone preference | [optional] [default to 'UTC']

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


