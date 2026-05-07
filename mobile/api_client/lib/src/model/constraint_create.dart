//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:built_value/json_object.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'constraint_create.g.dart';

/// Schema for creating a constraint.
///
/// Properties:
/// * [key] - Constraint key/identifier
/// * [orgId] - Organization ID
/// * [params] 
/// * [predicate] - Constraint predicate/rule
/// * [type] - Constraint type: hard or soft
/// * [weight] 
@BuiltValue()
abstract class ConstraintCreate implements Built<ConstraintCreate, ConstraintCreateBuilder> {
  /// Constraint key/identifier
  @BuiltValueField(wireName: r'key')
  String get key;

  /// Organization ID
  @BuiltValueField(wireName: r'org_id')
  String get orgId;

  @BuiltValueField(wireName: r'params')
  BuiltMap<String, JsonObject?>? get params;

  /// Constraint predicate/rule
  @BuiltValueField(wireName: r'predicate')
  String get predicate;

  /// Constraint type: hard or soft
  @BuiltValueField(wireName: r'type')
  String get type;

  @BuiltValueField(wireName: r'weight')
  int? get weight;

  ConstraintCreate._();

  factory ConstraintCreate([void updates(ConstraintCreateBuilder b)]) = _$ConstraintCreate;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(ConstraintCreateBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<ConstraintCreate> get serializer => _$ConstraintCreateSerializer();
}

class _$ConstraintCreateSerializer implements PrimitiveSerializer<ConstraintCreate> {
  @override
  final Iterable<Type> types = const [ConstraintCreate, _$ConstraintCreate];

  @override
  final String wireName = r'ConstraintCreate';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    ConstraintCreate object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'key';
    yield serializers.serialize(
      object.key,
      specifiedType: const FullType(String),
    );
    yield r'org_id';
    yield serializers.serialize(
      object.orgId,
      specifiedType: const FullType(String),
    );
    if (object.params != null) {
      yield r'params';
      yield serializers.serialize(
        object.params,
        specifiedType: const FullType.nullable(BuiltMap, [FullType(String), FullType.nullable(JsonObject)]),
      );
    }
    yield r'predicate';
    yield serializers.serialize(
      object.predicate,
      specifiedType: const FullType(String),
    );
    yield r'type';
    yield serializers.serialize(
      object.type,
      specifiedType: const FullType(String),
    );
    if (object.weight != null) {
      yield r'weight';
      yield serializers.serialize(
        object.weight,
        specifiedType: const FullType.nullable(int),
      );
    }
  }

  @override
  Object serialize(
    Serializers serializers,
    ConstraintCreate object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required ConstraintCreateBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'key':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.key = valueDes;
          break;
        case r'org_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.orgId = valueDes;
          break;
        case r'params':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(BuiltMap, [FullType(String), FullType.nullable(JsonObject)]),
          ) as BuiltMap<String, JsonObject?>?;
          if (valueDes == null) continue;
          result.params.replace(valueDes);
          break;
        case r'predicate':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.predicate = valueDes;
          break;
        case r'type':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.type = valueDes;
          break;
        case r'weight':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(int),
          ) as int?;
          if (valueDes == null) continue;
          result.weight = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  ConstraintCreate deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = ConstraintCreateBuilder();
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

