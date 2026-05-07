import 'package:test/test.dart';
import 'package:signupflow_api/signupflow_api.dart';


/// tests for HealthApi
void main() {
  final instance = SignupflowApi().getHealthApi();

  group(HealthApi, () {
    // Health Check
    //
    // Health check endpoint with database connectivity check.  Returns:     200 OK: Service and database are healthy     503 Service Unavailable: Database connection failed
    //
    //Future<JsonObject> healthCheck() async
    test('test healthCheck', () async {
      // TODO
    });

  });
}
