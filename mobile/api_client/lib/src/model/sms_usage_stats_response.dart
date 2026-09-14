//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'sms_usage_stats_response.g.dart';

/// Response with SMS usage statistics for organization.
///
/// Properties:
/// * [budgetLimitCents]
/// * [budgetUsedPercentage]
/// * [messagesDelivered]
/// * [messagesFailed]
/// * [messagesRemaining]
/// * [messagesSent]
/// * [monthYear]
/// * [totalCostCents]
@BuiltValue()
abstract class SmsUsageStatsResponse implements Built<SmsUsageStatsResponse, SmsUsageStatsResponseBuilder> {
  @BuiltValueField(wireName: r'budget_limit_cents')
  int get budgetLimitCents;

  @BuiltValueField(wireName: r'budget_used_percentage')
  num get budgetUsedPercentage;

  @BuiltValueField(wireName: r'messages_delivered')
  int get messagesDelivered;

  @BuiltValueField(wireName: r'messages_failed')
  int get messagesFailed;

  @BuiltValueField(wireName: r'messages_remaining')
  int? get messagesRemaining;

  @BuiltValueField(wireName: r'messages_sent')
  int get messagesSent;

  @BuiltValueField(wireName: r'month_year')
  String get monthYear;

  @BuiltValueField(wireName: r'total_cost_cents')
  int get totalCostCents;

  SmsUsageStatsResponse._();

  factory SmsUsageStatsResponse([void updates(SmsUsageStatsResponseBuilder b)]) = _$SmsUsageStatsResponse;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(SmsUsageStatsResponseBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<SmsUsageStatsResponse> get serializer => _$SmsUsageStatsResponseSerializer();
}

class _$SmsUsageStatsResponseSerializer implements PrimitiveSerializer<SmsUsageStatsResponse> {
  @override
  final Iterable<Type> types = const [SmsUsageStatsResponse, _$SmsUsageStatsResponse];

  @override
  final String wireName = r'SmsUsageStatsResponse';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    SmsUsageStatsResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'budget_limit_cents';
    yield serializers.serialize(
      object.budgetLimitCents,
      specifiedType: const FullType(int),
    );
    yield r'budget_used_percentage';
    yield serializers.serialize(
      object.budgetUsedPercentage,
      specifiedType: const FullType(num),
    );
    yield r'messages_delivered';
    yield serializers.serialize(
      object.messagesDelivered,
      specifiedType: const FullType(int),
    );
    yield r'messages_failed';
    yield serializers.serialize(
      object.messagesFailed,
      specifiedType: const FullType(int),
    );
    if (object.messagesRemaining != null) {
      yield r'messages_remaining';
      yield serializers.serialize(
        object.messagesRemaining,
        specifiedType: const FullType.nullable(int),
      );
    }
    yield r'messages_sent';
    yield serializers.serialize(
      object.messagesSent,
      specifiedType: const FullType(int),
    );
    yield r'month_year';
    yield serializers.serialize(
      object.monthYear,
      specifiedType: const FullType(String),
    );
    yield r'total_cost_cents';
    yield serializers.serialize(
      object.totalCostCents,
      specifiedType: const FullType(int),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    SmsUsageStatsResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required SmsUsageStatsResponseBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'budget_limit_cents':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.budgetLimitCents = valueDes;
          break;
        case r'budget_used_percentage':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(num),
          ) as num;
          result.budgetUsedPercentage = valueDes;
          break;
        case r'messages_delivered':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.messagesDelivered = valueDes;
          break;
        case r'messages_failed':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.messagesFailed = valueDes;
          break;
        case r'messages_remaining':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(int),
          ) as int?;
          if (valueDes == null) continue;
          result.messagesRemaining = valueDes;
          break;
        case r'messages_sent':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.messagesSent = valueDes;
          break;
        case r'month_year':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.monthYear = valueDes;
          break;
        case r'total_cost_cents':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.totalCostCents = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  SmsUsageStatsResponse deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = SmsUsageStatsResponseBuilder();
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

