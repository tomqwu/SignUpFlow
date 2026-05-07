//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:signupflow_api/src/model/fairness_metrics.dart';
import 'package:signupflow_api/src/model/stability_metrics.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'solution_metrics.g.dart';

/// Schema for solution metrics.
///
/// Properties:
/// * [fairness] 
/// * [hardViolations] 
/// * [healthScore] 
/// * [softScore] 
/// * [solveMs] 
/// * [stability] 
@BuiltValue()
abstract class SolutionMetrics implements Built<SolutionMetrics, SolutionMetricsBuilder> {
  @BuiltValueField(wireName: r'fairness')
  FairnessMetrics get fairness;

  @BuiltValueField(wireName: r'hard_violations')
  int get hardViolations;

  @BuiltValueField(wireName: r'health_score')
  num get healthScore;

  @BuiltValueField(wireName: r'soft_score')
  num get softScore;

  @BuiltValueField(wireName: r'solve_ms')
  num get solveMs;

  @BuiltValueField(wireName: r'stability')
  StabilityMetrics? get stability;

  SolutionMetrics._();

  factory SolutionMetrics([void updates(SolutionMetricsBuilder b)]) = _$SolutionMetrics;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(SolutionMetricsBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<SolutionMetrics> get serializer => _$SolutionMetricsSerializer();
}

class _$SolutionMetricsSerializer implements PrimitiveSerializer<SolutionMetrics> {
  @override
  final Iterable<Type> types = const [SolutionMetrics, _$SolutionMetrics];

  @override
  final String wireName = r'SolutionMetrics';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    SolutionMetrics object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'fairness';
    yield serializers.serialize(
      object.fairness,
      specifiedType: const FullType(FairnessMetrics),
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
    if (object.stability != null) {
      yield r'stability';
      yield serializers.serialize(
        object.stability,
        specifiedType: const FullType(StabilityMetrics),
      );
    }
  }

  @override
  Object serialize(
    Serializers serializers,
    SolutionMetrics object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required SolutionMetricsBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'fairness':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(FairnessMetrics),
          ) as FairnessMetrics;
          result.fairness.replace(valueDes);
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
        case r'stability':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(StabilityMetrics),
          ) as StabilityMetrics;
          result.stability.replace(valueDes);
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  SolutionMetrics deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = SolutionMetricsBuilder();
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

