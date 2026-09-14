import 'package:test/test.dart';
import 'package:signupflow_api/signupflow_api.dart';

// tests for SendBroadcastRequest
void main() {
  final instance = SendBroadcastRequestBuilder();
  // TODO add properties to the builder and call build()

  group(SendBroadcastRequest, () {
    // Bypass rate limits if urgent
    // bool isUrgent (default value: false)
    test('to test the property `isUrgent`', () async {
      // TODO
    });

    // Message content (max 1600 chars)
    // String messageText
    test('to test the property `messageText`', () async {
      // TODO
    });

    // List of person IDs (max 200)
    // BuiltList<int> recipientIds
    test('to test the property `recipientIds`', () async {
      // TODO
    });

  });
}
