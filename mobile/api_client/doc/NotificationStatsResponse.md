# signupflow_api.model.NotificationStatsResponse

## Load the model package
```dart
import 'package:signupflow_api/api.dart';
```

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**daysAnalyzed** | **int** |  | 
**deliveredNotifications** | **int** |  | 
**orgId** | **String** |  | 
**recentFailures** | [**BuiltList&lt;NotificationResponse&gt;**](NotificationResponse.md) | Recent failed notifications | 
**statusBreakdown** | **BuiltMap&lt;String, int&gt;** | Count of notifications by status | 
**successRate** | **num** | Delivery success rate percentage | 
**totalNotifications** | **int** |  | 
**typeBreakdown** | **BuiltMap&lt;String, int&gt;** | Count of notifications by type | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


