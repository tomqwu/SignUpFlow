# signupflow_api.api.InvitationsApi

## Load the API package
```dart
import 'package:signupflow_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**acceptInvitation**](InvitationsApi.md#acceptinvitation) | **POST** /api/v1/invitations/{token}/accept | Accept Invitation
[**cancelInvitation**](InvitationsApi.md#cancelinvitation) | **DELETE** /api/v1/invitations/{invitation_id} | Cancel Invitation
[**createInvitation**](InvitationsApi.md#createinvitation) | **POST** /api/v1/invitations | Create Invitation
[**listInvitations**](InvitationsApi.md#listinvitations) | **GET** /api/v1/invitations | List Invitations
[**resendInvitation**](InvitationsApi.md#resendinvitation) | **POST** /api/v1/invitations/{invitation_id}/resend | Resend Invitation
[**verifyInvitation**](InvitationsApi.md#verifyinvitation) | **GET** /api/v1/invitations/{token} | Verify Invitation


# **acceptInvitation**
> InvitationAcceptResponse acceptInvitation(token, invitationAccept)

Accept Invitation

Accept an invitation and create a new account.  This creates a new Person with the invited roles and marks the invitation as accepted.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getInvitationsApi();
final String token = token_example; // String | 
final InvitationAccept invitationAccept = ; // InvitationAccept | 

try {
    final response = api.acceptInvitation(token, invitationAccept);
    print(response);
} catch on DioException (e) {
    print('Exception when calling InvitationsApi->acceptInvitation: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **String**|  | 
 **invitationAccept** | [**InvitationAccept**](InvitationAccept.md)|  | 

### Return type

[**InvitationAcceptResponse**](InvitationAcceptResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **cancelInvitation**
> cancelInvitation(invitationId)

Cancel Invitation

Cancel a pending invitation (admin only).

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getInvitationsApi();
final String invitationId = invitationId_example; // String | 

try {
    api.cancelInvitation(invitationId);
} catch on DioException (e) {
    print('Exception when calling InvitationsApi->cancelInvitation: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **invitationId** | **String**|  | 

### Return type

void (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createInvitation**
> InvitationResponse createInvitation(orgId, invitationCreate)

Create Invitation

Create a new invitation (admin only). Rate limited to 10 requests per 5 minutes per IP.  Sends an invitation email to a new user to join the organization.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getInvitationsApi();
final String orgId = orgId_example; // String | Organization ID
final InvitationCreate invitationCreate = ; // InvitationCreate | 

try {
    final response = api.createInvitation(orgId, invitationCreate);
    print(response);
} catch on DioException (e) {
    print('Exception when calling InvitationsApi->createInvitation: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**| Organization ID | 
 **invitationCreate** | [**InvitationCreate**](InvitationCreate.md)|  | 

### Return type

[**InvitationResponse**](InvitationResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listInvitations**
> ListResponseInvitationResponse listInvitations(orgId, status, q)

List Invitations

List all invitations for an organization (admin only).  Requires JWT authentication via Authorization header.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getInvitationsApi();
final String orgId = orgId_example; // String | Organization ID
final String status = status_example; // String | Filter by status (pending, accepted, expired, cancelled)
final String q = q_example; // String | Case-insensitive search on email and name

try {
    final response = api.listInvitations(orgId, status, q);
    print(response);
} catch on DioException (e) {
    print('Exception when calling InvitationsApi->listInvitations: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**| Organization ID | 
 **status** | **String**| Filter by status (pending, accepted, expired, cancelled) | [optional] 
 **q** | **String**| Case-insensitive search on email and name | [optional] 

### Return type

[**ListResponseInvitationResponse**](ListResponseInvitationResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **resendInvitation**
> InvitationResponse resendInvitation(invitationId)

Resend Invitation

Resend an invitation email (admin only).  Generates a new token and extends the expiry date.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getInvitationsApi();
final String invitationId = invitationId_example; // String | 

try {
    final response = api.resendInvitation(invitationId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling InvitationsApi->resendInvitation: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **invitationId** | **String**|  | 

### Return type

[**InvitationResponse**](InvitationResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **verifyInvitation**
> InvitationVerify verifyInvitation(token)

Verify Invitation

Verify an invitation token. Rate limited to 10 requests per minute per IP.  Checks if the invitation is valid and not expired.

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getInvitationsApi();
final String token = token_example; // String | 

try {
    final response = api.verifyInvitation(token);
    print(response);
} catch on DioException (e) {
    print('Exception when calling InvitationsApi->verifyInvitation: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **String**|  | 

### Return type

[**InvitationVerify**](InvitationVerify.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

