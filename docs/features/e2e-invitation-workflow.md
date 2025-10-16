# Feature: Complete Invitation Workflow (E2E)

## User Story
**As a** new volunteer
**I want to** accept an organization invitation via invitation code
**So that** I can join the organization and start volunteering

## Background Context
- The system supports invitation-based registration for security
- Only users with valid invitation codes can create accounts
- Admins can create invitations with pre-assigned roles
- First user in an organization automatically becomes admin

## Scenarios

### Scenario 1: Admin Creates Invitation for New User
**Given** I am logged in as an admin user
**And** I am on the People management page
**When** I click "Invite User" button
**And** I enter the new user's email "newuser@example.com"
**And** I enter the new user's name "Jane Smith"
**And** I select roles "Greeter" and "Usher"
**And** I click "Send Invitation"
**Then** a new invitation is created with status "pending"
**And** an invitation token is generated
**And** I see a success message "Invitation sent successfully!"
**And** the invitation appears in the invitations list

### Scenario 2: User Accepts Invitation and Completes Registration
**Given** an invitation exists with token "valid-token-123"
**And** the invitation has email "newuser@example.com"
**And** the invitation has assigned roles "Greeter" and "Usher"
**When** I visit the signup page with parameter "?invitation=valid-token-123"
**And** I enter invitation code "valid-token-123"
**And** I click "Verify Invitation"
**Then** my email is pre-filled as "newuser@example.com"
**And** my name is pre-filled as "Jane Smith"
**And** my assigned roles "Greeter" and "Usher" are displayed
**And** the timezone is auto-detected from my browser
**When** I enter password "SecurePass123"
**And** I click "Complete Registration"
**Then** my account is created successfully
**And** I am automatically logged in
**And** I see the dashboard with my roles
**And** the invitation status changes to "accepted"

### Scenario 3: User Tries Invalid Invitation Code
**Given** I am on the signup page
**When** I enter invitation code "invalid-token-999"
**And** I click "Verify Invitation"
**Then** I see an error message "Invalid or expired invitation code"
**And** the registration form does not appear

### Scenario 4: User Tries Expired Invitation Code
**Given** an invitation exists with token "expired-token-456"
**And** the invitation was created more than 7 days ago
**When** I visit the signup page
**And** I enter invitation code "expired-token-456"
**And** I click "Verify Invitation"
**Then** I see an error message "Invalid or expired invitation code"
**And** the registration form does not appear

### Scenario 5: User Tries Already-Used Invitation Code
**Given** an invitation exists with token "used-token-789"
**And** the invitation has status "accepted"
**When** I visit the signup page
**And** I enter invitation code "used-token-789"
**And** I click "Verify Invitation"
**Then** I see an error message "Invalid or expired invitation code"
**And** the registration form does not appear

### Scenario 6: Admin Resends Invitation
**Given** I am logged in as an admin
**And** an invitation exists with status "pending"
**When** I navigate to the People page
**And** I find the pending invitation in the list
**And** I click "Resend" button
**Then** I see a success message "Invitation resent successfully!"
**And** the invitation token remains the same
**And** the invitation expiry is extended

### Scenario 7: Admin Cancels Invitation
**Given** I am logged in as an admin
**And** an invitation exists with status "pending"
**When** I navigate to the People page
**And** I find the pending invitation in the list
**And** I click "Cancel" button
**And** I confirm the cancellation
**Then** the invitation is removed from the list
**And** I see a success message "Invitation cancelled successfully!"

### Scenario 8: First User Creates Organization
**Given** no organizations exist in the system
**When** I visit the signup page without an invitation code
**And** I choose "Create New Organization"
**And** I enter organization name "Grace Community Church"
**And** I enter my name "John Admin"
**And** I enter my email "admin@church.org"
**And** I enter password "AdminPass123"
**And** I click "Create Organization"
**Then** my organization is created
**And** my account is created with admin privileges
**And** I am automatically logged in
**And** I see the admin dashboard

## Test Data Requirements
- Valid test email addresses
- Test organization names
- Test user names
- Test passwords (min 6 characters)
- Test invitation tokens (32-character secure tokens)
- Test roles (Greeter, Usher, Tech, etc.)

## Expected UI Elements
- Invitation code input field
- "Verify Invitation" button
- Pre-filled email field (read-only)
- Pre-filled name field (read-only)
- Password input field
- Timezone dropdown (auto-detected)
- Assigned roles display area
- "Complete Registration" button
- Success/error messages
- "Invite User" button (admin only)
- Invitations list table (admin only)

## API Endpoints Involved
- `POST /api/invitations` - Create invitation (admin)
- `GET /api/invitations/verify?token={token}` - Verify invitation token
- `POST /api/invitations/{id}/accept` - Accept invitation and create account
- `POST /api/invitations/{id}/resend` - Resend invitation (admin)
- `DELETE /api/invitations/{id}` - Cancel invitation (admin)
- `GET /api/invitations` - List invitations (admin)

## Security Requirements
- Invitation tokens must be cryptographically secure (32+ bytes)
- Tokens must expire after 7 days
- Used tokens cannot be reused
- Only admins can create/manage invitations
- Email addresses in invitations must be unique per organization

## Success Criteria
✅ All E2E tests pass covering scenarios 1-8
✅ Invitation workflow works end-to-end without manual intervention
✅ Invalid/expired/used tokens are properly rejected
✅ Admin can manage (create/resend/cancel) invitations
✅ User registration is secure and only possible with valid invitation
✅ First user in system can create organization without invitation
