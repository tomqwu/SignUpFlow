//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'calendar_token_reset_response.g.dart';

/// Calendar token reset response.
///
/// Properties:
/// * [httpsUrl] 
/// * [message] 
/// * [token] 
/// * [webcalUrl] 
@BuiltValue()
abstract class CalendarTokenResetResponse implements Built<CalendarTokenResetResponse, CalendarTokenResetResponseBuilder> {
  @BuiltValueField(wireName: r'https_url')
  String get httpsUrl;

  @BuiltValueField(wireName: r'message')
  String get message;

  @BuiltValueField(wireName: r'token')
  String get token;

  @BuiltValueField(wireName: r'webcal_url')
  String get webcalUrl;

  CalendarTokenResetResponse._();

  factory CalendarTokenResetResponse([void updates(CalendarTokenResetResponseBuilder b)]) = _$CalendarTokenResetResponse;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(CalendarTokenResetResponseBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<CalendarTokenResetResponse> get serializer => _$CalendarTokenResetResponseSerializer();
}

class _$CalendarTokenResetResponseSerializer implements PrimitiveSerializer<CalendarTokenResetResponse> {
  @override
  final Iterable<Type> types = const [CalendarTokenResetResponse, _$CalendarTokenResetResponse];

  @override
  final String wireName = r'CalendarTokenResetResponse';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    CalendarTokenResetResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'https_url';
    yield serializers.serialize(
      object.httpsUrl,
      specifiedType: const FullType(String),
    );
    yield r'message';
    yield serializers.serialize(
      object.message,
      specifiedType: const FullType(String),
    );
    yield r'token';
    yield serializers.serialize(
      object.token,
      specifiedType: const FullType(String),
    );
    yield r'webcal_url';
    yield serializers.serialize(
      object.webcalUrl,
      specifiedType: const FullType(String),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    CalendarTokenResetResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required CalendarTokenResetResponseBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'https_url':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.httpsUrl = valueDes;
          break;
        case r'message':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.message = valueDes;
          break;
        case r'token':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.token = valueDes;
          break;
        case r'webcal_url':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.webcalUrl = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  CalendarTokenResetResponse deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = CalendarTokenResetResponseBuilder();
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

