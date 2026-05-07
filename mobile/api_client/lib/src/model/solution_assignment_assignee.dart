//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'solution_assignment_assignee.g.dart';

/// One assignee inside a per-event assignment group.
///
/// Properties:
/// * [assignedAt] 
/// * [assignmentId] 
/// * [personId] 
/// * [personName] 
@BuiltValue()
abstract class SolutionAssignmentAssignee implements Built<SolutionAssignmentAssignee, SolutionAssignmentAssigneeBuilder> {
  @BuiltValueField(wireName: r'assigned_at')
  DateTime? get assignedAt;

  @BuiltValueField(wireName: r'assignment_id')
  int get assignmentId;

  @BuiltValueField(wireName: r'person_id')
  String get personId;

  @BuiltValueField(wireName: r'person_name')
  String? get personName;

  SolutionAssignmentAssignee._();

  factory SolutionAssignmentAssignee([void updates(SolutionAssignmentAssigneeBuilder b)]) = _$SolutionAssignmentAssignee;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(SolutionAssignmentAssigneeBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<SolutionAssignmentAssignee> get serializer => _$SolutionAssignmentAssigneeSerializer();
}

class _$SolutionAssignmentAssigneeSerializer implements PrimitiveSerializer<SolutionAssignmentAssignee> {
  @override
  final Iterable<Type> types = const [SolutionAssignmentAssignee, _$SolutionAssignmentAssignee];

  @override
  final String wireName = r'SolutionAssignmentAssignee';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    SolutionAssignmentAssignee object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    if (object.assignedAt != null) {
      yield r'assigned_at';
      yield serializers.serialize(
        object.assignedAt,
        specifiedType: const FullType.nullable(DateTime),
      );
    }
    yield r'assignment_id';
    yield serializers.serialize(
      object.assignmentId,
      specifiedType: const FullType(int),
    );
    yield r'person_id';
    yield serializers.serialize(
      object.personId,
      specifiedType: const FullType(String),
    );
    if (object.personName != null) {
      yield r'person_name';
      yield serializers.serialize(
        object.personName,
        specifiedType: const FullType.nullable(String),
      );
    }
  }

  @override
  Object serialize(
    Serializers serializers,
    SolutionAssignmentAssignee object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required SolutionAssignmentAssigneeBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'assigned_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(DateTime),
          ) as DateTime?;
          if (valueDes == null) continue;
          result.assignedAt = valueDes;
          break;
        case r'assignment_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.assignmentId = valueDes;
          break;
        case r'person_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.personId = valueDes;
          break;
        case r'person_name':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.personName = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  SolutionAssignmentAssignee deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = SolutionAssignmentAssigneeBuilder();
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

