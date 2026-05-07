//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'stability_metrics.g.dart';

/// Stability metrics relative to the org's currently-published solution.
///
/// Properties:
/// * [affectedPersons] 
/// * [movesFromPublished] 
@BuiltValue()
abstract class StabilityMetrics implements Built<StabilityMetrics, StabilityMetricsBuilder> {
  @BuiltValueField(wireName: r'affected_persons')
  int? get affectedPersons;

  @BuiltValueField(wireName: r'moves_from_published')
  int? get movesFromPublished;

  StabilityMetrics._();

  factory StabilityMetrics([void updates(StabilityMetricsBuilder b)]) = _$StabilityMetrics;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(StabilityMetricsBuilder b) => b
      ..affectedPersons = 0
      ..movesFromPublished = 0;

  @BuiltValueSerializer(custom: true)
  static Serializer<StabilityMetrics> get serializer => _$StabilityMetricsSerializer();
}

class _$StabilityMetricsSerializer implements PrimitiveSerializer<StabilityMetrics> {
  @override
  final Iterable<Type> types = const [StabilityMetrics, _$StabilityMetrics];

  @override
  final String wireName = r'StabilityMetrics';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    StabilityMetrics object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    if (object.affectedPersons != null) {
      yield r'affected_persons';
      yield serializers.serialize(
        object.affectedPersons,
        specifiedType: const FullType(int),
      );
    }
    if (object.movesFromPublished != null) {
      yield r'moves_from_published';
      yield serializers.serialize(
        object.movesFromPublished,
        specifiedType: const FullType(int),
      );
    }
  }

  @override
  Object serialize(
    Serializers serializers,
    StabilityMetrics object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required StabilityMetricsBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'affected_persons':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.affectedPersons = valueDes;
          break;
        case r'moves_from_published':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.movesFromPublished = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  StabilityMetrics deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = StabilityMetricsBuilder();
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

