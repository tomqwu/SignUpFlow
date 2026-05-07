//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:signupflow_api/src/model/date.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'availability_exception_response.g.dart';

/// Schema for an availability exception row.
///
/// Properties:
/// * [exceptionDate] 
/// * [id] 
@BuiltValue()
abstract class AvailabilityExceptionResponse implements Built<AvailabilityExceptionResponse, AvailabilityExceptionResponseBuilder> {
  @BuiltValueField(wireName: r'exception_date')
  Date get exceptionDate;

  @BuiltValueField(wireName: r'id')
  int get id;

  AvailabilityExceptionResponse._();

  factory AvailabilityExceptionResponse([void updates(AvailabilityExceptionResponseBuilder b)]) = _$AvailabilityExceptionResponse;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(AvailabilityExceptionResponseBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<AvailabilityExceptionResponse> get serializer => _$AvailabilityExceptionResponseSerializer();
}

class _$AvailabilityExceptionResponseSerializer implements PrimitiveSerializer<AvailabilityExceptionResponse> {
  @override
  final Iterable<Type> types = const [AvailabilityExceptionResponse, _$AvailabilityExceptionResponse];

  @override
  final String wireName = r'AvailabilityExceptionResponse';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    AvailabilityExceptionResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'exception_date';
    yield serializers.serialize(
      object.exceptionDate,
      specifiedType: const FullType(Date),
    );
    yield r'id';
    yield serializers.serialize(
      object.id,
      specifiedType: const FullType(int),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    AvailabilityExceptionResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required AvailabilityExceptionResponseBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'exception_date':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(Date),
          ) as Date;
          result.exceptionDate = valueDes;
          break;
        case r'id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.id = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  AvailabilityExceptionResponse deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = AvailabilityExceptionResponseBuilder();
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

