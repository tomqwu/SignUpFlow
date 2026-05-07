import 'package:test/test.dart';
import 'package:signupflow_api/signupflow_api.dart';


/// tests for AnalyticsApi
void main() {
  final instance = SignupflowApi().getAnalyticsApi();

  group(AnalyticsApi, () {
    // Get Burnout Risk
    //
    // Identify volunteers at risk of burnout (serving too frequently).
    //
    //Future<JsonObject> getBurnoutRisk(String orgId, { int threshold }) async
    test('test getBurnoutRisk', () async {
      // TODO
    });

    // Get Schedule Health
    //
    // Get schedule health metrics.
    //
    //Future<JsonObject> getScheduleHealth(String orgId) async
    test('test getScheduleHealth', () async {
      // TODO
    });

    // Get Volunteer Stats
    //
    // Get volunteer participation statistics.
    //
    //Future<JsonObject> getVolunteerStats(String orgId, { int days }) async
    test('test getVolunteerStats', () async {
      // TODO
    });

  });
}
