//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:signupflow_api/src/model/violation_info.dart';
import 'package:signupflow_api/src/model/solution_metrics.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'solve_response.g.dart';

/// Schema for solve response.
///
/// Properties:
/// * [assignmentCount] 
/// * [message] 
/// * [metrics] 
/// * [solutionId] - Database ID of saved solution
/// * [violations] 
@BuiltValue()
abstract class SolveResponse implements Built<SolveResponse, SolveResponseBuilder> {
  @BuiltValueField(wireName: r'assignment_count')
  int get assignmentCount;

  @BuiltValueField(wireName: r'message')
  String get message;

  @BuiltValueField(wireName: r'metrics')
  SolutionMetrics get metrics;

  /// Database ID of saved solution
  @BuiltValueField(wireName: r'solution_id')
  int get solutionId;

  @BuiltValueField(wireName: r'violations')
  BuiltList<ViolationInfo> get violations;

  SolveResponse._();

  factory SolveResponse([void updates(SolveResponseBuilder b)]) = _$SolveResponse;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(SolveResponseBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<SolveResponse> get serializer => _$SolveResponseSerializer();
}

class _$SolveResponseSerializer implements PrimitiveSerializer<SolveResponse> {
  @override
  final Iterable<Type> types = const [SolveResponse, _$SolveResponse];

  @override
  final String wireName = r'SolveResponse';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    SolveResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'assignment_count';
    yield serializers.serialize(
      object.assignmentCount,
      specifiedType: const FullType(int),
    );
    yield r'message';
    yield serializers.serialize(
      object.message,
      specifiedType: const FullType(String),
    );
    yield r'metrics';
    yield serializers.serialize(
      object.metrics,
      specifiedType: const FullType(SolutionMetrics),
    );
    yield r'solution_id';
    yield serializers.serialize(
      object.solutionId,
      specifiedType: const FullType(int),
    );
    yield r'violations';
    yield serializers.serialize(
      object.violations,
      specifiedType: const FullType(BuiltList, [FullType(ViolationInfo)]),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    SolveResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required SolveResponseBuilder result,
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
        case r'message':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.message = valueDes;
          break;
        case r'metrics':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(SolutionMetrics),
          ) as SolutionMetrics;
          result.metrics.replace(valueDes);
          break;
        case r'solution_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.solutionId = valueDes;
          break;
        case r'violations':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(ViolationInfo)]),
          ) as BuiltList<ViolationInfo>;
          result.violations.replace(valueDes);
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  SolveResponse deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = SolveResponseBuilder();
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

