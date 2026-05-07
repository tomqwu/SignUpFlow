//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'invitation_accept.g.dart';

/// Schema for accepting an invitation.
///
/// Properties:
/// * [password] - Password for the new account (min 6 characters)
/// * [timezone] - User's timezone preference
@BuiltValue()
abstract class InvitationAccept implements Built<InvitationAccept, InvitationAcceptBuilder> {
  /// Password for the new account (min 6 characters)
  @BuiltValueField(wireName: r'password')
  String get password;

  /// User's timezone preference
  @BuiltValueField(wireName: r'timezone')
  String? get timezone;

  InvitationAccept._();

  factory InvitationAccept([void updates(InvitationAcceptBuilder b)]) = _$InvitationAccept;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(InvitationAcceptBuilder b) => b
      ..timezone = 'UTC';

  @BuiltValueSerializer(custom: true)
  static Serializer<InvitationAccept> get serializer => _$InvitationAcceptSerializer();
}

class _$InvitationAcceptSerializer implements PrimitiveSerializer<InvitationAccept> {
  @override
  final Iterable<Type> types = const [InvitationAccept, _$InvitationAccept];

  @override
  final String wireName = r'InvitationAccept';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    InvitationAccept object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'password';
    yield serializers.serialize(
      object.password,
      specifiedType: const FullType(String),
    );
    if (object.timezone != null) {
      yield r'timezone';
      yield serializers.serialize(
        object.timezone,
        specifiedType: const FullType(String),
      );
    }
  }

  @override
  Object serialize(
    Serializers serializers,
    InvitationAccept object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required InvitationAcceptBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'password':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.password = valueDes;
          break;
        case r'timezone':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
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
  InvitationAccept deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = InvitationAcceptBuilder();
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

