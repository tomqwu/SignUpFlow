//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:signupflow_api/src/model/date.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'holiday_create.g.dart';

/// HolidayCreate
///
/// Properties:
/// * [date] 
/// * [isLongWeekend] 
/// * [label] 
/// * [orgId] - Organization ID
@BuiltValue()
abstract class HolidayCreate implements Built<HolidayCreate, HolidayCreateBuilder> {
  @BuiltValueField(wireName: r'date')
  Date get date;

  @BuiltValueField(wireName: r'is_long_weekend')
  bool? get isLongWeekend;

  @BuiltValueField(wireName: r'label')
  String get label;

  /// Organization ID
  @BuiltValueField(wireName: r'org_id')
  String get orgId;

  HolidayCreate._();

  factory HolidayCreate([void updates(HolidayCreateBuilder b)]) = _$HolidayCreate;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(HolidayCreateBuilder b) => b
      ..isLongWeekend = false;

  @BuiltValueSerializer(custom: true)
  static Serializer<HolidayCreate> get serializer => _$HolidayCreateSerializer();
}

class _$HolidayCreateSerializer implements PrimitiveSerializer<HolidayCreate> {
  @override
  final Iterable<Type> types = const [HolidayCreate, _$HolidayCreate];

  @override
  final String wireName = r'HolidayCreate';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    HolidayCreate object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'date';
    yield serializers.serialize(
      object.date,
      specifiedType: const FullType(Date),
    );
    if (object.isLongWeekend != null) {
      yield r'is_long_weekend';
      yield serializers.serialize(
        object.isLongWeekend,
        specifiedType: const FullType(bool),
      );
    }
    yield r'label';
    yield serializers.serialize(
      object.label,
      specifiedType: const FullType(String),
    );
    yield r'org_id';
    yield serializers.serialize(
      object.orgId,
      specifiedType: const FullType(String),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    HolidayCreate object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required HolidayCreateBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'date':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(Date),
          ) as Date;
          result.date = valueDes;
          break;
        case r'is_long_weekend':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(bool),
          ) as bool;
          result.isLongWeekend = valueDes;
          break;
        case r'label':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.label = valueDes;
          break;
        case r'org_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.orgId = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  HolidayCreate deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = HolidayCreateBuilder();
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

