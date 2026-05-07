import 'package:test/test.dart';
import 'package:signupflow_api/signupflow_api.dart';

// tests for EmailPreferenceResponse
void main() {
  final instance = EmailPreferenceResponseBuilder();
  // TODO add properties to the builder and call build()

  group(EmailPreferenceResponse, () {
    // Hour to send digests (0-23)
    // int digestHour (default value: 8)
    test('to test the property `digestHour`', () async {
      // TODO
    });

    // List of enabled notification types
    // BuiltList<String> enabledTypes
    test('to test the property `enabledTypes`', () async {
      // TODO
    });

    // Email frequency (immediate, daily, weekly, disabled)
    // String frequency (default value: 'immediate')
    test('to test the property `frequency`', () async {
      // TODO
    });

    // int id
    test('to test the property `id`', () async {
      // TODO
    });

    // Email language preference (ISO 639-1 code)
    // String language (default value: 'en')
    test('to test the property `language`', () async {
      // TODO
    });

    // String orgId
    test('to test the property `orgId`', () async {
      // TODO
    });

    // String personId
    test('to test the property `personId`', () async {
      // TODO
    });

    // Timezone for digest scheduling
    // String timezone (default value: 'UTC')
    test('to test the property `timezone`', () async {
      // TODO
    });

    // String unsubscribeToken
    test('to test the property `unsubscribeToken`', () async {
      // TODO
    });

    // DateTime updatedAt
    test('to test the property `updatedAt`', () async {
      // TODO
    });

  });
}
