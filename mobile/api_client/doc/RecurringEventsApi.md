# signupflow_api.api.RecurringEventsApi

## Load the API package
```dart
import 'package:signupflow_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**createRecurringSeries**](RecurringEventsApi.md#createrecurringseries) | **POST** /api/v1/recurring-series | Create Recurring Series
[**deleteRecurringSeries**](RecurringEventsApi.md#deleterecurringseries) | **DELETE** /api/v1/recurring-series/{series_id} | Delete Recurring Series
[**getRecurringSeries**](RecurringEventsApi.md#getrecurringseries) | **GET** /api/v1/recurring-series/{series_id} | Get Recurring Series
[**getSeriesOccurrences**](RecurringEventsApi.md#getseriesoccurrences) | **GET** /api/v1/recurring-series/{series_id}/occurrences | Get Series Occurrences
[**listRecurringSeries**](RecurringEventsApi.md#listrecurringseries) | **GET** /api/v1/recurring-series | List Recurring Series
[**previewOccurrences**](RecurringEventsApi.md#previewoccurrences) | **POST** /api/v1/recurring-series/preview | Preview Occurrences
[**updateSeriesTemplate**](RecurringEventsApi.md#updateseriestemplate) | **PUT** /api/v1/recurring-series/{series_id} | Update Series Template


# **createRecurringSeries**
> RecurringSeriesResponse createRecurringSeries(orgId, recurringSeriesCreate)

Create Recurring Series

Create a new recurring event series and generate all occurrences.  Requires admin access. Creates: 1. RecurringSeries template 2. Individual Event occurrences based on pattern 3. Links occurrences to series  Returns the created series with occurrence count.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getRecurringEventsApi();
final String orgId = orgId_example; // String | Organization ID
final RecurringSeriesCreate recurringSeriesCreate = ; // RecurringSeriesCreate | 

try {
    final response = api.createRecurringSeries(orgId, recurringSeriesCreate);
    print(response);
} catch on DioException (e) {
    print('Exception when calling RecurringEventsApi->createRecurringSeries: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**| Organization ID | 
 **recurringSeriesCreate** | [**RecurringSeriesCreate**](RecurringSeriesCreate.md)|  | 

### Return type

[**RecurringSeriesResponse**](RecurringSeriesResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteRecurringSeries**
> JsonObject deleteRecurringSeries(seriesId)

Delete Recurring Series

Delete a recurring series and all its occurrences.  Requires admin access. Deletes: 1. All event occurrences linked to series 2. All exceptions for those occurrences 3. The series itself  Warning: This is irreversible!

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getRecurringEventsApi();
final String seriesId = seriesId_example; // String | 

try {
    final response = api.deleteRecurringSeries(seriesId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling RecurringEventsApi->deleteRecurringSeries: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **seriesId** | **String**|  | 

### Return type

[**JsonObject**](JsonObject.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getRecurringSeries**
> RecurringSeriesResponse getRecurringSeries(seriesId)

Get Recurring Series

Get a specific recurring series by ID.  Returns series details with occurrence count.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getRecurringEventsApi();
final String seriesId = seriesId_example; // String | 

try {
    final response = api.getRecurringSeries(seriesId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling RecurringEventsApi->getRecurringSeries: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **seriesId** | **String**|  | 

### Return type

[**RecurringSeriesResponse**](RecurringSeriesResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getSeriesOccurrences**
> JsonObject getSeriesOccurrences(seriesId)

Get Series Occurrences

Get all event occurrences for a recurring series.  Returns list of Event objects with exception indicators.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getRecurringEventsApi();
final String seriesId = seriesId_example; // String | 

try {
    final response = api.getSeriesOccurrences(seriesId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling RecurringEventsApi->getSeriesOccurrences: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **seriesId** | **String**|  | 

### Return type

[**JsonObject**](JsonObject.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listRecurringSeries**
> ListResponseRecurringSeriesResponse listRecurringSeries(orgId, activeOnly, limit, offset)

List Recurring Series

List all recurring series for an organization, scoped to the caller's org.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getRecurringEventsApi();
final String orgId = orgId_example; // String | Organization ID
final bool activeOnly = true; // bool | Only return active series
final int limit = 56; // int | Page size, max 200
final int offset = 56; // int | Number of rows to skip

try {
    final response = api.listRecurringSeries(orgId, activeOnly, limit, offset);
    print(response);
} catch on DioException (e) {
    print('Exception when calling RecurringEventsApi->listRecurringSeries: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**| Organization ID | 
 **activeOnly** | **bool**| Only return active series | [optional] [default to true]
 **limit** | **int**| Page size, max 200 | [optional] [default to 50]
 **offset** | **int**| Number of rows to skip | [optional] [default to 0]

### Return type

[**ListResponseRecurringSeriesResponse**](ListResponseRecurringSeriesResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **previewOccurrences**
> BuiltList<OccurrencePreview> previewOccurrences(orgId, previewRequest)

Preview Occurrences

Preview occurrences for a recurring pattern WITHOUT creating them.  Used by the UI calendar preview to show occurrences before saving. Returns up to 100 occurrences for preview.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getRecurringEventsApi();
final String orgId = orgId_example; // String | Organization ID
final PreviewRequest previewRequest = ; // PreviewRequest | 

try {
    final response = api.previewOccurrences(orgId, previewRequest);
    print(response);
} catch on DioException (e) {
    print('Exception when calling RecurringEventsApi->previewOccurrences: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**| Organization ID | 
 **previewRequest** | [**PreviewRequest**](PreviewRequest.md)|  | 

### Return type

[**BuiltList&lt;OccurrencePreview&gt;**](OccurrencePreview.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateSeriesTemplate**
> JsonObject updateSeriesTemplate(seriesId, title, location, requestBody)

Update Series Template

Update the series template (affects future occurrences).  Only updates the template - existing occurrences are NOT changed. Use this to modify what future occurrences will look like.  Note: To modify recurrence pattern, delete and recreate the series.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getRecurringEventsApi();
final String seriesId = seriesId_example; // String | 
final String title = title_example; // String | 
final String location = location_example; // String | 
final BuiltMap<String, JsonObject> requestBody = Object; // BuiltMap<String, JsonObject> | 

try {
    final response = api.updateSeriesTemplate(seriesId, title, location, requestBody);
    print(response);
} catch on DioException (e) {
    print('Exception when calling RecurringEventsApi->updateSeriesTemplate: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **seriesId** | **String**|  | 
 **title** | **String**|  | [optional] 
 **location** | **String**|  | [optional] 
 **requestBody** | [**BuiltMap&lt;String, JsonObject&gt;**](JsonObject.md)|  | [optional] 

### Return type

[**JsonObject**](JsonObject.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

