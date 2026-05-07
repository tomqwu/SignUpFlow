# signupflow_api.api.EventsApi

## Load the API package
```dart
import 'package:signupflow_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**createEvent**](EventsApi.md#createevent) | **POST** /api/v1/events/ | Create Event
[**deleteEvent**](EventsApi.md#deleteevent) | **DELETE** /api/v1/events/{event_id} | Delete Event
[**getAllAssignments**](EventsApi.md#getallassignments) | **GET** /api/v1/events/assignments/all | Get All Assignments
[**getAvailablePeople**](EventsApi.md#getavailablepeople) | **GET** /api/v1/events/{event_id}/available-people | Get Available People
[**getEvent**](EventsApi.md#getevent) | **GET** /api/v1/events/{event_id} | Get Event
[**listEvents**](EventsApi.md#listevents) | **GET** /api/v1/events/ | List Events
[**manageAssignment**](EventsApi.md#manageassignment) | **POST** /api/v1/events/{event_id}/assignments | Manage Assignment
[**updateEvent**](EventsApi.md#updateevent) | **PUT** /api/v1/events/{event_id} | Update Event
[**validateEvent**](EventsApi.md#validateevent) | **GET** /api/v1/events/{event_id}/validation | Validate Event


# **createEvent**
> EventResponse createEvent(eventCreate)

Create Event

Create a new event (admin only).

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getEventsApi();
final EventCreate eventCreate = ; // EventCreate | 

try {
    final response = api.createEvent(eventCreate);
    print(response);
} catch on DioException (e) {
    print('Exception when calling EventsApi->createEvent: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **eventCreate** | [**EventCreate**](EventCreate.md)|  | 

### Return type

[**EventResponse**](EventResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteEvent**
> deleteEvent(eventId)

Delete Event

Delete event (admin only).

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getEventsApi();
final String eventId = eventId_example; // String | 

try {
    api.deleteEvent(eventId);
} catch on DioException (e) {
    print('Exception when calling EventsApi->deleteEvent: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **eventId** | **String**|  | 

### Return type

void (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getAllAssignments**
> JsonObject getAllAssignments(orgId)

Get All Assignments

Get all assignments for an organization (both from solutions and manual).

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getEventsApi();
final String orgId = orgId_example; // String | Organization ID

try {
    final response = api.getAllAssignments(orgId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling EventsApi->getAllAssignments: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**| Organization ID | 

### Return type

[**JsonObject**](JsonObject.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getAvailablePeople**
> BuiltList<AvailablePerson> getAvailablePeople(eventId)

Get Available People

Get people available for this event based on roles.  Returns list of people who have matching roles, with flags indicating if they're already assigned or have blocked the event date.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getEventsApi();
final String eventId = eventId_example; // String | 

try {
    final response = api.getAvailablePeople(eventId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling EventsApi->getAvailablePeople: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **eventId** | **String**|  | 

### Return type

[**BuiltList&lt;AvailablePerson&gt;**](AvailablePerson.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getEvent**
> EventResponse getEvent(eventId)

Get Event

Get event by ID.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getEventsApi();
final String eventId = eventId_example; // String | 

try {
    final response = api.getEvent(eventId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling EventsApi->getEvent: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **eventId** | **String**|  | 

### Return type

[**EventResponse**](EventResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listEvents**
> ListResponseEventResponse listEvents(orgId, eventType, startAfter, startBefore, q, status, limit, offset)

List Events

List events with optional filters.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getEventsApi();
final String orgId = orgId_example; // String | Filter by organization ID
final String eventType = eventType_example; // String | Filter by event type
final DateTime startAfter = 2013-10-20T19:20:30+01:00; // DateTime | Filter events starting after this time
final DateTime startBefore = 2013-10-20T19:20:30+01:00; // DateTime | Filter events starting before this time
final String q = q_example; // String | Case-insensitive search on event type and id
final String status = status_example; // String | Filter by computed status: 'upcoming', 'past', or 'ongoing'
final int limit = 56; // int | Page size, max 200
final int offset = 56; // int | Number of rows to skip

try {
    final response = api.listEvents(orgId, eventType, startAfter, startBefore, q, status, limit, offset);
    print(response);
} catch on DioException (e) {
    print('Exception when calling EventsApi->listEvents: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**| Filter by organization ID | [optional] 
 **eventType** | **String**| Filter by event type | [optional] 
 **startAfter** | **DateTime**| Filter events starting after this time | [optional] 
 **startBefore** | **DateTime**| Filter events starting before this time | [optional] 
 **q** | **String**| Case-insensitive search on event type and id | [optional] 
 **status** | **String**| Filter by computed status: 'upcoming', 'past', or 'ongoing' | [optional] 
 **limit** | **int**| Page size, max 200 | [optional] [default to 50]
 **offset** | **int**| Number of rows to skip | [optional] [default to 0]

### Return type

[**ListResponseEventResponse**](ListResponseEventResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **manageAssignment**
> JsonObject manageAssignment(eventId, assignmentRequest)

Manage Assignment

Assign or unassign a person to/from an event (admin only).

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getEventsApi();
final String eventId = eventId_example; // String | 
final AssignmentRequest assignmentRequest = ; // AssignmentRequest | 

try {
    final response = api.manageAssignment(eventId, assignmentRequest);
    print(response);
} catch on DioException (e) {
    print('Exception when calling EventsApi->manageAssignment: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **eventId** | **String**|  | 
 **assignmentRequest** | [**AssignmentRequest**](AssignmentRequest.md)|  | 

### Return type

[**JsonObject**](JsonObject.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateEvent**
> EventResponse updateEvent(eventId, eventUpdate)

Update Event

Update event (admin only).

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getEventsApi();
final String eventId = eventId_example; // String | 
final EventUpdate eventUpdate = ; // EventUpdate | 

try {
    final response = api.updateEvent(eventId, eventUpdate);
    print(response);
} catch on DioException (e) {
    print('Exception when calling EventsApi->updateEvent: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **eventId** | **String**|  | 
 **eventUpdate** | [**EventUpdate**](EventUpdate.md)|  | 

### Return type

[**EventResponse**](EventResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **validateEvent**
> BuiltMap<String, JsonObject> validateEvent(eventId)

Validate Event

Validate if event has proper configuration and enough people.  Checks: 1. Event has role requirements configured 2. Enough people available for each role 3. No assigned people are blocked on the event date  Returns:     Dictionary with is_valid flag and list of validation warnings

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getEventsApi();
final String eventId = eventId_example; // String | 

try {
    final response = api.validateEvent(eventId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling EventsApi->validateEvent: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **eventId** | **String**|  | 

### Return type

[**BuiltMap&lt;String, JsonObject&gt;**](JsonObject.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

