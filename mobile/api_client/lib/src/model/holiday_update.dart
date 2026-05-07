//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:signupflow_api/src/model/date.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'holiday_update.g.dart';

/// HolidayUpdate
///
/// Properties:
/// * [date] 
/// * [isLongWeekend] 
/// * [label] 
@BuiltValue()
abstract class HolidayUpdate implements Built<HolidayUpdate, HolidayUpdateBuilder> {
  @BuiltValueField(wireName: r'date')
  Date? get date;

  @BuiltValueField(wireName: r'is_long_weekend')
  bool? get isLongWeekend;

  @BuiltValueField(wireName: r'label')
  String? get label;

  HolidayUpdate._();

  factory HolidayUpdate([void updates(HolidayUpdateBuilder b)]) = _$HolidayUpdate;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(HolidayUpdateBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<HolidayUpdate> get serializer => _$HolidayUpdateSerializer();
}

class _$HolidayUpdateSerializer implements PrimitiveSerializer<HolidayUpdate> {
  @override
  final Iterable<Type> types = const [HolidayUpdate, _$HolidayUpdate];

  @override
  final String wireName = r'HolidayUpdate';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    HolidayUpdate object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    if (object.date != null) {
      yield r'date';
      yield serializers.serialize(
        object.date,
        specifiedType: const FullType.nullable(Date),
      );
    }
    if (object.isLongWeekend != null) {
      yield r'is_long_weekend';
      yield serializers.serialize(
        object.isLongWeekend,
        specifiedType: const FullType.nullable(bool),
      );
    }
    if (object.label != null) {
      yield r'label';
      yield serializers.serialize(
        object.label,
        specifiedType: const FullType.nullable(String),
      );
    }
  }

  @override
  Object serialize(
    Serializers serializers,
    HolidayUpdate object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required HolidayUpdateBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'date':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(Date),
          ) as Date?;
          if (valueDes == null) continue;
          result.date = valueDes;
          break;
        case r'is_long_weekend':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(bool),
          ) as bool?;
          if (valueDes == null) continue;
          result.isLongWeekend = valueDes;
          break;
        case r'label':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.label = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  HolidayUpdate deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = HolidayUpdateBuilder();
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

