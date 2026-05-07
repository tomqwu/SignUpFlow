//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'assignment_response.g.dart';

/// Single-assignment response shape returned by self-service mutations.
///
/// Properties:
/// * [assignedAt] 
/// * [declineReason] 
/// * [eventId] 
/// * [id] 
/// * [personId] 
/// * [role] 
/// * [status] 
@BuiltValue()
abstract class AssignmentResponse implements Built<AssignmentResponse, AssignmentResponseBuilder> {
  @BuiltValueField(wireName: r'assigned_at')
  DateTime get assignedAt;

  @BuiltValueField(wireName: r'decline_reason')
  String? get declineReason;

  @BuiltValueField(wireName: r'event_id')
  String get eventId;

  @BuiltValueField(wireName: r'id')
  int get id;

  @BuiltValueField(wireName: r'person_id')
  String get personId;

  @BuiltValueField(wireName: r'role')
  String? get role;

  @BuiltValueField(wireName: r'status')
  String get status;

  AssignmentResponse._();

  factory AssignmentResponse([void updates(AssignmentResponseBuilder b)]) = _$AssignmentResponse;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(AssignmentResponseBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<AssignmentResponse> get serializer => _$AssignmentResponseSerializer();
}

class _$AssignmentResponseSerializer implements PrimitiveSerializer<AssignmentResponse> {
  @override
  final Iterable<Type> types = const [AssignmentResponse, _$AssignmentResponse];

  @override
  final String wireName = r'AssignmentResponse';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    AssignmentResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'assigned_at';
    yield serializers.serialize(
      object.assignedAt,
      specifiedType: const FullType(DateTime),
    );
    yield r'decline_reason';
    yield object.declineReason == null ? null : serializers.serialize(
      object.declineReason,
      specifiedType: const FullType.nullable(String),
    );
    yield r'event_id';
    yield serializers.serialize(
      object.eventId,
      specifiedType: const FullType(String),
    );
    yield r'id';
    yield serializers.serialize(
      object.id,
      specifiedType: const FullType(int),
    );
    yield r'person_id';
    yield serializers.serialize(
      object.personId,
      specifiedType: const FullType(String),
    );
    yield r'role';
    yield object.role == null ? null : serializers.serialize(
      object.role,
      specifiedType: const FullType.nullable(String),
    );
    yield r'status';
    yield serializers.serialize(
      object.status,
      specifiedType: const FullType(String),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    AssignmentResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required AssignmentResponseBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'assigned_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(DateTime),
          ) as DateTime;
          result.assignedAt = valueDes;
          break;
        case r'decline_reason':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.declineReason = valueDes;
          break;
        case r'event_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.eventId = valueDes;
          break;
        case r'id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.id = valueDes;
          break;
        case r'person_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.personId = valueDes;
          break;
        case r'role':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.role = valueDes;
          break;
        case r'status':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.status = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  AssignmentResponse deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = AssignmentResponseBuilder();
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

