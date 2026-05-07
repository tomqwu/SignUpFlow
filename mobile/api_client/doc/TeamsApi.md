# signupflow_api.api.TeamsApi

## Load the API package
```dart
import 'package:signupflow_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**addTeamMembers**](TeamsApi.md#addteammembers) | **POST** /api/v1/teams/{team_id}/members | Add Team Members
[**createTeam**](TeamsApi.md#createteam) | **POST** /api/v1/teams/ | Create Team
[**deleteTeam**](TeamsApi.md#deleteteam) | **DELETE** /api/v1/teams/{team_id} | Delete Team
[**getTeam**](TeamsApi.md#getteam) | **GET** /api/v1/teams/{team_id} | Get Team
[**listTeams**](TeamsApi.md#listteams) | **GET** /api/v1/teams/ | List Teams
[**removeTeamMembers**](TeamsApi.md#removeteammembers) | **DELETE** /api/v1/teams/{team_id}/members | Remove Team Members
[**updateTeam**](TeamsApi.md#updateteam) | **PUT** /api/v1/teams/{team_id} | Update Team


# **addTeamMembers**
> addTeamMembers(teamId, teamMemberAdd)

Add Team Members

Add members to team (admin only).

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getTeamsApi();
final String teamId = teamId_example; // String | 
final TeamMemberAdd teamMemberAdd = ; // TeamMemberAdd | 

try {
    api.addTeamMembers(teamId, teamMemberAdd);
} catch on DioException (e) {
    print('Exception when calling TeamsApi->addTeamMembers: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **teamId** | **String**|  | 
 **teamMemberAdd** | [**TeamMemberAdd**](TeamMemberAdd.md)|  | 

### Return type

void (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createTeam**
> TeamResponse createTeam(teamCreate)

Create Team

Create a new team (admin only).

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getTeamsApi();
final TeamCreate teamCreate = ; // TeamCreate | 

try {
    final response = api.createTeam(teamCreate);
    print(response);
} catch on DioException (e) {
    print('Exception when calling TeamsApi->createTeam: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **teamCreate** | [**TeamCreate**](TeamCreate.md)|  | 

### Return type

[**TeamResponse**](TeamResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteTeam**
> deleteTeam(teamId)

Delete Team

Delete team (admin only).

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getTeamsApi();
final String teamId = teamId_example; // String | 

try {
    api.deleteTeam(teamId);
} catch on DioException (e) {
    print('Exception when calling TeamsApi->deleteTeam: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **teamId** | **String**|  | 

### Return type

void (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getTeam**
> TeamResponse getTeam(teamId)

Get Team

Get team by ID. Users can only view teams from their own organization.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getTeamsApi();
final String teamId = teamId_example; // String | 

try {
    final response = api.getTeam(teamId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling TeamsApi->getTeam: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **teamId** | **String**|  | 

### Return type

[**TeamResponse**](TeamResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listTeams**
> ListResponseTeamResponse listTeams(orgId, q, limit, offset)

List Teams

List teams. Users can only see teams from their own organization.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getTeamsApi();
final String orgId = orgId_example; // String | Filter by organization ID
final String q = q_example; // String | Case-insensitive search on name and description
final int limit = 56; // int | Page size, max 200
final int offset = 56; // int | Number of rows to skip

try {
    final response = api.listTeams(orgId, q, limit, offset);
    print(response);
} catch on DioException (e) {
    print('Exception when calling TeamsApi->listTeams: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**| Filter by organization ID | [optional] 
 **q** | **String**| Case-insensitive search on name and description | [optional] 
 **limit** | **int**| Page size, max 200 | [optional] [default to 50]
 **offset** | **int**| Number of rows to skip | [optional] [default to 0]

### Return type

[**ListResponseTeamResponse**](ListResponseTeamResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **removeTeamMembers**
> removeTeamMembers(teamId, teamMemberRemove)

Remove Team Members

Remove members from team (admin only).

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getTeamsApi();
final String teamId = teamId_example; // String | 
final TeamMemberRemove teamMemberRemove = ; // TeamMemberRemove | 

try {
    api.removeTeamMembers(teamId, teamMemberRemove);
} catch on DioException (e) {
    print('Exception when calling TeamsApi->removeTeamMembers: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **teamId** | **String**|  | 
 **teamMemberRemove** | [**TeamMemberRemove**](TeamMemberRemove.md)|  | 

### Return type

void (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateTeam**
> TeamResponse updateTeam(teamId, teamUpdate)

Update Team

Update team (admin only).

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getTeamsApi();
final String teamId = teamId_example; // String | 
final TeamUpdate teamUpdate = ; // TeamUpdate | 

try {
    final response = api.updateTeam(teamId, teamUpdate);
    print(response);
} catch on DioException (e) {
    print('Exception when calling TeamsApi->updateTeam: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **teamId** | **String**|  | 
 **teamUpdate** | [**TeamUpdate**](TeamUpdate.md)|  | 

### Return type

[**TeamResponse**](TeamResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

