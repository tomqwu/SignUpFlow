//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'availability_rrule_response.g.dart';

/// Schema for the single rrule string per person.
///
/// Properties:
/// * [rrule] 
@BuiltValue()
abstract class AvailabilityRruleResponse implements Built<AvailabilityRruleResponse, AvailabilityRruleResponseBuilder> {
  @BuiltValueField(wireName: r'rrule')
  String? get rrule;

  AvailabilityRruleResponse._();

  factory AvailabilityRruleResponse([void updates(AvailabilityRruleResponseBuilder b)]) = _$AvailabilityRruleResponse;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(AvailabilityRruleResponseBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<AvailabilityRruleResponse> get serializer => _$AvailabilityRruleResponseSerializer();
}

class _$AvailabilityRruleResponseSerializer implements PrimitiveSerializer<AvailabilityRruleResponse> {
  @override
  final Iterable<Type> types = const [AvailabilityRruleResponse, _$AvailabilityRruleResponse];

  @override
  final String wireName = r'AvailabilityRruleResponse';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    AvailabilityRruleResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'rrule';
    yield object.rrule == null ? null : serializers.serialize(
      object.rrule,
      specifiedType: const FullType.nullable(String),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    AvailabilityRruleResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required AvailabilityRruleResponseBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'rrule':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.rrule = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  AvailabilityRruleResponse deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = AvailabilityRruleResponseBuilder();
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

