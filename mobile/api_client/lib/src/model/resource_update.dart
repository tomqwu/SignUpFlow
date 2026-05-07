//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:built_value/json_object.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'resource_update.g.dart';

/// All fields optional (PATCH-style update).
///
/// Properties:
/// * [capacity] 
/// * [extraData] 
/// * [location] 
/// * [type] 
@BuiltValue()
abstract class ResourceUpdate implements Built<ResourceUpdate, ResourceUpdateBuilder> {
  @BuiltValueField(wireName: r'capacity')
  int? get capacity;

  @BuiltValueField(wireName: r'extra_data')
  BuiltMap<String, JsonObject?>? get extraData;

  @BuiltValueField(wireName: r'location')
  String? get location;

  @BuiltValueField(wireName: r'type')
  String? get type;

  ResourceUpdate._();

  factory ResourceUpdate([void updates(ResourceUpdateBuilder b)]) = _$ResourceUpdate;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(ResourceUpdateBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<ResourceUpdate> get serializer => _$ResourceUpdateSerializer();
}

class _$ResourceUpdateSerializer implements PrimitiveSerializer<ResourceUpdate> {
  @override
  final Iterable<Type> types = const [ResourceUpdate, _$ResourceUpdate];

  @override
  final String wireName = r'ResourceUpdate';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    ResourceUpdate object, {
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
    if (object.location != null) {
      yield r'location';
      yield serializers.serialize(
        object.location,
        specifiedType: const FullType.nullable(String),
      );
    }
    if (object.type != null) {
      yield r'type';
      yield serializers.serialize(
        object.type,
        specifiedType: const FullType.nullable(String),
      );
    }
  }

  @override
  Object serialize(
    Serializers serializers,
    ResourceUpdate object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required ResourceUpdateBuilder result,
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
        case r'location':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.location = valueDes;
          break;
        case r'type':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
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
  ResourceUpdate deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = ResourceUpdateBuilder();
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

