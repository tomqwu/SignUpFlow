//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:signupflow_api/src/model/bulk_import_item_error.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'bulk_import_response.g.dart';

/// Result of a bulk people import request.
///
/// Properties:
/// * [created] 
/// * [errors] 
/// * [skipped] 
@BuiltValue()
abstract class BulkImportResponse implements Built<BulkImportResponse, BulkImportResponseBuilder> {
  @BuiltValueField(wireName: r'created')
  int get created;

  @BuiltValueField(wireName: r'errors')
  BuiltList<BulkImportItemError> get errors;

  @BuiltValueField(wireName: r'skipped')
  int get skipped;

  BulkImportResponse._();

  factory BulkImportResponse([void updates(BulkImportResponseBuilder b)]) = _$BulkImportResponse;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(BulkImportResponseBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<BulkImportResponse> get serializer => _$BulkImportResponseSerializer();
}

class _$BulkImportResponseSerializer implements PrimitiveSerializer<BulkImportResponse> {
  @override
  final Iterable<Type> types = const [BulkImportResponse, _$BulkImportResponse];

  @override
  final String wireName = r'BulkImportResponse';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    BulkImportResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'created';
    yield serializers.serialize(
      object.created,
      specifiedType: const FullType(int),
    );
    yield r'errors';
    yield serializers.serialize(
      object.errors,
      specifiedType: const FullType(BuiltList, [FullType(BulkImportItemError)]),
    );
    yield r'skipped';
    yield serializers.serialize(
      object.skipped,
      specifiedType: const FullType(int),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    BulkImportResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required BulkImportResponseBuilder result,
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
            specifiedType: const FullType(BuiltList, [FullType(BulkImportItemError)]),
          ) as BuiltList<BulkImportItemError>;
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
  BulkImportResponse deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = BulkImportResponseBuilder();
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

