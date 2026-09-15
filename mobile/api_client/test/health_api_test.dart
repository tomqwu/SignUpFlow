import 'package:test/test.dart';
import 'package:signupflow_api/signupflow_api.dart';


/// tests for HealthApi
void main() {
  final instance = SignupflowApi().getHealthApi();

  group(HealthApi, () {
    // Health Check
    //
    // Return process liveness without opening a dependency connection.
    //
    //Future<JsonObject> healthCheck() async
    test('test healthCheck', () async {
      // TODO
    });

  });
}
