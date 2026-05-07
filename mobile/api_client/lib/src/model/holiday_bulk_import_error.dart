//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'holiday_bulk_import_error.g.dart';

/// HolidayBulkImportError
///
/// Properties:
/// * [label] 
/// * [message] 
/// * [row] 
@BuiltValue()
abstract class HolidayBulkImportError implements Built<HolidayBulkImportError, HolidayBulkImportErrorBuilder> {
  @BuiltValueField(wireName: r'label')
  String? get label;

  @BuiltValueField(wireName: r'message')
  String get message;

  @BuiltValueField(wireName: r'row')
  int get row;

  HolidayBulkImportError._();

  factory HolidayBulkImportError([void updates(HolidayBulkImportErrorBuilder b)]) = _$HolidayBulkImportError;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(HolidayBulkImportErrorBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<HolidayBulkImportError> get serializer => _$HolidayBulkImportErrorSerializer();
}

class _$HolidayBulkImportErrorSerializer implements PrimitiveSerializer<HolidayBulkImportError> {
  @override
  final Iterable<Type> types = const [HolidayBulkImportError, _$HolidayBulkImportError];

  @override
  final String wireName = r'HolidayBulkImportError';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    HolidayBulkImportError object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'label';
    yield object.label == null ? null : serializers.serialize(
      object.label,
      specifiedType: const FullType.nullable(String),
    );
    yield r'message';
    yield serializers.serialize(
      object.message,
      specifiedType: const FullType(String),
    );
    yield r'row';
    yield serializers.serialize(
      object.row,
      specifiedType: const FullType(int),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    HolidayBulkImportError object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required HolidayBulkImportErrorBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'label':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.label = valueDes;
          break;
        case r'message':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.message = valueDes;
          break;
        case r'row':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.row = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  HolidayBulkImportError deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = HolidayBulkImportErrorBuilder();
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

