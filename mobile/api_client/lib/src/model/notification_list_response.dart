//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:signupflow_api/src/model/notification_response.dart';
import 'package:built_collection/built_collection.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'notification_list_response.g.dart';

/// Schema for paginated notification list.
///
/// Properties:
/// * [limit] 
/// * [notifications] 
/// * [offset] 
/// * [total] 
@BuiltValue()
abstract class NotificationListResponse implements Built<NotificationListResponse, NotificationListResponseBuilder> {
  @BuiltValueField(wireName: r'limit')
  int get limit;

  @BuiltValueField(wireName: r'notifications')
  BuiltList<NotificationResponse> get notifications;

  @BuiltValueField(wireName: r'offset')
  int get offset;

  @BuiltValueField(wireName: r'total')
  int get total;

  NotificationListResponse._();

  factory NotificationListResponse([void updates(NotificationListResponseBuilder b)]) = _$NotificationListResponse;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(NotificationListResponseBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<NotificationListResponse> get serializer => _$NotificationListResponseSerializer();
}

class _$NotificationListResponseSerializer implements PrimitiveSerializer<NotificationListResponse> {
  @override
  final Iterable<Type> types = const [NotificationListResponse, _$NotificationListResponse];

  @override
  final String wireName = r'NotificationListResponse';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    NotificationListResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'limit';
    yield serializers.serialize(
      object.limit,
      specifiedType: const FullType(int),
    );
    yield r'notifications';
    yield serializers.serialize(
      object.notifications,
      specifiedType: const FullType(BuiltList, [FullType(NotificationResponse)]),
    );
    yield r'offset';
    yield serializers.serialize(
      object.offset,
      specifiedType: const FullType(int),
    );
    yield r'total';
    yield serializers.serialize(
      object.total,
      specifiedType: const FullType(int),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    NotificationListResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required NotificationListResponseBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'limit':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.limit = valueDes;
          break;
        case r'notifications':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(NotificationResponse)]),
          ) as BuiltList<NotificationResponse>;
          result.notifications.replace(valueDes);
          break;
        case r'offset':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.offset = valueDes;
          break;
        case r'total':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.total = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  NotificationListResponse deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = NotificationListResponseBuilder();
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

