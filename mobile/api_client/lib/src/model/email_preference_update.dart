//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'email_preference_update.g.dart';

/// Schema for updating email preferences.
///
/// Properties:
/// * [digestHour] 
/// * [enabledTypes] 
/// * [frequency] 
/// * [language] 
/// * [timezone] 
@BuiltValue()
abstract class EmailPreferenceUpdate implements Built<EmailPreferenceUpdate, EmailPreferenceUpdateBuilder> {
  @BuiltValueField(wireName: r'digest_hour')
  int? get digestHour;

  @BuiltValueField(wireName: r'enabled_types')
  BuiltList<String>? get enabledTypes;

  @BuiltValueField(wireName: r'frequency')
  String? get frequency;

  @BuiltValueField(wireName: r'language')
  String? get language;

  @BuiltValueField(wireName: r'timezone')
  String? get timezone;

  EmailPreferenceUpdate._();

  factory EmailPreferenceUpdate([void updates(EmailPreferenceUpdateBuilder b)]) = _$EmailPreferenceUpdate;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(EmailPreferenceUpdateBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<EmailPreferenceUpdate> get serializer => _$EmailPreferenceUpdateSerializer();
}

class _$EmailPreferenceUpdateSerializer implements PrimitiveSerializer<EmailPreferenceUpdate> {
  @override
  final Iterable<Type> types = const [EmailPreferenceUpdate, _$EmailPreferenceUpdate];

  @override
  final String wireName = r'EmailPreferenceUpdate';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    EmailPreferenceUpdate object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    if (object.digestHour != null) {
      yield r'digest_hour';
      yield serializers.serialize(
        object.digestHour,
        specifiedType: const FullType.nullable(int),
      );
    }
    if (object.enabledTypes != null) {
      yield r'enabled_types';
      yield serializers.serialize(
        object.enabledTypes,
        specifiedType: const FullType.nullable(BuiltList, [FullType(String)]),
      );
    }
    if (object.frequency != null) {
      yield r'frequency';
      yield serializers.serialize(
        object.frequency,
        specifiedType: const FullType.nullable(String),
      );
    }
    if (object.language != null) {
      yield r'language';
      yield serializers.serialize(
        object.language,
        specifiedType: const FullType.nullable(String),
      );
    }
    if (object.timezone != null) {
      yield r'timezone';
      yield serializers.serialize(
        object.timezone,
        specifiedType: const FullType.nullable(String),
      );
    }
  }

  @override
  Object serialize(
    Serializers serializers,
    EmailPreferenceUpdate object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required EmailPreferenceUpdateBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'digest_hour':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(int),
          ) as int?;
          if (valueDes == null) continue;
          result.digestHour = valueDes;
          break;
        case r'enabled_types':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(BuiltList, [FullType(String)]),
          ) as BuiltList<String>?;
          if (valueDes == null) continue;
          result.enabledTypes.replace(valueDes);
          break;
        case r'frequency':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.frequency = valueDes;
          break;
        case r'language':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.language = valueDes;
          break;
        case r'timezone':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.timezone = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  EmailPreferenceUpdate deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = EmailPreferenceUpdateBuilder();
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

