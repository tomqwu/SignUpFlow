import 'package:test/test.dart';
import 'package:built_collection/built_collection.dart';
import 'package:signupflow_api/signupflow_api.dart';

// tests for SendBroadcastRequest
void main() {
  final instance = (SendBroadcastRequestBuilder()
        ..messageText = 'Practice moved to 7 PM'
        ..recipientIds = ListBuilder<String>(['member-alpha', 'member-beta']))
      .build();

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
    // BuiltList<String> recipientIds
    test('to test the property `recipientIds`', () async {
      expect(instance.recipientIds, ['member-alpha', 'member-beta']);
    });
  });
}
