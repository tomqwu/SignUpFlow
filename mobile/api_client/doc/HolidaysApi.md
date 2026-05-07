# signupflow_api.api.HolidaysApi

## Load the API package
```dart
import 'package:signupflow_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**bulkImportHolidays**](HolidaysApi.md#bulkimportholidays) | **POST** /api/v1/holidays/bulk | Bulk Import Holidays
[**createHoliday**](HolidaysApi.md#createholiday) | **POST** /api/v1/holidays/ | Create Holiday
[**deleteHoliday**](HolidaysApi.md#deleteholiday) | **DELETE** /api/v1/holidays/{holiday_id} | Delete Holiday
[**getHoliday**](HolidaysApi.md#getholiday) | **GET** /api/v1/holidays/{holiday_id} | Get Holiday
[**listHolidays**](HolidaysApi.md#listholidays) | **GET** /api/v1/holidays/ | List Holidays
[**updateHoliday**](HolidaysApi.md#updateholiday) | **PUT** /api/v1/holidays/{holiday_id} | Update Holiday


# **bulkImportHolidays**
> HolidayBulkImportResponse bulkImportHolidays(orgId, holidayBulkImport)

Bulk Import Holidays

Admin-only bulk-create holidays for one org.  Common pattern for importing a full year's federal/diocesan calendar in one request. Skips dates that already have a holiday row in the target org; returns those as errors so the caller can decide whether to retry.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getHolidaysApi();
final String orgId = orgId_example; // String | Organization to import into
final HolidayBulkImport holidayBulkImport = ; // HolidayBulkImport | 

try {
    final response = api.bulkImportHolidays(orgId, holidayBulkImport);
    print(response);
} catch on DioException (e) {
    print('Exception when calling HolidaysApi->bulkImportHolidays: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**| Organization to import into | 
 **holidayBulkImport** | [**HolidayBulkImport**](HolidayBulkImport.md)|  | 

### Return type

[**HolidayBulkImportResponse**](HolidayBulkImportResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createHoliday**
> HolidayResponse createHoliday(holidayCreate)

Create Holiday

Create a single holiday (admin only).

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getHolidaysApi();
final HolidayCreate holidayCreate = ; // HolidayCreate | 

try {
    final response = api.createHoliday(holidayCreate);
    print(response);
} catch on DioException (e) {
    print('Exception when calling HolidaysApi->createHoliday: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **holidayCreate** | [**HolidayCreate**](HolidayCreate.md)|  | 

### Return type

[**HolidayResponse**](HolidayResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteHoliday**
> deleteHoliday(holidayId)

Delete Holiday

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getHolidaysApi();
final int holidayId = 56; // int | 

try {
    api.deleteHoliday(holidayId);
} catch on DioException (e) {
    print('Exception when calling HolidaysApi->deleteHoliday: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **holidayId** | **int**|  | 

### Return type

void (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getHoliday**
> HolidayResponse getHoliday(holidayId)

Get Holiday

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getHolidaysApi();
final int holidayId = 56; // int | 

try {
    final response = api.getHoliday(holidayId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling HolidaysApi->getHoliday: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **holidayId** | **int**|  | 

### Return type

[**HolidayResponse**](HolidayResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listHolidays**
> ListResponseHolidayResponse listHolidays(orgId, limit, offset)

List Holidays

List holidays for one org. Caller must be a member.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getHolidaysApi();
final String orgId = orgId_example; // String | Organization ID
final int limit = 56; // int | Page size, max 200
final int offset = 56; // int | Number of rows to skip

try {
    final response = api.listHolidays(orgId, limit, offset);
    print(response);
} catch on DioException (e) {
    print('Exception when calling HolidaysApi->listHolidays: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**| Organization ID | 
 **limit** | **int**| Page size, max 200 | [optional] [default to 50]
 **offset** | **int**| Number of rows to skip | [optional] [default to 0]

### Return type

[**ListResponseHolidayResponse**](ListResponseHolidayResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateHoliday**
> HolidayResponse updateHoliday(holidayId, holidayUpdate)

Update Holiday

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getHolidaysApi();
final int holidayId = 56; // int | 
final HolidayUpdate holidayUpdate = ; // HolidayUpdate | 

try {
    final response = api.updateHoliday(holidayId, holidayUpdate);
    print(response);
} catch on DioException (e) {
    print('Exception when calling HolidaysApi->updateHoliday: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **holidayId** | **int**|  | 
 **holidayUpdate** | [**HolidayUpdate**](HolidayUpdate.md)|  | 

### Return type

[**HolidayResponse**](HolidayResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

