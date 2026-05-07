//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:signupflow_api/src/model/invitation_response.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'invitation_verify.g.dart';

/// Schema for verifying an invitation token.
///
/// Properties:
/// * [invitation] 
/// * [message] 
/// * [valid] 
@BuiltValue()
abstract class InvitationVerify implements Built<InvitationVerify, InvitationVerifyBuilder> {
  @BuiltValueField(wireName: r'invitation')
  InvitationResponse? get invitation;

  @BuiltValueField(wireName: r'message')
  String? get message;

  @BuiltValueField(wireName: r'valid')
  bool get valid;

  InvitationVerify._();

  factory InvitationVerify([void updates(InvitationVerifyBuilder b)]) = _$InvitationVerify;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(InvitationVerifyBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<InvitationVerify> get serializer => _$InvitationVerifySerializer();
}

class _$InvitationVerifySerializer implements PrimitiveSerializer<InvitationVerify> {
  @override
  final Iterable<Type> types = const [InvitationVerify, _$InvitationVerify];

  @override
  final String wireName = r'InvitationVerify';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    InvitationVerify object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    if (object.invitation != null) {
      yield r'invitation';
      yield serializers.serialize(
        object.invitation,
        specifiedType: const FullType.nullable(InvitationResponse),
      );
    }
    if (object.message != null) {
      yield r'message';
      yield serializers.serialize(
        object.message,
        specifiedType: const FullType.nullable(String),
      );
    }
    yield r'valid';
    yield serializers.serialize(
      object.valid,
      specifiedType: const FullType(bool),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    InvitationVerify object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required InvitationVerifyBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'invitation':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(InvitationResponse),
          ) as InvitationResponse?;
          if (valueDes == null) continue;
          result.invitation.replace(valueDes);
          break;
        case r'message':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.message = valueDes;
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
  InvitationVerify deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = InvitationVerifyBuilder();
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

