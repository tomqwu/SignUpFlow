//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:built_value/json_object.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'notification_response.g.dart';

/// Schema for notification response.
///
/// Properties:
/// * [clickedAt] 
/// * [createdAt] 
/// * [deliveredAt] 
/// * [errorMessage] 
/// * [eventId] 
/// * [id] 
/// * [openedAt] 
/// * [orgId] 
/// * [recipientId] 
/// * [retryCount] 
/// * [sendgridMessageId] 
/// * [sentAt] 
/// * [status] - Notification status (pending, sent, delivered, etc.)
/// * [templateData] 
/// * [type] - Notification type (assignment, reminder, update, cancellation)
@BuiltValue()
abstract class NotificationResponse implements Built<NotificationResponse, NotificationResponseBuilder> {
  @BuiltValueField(wireName: r'clicked_at')
  DateTime? get clickedAt;

  @BuiltValueField(wireName: r'created_at')
  DateTime get createdAt;

  @BuiltValueField(wireName: r'delivered_at')
  DateTime? get deliveredAt;

  @BuiltValueField(wireName: r'error_message')
  String? get errorMessage;

  @BuiltValueField(wireName: r'event_id')
  String? get eventId;

  @BuiltValueField(wireName: r'id')
  int get id;

  @BuiltValueField(wireName: r'opened_at')
  DateTime? get openedAt;

  @BuiltValueField(wireName: r'org_id')
  String get orgId;

  @BuiltValueField(wireName: r'recipient_id')
  String get recipientId;

  @BuiltValueField(wireName: r'retry_count')
  int get retryCount;

  @BuiltValueField(wireName: r'sendgrid_message_id')
  String? get sendgridMessageId;

  @BuiltValueField(wireName: r'sent_at')
  DateTime? get sentAt;

  /// Notification status (pending, sent, delivered, etc.)
  @BuiltValueField(wireName: r'status')
  String get status;

  @BuiltValueField(wireName: r'template_data')
  BuiltMap<String, JsonObject?>? get templateData;

  /// Notification type (assignment, reminder, update, cancellation)
  @BuiltValueField(wireName: r'type')
  String get type;

  NotificationResponse._();

  factory NotificationResponse([void updates(NotificationResponseBuilder b)]) = _$NotificationResponse;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(NotificationResponseBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<NotificationResponse> get serializer => _$NotificationResponseSerializer();
}

class _$NotificationResponseSerializer implements PrimitiveSerializer<NotificationResponse> {
  @override
  final Iterable<Type> types = const [NotificationResponse, _$NotificationResponse];

  @override
  final String wireName = r'NotificationResponse';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    NotificationResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    if (object.clickedAt != null) {
      yield r'clicked_at';
      yield serializers.serialize(
        object.clickedAt,
        specifiedType: const FullType.nullable(DateTime),
      );
    }
    yield r'created_at';
    yield serializers.serialize(
      object.createdAt,
      specifiedType: const FullType(DateTime),
    );
    if (object.deliveredAt != null) {
      yield r'delivered_at';
      yield serializers.serialize(
        object.deliveredAt,
        specifiedType: const FullType.nullable(DateTime),
      );
    }
    if (object.errorMessage != null) {
      yield r'error_message';
      yield serializers.serialize(
        object.errorMessage,
        specifiedType: const FullType.nullable(String),
      );
    }
    if (object.eventId != null) {
      yield r'event_id';
      yield serializers.serialize(
        object.eventId,
        specifiedType: const FullType.nullable(String),
      );
    }
    yield r'id';
    yield serializers.serialize(
      object.id,
      specifiedType: const FullType(int),
    );
    if (object.openedAt != null) {
      yield r'opened_at';
      yield serializers.serialize(
        object.openedAt,
        specifiedType: const FullType.nullable(DateTime),
      );
    }
    yield r'org_id';
    yield serializers.serialize(
      object.orgId,
      specifiedType: const FullType(String),
    );
    yield r'recipient_id';
    yield serializers.serialize(
      object.recipientId,
      specifiedType: const FullType(String),
    );
    yield r'retry_count';
    yield serializers.serialize(
      object.retryCount,
      specifiedType: const FullType(int),
    );
    if (object.sendgridMessageId != null) {
      yield r'sendgrid_message_id';
      yield serializers.serialize(
        object.sendgridMessageId,
        specifiedType: const FullType.nullable(String),
      );
    }
    if (object.sentAt != null) {
      yield r'sent_at';
      yield serializers.serialize(
        object.sentAt,
        specifiedType: const FullType.nullable(DateTime),
      );
    }
    yield r'status';
    yield serializers.serialize(
      object.status,
      specifiedType: const FullType(String),
    );
    if (object.templateData != null) {
      yield r'template_data';
      yield serializers.serialize(
        object.templateData,
        specifiedType: const FullType.nullable(BuiltMap, [FullType(String), FullType.nullable(JsonObject)]),
      );
    }
    yield r'type';
    yield serializers.serialize(
      object.type,
      specifiedType: const FullType(String),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    NotificationResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required NotificationResponseBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'clicked_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(DateTime),
          ) as DateTime?;
          if (valueDes == null) continue;
          result.clickedAt = valueDes;
          break;
        case r'created_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(DateTime),
          ) as DateTime;
          result.createdAt = valueDes;
          break;
        case r'delivered_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(DateTime),
          ) as DateTime?;
          if (valueDes == null) continue;
          result.deliveredAt = valueDes;
          break;
        case r'error_message':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.errorMessage = valueDes;
          break;
        case r'event_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.eventId = valueDes;
          break;
        case r'id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.id = valueDes;
          break;
        case r'opened_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(DateTime),
          ) as DateTime?;
          if (valueDes == null) continue;
          result.openedAt = valueDes;
          break;
        case r'org_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.orgId = valueDes;
          break;
        case r'recipient_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.recipientId = valueDes;
          break;
        case r'retry_count':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.retryCount = valueDes;
          break;
        case r'sendgrid_message_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.sendgridMessageId = valueDes;
          break;
        case r'sent_at':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(DateTime),
          ) as DateTime?;
          if (valueDes == null) continue;
          result.sentAt = valueDes;
          break;
        case r'status':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.status = valueDes;
          break;
        case r'template_data':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(BuiltMap, [FullType(String), FullType.nullable(JsonObject)]),
          ) as BuiltMap<String, JsonObject?>?;
          if (valueDes == null) continue;
          result.templateData.replace(valueDes);
          break;
        case r'type':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.type = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  NotificationResponse deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = NotificationResponseBuilder();
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

