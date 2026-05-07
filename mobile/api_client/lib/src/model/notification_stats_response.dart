//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:signupflow_api/src/model/notification_response.dart';
import 'package:built_collection/built_collection.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'notification_stats_response.g.dart';

/// Schema for organization notification statistics.
///
/// Properties:
/// * [daysAnalyzed] 
/// * [deliveredNotifications] 
/// * [orgId] 
/// * [recentFailures] - Recent failed notifications
/// * [statusBreakdown] - Count of notifications by status
/// * [successRate] - Delivery success rate percentage
/// * [totalNotifications] 
/// * [typeBreakdown] - Count of notifications by type
@BuiltValue()
abstract class NotificationStatsResponse implements Built<NotificationStatsResponse, NotificationStatsResponseBuilder> {
  @BuiltValueField(wireName: r'days_analyzed')
  int get daysAnalyzed;

  @BuiltValueField(wireName: r'delivered_notifications')
  int get deliveredNotifications;

  @BuiltValueField(wireName: r'org_id')
  String get orgId;

  /// Recent failed notifications
  @BuiltValueField(wireName: r'recent_failures')
  BuiltList<NotificationResponse> get recentFailures;

  /// Count of notifications by status
  @BuiltValueField(wireName: r'status_breakdown')
  BuiltMap<String, int> get statusBreakdown;

  /// Delivery success rate percentage
  @BuiltValueField(wireName: r'success_rate')
  num get successRate;

  @BuiltValueField(wireName: r'total_notifications')
  int get totalNotifications;

  /// Count of notifications by type
  @BuiltValueField(wireName: r'type_breakdown')
  BuiltMap<String, int> get typeBreakdown;

  NotificationStatsResponse._();

  factory NotificationStatsResponse([void updates(NotificationStatsResponseBuilder b)]) = _$NotificationStatsResponse;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(NotificationStatsResponseBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<NotificationStatsResponse> get serializer => _$NotificationStatsResponseSerializer();
}

class _$NotificationStatsResponseSerializer implements PrimitiveSerializer<NotificationStatsResponse> {
  @override
  final Iterable<Type> types = const [NotificationStatsResponse, _$NotificationStatsResponse];

  @override
  final String wireName = r'NotificationStatsResponse';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    NotificationStatsResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'days_analyzed';
    yield serializers.serialize(
      object.daysAnalyzed,
      specifiedType: const FullType(int),
    );
    yield r'delivered_notifications';
    yield serializers.serialize(
      object.deliveredNotifications,
      specifiedType: const FullType(int),
    );
    yield r'org_id';
    yield serializers.serialize(
      object.orgId,
      specifiedType: const FullType(String),
    );
    yield r'recent_failures';
    yield serializers.serialize(
      object.recentFailures,
      specifiedType: const FullType(BuiltList, [FullType(NotificationResponse)]),
    );
    yield r'status_breakdown';
    yield serializers.serialize(
      object.statusBreakdown,
      specifiedType: const FullType(BuiltMap, [FullType(String), FullType(int)]),
    );
    yield r'success_rate';
    yield serializers.serialize(
      object.successRate,
      specifiedType: const FullType(num),
    );
    yield r'total_notifications';
    yield serializers.serialize(
      object.totalNotifications,
      specifiedType: const FullType(int),
    );
    yield r'type_breakdown';
    yield serializers.serialize(
      object.typeBreakdown,
      specifiedType: const FullType(BuiltMap, [FullType(String), FullType(int)]),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    NotificationStatsResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required NotificationStatsResponseBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'days_analyzed':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.daysAnalyzed = valueDes;
          break;
        case r'delivered_notifications':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.deliveredNotifications = valueDes;
          break;
        case r'org_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.orgId = valueDes;
          break;
        case r'recent_failures':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(NotificationResponse)]),
          ) as BuiltList<NotificationResponse>;
          result.recentFailures.replace(valueDes);
          break;
        case r'status_breakdown':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltMap, [FullType(String), FullType(int)]),
          ) as BuiltMap<String, int>;
          result.statusBreakdown.replace(valueDes);
          break;
        case r'success_rate':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(num),
          ) as num;
          result.successRate = valueDes;
          break;
        case r'total_notifications':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.totalNotifications = valueDes;
          break;
        case r'type_breakdown':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltMap, [FullType(String), FullType(int)]),
          ) as BuiltMap<String, int>;
          result.typeBreakdown.replace(valueDes);
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  NotificationStatsResponse deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = NotificationStatsResponseBuilder();
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

