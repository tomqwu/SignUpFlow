//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:signupflow_api/src/model/date.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'holiday_bulk_import_item.g.dart';

/// One item in a holiday bulk-import payload (no `id`; assigned by DB).
///
/// Properties:
/// * [date] 
/// * [isLongWeekend] 
/// * [label] 
@BuiltValue()
abstract class HolidayBulkImportItem implements Built<HolidayBulkImportItem, HolidayBulkImportItemBuilder> {
  @BuiltValueField(wireName: r'date')
  Date get date;

  @BuiltValueField(wireName: r'is_long_weekend')
  bool? get isLongWeekend;

  @BuiltValueField(wireName: r'label')
  String get label;

  HolidayBulkImportItem._();

  factory HolidayBulkImportItem([void updates(HolidayBulkImportItemBuilder b)]) = _$HolidayBulkImportItem;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(HolidayBulkImportItemBuilder b) => b
      ..isLongWeekend = false;

  @BuiltValueSerializer(custom: true)
  static Serializer<HolidayBulkImportItem> get serializer => _$HolidayBulkImportItemSerializer();
}

class _$HolidayBulkImportItemSerializer implements PrimitiveSerializer<HolidayBulkImportItem> {
  @override
  final Iterable<Type> types = const [HolidayBulkImportItem, _$HolidayBulkImportItem];

  @override
  final String wireName = r'HolidayBulkImportItem';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    HolidayBulkImportItem object, {
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
  }

  @override
  Object serialize(
    Serializers serializers,
    HolidayBulkImportItem object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required HolidayBulkImportItemBuilder result,
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
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  HolidayBulkImportItem deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = HolidayBulkImportItemBuilder();
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

