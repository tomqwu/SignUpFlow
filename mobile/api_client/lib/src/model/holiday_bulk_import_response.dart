//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:signupflow_api/src/model/holiday_bulk_import_error.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'holiday_bulk_import_response.g.dart';

/// HolidayBulkImportResponse
///
/// Properties:
/// * [created] 
/// * [errors] 
/// * [skipped] 
@BuiltValue()
abstract class HolidayBulkImportResponse implements Built<HolidayBulkImportResponse, HolidayBulkImportResponseBuilder> {
  @BuiltValueField(wireName: r'created')
  int get created;

  @BuiltValueField(wireName: r'errors')
  BuiltList<HolidayBulkImportError>? get errors;

  @BuiltValueField(wireName: r'skipped')
  int get skipped;

  HolidayBulkImportResponse._();

  factory HolidayBulkImportResponse([void updates(HolidayBulkImportResponseBuilder b)]) = _$HolidayBulkImportResponse;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(HolidayBulkImportResponseBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<HolidayBulkImportResponse> get serializer => _$HolidayBulkImportResponseSerializer();
}

class _$HolidayBulkImportResponseSerializer implements PrimitiveSerializer<HolidayBulkImportResponse> {
  @override
  final Iterable<Type> types = const [HolidayBulkImportResponse, _$HolidayBulkImportResponse];

  @override
  final String wireName = r'HolidayBulkImportResponse';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    HolidayBulkImportResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'created';
    yield serializers.serialize(
      object.created,
      specifiedType: const FullType(int),
    );
    if (object.errors != null) {
      yield r'errors';
      yield serializers.serialize(
        object.errors,
        specifiedType: const FullType(BuiltList, [FullType(HolidayBulkImportError)]),
      );
    }
    yield r'skipped';
    yield serializers.serialize(
      object.skipped,
      specifiedType: const FullType(int),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    HolidayBulkImportResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required HolidayBulkImportResponseBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'created':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.created = valueDes;
          break;
        case r'errors':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(HolidayBulkImportError)]),
          ) as BuiltList<HolidayBulkImportError>;
          result.errors.replace(valueDes);
          break;
        case r'skipped':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.skipped = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  HolidayBulkImportResponse deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = HolidayBulkImportResponseBuilder();
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

