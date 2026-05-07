//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:signupflow_api/src/model/date.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'preview_request.g.dart';

/// Request for previewing occurrences without saving.
///
/// Properties:
/// * [duration] 
/// * [endConditionType] 
/// * [endDate] 
/// * [frequencyInterval] 
/// * [occurrenceCount] 
/// * [patternType] 
/// * [selectedDays] 
/// * [startDate] 
/// * [startTime] 
/// * [weekdayName] 
/// * [weekdayPosition] 
@BuiltValue()
abstract class PreviewRequest implements Built<PreviewRequest, PreviewRequestBuilder> {
  @BuiltValueField(wireName: r'duration')
  int get duration;

  @BuiltValueField(wireName: r'end_condition_type')
  String get endConditionType;

  @BuiltValueField(wireName: r'end_date')
  Date? get endDate;

  @BuiltValueField(wireName: r'frequency_interval')
  int? get frequencyInterval;

  @BuiltValueField(wireName: r'occurrence_count')
  int? get occurrenceCount;

  @BuiltValueField(wireName: r'pattern_type')
  String get patternType;

  @BuiltValueField(wireName: r'selected_days')
  BuiltList<String>? get selectedDays;

  @BuiltValueField(wireName: r'start_date')
  Date get startDate;

  @BuiltValueField(wireName: r'start_time')
  String get startTime;

  @BuiltValueField(wireName: r'weekday_name')
  String? get weekdayName;

  @BuiltValueField(wireName: r'weekday_position')
  String? get weekdayPosition;

  PreviewRequest._();

  factory PreviewRequest([void updates(PreviewRequestBuilder b)]) = _$PreviewRequest;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(PreviewRequestBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<PreviewRequest> get serializer => _$PreviewRequestSerializer();
}

class _$PreviewRequestSerializer implements PrimitiveSerializer<PreviewRequest> {
  @override
  final Iterable<Type> types = const [PreviewRequest, _$PreviewRequest];

  @override
  final String wireName = r'PreviewRequest';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    PreviewRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'duration';
    yield serializers.serialize(
      object.duration,
      specifiedType: const FullType(int),
    );
    yield r'end_condition_type';
    yield serializers.serialize(
      object.endConditionType,
      specifiedType: const FullType(String),
    );
    if (object.endDate != null) {
      yield r'end_date';
      yield serializers.serialize(
        object.endDate,
        specifiedType: const FullType.nullable(Date),
      );
    }
    if (object.frequencyInterval != null) {
      yield r'frequency_interval';
      yield serializers.serialize(
        object.frequencyInterval,
        specifiedType: const FullType.nullable(int),
      );
    }
    if (object.occurrenceCount != null) {
      yield r'occurrence_count';
      yield serializers.serialize(
        object.occurrenceCount,
        specifiedType: const FullType.nullable(int),
      );
    }
    yield r'pattern_type';
    yield serializers.serialize(
      object.patternType,
      specifiedType: const FullType(String),
    );
    if (object.selectedDays != null) {
      yield r'selected_days';
      yield serializers.serialize(
        object.selectedDays,
        specifiedType: const FullType.nullable(BuiltList, [FullType(String)]),
      );
    }
    yield r'start_date';
    yield serializers.serialize(
      object.startDate,
      specifiedType: const FullType(Date),
    );
    yield r'start_time';
    yield serializers.serialize(
      object.startTime,
      specifiedType: const FullType(String),
    );
    if (object.weekdayName != null) {
      yield r'weekday_name';
      yield serializers.serialize(
        object.weekdayName,
        specifiedType: const FullType.nullable(String),
      );
    }
    if (object.weekdayPosition != null) {
      yield r'weekday_position';
      yield serializers.serialize(
        object.weekdayPosition,
        specifiedType: const FullType.nullable(String),
      );
    }
  }

  @override
  Object serialize(
    Serializers serializers,
    PreviewRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required PreviewRequestBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'duration':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.duration = valueDes;
          break;
        case r'end_condition_type':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.endConditionType = valueDes;
          break;
        case r'end_date':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(Date),
          ) as Date?;
          if (valueDes == null) continue;
          result.endDate = valueDes;
          break;
        case r'frequency_interval':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(int),
          ) as int?;
          if (valueDes == null) continue;
          result.frequencyInterval = valueDes;
          break;
        case r'occurrence_count':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(int),
          ) as int?;
          if (valueDes == null) continue;
          result.occurrenceCount = valueDes;
          break;
        case r'pattern_type':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.patternType = valueDes;
          break;
        case r'selected_days':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(BuiltList, [FullType(String)]),
          ) as BuiltList<String>?;
          if (valueDes == null) continue;
          result.selectedDays.replace(valueDes);
          break;
        case r'start_date':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(Date),
          ) as Date;
          result.startDate = valueDes;
          break;
        case r'start_time':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.startTime = valueDes;
          break;
        case r'weekday_name':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.weekdayName = valueDes;
          break;
        case r'weekday_position':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.weekdayPosition = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  PreviewRequest deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = PreviewRequestBuilder();
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

