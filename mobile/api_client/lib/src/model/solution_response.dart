//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:built_value/json_object.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'solution_response.g.dart';

/// Schema for solution response.
///
/// Properties:
/// * [assignmentCount] 
/// * [createdAt] 
/// * [hardViolations] 
/// * [healthScore] 
/// * [id] 
/// * [isPublished] 
/// * [metrics] 
/// * [orgId] 
/// * [publishedAt] 
/// * [softScore] 
/// * [solveMs] 
@BuiltValue()
abstract class SolutionResponse implements Built<SolutionResponse, SolutionResponseBuilder> {
  @BuiltValueField(wireName: r'assignment_count')
  int? get assignmentCount;

  @BuiltValueField(wireName: r'created_at')
  DateTime get createdAt;

  @BuiltValueField(wireName: r'hard_violations')
  int get hardViolations;

  @BuiltValueField(wireName: r'health_score')
  num get healthScore;

  @BuiltValueField(wireName: r'id')
  int get id;

  @BuiltValueField(wireName: r'is_published')
  bool? get isPublished;

  @BuiltValueField(wireName: r'metrics')
  BuiltMap<String, JsonObject?>? get metrics;

  @BuiltValueField(wireName: r'org_id')
  String get orgId;

  @BuiltValueField(wireName: r'published_at')
  DateTime? get publishedAt;

  @BuiltValueField(wireName: r'soft_score')
  num get softScore;

  @BuiltValueField(wireName: r'solve_ms')
  num get solveMs;

  SolutionResponse._();

  factory SolutionResponse([void updates(SolutionResponseBuilder b)]) = _$SolutionResponse;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(SolutionResponseBuilder b) => b
      ..assignmentCount = 0
      ..isPublished = false;

  @BuiltValueSerializer(custom: true)
  static Serializer<SolutionResponse> get serializer => _$SolutionResponseSerializer();
}

class _$SolutionResponseSerializer implements PrimitiveSerializer<SolutionResponse> {
  @override
  final Iterable<Type> types = const [SolutionResponse, _$SolutionResponse];

  @override
  final String wireName = r'SolutionResponse';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    SolutionResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    if (object.assignmentCount != null) {
      yield r'assignment_count';
      yield serializers.serialize(
        object.assignmentCount,
        specifiedType: const FullType(int),
      );
    }
    yield r'created_at';
    yield serializers.serialize(
      object.createdAt,
      specifiedType: const FullType(DateTime),
    );
    yield r'hard_violations';
    yield serializers.serialize(
      object.hardViolations,
      specifiedType: const FullType(int),
    );
    yield r'health_score';
    yield serializers.serialize(
      object.healthScore,
      specifiedType: const FullType(num),
    );
    yield r'id';
    yield serializers.serialize(
      object.id,
      specifiedType: const FullType(int),
    );
    if (object.isPublished != null) {
      yield r'is_published';
      yield serializers.serialize(
        object.isPublished,
        specifiedType: const FullType(bool),
      );
    }
    yield r'metrics';
    yield object.metrics == null ? null : serializers.serialize(
      object.metrics,
      specifiedType: const FullType.nullable(BuiltMap, [FullType(String), FullType.nullable(JsonObject)]),
    );
    yield r'org_id';
    yield serializers.serialize(
      object.orgId,
      specifiedType: const FullType(String),
    );
    if (object.publishedAt != null) {
      yield r'published_at';
      yield serializers.serialize(
        object.publishedAt,
        specifiedType: const FullType.nullable(DateTime),
      );
    }
    yield r'soft_score';
    yield serializers.serialize(
      object.softScore,
      specifiedType: const FullType(num),
    );
    yield r'solve_ms';
    yield serializers.serialize(
      object.solveMs,
      specifiedType: const FullType(num),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    SolutionResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required SolutionResponseBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'assignment_count':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.assignmentCount = valueDes;
          break;
        case r'created_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(DateTime),
          ) as DateTime;
          result.createdAt = valueDes;
          break;
        case r'hard_violations':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.hardViolations = valueDes;
          break;
        case r'health_score':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(num),
          ) as num;
          result.healthScore = valueDes;
          break;
        case r'id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.id = valueDes;
          break;
        case r'is_published':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(bool),
          ) as bool;
          result.isPublished = valueDes;
          break;
        case r'metrics':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(BuiltMap, [FullType(String), FullType.nullable(JsonObject)]),
          ) as BuiltMap<String, JsonObject?>?;
          if (valueDes == null) continue;
          result.metrics.replace(valueDes);
          break;
        case r'org_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.orgId = valueDes;
          break;
        case r'published_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(DateTime),
          ) as DateTime?;
          if (valueDes == null) continue;
          result.publishedAt = valueDes;
          break;
        case r'soft_score':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(num),
          ) as num;
          result.softScore = valueDes;
          break;
        case r'solve_ms':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(num),
          ) as num;
          result.solveMs = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  SolutionResponse deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = SolutionResponseBuilder();
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

