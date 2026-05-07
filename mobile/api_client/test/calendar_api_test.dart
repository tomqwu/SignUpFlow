import 'package:test/test.dart';
import 'package:signupflow_api/signupflow_api.dart';


/// tests for CalendarApi
void main() {
  final instance = SignupflowApi().getCalendarApi();

  group(CalendarApi, () {
    // Admin Reset Calendar Token
    //
    // Admin-only force-reset of another user's calendar token.  Same as `/calendar/reset-token` but explicitly an admin override of a target user's token. Always audited as `calendar.token.admin_reset`.
    //
    //Future<CalendarTokenResetResponse> adminResetCalendarToken(String personId) async
    test('test adminResetCalendarToken', () async {
      // TODO
    });

    // Calendar Feed
    //
    // Public calendar feed endpoint for subscriptions.  This endpoint is accessed by calendar applications using the subscription URL. It returns an ICS file that is automatically refreshed by the calendar app.
    //
    //Future<JsonObject> calendarFeed(String token) async
    test('test calendarFeed', () async {
      // TODO
    });

    // Export Organization Events
    //
    // Export all organization events as ICS file (admin only).  This endpoint is for administrators to export all events in the organization.
    //
    //Future<JsonObject> exportOrganizationEvents(String orgId, String personId, { bool includeAssignments }) async
    test('test exportOrganizationEvents', () async {
      // TODO
    });

    // Export Personal Schedule
    //
    // Export personal schedule as ICS file.  This endpoint downloads an ICS file with all assigned events for a person.
    //
    //Future<JsonObject> exportPersonalSchedule(String personId) async
    test('test exportPersonalSchedule', () async {
      // TODO
    });

    // Get Subscription Url
    //
    // Get calendar subscription URL for a person.  Returns a webcal:// URL that can be used to subscribe to the calendar in Google Calendar, Apple Calendar, Outlook, etc. Caller must be the target person or an admin in the same organization.
    //
    //Future<CalendarSubscriptionResponse> getSubscriptionUrl(String personId) async
    test('test getSubscriptionUrl', () async {
      // TODO
    });

    // Reset Calendar Token
    //
    // Reset calendar subscription token for a person.  This invalidates the old subscription URL and generates a new one. Caller must be the target person or an admin in the same organization. Use `/calendar/{person_id}/admin-reset` for the admin-only flow.
    //
    //Future<CalendarTokenResetResponse> resetCalendarToken(String personId) async
    test('test resetCalendarToken', () async {
      // TODO
    });

  });
}
