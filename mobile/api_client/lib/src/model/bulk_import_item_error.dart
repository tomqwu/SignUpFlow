//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'bulk_import_item_error.g.dart';

/// One row that the bulk importer rejected.
///
/// Properties:
/// * [id] 
/// * [index] - Position in the original payload (0-based)
/// * [reason] - Why this row was rejected
@BuiltValue()
abstract class BulkImportItemError implements Built<BulkImportItemError, BulkImportItemErrorBuilder> {
  @BuiltValueField(wireName: r'id')
  String? get id;

  /// Position in the original payload (0-based)
  @BuiltValueField(wireName: r'index')
  int get index;

  /// Why this row was rejected
  @BuiltValueField(wireName: r'reason')
  String get reason;

  BulkImportItemError._();

  factory BulkImportItemError([void updates(BulkImportItemErrorBuilder b)]) = _$BulkImportItemError;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(BulkImportItemErrorBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<BulkImportItemError> get serializer => _$BulkImportItemErrorSerializer();
}

class _$BulkImportItemErrorSerializer implements PrimitiveSerializer<BulkImportItemError> {
  @override
  final Iterable<Type> types = const [BulkImportItemError, _$BulkImportItemError];

  @override
  final String wireName = r'BulkImportItemError';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    BulkImportItemError object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    if (object.id != null) {
      yield r'id';
      yield serializers.serialize(
        object.id,
        specifiedType: const FullType.nullable(String),
      );
    }
    yield r'index';
    yield serializers.serialize(
      object.index,
      specifiedType: const FullType(int),
    );
    yield r'reason';
    yield serializers.serialize(
      object.reason,
      specifiedType: const FullType(String),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    BulkImportItemError object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required BulkImportItemErrorBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.id = valueDes;
          break;
        case r'index':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.index = valueDes;
          break;
        case r'reason':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.reason = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  BulkImportItemError deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = BulkImportItemErrorBuilder();
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

