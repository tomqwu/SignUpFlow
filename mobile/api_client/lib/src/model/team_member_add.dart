//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'team_member_add.g.dart';

/// Schema for adding team members.
///
/// Properties:
/// * [personIds] - List of person IDs to add
@BuiltValue()
abstract class TeamMemberAdd implements Built<TeamMemberAdd, TeamMemberAddBuilder> {
  /// List of person IDs to add
  @BuiltValueField(wireName: r'person_ids')
  BuiltList<String> get personIds;

  TeamMemberAdd._();

  factory TeamMemberAdd([void updates(TeamMemberAddBuilder b)]) = _$TeamMemberAdd;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(TeamMemberAddBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<TeamMemberAdd> get serializer => _$TeamMemberAddSerializer();
}

class _$TeamMemberAddSerializer implements PrimitiveSerializer<TeamMemberAdd> {
  @override
  final Iterable<Type> types = const [TeamMemberAdd, _$TeamMemberAdd];

  @override
  final String wireName = r'TeamMemberAdd';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    TeamMemberAdd object, {
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
    TeamMemberAdd object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required TeamMemberAddBuilder result,
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
  TeamMemberAdd deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = TeamMemberAddBuilder();
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

