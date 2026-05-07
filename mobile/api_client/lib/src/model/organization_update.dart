//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:built_value/json_object.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'organization_update.g.dart';

/// Schema for updating an organization.
///
/// Properties:
/// * [config] 
/// * [name] 
/// * [region] 
@BuiltValue()
abstract class OrganizationUpdate implements Built<OrganizationUpdate, OrganizationUpdateBuilder> {
  @BuiltValueField(wireName: r'config')
  BuiltMap<String, JsonObject?>? get config;

  @BuiltValueField(wireName: r'name')
  String? get name;

  @BuiltValueField(wireName: r'region')
  String? get region;

  OrganizationUpdate._();

  factory OrganizationUpdate([void updates(OrganizationUpdateBuilder b)]) = _$OrganizationUpdate;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(OrganizationUpdateBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<OrganizationUpdate> get serializer => _$OrganizationUpdateSerializer();
}

class _$OrganizationUpdateSerializer implements PrimitiveSerializer<OrganizationUpdate> {
  @override
  final Iterable<Type> types = const [OrganizationUpdate, _$OrganizationUpdate];

  @override
  final String wireName = r'OrganizationUpdate';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    OrganizationUpdate object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    if (object.config != null) {
      yield r'config';
      yield serializers.serialize(
        object.config,
        specifiedType: const FullType.nullable(BuiltMap, [FullType(String), FullType.nullable(JsonObject)]),
      );
    }
    if (object.name != null) {
      yield r'name';
      yield serializers.serialize(
        object.name,
        specifiedType: const FullType.nullable(String),
      );
    }
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
    OrganizationUpdate object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required OrganizationUpdateBuilder result,
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
        case r'name':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
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
  OrganizationUpdate deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = OrganizationUpdateBuilder();
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

