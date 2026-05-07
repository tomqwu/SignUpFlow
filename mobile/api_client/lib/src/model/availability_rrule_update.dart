//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'availability_rrule_update.g.dart';

/// Schema for setting the rrule string.
///
/// Properties:
/// * [rrule] - iCalendar RRULE expression
@BuiltValue()
abstract class AvailabilityRruleUpdate implements Built<AvailabilityRruleUpdate, AvailabilityRruleUpdateBuilder> {
  /// iCalendar RRULE expression
  @BuiltValueField(wireName: r'rrule')
  String get rrule;

  AvailabilityRruleUpdate._();

  factory AvailabilityRruleUpdate([void updates(AvailabilityRruleUpdateBuilder b)]) = _$AvailabilityRruleUpdate;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(AvailabilityRruleUpdateBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<AvailabilityRruleUpdate> get serializer => _$AvailabilityRruleUpdateSerializer();
}

class _$AvailabilityRruleUpdateSerializer implements PrimitiveSerializer<AvailabilityRruleUpdate> {
  @override
  final Iterable<Type> types = const [AvailabilityRruleUpdate, _$AvailabilityRruleUpdate];

  @override
  final String wireName = r'AvailabilityRruleUpdate';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    AvailabilityRruleUpdate object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'rrule';
    yield serializers.serialize(
      object.rrule,
      specifiedType: const FullType(String),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    AvailabilityRruleUpdate object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required AvailabilityRruleUpdateBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'rrule':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
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
  AvailabilityRruleUpdate deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = AvailabilityRruleUpdateBuilder();
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

