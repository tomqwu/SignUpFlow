//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:built_value/json_object.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'team_create.g.dart';

/// Schema for creating a team.
///
/// Properties:
/// * [description] 
/// * [extraData] 
/// * [id] - Unique team ID
/// * [memberIds] 
/// * [name] - Team name
/// * [orgId] - Organization ID
@BuiltValue()
abstract class TeamCreate implements Built<TeamCreate, TeamCreateBuilder> {
  @BuiltValueField(wireName: r'description')
  String? get description;

  @BuiltValueField(wireName: r'extra_data')
  BuiltMap<String, JsonObject?>? get extraData;

  /// Unique team ID
  @BuiltValueField(wireName: r'id')
  String get id;

  @BuiltValueField(wireName: r'member_ids')
  BuiltList<String>? get memberIds;

  /// Team name
  @BuiltValueField(wireName: r'name')
  String get name;

  /// Organization ID
  @BuiltValueField(wireName: r'org_id')
  String get orgId;

  TeamCreate._();

  factory TeamCreate([void updates(TeamCreateBuilder b)]) = _$TeamCreate;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(TeamCreateBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<TeamCreate> get serializer => _$TeamCreateSerializer();
}

class _$TeamCreateSerializer implements PrimitiveSerializer<TeamCreate> {
  @override
  final Iterable<Type> types = const [TeamCreate, _$TeamCreate];

  @override
  final String wireName = r'TeamCreate';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    TeamCreate object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    if (object.description != null) {
      yield r'description';
      yield serializers.serialize(
        object.description,
        specifiedType: const FullType.nullable(String),
      );
    }
    if (object.extraData != null) {
      yield r'extra_data';
      yield serializers.serialize(
        object.extraData,
        specifiedType: const FullType.nullable(BuiltMap, [FullType(String), FullType.nullable(JsonObject)]),
      );
    }
    yield r'id';
    yield serializers.serialize(
      object.id,
      specifiedType: const FullType(String),
    );
    if (object.memberIds != null) {
      yield r'member_ids';
      yield serializers.serialize(
        object.memberIds,
        specifiedType: const FullType.nullable(BuiltList, [FullType(String)]),
      );
    }
    yield r'name';
    yield serializers.serialize(
      object.name,
      specifiedType: const FullType(String),
    );
    yield r'org_id';
    yield serializers.serialize(
      object.orgId,
      specifiedType: const FullType(String),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    TeamCreate object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required TeamCreateBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'description':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.description = valueDes;
          break;
        case r'extra_data':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(BuiltMap, [FullType(String), FullType.nullable(JsonObject)]),
          ) as BuiltMap<String, JsonObject?>?;
          if (valueDes == null) continue;
          result.extraData.replace(valueDes);
          break;
        case r'id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.id = valueDes;
          break;
        case r'member_ids':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(BuiltList, [FullType(String)]),
          ) as BuiltList<String>?;
          if (valueDes == null) continue;
          result.memberIds.replace(valueDes);
          break;
        case r'name':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.name = valueDes;
          break;
        case r'org_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.orgId = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  TeamCreate deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = TeamCreateBuilder();
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

