//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'trial_request.g.dart';

/// Request schema for starting trial.
///
/// Properties:
/// * [billingCycle] - Billing cycle after trial
/// * [orgId] - Organization ID
/// * [planTier] - Plan tier to trial (starter, pro, enterprise)
/// * [trialDays] - Number of trial days
@BuiltValue()
abstract class TrialRequest implements Built<TrialRequest, TrialRequestBuilder> {
  /// Billing cycle after trial
  @BuiltValueField(wireName: r'billing_cycle')
  String? get billingCycle;

  /// Organization ID
  @BuiltValueField(wireName: r'org_id')
  String get orgId;

  /// Plan tier to trial (starter, pro, enterprise)
  @BuiltValueField(wireName: r'plan_tier')
  String get planTier;

  /// Number of trial days
  @BuiltValueField(wireName: r'trial_days')
  int? get trialDays;

  TrialRequest._();

  factory TrialRequest([void updates(TrialRequestBuilder b)]) = _$TrialRequest;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(TrialRequestBuilder b) => b
      ..billingCycle = 'monthly'
      ..trialDays = 14;

  @BuiltValueSerializer(custom: true)
  static Serializer<TrialRequest> get serializer => _$TrialRequestSerializer();
}

class _$TrialRequestSerializer implements PrimitiveSerializer<TrialRequest> {
  @override
  final Iterable<Type> types = const [TrialRequest, _$TrialRequest];

  @override
  final String wireName = r'TrialRequest';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    TrialRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    if (object.billingCycle != null) {
      yield r'billing_cycle';
      yield serializers.serialize(
        object.billingCycle,
        specifiedType: const FullType(String),
      );
    }
    yield r'org_id';
    yield serializers.serialize(
      object.orgId,
      specifiedType: const FullType(String),
    );
    yield r'plan_tier';
    yield serializers.serialize(
      object.planTier,
      specifiedType: const FullType(String),
    );
    if (object.trialDays != null) {
      yield r'trial_days';
      yield serializers.serialize(
        object.trialDays,
        specifiedType: const FullType(int),
      );
    }
  }

  @override
  Object serialize(
    Serializers serializers,
    TrialRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required TrialRequestBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'billing_cycle':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.billingCycle = valueDes;
          break;
        case r'org_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.orgId = valueDes;
          break;
        case r'plan_tier':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.planTier = valueDes;
          break;
        case r'trial_days':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.trialDays = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  TrialRequest deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = TrialRequestBuilder();
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
