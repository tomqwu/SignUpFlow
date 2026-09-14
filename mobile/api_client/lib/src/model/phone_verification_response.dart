//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'phone_verification_response.g.dart';

/// Response from phone verification.
///
/// Properties:
/// * [carrierType]
/// * [countryCode]
/// * [deliverable]
/// * [error]
/// * [formattedNumber]
/// * [valid]
@BuiltValue()
abstract class PhoneVerificationResponse implements Built<PhoneVerificationResponse, PhoneVerificationResponseBuilder> {
  @BuiltValueField(wireName: r'carrier_type')
  String get carrierType;

  @BuiltValueField(wireName: r'country_code')
  String? get countryCode;

  @BuiltValueField(wireName: r'deliverable')
  bool get deliverable;

  @BuiltValueField(wireName: r'error')
  String? get error;

  @BuiltValueField(wireName: r'formatted_number')
  String get formattedNumber;

  @BuiltValueField(wireName: r'valid')
  bool get valid;

  PhoneVerificationResponse._();

  factory PhoneVerificationResponse([void updates(PhoneVerificationResponseBuilder b)]) = _$PhoneVerificationResponse;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(PhoneVerificationResponseBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<PhoneVerificationResponse> get serializer => _$PhoneVerificationResponseSerializer();
}

class _$PhoneVerificationResponseSerializer implements PrimitiveSerializer<PhoneVerificationResponse> {
  @override
  final Iterable<Type> types = const [PhoneVerificationResponse, _$PhoneVerificationResponse];

  @override
  final String wireName = r'PhoneVerificationResponse';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    PhoneVerificationResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'carrier_type';
    yield serializers.serialize(
      object.carrierType,
      specifiedType: const FullType(String),
    );
    if (object.countryCode != null) {
      yield r'country_code';
      yield serializers.serialize(
        object.countryCode,
        specifiedType: const FullType.nullable(String),
      );
    }
    yield r'deliverable';
    yield serializers.serialize(
      object.deliverable,
      specifiedType: const FullType(bool),
    );
    if (object.error != null) {
      yield r'error';
      yield serializers.serialize(
        object.error,
        specifiedType: const FullType.nullable(String),
      );
    }
    yield r'formatted_number';
    yield serializers.serialize(
      object.formattedNumber,
      specifiedType: const FullType(String),
    );
    yield r'valid';
    yield serializers.serialize(
      object.valid,
      specifiedType: const FullType(bool),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    PhoneVerificationResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required PhoneVerificationResponseBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'carrier_type':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.carrierType = valueDes;
          break;
        case r'country_code':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.countryCode = valueDes;
          break;
        case r'deliverable':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(bool),
          ) as bool;
          result.deliverable = valueDes;
          break;
        case r'error':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.error = valueDes;
          break;
        case r'formatted_number':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.formattedNumber = valueDes;
          break;
        case r'valid':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(bool),
          ) as bool;
          result.valid = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  PhoneVerificationResponse deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = PhoneVerificationResponseBuilder();
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
