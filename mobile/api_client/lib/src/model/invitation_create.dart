//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'invitation_create.g.dart';

/// Schema for creating an invitation.
///
/// Properties:
/// * [email] - Email address of the invitee
/// * [name] - Full name of the invitee
/// * [roles] - Roles to assign (e.g., ['volunteer', 'admin'])
@BuiltValue()
abstract class InvitationCreate implements Built<InvitationCreate, InvitationCreateBuilder> {
  /// Email address of the invitee
  @BuiltValueField(wireName: r'email')
  String get email;

  /// Full name of the invitee
  @BuiltValueField(wireName: r'name')
  String get name;

  /// Roles to assign (e.g., ['volunteer', 'admin'])
  @BuiltValueField(wireName: r'roles')
  BuiltList<String> get roles;

  InvitationCreate._();

  factory InvitationCreate([void updates(InvitationCreateBuilder b)]) = _$InvitationCreate;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(InvitationCreateBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<InvitationCreate> get serializer => _$InvitationCreateSerializer();
}

class _$InvitationCreateSerializer implements PrimitiveSerializer<InvitationCreate> {
  @override
  final Iterable<Type> types = const [InvitationCreate, _$InvitationCreate];

  @override
  final String wireName = r'InvitationCreate';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    InvitationCreate object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'email';
    yield serializers.serialize(
      object.email,
      specifiedType: const FullType(String),
    );
    yield r'name';
    yield serializers.serialize(
      object.name,
      specifiedType: const FullType(String),
    );
    yield r'roles';
    yield serializers.serialize(
      object.roles,
      specifiedType: const FullType(BuiltList, [FullType(String)]),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    InvitationCreate object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required InvitationCreateBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'email':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.email = valueDes;
          break;
        case r'name':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.name = valueDes;
          break;
        case r'roles':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(String)]),
          ) as BuiltList<String>;
          result.roles.replace(valueDes);
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  InvitationCreate deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = InvitationCreateBuilder();
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

