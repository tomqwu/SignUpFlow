//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'downgrade_request.g.dart';

/// Request schema for downgrading plan.
///
/// Properties:
/// * [newPlanTier] - New plan tier (free, starter, pro)
/// * [orgId] - Organization ID
/// * [reason]
@BuiltValue()
abstract class DowngradeRequest implements Built<DowngradeRequest, DowngradeRequestBuilder> {
  /// New plan tier (free, starter, pro)
  @BuiltValueField(wireName: r'new_plan_tier')
  String get newPlanTier;

  /// Organization ID
  @BuiltValueField(wireName: r'org_id')
  String get orgId;

  @BuiltValueField(wireName: r'reason')
  String? get reason;

  DowngradeRequest._();

  factory DowngradeRequest([void updates(DowngradeRequestBuilder b)]) = _$DowngradeRequest;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(DowngradeRequestBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<DowngradeRequest> get serializer => _$DowngradeRequestSerializer();
}

class _$DowngradeRequestSerializer implements PrimitiveSerializer<DowngradeRequest> {
  @override
  final Iterable<Type> types = const [DowngradeRequest, _$DowngradeRequest];

  @override
  final String wireName = r'DowngradeRequest';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    DowngradeRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'new_plan_tier';
    yield serializers.serialize(
      object.newPlanTier,
      specifiedType: const FullType(String),
    );
    yield r'org_id';
    yield serializers.serialize(
      object.orgId,
      specifiedType: const FullType(String),
    );
    if (object.reason != null) {
      yield r'reason';
      yield serializers.serialize(
        object.reason,
        specifiedType: const FullType.nullable(String),
      );
    }
  }

  @override
  Object serialize(
    Serializers serializers,
    DowngradeRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required DowngradeRequestBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'new_plan_tier':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.newPlanTier = valueDes;
          break;
        case r'org_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.orgId = valueDes;
          break;
        case r'reason':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
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
  DowngradeRequest deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = DowngradeRequestBuilder();
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
