//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'fairness_metrics.g.dart';

/// Schema for fairness metrics.
///
/// Properties:
/// * [perPersonCounts] 
/// * [stdev] 
@BuiltValue()
abstract class FairnessMetrics implements Built<FairnessMetrics, FairnessMetricsBuilder> {
  @BuiltValueField(wireName: r'per_person_counts')
  BuiltMap<String, int> get perPersonCounts;

  @BuiltValueField(wireName: r'stdev')
  num get stdev;

  FairnessMetrics._();

  factory FairnessMetrics([void updates(FairnessMetricsBuilder b)]) = _$FairnessMetrics;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(FairnessMetricsBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<FairnessMetrics> get serializer => _$FairnessMetricsSerializer();
}

class _$FairnessMetricsSerializer implements PrimitiveSerializer<FairnessMetrics> {
  @override
  final Iterable<Type> types = const [FairnessMetrics, _$FairnessMetrics];

  @override
  final String wireName = r'FairnessMetrics';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    FairnessMetrics object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'per_person_counts';
    yield serializers.serialize(
      object.perPersonCounts,
      specifiedType: const FullType(BuiltMap, [FullType(String), FullType(int)]),
    );
    yield r'stdev';
    yield serializers.serialize(
      object.stdev,
      specifiedType: const FullType(num),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    FairnessMetrics object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required FairnessMetricsBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'per_person_counts':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltMap, [FullType(String), FullType(int)]),
          ) as BuiltMap<String, int>;
          result.perPersonCounts.replace(valueDes);
          break;
        case r'stdev':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(num),
          ) as num;
          result.stdev = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  FairnessMetrics deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = FairnessMetricsBuilder();
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

