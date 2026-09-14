//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'phone_verification_request.g.dart';

/// Request to verify phone number format and deliverability.
///
/// Properties:
/// * [phoneNumber] - Phone number in E.164 format (+12345678900)
@BuiltValue()
abstract class PhoneVerificationRequest implements Built<PhoneVerificationRequest, PhoneVerificationRequestBuilder> {
  /// Phone number in E.164 format (+12345678900)
  @BuiltValueField(wireName: r'phone_number')
  String get phoneNumber;

  PhoneVerificationRequest._();

  factory PhoneVerificationRequest([void updates(PhoneVerificationRequestBuilder b)]) = _$PhoneVerificationRequest;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(PhoneVerificationRequestBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<PhoneVerificationRequest> get serializer => _$PhoneVerificationRequestSerializer();
}

class _$PhoneVerificationRequestSerializer implements PrimitiveSerializer<PhoneVerificationRequest> {
  @override
  final Iterable<Type> types = const [PhoneVerificationRequest, _$PhoneVerificationRequest];

  @override
  final String wireName = r'PhoneVerificationRequest';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    PhoneVerificationRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'phone_number';
    yield serializers.serialize(
      object.phoneNumber,
      specifiedType: const FullType(String),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    PhoneVerificationRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required PhoneVerificationRequestBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'phone_number':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.phoneNumber = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  PhoneVerificationRequest deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = PhoneVerificationRequestBuilder();
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

