//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'fairness_stats.g.dart';

/// Fairness metrics + histogram of per-person assignment counts.
///
/// Properties:
/// * [histogram] 
/// * [perPersonCounts] 
/// * [stdev] 
@BuiltValue()
abstract class FairnessStats implements Built<FairnessStats, FairnessStatsBuilder> {
  @BuiltValueField(wireName: r'histogram')
  BuiltMap<String, int> get histogram;

  @BuiltValueField(wireName: r'per_person_counts')
  BuiltMap<String, int> get perPersonCounts;

  @BuiltValueField(wireName: r'stdev')
  num get stdev;

  FairnessStats._();

  factory FairnessStats([void updates(FairnessStatsBuilder b)]) = _$FairnessStats;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(FairnessStatsBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<FairnessStats> get serializer => _$FairnessStatsSerializer();
}

class _$FairnessStatsSerializer implements PrimitiveSerializer<FairnessStats> {
  @override
  final Iterable<Type> types = const [FairnessStats, _$FairnessStats];

  @override
  final String wireName = r'FairnessStats';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    FairnessStats object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'histogram';
    yield serializers.serialize(
      object.histogram,
      specifiedType: const FullType(BuiltMap, [FullType(String), FullType(int)]),
    );
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
    FairnessStats object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required FairnessStatsBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'histogram':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltMap, [FullType(String), FullType(int)]),
          ) as BuiltMap<String, int>;
          result.histogram.replace(valueDes);
          break;
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
  FairnessStats deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = FairnessStatsBuilder();
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

