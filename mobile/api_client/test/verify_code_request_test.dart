import 'package:test/test.dart';
import 'package:signupflow_api/signupflow_api.dart';

// tests for VerifyCodeRequest
void main() {
  final instance = (VerifyCodeRequestBuilder()
        ..personId = 'member-alpha'
        ..code = 123456)
      .build();

  group(VerifyCodeRequest, () {
    // 6-digit verification code
    // int code
    test('to test the property `code`', () async {
      // TODO
    });

    // String personId
    test('to test the property `personId`', () async {
      expect(instance.personId, 'member-alpha');
    });
  });
}
