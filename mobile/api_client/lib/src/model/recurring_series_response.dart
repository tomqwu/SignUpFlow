//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:signupflow_api/src/model/date.dart';
import 'package:built_value/json_object.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'recurring_series_response.g.dart';

/// Response model for recurring series.
///
/// Properties:
/// * [active] 
/// * [createdAt] 
/// * [createdBy] 
/// * [duration] 
/// * [endConditionType] 
/// * [endDate] 
/// * [frequencyInterval] 
/// * [id] 
/// * [location] 
/// * [occurrenceCount] 
/// * [occurrencePreviewCount] 
/// * [orgId] 
/// * [patternType] 
/// * [roleRequirements] 
/// * [selectedDays] 
/// * [startDate] 
/// * [title] 
/// * [updatedAt] 
/// * [weekdayName] 
/// * [weekdayPosition] 
@BuiltValue()
abstract class RecurringSeriesResponse implements Built<RecurringSeriesResponse, RecurringSeriesResponseBuilder> {
  @BuiltValueField(wireName: r'active')
  bool get active;

  @BuiltValueField(wireName: r'created_at')
  DateTime get createdAt;

  @BuiltValueField(wireName: r'created_by')
  String get createdBy;

  @BuiltValueField(wireName: r'duration')
  int get duration;

  @BuiltValueField(wireName: r'end_condition_type')
  String get endConditionType;

  @BuiltValueField(wireName: r'end_date')
  Date? get endDate;

  @BuiltValueField(wireName: r'frequency_interval')
  int? get frequencyInterval;

  @BuiltValueField(wireName: r'id')
  String get id;

  @BuiltValueField(wireName: r'location')
  String? get location;

  @BuiltValueField(wireName: r'occurrence_count')
  int? get occurrenceCount;

  @BuiltValueField(wireName: r'occurrence_preview_count')
  int? get occurrencePreviewCount;

  @BuiltValueField(wireName: r'org_id')
  String get orgId;

  @BuiltValueField(wireName: r'pattern_type')
  String get patternType;

  @BuiltValueField(wireName: r'role_requirements')
  BuiltMap<String, JsonObject?>? get roleRequirements;

  @BuiltValueField(wireName: r'selected_days')
  BuiltList<String>? get selectedDays;

  @BuiltValueField(wireName: r'start_date')
  Date get startDate;

  @BuiltValueField(wireName: r'title')
  String get title;

  @BuiltValueField(wireName: r'updated_at')
  DateTime get updatedAt;

  @BuiltValueField(wireName: r'weekday_name')
  String? get weekdayName;

  @BuiltValueField(wireName: r'weekday_position')
  String? get weekdayPosition;

  RecurringSeriesResponse._();

  factory RecurringSeriesResponse([void updates(RecurringSeriesResponseBuilder b)]) = _$RecurringSeriesResponse;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(RecurringSeriesResponseBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<RecurringSeriesResponse> get serializer => _$RecurringSeriesResponseSerializer();
}

class _$RecurringSeriesResponseSerializer implements PrimitiveSerializer<RecurringSeriesResponse> {
  @override
  final Iterable<Type> types = const [RecurringSeriesResponse, _$RecurringSeriesResponse];

  @override
  final String wireName = r'RecurringSeriesResponse';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    RecurringSeriesResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'active';
    yield serializers.serialize(
      object.active,
      specifiedType: const FullType(bool),
    );
    yield r'created_at';
    yield serializers.serialize(
      object.createdAt,
      specifiedType: const FullType(DateTime),
    );
    yield r'created_by';
    yield serializers.serialize(
      object.createdBy,
      specifiedType: const FullType(String),
    );
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
    yield r'end_date';
    yield object.endDate == null ? null : serializers.serialize(
      object.endDate,
      specifiedType: const FullType.nullable(Date),
    );
    yield r'frequency_interval';
    yield object.frequencyInterval == null ? null : serializers.serialize(
      object.frequencyInterval,
      specifiedType: const FullType.nullable(int),
    );
    yield r'id';
    yield serializers.serialize(
      object.id,
      specifiedType: const FullType(String),
    );
    yield r'location';
    yield object.location == null ? null : serializers.serialize(
      object.location,
      specifiedType: const FullType.nullable(String),
    );
    yield r'occurrence_count';
    yield object.occurrenceCount == null ? null : serializers.serialize(
      object.occurrenceCount,
      specifiedType: const FullType.nullable(int),
    );
    if (object.occurrencePreviewCount != null) {
      yield r'occurrence_preview_count';
      yield serializers.serialize(
        object.occurrencePreviewCount,
        specifiedType: const FullType.nullable(int),
      );
    }
    yield r'org_id';
    yield serializers.serialize(
      object.orgId,
      specifiedType: const FullType(String),
    );
    yield r'pattern_type';
    yield serializers.serialize(
      object.patternType,
      specifiedType: const FullType(String),
    );
    yield r'role_requirements';
    yield object.roleRequirements == null ? null : serializers.serialize(
      object.roleRequirements,
      specifiedType: const FullType.nullable(BuiltMap, [FullType(String), FullType.nullable(JsonObject)]),
    );
    yield r'selected_days';
    yield object.selectedDays == null ? null : serializers.serialize(
      object.selectedDays,
      specifiedType: const FullType.nullable(BuiltList, [FullType(String)]),
    );
    yield r'start_date';
    yield serializers.serialize(
      object.startDate,
      specifiedType: const FullType(Date),
    );
    yield r'title';
    yield serializers.serialize(
      object.title,
      specifiedType: const FullType(String),
    );
    yield r'updated_at';
    yield serializers.serialize(
      object.updatedAt,
      specifiedType: const FullType(DateTime),
    );
    yield r'weekday_name';
    yield object.weekdayName == null ? null : serializers.serialize(
      object.weekdayName,
      specifiedType: const FullType.nullable(String),
    );
    yield r'weekday_position';
    yield object.weekdayPosition == null ? null : serializers.serialize(
      object.weekdayPosition,
      specifiedType: const FullType.nullable(String),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    RecurringSeriesResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required RecurringSeriesResponseBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'active':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(bool),
          ) as bool;
          result.active = valueDes;
          break;
        case r'created_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(DateTime),
          ) as DateTime;
          result.createdAt = valueDes;
          break;
        case r'created_by':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.createdBy = valueDes;
          break;
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
        case r'id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.id = valueDes;
          break;
        case r'location':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.location = valueDes;
          break;
        case r'occurrence_count':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(int),
          ) as int?;
          if (valueDes == null) continue;
          result.occurrenceCount = valueDes;
          break;
        case r'occurrence_preview_count':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(int),
          ) as int?;
          if (valueDes == null) continue;
          result.occurrencePreviewCount = valueDes;
          break;
        case r'org_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.orgId = valueDes;
          break;
        case r'pattern_type':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.patternType = valueDes;
          break;
        case r'role_requirements':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(BuiltMap, [FullType(String), FullType.nullable(JsonObject)]),
          ) as BuiltMap<String, JsonObject?>?;
          if (valueDes == null) continue;
          result.roleRequirements.replace(valueDes);
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
        case r'title':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.title = valueDes;
          break;
        case r'updated_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(DateTime),
          ) as DateTime;
          result.updatedAt = valueDes;
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
  RecurringSeriesResponse deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = RecurringSeriesResponseBuilder();
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

