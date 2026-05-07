//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'available_person.g.dart';

/// Person available for an event.
///
/// Properties:
/// * [email] 
/// * [id] 
/// * [isAssigned] 
/// * [isBlocked] 
/// * [name] 
/// * [roles] 
@BuiltValue()
abstract class AvailablePerson implements Built<AvailablePerson, AvailablePersonBuilder> {
  @BuiltValueField(wireName: r'email')
  String? get email;

  @BuiltValueField(wireName: r'id')
  String get id;

  @BuiltValueField(wireName: r'is_assigned')
  bool get isAssigned;

  @BuiltValueField(wireName: r'is_blocked')
  bool? get isBlocked;

  @BuiltValueField(wireName: r'name')
  String get name;

  @BuiltValueField(wireName: r'roles')
  BuiltList<String> get roles;

  AvailablePerson._();

  factory AvailablePerson([void updates(AvailablePersonBuilder b)]) = _$AvailablePerson;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(AvailablePersonBuilder b) => b
      ..isBlocked = false;

  @BuiltValueSerializer(custom: true)
  static Serializer<AvailablePerson> get serializer => _$AvailablePersonSerializer();
}

class _$AvailablePersonSerializer implements PrimitiveSerializer<AvailablePerson> {
  @override
  final Iterable<Type> types = const [AvailablePerson, _$AvailablePerson];

  @override
  final String wireName = r'AvailablePerson';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    AvailablePerson object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'email';
    yield object.email == null ? null : serializers.serialize(
      object.email,
      specifiedType: const FullType.nullable(String),
    );
    yield r'id';
    yield serializers.serialize(
      object.id,
      specifiedType: const FullType(String),
    );
    yield r'is_assigned';
    yield serializers.serialize(
      object.isAssigned,
      specifiedType: const FullType(bool),
    );
    if (object.isBlocked != null) {
      yield r'is_blocked';
      yield serializers.serialize(
        object.isBlocked,
        specifiedType: const FullType(bool),
      );
    }
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
    AvailablePerson object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required AvailablePersonBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'email':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.email = valueDes;
          break;
        case r'id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.id = valueDes;
          break;
        case r'is_assigned':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(bool),
          ) as bool;
          result.isAssigned = valueDes;
          break;
        case r'is_blocked':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(bool),
          ) as bool;
          result.isBlocked = valueDes;
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
  AvailablePerson deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = AvailablePersonBuilder();
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

