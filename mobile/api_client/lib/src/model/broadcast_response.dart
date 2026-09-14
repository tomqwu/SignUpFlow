//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'broadcast_response.g.dart';

/// Response from broadcast send.
///
/// Properties:
/// * [estimatedCostCents]
/// * [message]
/// * [queuedCount]
/// * [skippedCount]
/// * [status]
/// * [totalRecipients]
@BuiltValue()
abstract class BroadcastResponse implements Built<BroadcastResponse, BroadcastResponseBuilder> {
  @BuiltValueField(wireName: r'estimated_cost_cents')
  int get estimatedCostCents;

  @BuiltValueField(wireName: r'message')
  String get message;

  @BuiltValueField(wireName: r'queued_count')
  int get queuedCount;

  @BuiltValueField(wireName: r'skipped_count')
  int get skippedCount;

  @BuiltValueField(wireName: r'status')
  String get status;

  @BuiltValueField(wireName: r'total_recipients')
  int get totalRecipients;

  BroadcastResponse._();

  factory BroadcastResponse([void updates(BroadcastResponseBuilder b)]) = _$BroadcastResponse;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(BroadcastResponseBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<BroadcastResponse> get serializer => _$BroadcastResponseSerializer();
}

class _$BroadcastResponseSerializer implements PrimitiveSerializer<BroadcastResponse> {
  @override
  final Iterable<Type> types = const [BroadcastResponse, _$BroadcastResponse];

  @override
  final String wireName = r'BroadcastResponse';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    BroadcastResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'estimated_cost_cents';
    yield serializers.serialize(
      object.estimatedCostCents,
      specifiedType: const FullType(int),
    );
    yield r'message';
    yield serializers.serialize(
      object.message,
      specifiedType: const FullType(String),
    );
    yield r'queued_count';
    yield serializers.serialize(
      object.queuedCount,
      specifiedType: const FullType(int),
    );
    yield r'skipped_count';
    yield serializers.serialize(
      object.skippedCount,
      specifiedType: const FullType(int),
    );
    yield r'status';
    yield serializers.serialize(
      object.status,
      specifiedType: const FullType(String),
    );
    yield r'total_recipients';
    yield serializers.serialize(
      object.totalRecipients,
      specifiedType: const FullType(int),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    BroadcastResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required BroadcastResponseBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'estimated_cost_cents':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.estimatedCostCents = valueDes;
          break;
        case r'message':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.message = valueDes;
          break;
        case r'queued_count':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.queuedCount = valueDes;
          break;
        case r'skipped_count':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.skippedCount = valueDes;
          break;
        case r'status':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.status = valueDes;
          break;
        case r'total_recipients':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.totalRecipients = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  BroadcastResponse deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = BroadcastResponseBuilder();
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

