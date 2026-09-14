//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'update_sms_preferences_request.g.dart';

/// Request to update SMS notification preferences.
///
/// Properties:
/// * [language] - Preferred language for SMS: en, es, pt, zh-CN, zh-TW, fr
/// * [notificationTypes] - List of notification types: assignment, reminder, change, cancellation
@BuiltValue()
abstract class UpdateSmsPreferencesRequest implements Built<UpdateSmsPreferencesRequest, UpdateSmsPreferencesRequestBuilder> {
  /// Preferred language for SMS: en, es, pt, zh-CN, zh-TW, fr
  @BuiltValueField(wireName: r'language')
  String? get language;

  /// List of notification types: assignment, reminder, change, cancellation
  @BuiltValueField(wireName: r'notification_types')
  BuiltList<String> get notificationTypes;

  UpdateSmsPreferencesRequest._();

  factory UpdateSmsPreferencesRequest([void updates(UpdateSmsPreferencesRequestBuilder b)]) = _$UpdateSmsPreferencesRequest;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(UpdateSmsPreferencesRequestBuilder b) => b
      ..language = 'en';

  @BuiltValueSerializer(custom: true)
  static Serializer<UpdateSmsPreferencesRequest> get serializer => _$UpdateSmsPreferencesRequestSerializer();
}

class _$UpdateSmsPreferencesRequestSerializer implements PrimitiveSerializer<UpdateSmsPreferencesRequest> {
  @override
  final Iterable<Type> types = const [UpdateSmsPreferencesRequest, _$UpdateSmsPreferencesRequest];

  @override
  final String wireName = r'UpdateSmsPreferencesRequest';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    UpdateSmsPreferencesRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    if (object.language != null) {
      yield r'language';
      yield serializers.serialize(
        object.language,
        specifiedType: const FullType(String),
      );
    }
    yield r'notification_types';
    yield serializers.serialize(
      object.notificationTypes,
      specifiedType: const FullType(BuiltList, [FullType(String)]),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    UpdateSmsPreferencesRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required UpdateSmsPreferencesRequestBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'language':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.language = valueDes;
          break;
        case r'notification_types':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(String)]),
          ) as BuiltList<String>;
          result.notificationTypes.replace(valueDes);
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  UpdateSmsPreferencesRequest deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = UpdateSmsPreferencesRequestBuilder();
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

