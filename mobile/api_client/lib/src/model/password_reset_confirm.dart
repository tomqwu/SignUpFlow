//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'password_reset_confirm.g.dart';

/// Confirm password reset with token.
///
/// Properties:
/// * [newPassword] 
/// * [token] 
@BuiltValue()
abstract class PasswordResetConfirm implements Built<PasswordResetConfirm, PasswordResetConfirmBuilder> {
  @BuiltValueField(wireName: r'new_password')
  String get newPassword;

  @BuiltValueField(wireName: r'token')
  String get token;

  PasswordResetConfirm._();

  factory PasswordResetConfirm([void updates(PasswordResetConfirmBuilder b)]) = _$PasswordResetConfirm;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(PasswordResetConfirmBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<PasswordResetConfirm> get serializer => _$PasswordResetConfirmSerializer();
}

class _$PasswordResetConfirmSerializer implements PrimitiveSerializer<PasswordResetConfirm> {
  @override
  final Iterable<Type> types = const [PasswordResetConfirm, _$PasswordResetConfirm];

  @override
  final String wireName = r'PasswordResetConfirm';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    PasswordResetConfirm object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'new_password';
    yield serializers.serialize(
      object.newPassword,
      specifiedType: const FullType(String),
    );
    yield r'token';
    yield serializers.serialize(
      object.token,
      specifiedType: const FullType(String),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    PasswordResetConfirm object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required PasswordResetConfirmBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'new_password':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.newPassword = valueDes;
          break;
        case r'token':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.token = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  PasswordResetConfirm deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = PasswordResetConfirmBuilder();
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

