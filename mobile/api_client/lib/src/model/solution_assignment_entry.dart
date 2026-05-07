//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:signupflow_api/src/model/solution_assignment_assignee.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'solution_assignment_entry.g.dart';

/// All assignees for one event in a solution.
///
/// Properties:
/// * [assignees] 
/// * [eventEnd] 
/// * [eventId] 
/// * [eventStart] 
/// * [eventType] 
@BuiltValue()
abstract class SolutionAssignmentEntry implements Built<SolutionAssignmentEntry, SolutionAssignmentEntryBuilder> {
  @BuiltValueField(wireName: r'assignees')
  BuiltList<SolutionAssignmentAssignee> get assignees;

  @BuiltValueField(wireName: r'event_end')
  DateTime? get eventEnd;

  @BuiltValueField(wireName: r'event_id')
  String get eventId;

  @BuiltValueField(wireName: r'event_start')
  DateTime? get eventStart;

  @BuiltValueField(wireName: r'event_type')
  String? get eventType;

  SolutionAssignmentEntry._();

  factory SolutionAssignmentEntry([void updates(SolutionAssignmentEntryBuilder b)]) = _$SolutionAssignmentEntry;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(SolutionAssignmentEntryBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<SolutionAssignmentEntry> get serializer => _$SolutionAssignmentEntrySerializer();
}

class _$SolutionAssignmentEntrySerializer implements PrimitiveSerializer<SolutionAssignmentEntry> {
  @override
  final Iterable<Type> types = const [SolutionAssignmentEntry, _$SolutionAssignmentEntry];

  @override
  final String wireName = r'SolutionAssignmentEntry';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    SolutionAssignmentEntry object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'assignees';
    yield serializers.serialize(
      object.assignees,
      specifiedType: const FullType(BuiltList, [FullType(SolutionAssignmentAssignee)]),
    );
    if (object.eventEnd != null) {
      yield r'event_end';
      yield serializers.serialize(
        object.eventEnd,
        specifiedType: const FullType.nullable(DateTime),
      );
    }
    yield r'event_id';
    yield serializers.serialize(
      object.eventId,
      specifiedType: const FullType(String),
    );
    if (object.eventStart != null) {
      yield r'event_start';
      yield serializers.serialize(
        object.eventStart,
        specifiedType: const FullType.nullable(DateTime),
      );
    }
    if (object.eventType != null) {
      yield r'event_type';
      yield serializers.serialize(
        object.eventType,
        specifiedType: const FullType.nullable(String),
      );
    }
  }

  @override
  Object serialize(
    Serializers serializers,
    SolutionAssignmentEntry object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required SolutionAssignmentEntryBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'assignees':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(SolutionAssignmentAssignee)]),
          ) as BuiltList<SolutionAssignmentAssignee>;
          result.assignees.replace(valueDes);
          break;
        case r'event_end':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(DateTime),
          ) as DateTime?;
          if (valueDes == null) continue;
          result.eventEnd = valueDes;
          break;
        case r'event_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.eventId = valueDes;
          break;
        case r'event_start':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(DateTime),
          ) as DateTime?;
          if (valueDes == null) continue;
          result.eventStart = valueDes;
          break;
        case r'event_type':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.eventType = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  SolutionAssignmentEntry deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = SolutionAssignmentEntryBuilder();
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

