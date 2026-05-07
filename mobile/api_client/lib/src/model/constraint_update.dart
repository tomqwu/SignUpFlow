//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:built_value/json_object.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'constraint_update.g.dart';

/// Schema for updating a constraint.
///
/// Properties:
/// * [params] 
/// * [predicate] 
/// * [type] 
/// * [weight] 
@BuiltValue()
abstract class ConstraintUpdate implements Built<ConstraintUpdate, ConstraintUpdateBuilder> {
  @BuiltValueField(wireName: r'params')
  BuiltMap<String, JsonObject?>? get params;

  @BuiltValueField(wireName: r'predicate')
  String? get predicate;

  @BuiltValueField(wireName: r'type')
  String? get type;

  @BuiltValueField(wireName: r'weight')
  int? get weight;

  ConstraintUpdate._();

  factory ConstraintUpdate([void updates(ConstraintUpdateBuilder b)]) = _$ConstraintUpdate;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(ConstraintUpdateBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<ConstraintUpdate> get serializer => _$ConstraintUpdateSerializer();
}

class _$ConstraintUpdateSerializer implements PrimitiveSerializer<ConstraintUpdate> {
  @override
  final Iterable<Type> types = const [ConstraintUpdate, _$ConstraintUpdate];

  @override
  final String wireName = r'ConstraintUpdate';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    ConstraintUpdate object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    if (object.params != null) {
      yield r'params';
      yield serializers.serialize(
        object.params,
        specifiedType: const FullType.nullable(BuiltMap, [FullType(String), FullType.nullable(JsonObject)]),
      );
    }
    if (object.predicate != null) {
      yield r'predicate';
      yield serializers.serialize(
        object.predicate,
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
    ConstraintUpdate object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required ConstraintUpdateBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
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
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.predicate = valueDes;
          break;
        case r'type':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
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
  ConstraintUpdate deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = ConstraintUpdateBuilder();
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

