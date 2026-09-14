//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'upgrade_request.g.dart';

/// Request schema for upgrading to paid plan.
///
/// Properties:
/// * [billingCycle] - Billing cycle (monthly, annual)
/// * [orgId] - Organization ID
/// * [paymentMethodId]
/// * [planTier] - Plan tier (starter, pro, enterprise)
/// * [trialDays]
@BuiltValue()
abstract class UpgradeRequest implements Built<UpgradeRequest, UpgradeRequestBuilder> {
  /// Billing cycle (monthly, annual)
  @BuiltValueField(wireName: r'billing_cycle')
  String get billingCycle;

  /// Organization ID
  @BuiltValueField(wireName: r'org_id')
  String get orgId;

  @BuiltValueField(wireName: r'payment_method_id')
  String? get paymentMethodId;

  /// Plan tier (starter, pro, enterprise)
  @BuiltValueField(wireName: r'plan_tier')
  String get planTier;

  @BuiltValueField(wireName: r'trial_days')
  int? get trialDays;

  UpgradeRequest._();

  factory UpgradeRequest([void updates(UpgradeRequestBuilder b)]) = _$UpgradeRequest;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(UpgradeRequestBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<UpgradeRequest> get serializer => _$UpgradeRequestSerializer();
}

class _$UpgradeRequestSerializer implements PrimitiveSerializer<UpgradeRequest> {
  @override
  final Iterable<Type> types = const [UpgradeRequest, _$UpgradeRequest];

  @override
  final String wireName = r'UpgradeRequest';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    UpgradeRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'billing_cycle';
    yield serializers.serialize(
      object.billingCycle,
      specifiedType: const FullType(String),
    );
    yield r'org_id';
    yield serializers.serialize(
      object.orgId,
      specifiedType: const FullType(String),
    );
    if (object.paymentMethodId != null) {
      yield r'payment_method_id';
      yield serializers.serialize(
        object.paymentMethodId,
        specifiedType: const FullType.nullable(String),
      );
    }
    yield r'plan_tier';
    yield serializers.serialize(
      object.planTier,
      specifiedType: const FullType(String),
    );
    if (object.trialDays != null) {
      yield r'trial_days';
      yield serializers.serialize(
        object.trialDays,
        specifiedType: const FullType.nullable(int),
      );
    }
  }

  @override
  Object serialize(
    Serializers serializers,
    UpgradeRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required UpgradeRequestBuilder result,
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
        case r'payment_method_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.paymentMethodId = valueDes;
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
            specifiedType: const FullType.nullable(int),
          ) as int?;
          if (valueDes == null) continue;
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
  UpgradeRequest deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = UpgradeRequestBuilder();
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

