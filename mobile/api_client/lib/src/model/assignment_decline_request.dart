//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'assignment_decline_request.g.dart';

/// Body for POST /assignments/{id}/decline.
///
/// Properties:
/// * [declineReason] 
@BuiltValue()
abstract class AssignmentDeclineRequest implements Built<AssignmentDeclineRequest, AssignmentDeclineRequestBuilder> {
  @BuiltValueField(wireName: r'decline_reason')
  String get declineReason;

  AssignmentDeclineRequest._();

  factory AssignmentDeclineRequest([void updates(AssignmentDeclineRequestBuilder b)]) = _$AssignmentDeclineRequest;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(AssignmentDeclineRequestBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<AssignmentDeclineRequest> get serializer => _$AssignmentDeclineRequestSerializer();
}

class _$AssignmentDeclineRequestSerializer implements PrimitiveSerializer<AssignmentDeclineRequest> {
  @override
  final Iterable<Type> types = const [AssignmentDeclineRequest, _$AssignmentDeclineRequest];

  @override
  final String wireName = r'AssignmentDeclineRequest';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    AssignmentDeclineRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'decline_reason';
    yield serializers.serialize(
      object.declineReason,
      specifiedType: const FullType(String),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    AssignmentDeclineRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required AssignmentDeclineRequestBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'decline_reason':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.declineReason = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  AssignmentDeclineRequest deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = AssignmentDeclineRequestBuilder();
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

