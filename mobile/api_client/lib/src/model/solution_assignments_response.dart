//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:signupflow_api/src/model/solution_assignment_entry.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'solution_assignments_response.g.dart';

/// Typed response for ``GET /solutions/{id}/assignments`` — events grouped.
///
/// Properties:
/// * [events] 
/// * [solutionId] 
/// * [totalAssignments] 
@BuiltValue()
abstract class SolutionAssignmentsResponse implements Built<SolutionAssignmentsResponse, SolutionAssignmentsResponseBuilder> {
  @BuiltValueField(wireName: r'events')
  BuiltList<SolutionAssignmentEntry> get events;

  @BuiltValueField(wireName: r'solution_id')
  int get solutionId;

  @BuiltValueField(wireName: r'total_assignments')
  int get totalAssignments;

  SolutionAssignmentsResponse._();

  factory SolutionAssignmentsResponse([void updates(SolutionAssignmentsResponseBuilder b)]) = _$SolutionAssignmentsResponse;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(SolutionAssignmentsResponseBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<SolutionAssignmentsResponse> get serializer => _$SolutionAssignmentsResponseSerializer();
}

class _$SolutionAssignmentsResponseSerializer implements PrimitiveSerializer<SolutionAssignmentsResponse> {
  @override
  final Iterable<Type> types = const [SolutionAssignmentsResponse, _$SolutionAssignmentsResponse];

  @override
  final String wireName = r'SolutionAssignmentsResponse';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    SolutionAssignmentsResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'events';
    yield serializers.serialize(
      object.events,
      specifiedType: const FullType(BuiltList, [FullType(SolutionAssignmentEntry)]),
    );
    yield r'solution_id';
    yield serializers.serialize(
      object.solutionId,
      specifiedType: const FullType(int),
    );
    yield r'total_assignments';
    yield serializers.serialize(
      object.totalAssignments,
      specifiedType: const FullType(int),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    SolutionAssignmentsResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required SolutionAssignmentsResponseBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'events':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(SolutionAssignmentEntry)]),
          ) as BuiltList<SolutionAssignmentEntry>;
          result.events.replace(valueDes);
          break;
        case r'solution_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.solutionId = valueDes;
          break;
        case r'total_assignments':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.totalAssignments = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  SolutionAssignmentsResponse deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = SolutionAssignmentsResponseBuilder();
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

