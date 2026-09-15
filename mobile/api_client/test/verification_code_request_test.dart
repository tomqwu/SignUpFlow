import 'package:test/test.dart';
import 'package:signupflow_api/signupflow_api.dart';

// tests for VerificationCodeRequest
void main() {
  final instance = (VerificationCodeRequestBuilder()
        ..personId = 'member-alpha'
        ..phoneNumber = '+14165550101')
      .build();

  group(VerificationCodeRequest, () {
    // String personId
    test('to test the property `personId`', () async {
      expect(instance.personId, 'member-alpha');
    });

    // Phone number in E.164 format
    // String phoneNumber
    test('to test the property `phoneNumber`', () async {
      // TODO
    });
  });
}
