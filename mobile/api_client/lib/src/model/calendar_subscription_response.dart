//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'calendar_subscription_response.g.dart';

/// Calendar subscription response.
///
/// Properties:
/// * [httpsUrl] 
/// * [message] 
/// * [token] 
/// * [webcalUrl] 
@BuiltValue()
abstract class CalendarSubscriptionResponse implements Built<CalendarSubscriptionResponse, CalendarSubscriptionResponseBuilder> {
  @BuiltValueField(wireName: r'https_url')
  String get httpsUrl;

  @BuiltValueField(wireName: r'message')
  String get message;

  @BuiltValueField(wireName: r'token')
  String get token;

  @BuiltValueField(wireName: r'webcal_url')
  String get webcalUrl;

  CalendarSubscriptionResponse._();

  factory CalendarSubscriptionResponse([void updates(CalendarSubscriptionResponseBuilder b)]) = _$CalendarSubscriptionResponse;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(CalendarSubscriptionResponseBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<CalendarSubscriptionResponse> get serializer => _$CalendarSubscriptionResponseSerializer();
}

class _$CalendarSubscriptionResponseSerializer implements PrimitiveSerializer<CalendarSubscriptionResponse> {
  @override
  final Iterable<Type> types = const [CalendarSubscriptionResponse, _$CalendarSubscriptionResponse];

  @override
  final String wireName = r'CalendarSubscriptionResponse';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    CalendarSubscriptionResponse object, {
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
    CalendarSubscriptionResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required CalendarSubscriptionResponseBuilder result,
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
  CalendarSubscriptionResponse deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = CalendarSubscriptionResponseBuilder();
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

