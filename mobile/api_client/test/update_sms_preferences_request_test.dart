import 'package:test/test.dart';
import 'package:signupflow_api/signupflow_api.dart';

// tests for UpdateSmsPreferencesRequest
void main() {
  final instance = UpdateSmsPreferencesRequestBuilder();
  // TODO add properties to the builder and call build()

  group(UpdateSmsPreferencesRequest, () {
    // Preferred language for SMS: en, es, pt, zh-CN, zh-TW, fr
    // String language (default value: 'en')
    test('to test the property `language`', () async {
      // TODO
    });

    // List of notification types: assignment, reminder, change, cancellation
    // BuiltList<String> notificationTypes
    test('to test the property `notificationTypes`', () async {
      // TODO
    });

  });
}
