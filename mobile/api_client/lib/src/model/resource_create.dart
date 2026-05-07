//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:built_value/json_object.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'resource_create.g.dart';

/// ResourceCreate
///
/// Properties:
/// * [capacity] 
/// * [extraData] 
/// * [id] - Caller-supplied unique id
/// * [location] 
/// * [orgId] - Owning organization
/// * [type] - e.g. 'room', 'venue', 'equipment'
@BuiltValue()
abstract class ResourceCreate implements Built<ResourceCreate, ResourceCreateBuilder> {
  @BuiltValueField(wireName: r'capacity')
  int? get capacity;

  @BuiltValueField(wireName: r'extra_data')
  BuiltMap<String, JsonObject?>? get extraData;

  /// Caller-supplied unique id
  @BuiltValueField(wireName: r'id')
  String get id;

  @BuiltValueField(wireName: r'location')
  String get location;

  /// Owning organization
  @BuiltValueField(wireName: r'org_id')
  String get orgId;

  /// e.g. 'room', 'venue', 'equipment'
  @BuiltValueField(wireName: r'type')
  String get type;

  ResourceCreate._();

  factory ResourceCreate([void updates(ResourceCreateBuilder b)]) = _$ResourceCreate;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(ResourceCreateBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<ResourceCreate> get serializer => _$ResourceCreateSerializer();
}

class _$ResourceCreateSerializer implements PrimitiveSerializer<ResourceCreate> {
  @override
  final Iterable<Type> types = const [ResourceCreate, _$ResourceCreate];

  @override
  final String wireName = r'ResourceCreate';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    ResourceCreate object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    if (object.capacity != null) {
      yield r'capacity';
      yield serializers.serialize(
        object.capacity,
        specifiedType: const FullType.nullable(int),
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
    yield r'location';
    yield serializers.serialize(
      object.location,
      specifiedType: const FullType(String),
    );
    yield r'org_id';
    yield serializers.serialize(
      object.orgId,
      specifiedType: const FullType(String),
    );
    yield r'type';
    yield serializers.serialize(
      object.type,
      specifiedType: const FullType(String),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    ResourceCreate object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required ResourceCreateBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'capacity':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(int),
          ) as int?;
          if (valueDes == null) continue;
          result.capacity = valueDes;
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
        case r'location':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.location = valueDes;
          break;
        case r'org_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.orgId = valueDes;
          break;
        case r'type':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.type = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  ResourceCreate deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = ResourceCreateBuilder();
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

