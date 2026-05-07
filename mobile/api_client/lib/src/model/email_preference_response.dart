//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'email_preference_response.g.dart';

/// Schema for email preference response.
///
/// Properties:
/// * [digestHour] - Hour to send digests (0-23)
/// * [enabledTypes] - List of enabled notification types
/// * [frequency] - Email frequency (immediate, daily, weekly, disabled)
/// * [id] 
/// * [language] - Email language preference (ISO 639-1 code)
/// * [orgId] 
/// * [personId] 
/// * [timezone] - Timezone for digest scheduling
/// * [unsubscribeToken] 
/// * [updatedAt] 
@BuiltValue()
abstract class EmailPreferenceResponse implements Built<EmailPreferenceResponse, EmailPreferenceResponseBuilder> {
  /// Hour to send digests (0-23)
  @BuiltValueField(wireName: r'digest_hour')
  int? get digestHour;

  /// List of enabled notification types
  @BuiltValueField(wireName: r'enabled_types')
  BuiltList<String>? get enabledTypes;

  /// Email frequency (immediate, daily, weekly, disabled)
  @BuiltValueField(wireName: r'frequency')
  String? get frequency;

  @BuiltValueField(wireName: r'id')
  int? get id;

  /// Email language preference (ISO 639-1 code)
  @BuiltValueField(wireName: r'language')
  String? get language;

  @BuiltValueField(wireName: r'org_id')
  String get orgId;

  @BuiltValueField(wireName: r'person_id')
  String get personId;

  /// Timezone for digest scheduling
  @BuiltValueField(wireName: r'timezone')
  String? get timezone;

  @BuiltValueField(wireName: r'unsubscribe_token')
  String? get unsubscribeToken;

  @BuiltValueField(wireName: r'updated_at')
  DateTime? get updatedAt;

  EmailPreferenceResponse._();

  factory EmailPreferenceResponse([void updates(EmailPreferenceResponseBuilder b)]) = _$EmailPreferenceResponse;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(EmailPreferenceResponseBuilder b) => b
      ..digestHour = 8
      ..frequency = 'immediate'
      ..language = 'en'
      ..timezone = 'UTC';

  @BuiltValueSerializer(custom: true)
  static Serializer<EmailPreferenceResponse> get serializer => _$EmailPreferenceResponseSerializer();
}

class _$EmailPreferenceResponseSerializer implements PrimitiveSerializer<EmailPreferenceResponse> {
  @override
  final Iterable<Type> types = const [EmailPreferenceResponse, _$EmailPreferenceResponse];

  @override
  final String wireName = r'EmailPreferenceResponse';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    EmailPreferenceResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    if (object.digestHour != null) {
      yield r'digest_hour';
      yield serializers.serialize(
        object.digestHour,
        specifiedType: const FullType(int),
      );
    }
    if (object.enabledTypes != null) {
      yield r'enabled_types';
      yield serializers.serialize(
        object.enabledTypes,
        specifiedType: const FullType(BuiltList, [FullType(String)]),
      );
    }
    if (object.frequency != null) {
      yield r'frequency';
      yield serializers.serialize(
        object.frequency,
        specifiedType: const FullType(String),
      );
    }
    if (object.id != null) {
      yield r'id';
      yield serializers.serialize(
        object.id,
        specifiedType: const FullType.nullable(int),
      );
    }
    if (object.language != null) {
      yield r'language';
      yield serializers.serialize(
        object.language,
        specifiedType: const FullType(String),
      );
    }
    yield r'org_id';
    yield serializers.serialize(
      object.orgId,
      specifiedType: const FullType(String),
    );
    yield r'person_id';
    yield serializers.serialize(
      object.personId,
      specifiedType: const FullType(String),
    );
    if (object.timezone != null) {
      yield r'timezone';
      yield serializers.serialize(
        object.timezone,
        specifiedType: const FullType(String),
      );
    }
    if (object.unsubscribeToken != null) {
      yield r'unsubscribe_token';
      yield serializers.serialize(
        object.unsubscribeToken,
        specifiedType: const FullType.nullable(String),
      );
    }
    if (object.updatedAt != null) {
      yield r'updated_at';
      yield serializers.serialize(
        object.updatedAt,
        specifiedType: const FullType.nullable(DateTime),
      );
    }
  }

  @override
  Object serialize(
    Serializers serializers,
    EmailPreferenceResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required EmailPreferenceResponseBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'digest_hour':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.digestHour = valueDes;
          break;
        case r'enabled_types':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(String)]),
          ) as BuiltList<String>;
          result.enabledTypes.replace(valueDes);
          break;
        case r'frequency':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.frequency = valueDes;
          break;
        case r'id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(int),
          ) as int?;
          if (valueDes == null) continue;
          result.id = valueDes;
          break;
        case r'language':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.language = valueDes;
          break;
        case r'org_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.orgId = valueDes;
          break;
        case r'person_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.personId = valueDes;
          break;
        case r'timezone':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.timezone = valueDes;
          break;
        case r'unsubscribe_token':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.unsubscribeToken = valueDes;
          break;
        case r'updated_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(DateTime),
          ) as DateTime?;
          if (valueDes == null) continue;
          result.updatedAt = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  EmailPreferenceResponse deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = EmailPreferenceResponseBuilder();
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

