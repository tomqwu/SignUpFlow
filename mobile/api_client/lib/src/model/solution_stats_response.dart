//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:signupflow_api/src/model/fairness_stats.dart';
import 'package:signupflow_api/src/model/stability_metrics.dart';
import 'package:signupflow_api/src/model/workload_stats.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'solution_stats_response.g.dart';

/// Stats response for ``GET /solutions/{id}/stats`` (admin only).
///
/// Properties:
/// * [fairness] 
/// * [solutionId] 
/// * [stability] 
/// * [workload] 
@BuiltValue()
abstract class SolutionStatsResponse implements Built<SolutionStatsResponse, SolutionStatsResponseBuilder> {
  @BuiltValueField(wireName: r'fairness')
  FairnessStats get fairness;

  @BuiltValueField(wireName: r'solution_id')
  int get solutionId;

  @BuiltValueField(wireName: r'stability')
  StabilityMetrics get stability;

  @BuiltValueField(wireName: r'workload')
  WorkloadStats get workload;

  SolutionStatsResponse._();

  factory SolutionStatsResponse([void updates(SolutionStatsResponseBuilder b)]) = _$SolutionStatsResponse;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(SolutionStatsResponseBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<SolutionStatsResponse> get serializer => _$SolutionStatsResponseSerializer();
}

class _$SolutionStatsResponseSerializer implements PrimitiveSerializer<SolutionStatsResponse> {
  @override
  final Iterable<Type> types = const [SolutionStatsResponse, _$SolutionStatsResponse];

  @override
  final String wireName = r'SolutionStatsResponse';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    SolutionStatsResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'fairness';
    yield serializers.serialize(
      object.fairness,
      specifiedType: const FullType(FairnessStats),
    );
    yield r'solution_id';
    yield serializers.serialize(
      object.solutionId,
      specifiedType: const FullType(int),
    );
    yield r'stability';
    yield serializers.serialize(
      object.stability,
      specifiedType: const FullType(StabilityMetrics),
    );
    yield r'workload';
    yield serializers.serialize(
      object.workload,
      specifiedType: const FullType(WorkloadStats),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    SolutionStatsResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required SolutionStatsResponseBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'fairness':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(FairnessStats),
          ) as FairnessStats;
          result.fairness.replace(valueDes);
          break;
        case r'solution_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.solutionId = valueDes;
          break;
        case r'stability':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(StabilityMetrics),
          ) as StabilityMetrics;
          result.stability.replace(valueDes);
          break;
        case r'workload':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(WorkloadStats),
          ) as WorkloadStats;
          result.workload.replace(valueDes);
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  SolutionStatsResponse deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = SolutionStatsResponseBuilder();
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

