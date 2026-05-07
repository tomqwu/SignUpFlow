//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:signupflow_api/src/model/assignment_change.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'solution_diff_response.g.dart';

/// Diff between two solutions in the same org.
///
/// Properties:
/// * [added] 
/// * [affectedPersons] 
/// * [moves] 
/// * [removed] 
/// * [solutionAId] 
/// * [solutionBId] 
/// * [unchangedCount] 
@BuiltValue()
abstract class SolutionDiffResponse implements Built<SolutionDiffResponse, SolutionDiffResponseBuilder> {
  @BuiltValueField(wireName: r'added')
  BuiltList<AssignmentChange> get added;

  @BuiltValueField(wireName: r'affected_persons')
  BuiltList<String> get affectedPersons;

  @BuiltValueField(wireName: r'moves')
  int get moves;

  @BuiltValueField(wireName: r'removed')
  BuiltList<AssignmentChange> get removed;

  @BuiltValueField(wireName: r'solution_a_id')
  int get solutionAId;

  @BuiltValueField(wireName: r'solution_b_id')
  int get solutionBId;

  @BuiltValueField(wireName: r'unchanged_count')
  int get unchangedCount;

  SolutionDiffResponse._();

  factory SolutionDiffResponse([void updates(SolutionDiffResponseBuilder b)]) = _$SolutionDiffResponse;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(SolutionDiffResponseBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<SolutionDiffResponse> get serializer => _$SolutionDiffResponseSerializer();
}

class _$SolutionDiffResponseSerializer implements PrimitiveSerializer<SolutionDiffResponse> {
  @override
  final Iterable<Type> types = const [SolutionDiffResponse, _$SolutionDiffResponse];

  @override
  final String wireName = r'SolutionDiffResponse';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    SolutionDiffResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'added';
    yield serializers.serialize(
      object.added,
      specifiedType: const FullType(BuiltList, [FullType(AssignmentChange)]),
    );
    yield r'affected_persons';
    yield serializers.serialize(
      object.affectedPersons,
      specifiedType: const FullType(BuiltList, [FullType(String)]),
    );
    yield r'moves';
    yield serializers.serialize(
      object.moves,
      specifiedType: const FullType(int),
    );
    yield r'removed';
    yield serializers.serialize(
      object.removed,
      specifiedType: const FullType(BuiltList, [FullType(AssignmentChange)]),
    );
    yield r'solution_a_id';
    yield serializers.serialize(
      object.solutionAId,
      specifiedType: const FullType(int),
    );
    yield r'solution_b_id';
    yield serializers.serialize(
      object.solutionBId,
      specifiedType: const FullType(int),
    );
    yield r'unchanged_count';
    yield serializers.serialize(
      object.unchangedCount,
      specifiedType: const FullType(int),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    SolutionDiffResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required SolutionDiffResponseBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'added':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(AssignmentChange)]),
          ) as BuiltList<AssignmentChange>;
          result.added.replace(valueDes);
          break;
        case r'affected_persons':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(String)]),
          ) as BuiltList<String>;
          result.affectedPersons.replace(valueDes);
          break;
        case r'moves':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.moves = valueDes;
          break;
        case r'removed':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(AssignmentChange)]),
          ) as BuiltList<AssignmentChange>;
          result.removed.replace(valueDes);
          break;
        case r'solution_a_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.solutionAId = valueDes;
          break;
        case r'solution_b_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.solutionBId = valueDes;
          break;
        case r'unchanged_count':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.unchangedCount = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  SolutionDiffResponse deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = SolutionDiffResponseBuilder();
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

