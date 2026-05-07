//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'export_format.g.dart';

/// Schema for export format request.
///
/// Properties:
/// * [format] - Export format: json, csv, pdf, or ics
/// * [scope] - Export scope: org, person:{id}, or team:{id}
@BuiltValue()
abstract class ExportFormat implements Built<ExportFormat, ExportFormatBuilder> {
  /// Export format: json, csv, pdf, or ics
  @BuiltValueField(wireName: r'format')
  String get format;

  /// Export scope: org, person:{id}, or team:{id}
  @BuiltValueField(wireName: r'scope')
  String? get scope;

  ExportFormat._();

  factory ExportFormat([void updates(ExportFormatBuilder b)]) = _$ExportFormat;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(ExportFormatBuilder b) => b
      ..scope = 'org';

  @BuiltValueSerializer(custom: true)
  static Serializer<ExportFormat> get serializer => _$ExportFormatSerializer();
}

class _$ExportFormatSerializer implements PrimitiveSerializer<ExportFormat> {
  @override
  final Iterable<Type> types = const [ExportFormat, _$ExportFormat];

  @override
  final String wireName = r'ExportFormat';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    ExportFormat object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'format';
    yield serializers.serialize(
      object.format,
      specifiedType: const FullType(String),
    );
    if (object.scope != null) {
      yield r'scope';
      yield serializers.serialize(
        object.scope,
        specifiedType: const FullType(String),
      );
    }
  }

  @override
  Object serialize(
    Serializers serializers,
    ExportFormat object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required ExportFormatBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'format':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.format = valueDes;
          break;
        case r'scope':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.scope = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  ExportFormat deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = ExportFormatBuilder();
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

