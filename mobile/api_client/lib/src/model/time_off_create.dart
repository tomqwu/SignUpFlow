//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:signupflow_api/src/model/date.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'time_off_create.g.dart';

/// Schema for creating time-off period.
///
/// Properties:
/// * [endDate] - End date of time-off
/// * [reason] 
/// * [startDate] - Start date of time-off
@BuiltValue()
abstract class TimeOffCreate implements Built<TimeOffCreate, TimeOffCreateBuilder> {
  /// End date of time-off
  @BuiltValueField(wireName: r'end_date')
  Date get endDate;

  @BuiltValueField(wireName: r'reason')
  String? get reason;

  /// Start date of time-off
  @BuiltValueField(wireName: r'start_date')
  Date get startDate;

  TimeOffCreate._();

  factory TimeOffCreate([void updates(TimeOffCreateBuilder b)]) = _$TimeOffCreate;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(TimeOffCreateBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<TimeOffCreate> get serializer => _$TimeOffCreateSerializer();
}

class _$TimeOffCreateSerializer implements PrimitiveSerializer<TimeOffCreate> {
  @override
  final Iterable<Type> types = const [TimeOffCreate, _$TimeOffCreate];

  @override
  final String wireName = r'TimeOffCreate';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    TimeOffCreate object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'end_date';
    yield serializers.serialize(
      object.endDate,
      specifiedType: const FullType(Date),
    );
    if (object.reason != null) {
      yield r'reason';
      yield serializers.serialize(
        object.reason,
        specifiedType: const FullType.nullable(String),
      );
    }
    yield r'start_date';
    yield serializers.serialize(
      object.startDate,
      specifiedType: const FullType(Date),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    TimeOffCreate object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required TimeOffCreateBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'end_date':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(Date),
          ) as Date;
          result.endDate = valueDes;
          break;
        case r'reason':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.reason = valueDes;
          break;
        case r'start_date':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(Date),
          ) as Date;
          result.startDate = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  TimeOffCreate deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = TimeOffCreateBuilder();
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

