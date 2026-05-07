# signupflow_api.model.EmailPreferenceResponse

## Load the model package
```dart
import 'package:signupflow_api/api.dart';
```

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**digestHour** | **int** | Hour to send digests (0-23) | [optional] [default to 8]
**enabledTypes** | **BuiltList&lt;String&gt;** | List of enabled notification types | [optional] 
**frequency** | **String** | Email frequency (immediate, daily, weekly, disabled) | [optional] [default to 'immediate']
**id** | **int** |  | [optional] 
**language** | **String** | Email language preference (ISO 639-1 code) | [optional] [default to 'en']
**orgId** | **String** |  | 
**personId** | **String** |  | 
**timezone** | **String** | Timezone for digest scheduling | [optional] [default to 'UTC']
**unsubscribeToken** | **String** |  | [optional] 
**updatedAt** | [**DateTime**](DateTime.md) |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


