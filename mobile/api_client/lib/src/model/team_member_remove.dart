//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'team_member_remove.g.dart';

/// Schema for removing team members.
///
/// Properties:
/// * [personIds] - List of person IDs to remove
@BuiltValue()
abstract class TeamMemberRemove implements Built<TeamMemberRemove, TeamMemberRemoveBuilder> {
  /// List of person IDs to remove
  @BuiltValueField(wireName: r'person_ids')
  BuiltList<String> get personIds;

  TeamMemberRemove._();

  factory TeamMemberRemove([void updates(TeamMemberRemoveBuilder b)]) = _$TeamMemberRemove;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(TeamMemberRemoveBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<TeamMemberRemove> get serializer => _$TeamMemberRemoveSerializer();
}

class _$TeamMemberRemoveSerializer implements PrimitiveSerializer<TeamMemberRemove> {
  @override
  final Iterable<Type> types = const [TeamMemberRemove, _$TeamMemberRemove];

  @override
  final String wireName = r'TeamMemberRemove';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    TeamMemberRemove object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'person_ids';
    yield serializers.serialize(
      object.personIds,
      specifiedType: const FullType(BuiltList, [FullType(String)]),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    TeamMemberRemove object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required TeamMemberRemoveBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'person_ids':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(String)]),
          ) as BuiltList<String>;
          result.personIds.replace(valueDes);
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  TeamMemberRemove deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = TeamMemberRemoveBuilder();
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

