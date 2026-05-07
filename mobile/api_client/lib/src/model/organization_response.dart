//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:built_value/json_object.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'organization_response.g.dart';

/// Schema for organization response.
///
/// Properties:
/// * [cancelledAt] 
/// * [config] 
/// * [createdAt] 
/// * [dataRetentionUntil] 
/// * [deletionScheduledAt] 
/// * [id] 
/// * [name] - Organization name
/// * [region] 
/// * [updatedAt] 
@BuiltValue()
abstract class OrganizationResponse implements Built<OrganizationResponse, OrganizationResponseBuilder> {
  @BuiltValueField(wireName: r'cancelled_at')
  DateTime? get cancelledAt;

  @BuiltValueField(wireName: r'config')
  BuiltMap<String, JsonObject?>? get config;

  @BuiltValueField(wireName: r'created_at')
  DateTime get createdAt;

  @BuiltValueField(wireName: r'data_retention_until')
  DateTime? get dataRetentionUntil;

  @BuiltValueField(wireName: r'deletion_scheduled_at')
  DateTime? get deletionScheduledAt;

  @BuiltValueField(wireName: r'id')
  String get id;

  /// Organization name
  @BuiltValueField(wireName: r'name')
  String get name;

  @BuiltValueField(wireName: r'region')
  String? get region;

  @BuiltValueField(wireName: r'updated_at')
  DateTime get updatedAt;

  OrganizationResponse._();

  factory OrganizationResponse([void updates(OrganizationResponseBuilder b)]) = _$OrganizationResponse;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(OrganizationResponseBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<OrganizationResponse> get serializer => _$OrganizationResponseSerializer();
}

class _$OrganizationResponseSerializer implements PrimitiveSerializer<OrganizationResponse> {
  @override
  final Iterable<Type> types = const [OrganizationResponse, _$OrganizationResponse];

  @override
  final String wireName = r'OrganizationResponse';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    OrganizationResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    if (object.cancelledAt != null) {
      yield r'cancelled_at';
      yield serializers.serialize(
        object.cancelledAt,
        specifiedType: const FullType.nullable(DateTime),
      );
    }
    if (object.config != null) {
      yield r'config';
      yield serializers.serialize(
        object.config,
        specifiedType: const FullType.nullable(BuiltMap, [FullType(String), FullType.nullable(JsonObject)]),
      );
    }
    yield r'created_at';
    yield serializers.serialize(
      object.createdAt,
      specifiedType: const FullType(DateTime),
    );
    if (object.dataRetentionUntil != null) {
      yield r'data_retention_until';
      yield serializers.serialize(
        object.dataRetentionUntil,
        specifiedType: const FullType.nullable(DateTime),
      );
    }
    if (object.deletionScheduledAt != null) {
      yield r'deletion_scheduled_at';
      yield serializers.serialize(
        object.deletionScheduledAt,
        specifiedType: const FullType.nullable(DateTime),
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
    yield r'updated_at';
    yield serializers.serialize(
      object.updatedAt,
      specifiedType: const FullType(DateTime),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    OrganizationResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required OrganizationResponseBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'cancelled_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(DateTime),
          ) as DateTime?;
          if (valueDes == null) continue;
          result.cancelledAt = valueDes;
          break;
        case r'config':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(BuiltMap, [FullType(String), FullType.nullable(JsonObject)]),
          ) as BuiltMap<String, JsonObject?>?;
          if (valueDes == null) continue;
          result.config.replace(valueDes);
          break;
        case r'created_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(DateTime),
          ) as DateTime;
          result.createdAt = valueDes;
          break;
        case r'data_retention_until':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(DateTime),
          ) as DateTime?;
          if (valueDes == null) continue;
          result.dataRetentionUntil = valueDes;
          break;
        case r'deletion_scheduled_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(DateTime),
          ) as DateTime?;
          if (valueDes == null) continue;
          result.deletionScheduledAt = valueDes;
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
        case r'updated_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(DateTime),
          ) as DateTime;
          result.updatedAt = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  OrganizationResponse deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = OrganizationResponseBuilder();
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

