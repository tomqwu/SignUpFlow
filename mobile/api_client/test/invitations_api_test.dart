import 'package:test/test.dart';
import 'package:signupflow_api/signupflow_api.dart';


/// tests for InvitationsApi
void main() {
  final instance = SignupflowApi().getInvitationsApi();

  group(InvitationsApi, () {
    // Accept Invitation
    //
    // Accept an invitation and create a new account.  This creates a new Person with the invited roles and marks the invitation as accepted.
    //
    //Future<InvitationAcceptResponse> acceptInvitation(String token, InvitationAccept invitationAccept) async
    test('test acceptInvitation', () async {
      // TODO
    });

    // Cancel Invitation
    //
    // Cancel a pending invitation (admin only).
    //
    //Future cancelInvitation(String invitationId) async
    test('test cancelInvitation', () async {
      // TODO
    });

    // Create Invitation
    //
    // Create a new invitation (admin only). Rate limited to 10 requests per 5 minutes per IP.  Sends an invitation email to a new user to join the organization.
    //
    //Future<InvitationResponse> createInvitation(String orgId, InvitationCreate invitationCreate) async
    test('test createInvitation', () async {
      // TODO
    });

    // List Invitations
    //
    // List all invitations for an organization (admin only).  Requires JWT authentication via Authorization header.
    //
    //Future<ListResponseInvitationResponse> listInvitations(String orgId, { String status, String q }) async
    test('test listInvitations', () async {
      // TODO
    });

    // Resend Invitation
    //
    // Resend an invitation email (admin only).  Generates a new token and extends the expiry date.
    //
    //Future<InvitationResponse> resendInvitation(String invitationId) async
    test('test resendInvitation', () async {
      // TODO
    });

    // Verify Invitation
    //
    // Verify an invitation token. Rate limited to 10 requests per minute per IP.  Checks if the invitation is valid and not expired.
    //
    //Future<InvitationVerify> verifyInvitation(String token) async
    test('test verifyInvitation', () async {
      // TODO
    });

  });
}
