//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:built_value/json_object.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'organization_create.g.dart';

/// Schema for creating an organization.
///
/// Properties:
/// * [config] 
/// * [id] - Unique organization ID
/// * [name] - Organization name
/// * [region] 
@BuiltValue()
abstract class OrganizationCreate implements Built<OrganizationCreate, OrganizationCreateBuilder> {
  @BuiltValueField(wireName: r'config')
  BuiltMap<String, JsonObject?>? get config;

  /// Unique organization ID
  @BuiltValueField(wireName: r'id')
  String get id;

  /// Organization name
  @BuiltValueField(wireName: r'name')
  String get name;

  @BuiltValueField(wireName: r'region')
  String? get region;

  OrganizationCreate._();

  factory OrganizationCreate([void updates(OrganizationCreateBuilder b)]) = _$OrganizationCreate;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(OrganizationCreateBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<OrganizationCreate> get serializer => _$OrganizationCreateSerializer();
}

class _$OrganizationCreateSerializer implements PrimitiveSerializer<OrganizationCreate> {
  @override
  final Iterable<Type> types = const [OrganizationCreate, _$OrganizationCreate];

  @override
  final String wireName = r'OrganizationCreate';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    OrganizationCreate object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    if (object.config != null) {
      yield r'config';
      yield serializers.serialize(
        object.config,
        specifiedType: const FullType.nullable(BuiltMap, [FullType(String), FullType.nullable(JsonObject)]),
      );
    }
    yield r'id';
    yield serializers.serialize(
      object.id,
      specifiedType: const FullType(String),
    );
    yield r'name';
    yield serializers.serialize(
      object.name,
      specifiedType: const FullType(String),
    );
    if (object.region != null) {
      yield r'region';
      yield serializers.serialize(
        object.region,
        specifiedType: const FullType.nullable(String),
      );
    }
  }

  @override
  Object serialize(
    Serializers serializers,
    OrganizationCreate object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required OrganizationCreateBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'config':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(BuiltMap, [FullType(String), FullType.nullable(JsonObject)]),
          ) as BuiltMap<String, JsonObject?>?;
          if (valueDes == null) continue;
          result.config.replace(valueDes);
          break;
        case r'id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.id = valueDes;
          break;
        case r'name':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.name = valueDes;
          break;
        case r'region':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.region = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  OrganizationCreate deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = OrganizationCreateBuilder();
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

