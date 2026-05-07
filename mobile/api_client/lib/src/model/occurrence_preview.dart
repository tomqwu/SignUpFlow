//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:built_value/json_object.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'occurrence_preview.g.dart';

/// Preview of generated occurrences.
///
/// Properties:
/// * [endTime] 
/// * [holidayLabel] 
/// * [isHolidayConflict] 
/// * [location] 
/// * [occurrenceSequence] 
/// * [roleRequirements] 
/// * [startTime] 
/// * [title] 
@BuiltValue()
abstract class OccurrencePreview implements Built<OccurrencePreview, OccurrencePreviewBuilder> {
  @BuiltValueField(wireName: r'end_time')
  DateTime get endTime;

  @BuiltValueField(wireName: r'holiday_label')
  String? get holidayLabel;

  @BuiltValueField(wireName: r'is_holiday_conflict')
  bool? get isHolidayConflict;

  @BuiltValueField(wireName: r'location')
  String? get location;

  @BuiltValueField(wireName: r'occurrence_sequence')
  int get occurrenceSequence;

  @BuiltValueField(wireName: r'role_requirements')
  BuiltMap<String, JsonObject?>? get roleRequirements;

  @BuiltValueField(wireName: r'start_time')
  DateTime get startTime;

  @BuiltValueField(wireName: r'title')
  String get title;

  OccurrencePreview._();

  factory OccurrencePreview([void updates(OccurrencePreviewBuilder b)]) = _$OccurrencePreview;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(OccurrencePreviewBuilder b) => b
      ..isHolidayConflict = false;

  @BuiltValueSerializer(custom: true)
  static Serializer<OccurrencePreview> get serializer => _$OccurrencePreviewSerializer();
}

class _$OccurrencePreviewSerializer implements PrimitiveSerializer<OccurrencePreview> {
  @override
  final Iterable<Type> types = const [OccurrencePreview, _$OccurrencePreview];

  @override
  final String wireName = r'OccurrencePreview';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    OccurrencePreview object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'end_time';
    yield serializers.serialize(
      object.endTime,
      specifiedType: const FullType(DateTime),
    );
    if (object.holidayLabel != null) {
      yield r'holiday_label';
      yield serializers.serialize(
        object.holidayLabel,
        specifiedType: const FullType.nullable(String),
      );
    }
    if (object.isHolidayConflict != null) {
      yield r'is_holiday_conflict';
      yield serializers.serialize(
        object.isHolidayConflict,
        specifiedType: const FullType(bool),
      );
    }
    yield r'location';
    yield object.location == null ? null : serializers.serialize(
      object.location,
      specifiedType: const FullType.nullable(String),
    );
    yield r'occurrence_sequence';
    yield serializers.serialize(
      object.occurrenceSequence,
      specifiedType: const FullType(int),
    );
    yield r'role_requirements';
    yield object.roleRequirements == null ? null : serializers.serialize(
      object.roleRequirements,
      specifiedType: const FullType.nullable(BuiltMap, [FullType(String), FullType.nullable(JsonObject)]),
    );
    yield r'start_time';
    yield serializers.serialize(
      object.startTime,
      specifiedType: const FullType(DateTime),
    );
    yield r'title';
    yield serializers.serialize(
      object.title,
      specifiedType: const FullType(String),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    OccurrencePreview object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required OccurrencePreviewBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'end_time':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(DateTime),
          ) as DateTime;
          result.endTime = valueDes;
          break;
        case r'holiday_label':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.holidayLabel = valueDes;
          break;
        case r'is_holiday_conflict':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(bool),
          ) as bool;
          result.isHolidayConflict = valueDes;
          break;
        case r'location':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.location = valueDes;
          break;
        case r'occurrence_sequence':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.occurrenceSequence = valueDes;
          break;
        case r'role_requirements':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(BuiltMap, [FullType(String), FullType.nullable(JsonObject)]),
          ) as BuiltMap<String, JsonObject?>?;
          if (valueDes == null) continue;
          result.roleRequirements.replace(valueDes);
          break;
        case r'start_time':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(DateTime),
          ) as DateTime;
          result.startTime = valueDes;
          break;
        case r'title':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.title = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  OccurrencePreview deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = OccurrencePreviewBuilder();
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

