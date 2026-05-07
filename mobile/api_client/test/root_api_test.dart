import 'package:test/test.dart';
import 'package:signupflow_api/signupflow_api.dart';


/// tests for RootApi
void main() {
  final instance = SignupflowApi().getRootApi();

  group(RootApi, () {
    // Api Info
    //
    // API information endpoint.
    //
    //Future<JsonObject> apiInfo() async
    test('test apiInfo', () async {
      // TODO
    });

  });
}
