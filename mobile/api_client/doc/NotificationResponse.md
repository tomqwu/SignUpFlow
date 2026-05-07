# signupflow_api.model.NotificationResponse

## Load the model package
```dart
import 'package:signupflow_api/api.dart';
```

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**clickedAt** | [**DateTime**](DateTime.md) |  | [optional] 
**createdAt** | [**DateTime**](DateTime.md) |  | 
**deliveredAt** | [**DateTime**](DateTime.md) |  | [optional] 
**errorMessage** | **String** |  | [optional] 
**eventId** | **String** |  | [optional] 
**id** | **int** |  | 
**openedAt** | [**DateTime**](DateTime.md) |  | [optional] 
**orgId** | **String** |  | 
**recipientId** | **String** |  | 
**retryCount** | **int** |  | 
**sendgridMessageId** | **String** |  | [optional] 
**sentAt** | [**DateTime**](DateTime.md) |  | [optional] 
**status** | **String** | Notification status (pending, sent, delivered, etc.) | 
**templateData** | [**BuiltMap&lt;String, JsonObject&gt;**](JsonObject.md) |  | [optional] 
**type** | **String** | Notification type (assignment, reminder, update, cancellation) | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


