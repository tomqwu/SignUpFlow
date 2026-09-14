//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'send_event_reminder_request.g.dart';

/// Request to send event reminder to all assigned volunteers.
///
/// Properties:
/// * [eventId]
/// * [hoursBefore] - Hours before event to send reminder
/// * [language] - Language code
@BuiltValue()
abstract class SendEventReminderRequest implements Built<SendEventReminderRequest, SendEventReminderRequestBuilder> {
  @BuiltValueField(wireName: r'event_id')
  String get eventId;

  /// Hours before event to send reminder
  @BuiltValueField(wireName: r'hours_before')
  int? get hoursBefore;

  /// Language code
  @BuiltValueField(wireName: r'language')
  String? get language;

  SendEventReminderRequest._();

  factory SendEventReminderRequest([void updates(SendEventReminderRequestBuilder b)]) = _$SendEventReminderRequest;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(SendEventReminderRequestBuilder b) => b
      ..hoursBefore = 24
      ..language = 'en';

  @BuiltValueSerializer(custom: true)
  static Serializer<SendEventReminderRequest> get serializer => _$SendEventReminderRequestSerializer();
}

class _$SendEventReminderRequestSerializer implements PrimitiveSerializer<SendEventReminderRequest> {
  @override
  final Iterable<Type> types = const [SendEventReminderRequest, _$SendEventReminderRequest];

  @override
  final String wireName = r'SendEventReminderRequest';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    SendEventReminderRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'event_id';
    yield serializers.serialize(
      object.eventId,
      specifiedType: const FullType(String),
    );
    if (object.hoursBefore != null) {
      yield r'hours_before';
      yield serializers.serialize(
        object.hoursBefore,
        specifiedType: const FullType(int),
      );
    }
    if (object.language != null) {
      yield r'language';
      yield serializers.serialize(
        object.language,
        specifiedType: const FullType(String),
      );
    }
  }

  @override
  Object serialize(
    Serializers serializers,
    SendEventReminderRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required SendEventReminderRequestBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'event_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.eventId = valueDes;
          break;
        case r'hours_before':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.hoursBefore = valueDes;
          break;
        case r'language':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.language = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  SendEventReminderRequest deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = SendEventReminderRequestBuilder();
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
