//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:signupflow_api/src/model/holiday_bulk_import_item.dart';
import 'package:built_collection/built_collection.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'holiday_bulk_import.g.dart';

/// HolidayBulkImport
///
/// Properties:
/// * [items] - Holidays to create (1-500 rows)
@BuiltValue()
abstract class HolidayBulkImport implements Built<HolidayBulkImport, HolidayBulkImportBuilder> {
  /// Holidays to create (1-500 rows)
  @BuiltValueField(wireName: r'items')
  BuiltList<HolidayBulkImportItem> get items;

  HolidayBulkImport._();

  factory HolidayBulkImport([void updates(HolidayBulkImportBuilder b)]) = _$HolidayBulkImport;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(HolidayBulkImportBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<HolidayBulkImport> get serializer => _$HolidayBulkImportSerializer();
}

class _$HolidayBulkImportSerializer implements PrimitiveSerializer<HolidayBulkImport> {
  @override
  final Iterable<Type> types = const [HolidayBulkImport, _$HolidayBulkImport];

  @override
  final String wireName = r'HolidayBulkImport';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    HolidayBulkImport object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'items';
    yield serializers.serialize(
      object.items,
      specifiedType: const FullType(BuiltList, [FullType(HolidayBulkImportItem)]),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    HolidayBulkImport object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required HolidayBulkImportBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'items':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(HolidayBulkImportItem)]),
          ) as BuiltList<HolidayBulkImportItem>;
          result.items.replace(valueDes);
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  HolidayBulkImport deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = HolidayBulkImportBuilder();
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

