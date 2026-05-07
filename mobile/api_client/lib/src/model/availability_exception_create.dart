//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:signupflow_api/src/model/date.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'availability_exception_create.g.dart';

/// Schema for adding a single-date availability exception.
///
/// Properties:
/// * [exceptionDate] - Single date the volunteer is blocked
@BuiltValue()
abstract class AvailabilityExceptionCreate implements Built<AvailabilityExceptionCreate, AvailabilityExceptionCreateBuilder> {
  /// Single date the volunteer is blocked
  @BuiltValueField(wireName: r'exception_date')
  Date get exceptionDate;

  AvailabilityExceptionCreate._();

  factory AvailabilityExceptionCreate([void updates(AvailabilityExceptionCreateBuilder b)]) = _$AvailabilityExceptionCreate;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(AvailabilityExceptionCreateBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<AvailabilityExceptionCreate> get serializer => _$AvailabilityExceptionCreateSerializer();
}

class _$AvailabilityExceptionCreateSerializer implements PrimitiveSerializer<AvailabilityExceptionCreate> {
  @override
  final Iterable<Type> types = const [AvailabilityExceptionCreate, _$AvailabilityExceptionCreate];

  @override
  final String wireName = r'AvailabilityExceptionCreate';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    AvailabilityExceptionCreate object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'exception_date';
    yield serializers.serialize(
      object.exceptionDate,
      specifiedType: const FullType(Date),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    AvailabilityExceptionCreate object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required AvailabilityExceptionCreateBuilder result,
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
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  AvailabilityExceptionCreate deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = AvailabilityExceptionCreateBuilder();
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

