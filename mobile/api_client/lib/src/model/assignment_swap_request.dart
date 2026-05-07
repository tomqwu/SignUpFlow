//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'assignment_swap_request.g.dart';

/// Body for POST /assignments/{id}/swap-request.
///
/// Properties:
/// * [note] 
@BuiltValue()
abstract class AssignmentSwapRequest implements Built<AssignmentSwapRequest, AssignmentSwapRequestBuilder> {
  @BuiltValueField(wireName: r'note')
  String? get note;

  AssignmentSwapRequest._();

  factory AssignmentSwapRequest([void updates(AssignmentSwapRequestBuilder b)]) = _$AssignmentSwapRequest;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(AssignmentSwapRequestBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<AssignmentSwapRequest> get serializer => _$AssignmentSwapRequestSerializer();
}

class _$AssignmentSwapRequestSerializer implements PrimitiveSerializer<AssignmentSwapRequest> {
  @override
  final Iterable<Type> types = const [AssignmentSwapRequest, _$AssignmentSwapRequest];

  @override
  final String wireName = r'AssignmentSwapRequest';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    AssignmentSwapRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    if (object.note != null) {
      yield r'note';
      yield serializers.serialize(
        object.note,
        specifiedType: const FullType.nullable(String),
      );
    }
  }

  @override
  Object serialize(
    Serializers serializers,
    AssignmentSwapRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required AssignmentSwapRequestBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'note':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.note = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  AssignmentSwapRequest deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = AssignmentSwapRequestBuilder();
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

