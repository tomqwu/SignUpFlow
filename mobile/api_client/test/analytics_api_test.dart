import 'package:test/test.dart';
import 'package:signupflow_api/signupflow_api.dart';


/// tests for AnalyticsApi
void main() {
  final instance = SignupflowApi().getAnalyticsApi();

  group(AnalyticsApi, () {
    // Get Burnout Risk
    //
    // Identify volunteers at risk of burnout (serving too frequently).  Admin-only within `org_id`. This endpoint returns other volunteers' names and emails, so peer volunteers can never read it.
    //
    //Future<JsonObject> getBurnoutRisk(String orgId, { int threshold }) async
    test('test getBurnoutRisk', () async {
      // TODO
    });

    // Get Schedule Health
    //
    // Get schedule health metrics.  Admin-only within `org_id`.
    //
    //Future<JsonObject> getScheduleHealth(String orgId) async
    test('test getScheduleHealth', () async {
      // TODO
    });

    // Get Volunteer Stats
    //
    // Get volunteer participation statistics.  Admin-only within `org_id`. The caller must be an authenticated admin whose own org matches the requested one.
    //
    //Future<JsonObject> getVolunteerStats(String orgId, { int days }) async
    test('test getVolunteerStats', () async {
      // TODO
    });

  });
}
