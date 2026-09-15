//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'send_broadcast_request.g.dart';

/// Request to send broadcast message.
///
/// Properties:
/// * [isUrgent] - Bypass rate limits if urgent
/// * [messageText] - Message content (max 1600 chars)
/// * [recipientIds] - List of person IDs (max 200)
@BuiltValue()
abstract class SendBroadcastRequest
    implements Built<SendBroadcastRequest, SendBroadcastRequestBuilder> {
  /// Bypass rate limits if urgent
  @BuiltValueField(wireName: r'is_urgent')
  bool? get isUrgent;

  /// Message content (max 1600 chars)
  @BuiltValueField(wireName: r'message_text')
  String get messageText;

  /// List of person IDs (max 200)
  @BuiltValueField(wireName: r'recipient_ids')
  BuiltList<String> get recipientIds;

  SendBroadcastRequest._();

  factory SendBroadcastRequest([void updates(SendBroadcastRequestBuilder b)]) =
      _$SendBroadcastRequest;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(SendBroadcastRequestBuilder b) => b..isUrgent = false;

  @BuiltValueSerializer(custom: true)
  static Serializer<SendBroadcastRequest> get serializer =>
      _$SendBroadcastRequestSerializer();
}

class _$SendBroadcastRequestSerializer
    implements PrimitiveSerializer<SendBroadcastRequest> {
  @override
  final Iterable<Type> types = const [
    SendBroadcastRequest,
    _$SendBroadcastRequest
  ];

  @override
  final String wireName = r'SendBroadcastRequest';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    SendBroadcastRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    if (object.isUrgent != null) {
      yield r'is_urgent';
      yield serializers.serialize(
        object.isUrgent,
        specifiedType: const FullType(bool),
      );
    }
    yield r'message_text';
    yield serializers.serialize(
      object.messageText,
      specifiedType: const FullType(String),
    );
    yield r'recipient_ids';
    yield serializers.serialize(
      object.recipientIds,
      specifiedType: const FullType(BuiltList, [FullType(String)]),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    SendBroadcastRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object,
            specifiedType: specifiedType)
        .toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required SendBroadcastRequestBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'is_urgent':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(bool),
          ) as bool;
          result.isUrgent = valueDes;
          break;
        case r'message_text':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.messageText = valueDes;
          break;
        case r'recipient_ids':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(String)]),
          ) as BuiltList<String>;
          result.recipientIds.replace(valueDes);
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  SendBroadcastRequest deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = SendBroadcastRequestBuilder();
    final serializedList = (serialized as Iterable<Object?>).toList();
    final unhandled = <Object?>[];
    _deserializeProperties(
      serializers,
      serialized,
      specifiedType: specifiedType,
      serializedList: serializedList,
      unhandled: unhandled,
      result: result,
    );
    return result.build();
  }
}
