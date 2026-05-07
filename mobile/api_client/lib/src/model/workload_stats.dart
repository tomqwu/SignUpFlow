//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'workload_stats.g.dart';

/// Aggregate workload distribution stats.
///
/// Properties:
/// * [distinctPersonsAssigned] 
/// * [maxEventsPerPerson] 
/// * [medianEventsPerPerson] 
/// * [minEventsPerPerson] 
/// * [totalEventsAssigned] 
@BuiltValue()
abstract class WorkloadStats implements Built<WorkloadStats, WorkloadStatsBuilder> {
  @BuiltValueField(wireName: r'distinct_persons_assigned')
  int get distinctPersonsAssigned;

  @BuiltValueField(wireName: r'max_events_per_person')
  int get maxEventsPerPerson;

  @BuiltValueField(wireName: r'median_events_per_person')
  num get medianEventsPerPerson;

  @BuiltValueField(wireName: r'min_events_per_person')
  int get minEventsPerPerson;

  @BuiltValueField(wireName: r'total_events_assigned')
  int get totalEventsAssigned;

  WorkloadStats._();

  factory WorkloadStats([void updates(WorkloadStatsBuilder b)]) = _$WorkloadStats;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(WorkloadStatsBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<WorkloadStats> get serializer => _$WorkloadStatsSerializer();
}

class _$WorkloadStatsSerializer implements PrimitiveSerializer<WorkloadStats> {
  @override
  final Iterable<Type> types = const [WorkloadStats, _$WorkloadStats];

  @override
  final String wireName = r'WorkloadStats';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    WorkloadStats object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'distinct_persons_assigned';
    yield serializers.serialize(
      object.distinctPersonsAssigned,
      specifiedType: const FullType(int),
    );
    yield r'max_events_per_person';
    yield serializers.serialize(
      object.maxEventsPerPerson,
      specifiedType: const FullType(int),
    );
    yield r'median_events_per_person';
    yield serializers.serialize(
      object.medianEventsPerPerson,
      specifiedType: const FullType(num),
    );
    yield r'min_events_per_person';
    yield serializers.serialize(
      object.minEventsPerPerson,
      specifiedType: const FullType(int),
    );
    yield r'total_events_assigned';
    yield serializers.serialize(
      object.totalEventsAssigned,
      specifiedType: const FullType(int),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    WorkloadStats object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required WorkloadStatsBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'distinct_persons_assigned':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.distinctPersonsAssigned = valueDes;
          break;
        case r'max_events_per_person':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.maxEventsPerPerson = valueDes;
          break;
        case r'median_events_per_person':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(num),
          ) as num;
          result.medianEventsPerPerson = valueDes;
          break;
        case r'min_events_per_person':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.minEventsPerPerson = valueDes;
          break;
        case r'total_events_assigned':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.totalEventsAssigned = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  WorkloadStats deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = WorkloadStatsBuilder();
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

