//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'verification_code_request.g.dart';

/// Request to generate and send verification code.
///
/// Properties:
/// * [personId]
/// * [phoneNumber] - Phone number in E.164 format
@BuiltValue()
abstract class VerificationCodeRequest implements Built<VerificationCodeRequest, VerificationCodeRequestBuilder> {
  @BuiltValueField(wireName: r'person_id')
  int get personId;

  /// Phone number in E.164 format
  @BuiltValueField(wireName: r'phone_number')
  String get phoneNumber;

  VerificationCodeRequest._();

  factory VerificationCodeRequest([void updates(VerificationCodeRequestBuilder b)]) = _$VerificationCodeRequest;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(VerificationCodeRequestBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<VerificationCodeRequest> get serializer => _$VerificationCodeRequestSerializer();
}

class _$VerificationCodeRequestSerializer implements PrimitiveSerializer<VerificationCodeRequest> {
  @override
  final Iterable<Type> types = const [VerificationCodeRequest, _$VerificationCodeRequest];

  @override
  final String wireName = r'VerificationCodeRequest';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    VerificationCodeRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'person_id';
    yield serializers.serialize(
      object.personId,
      specifiedType: const FullType(int),
    );
    yield r'phone_number';
    yield serializers.serialize(
      object.phoneNumber,
      specifiedType: const FullType(String),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    VerificationCodeRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required VerificationCodeRequestBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'person_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.personId = valueDes;
          break;
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
  VerificationCodeRequest deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = VerificationCodeRequestBuilder();
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

