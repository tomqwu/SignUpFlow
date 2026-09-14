//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'cancel_request.g.dart';

/// Request schema for cancelling subscription.
///
/// Properties:
/// * [feedback]
/// * [immediately] - Cancel immediately (True) or at period end (False)
/// * [orgId] - Organization ID
/// * [reason]
@BuiltValue()
abstract class CancelRequest implements Built<CancelRequest, CancelRequestBuilder> {
  @BuiltValueField(wireName: r'feedback')
  String? get feedback;

  /// Cancel immediately (True) or at period end (False)
  @BuiltValueField(wireName: r'immediately')
  bool? get immediately;

  /// Organization ID
  @BuiltValueField(wireName: r'org_id')
  String get orgId;

  @BuiltValueField(wireName: r'reason')
  String? get reason;

  CancelRequest._();

  factory CancelRequest([void updates(CancelRequestBuilder b)]) = _$CancelRequest;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(CancelRequestBuilder b) => b
      ..immediately = false;

  @BuiltValueSerializer(custom: true)
  static Serializer<CancelRequest> get serializer => _$CancelRequestSerializer();
}

class _$CancelRequestSerializer implements PrimitiveSerializer<CancelRequest> {
  @override
  final Iterable<Type> types = const [CancelRequest, _$CancelRequest];

  @override
  final String wireName = r'CancelRequest';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    CancelRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    if (object.feedback != null) {
      yield r'feedback';
      yield serializers.serialize(
        object.feedback,
        specifiedType: const FullType.nullable(String),
      );
    }
    if (object.immediately != null) {
      yield r'immediately';
      yield serializers.serialize(
        object.immediately,
        specifiedType: const FullType(bool),
      );
    }
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
    CancelRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required CancelRequestBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'feedback':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.feedback = valueDes;
          break;
        case r'immediately':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(bool),
          ) as bool;
          result.immediately = valueDes;
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
  CancelRequest deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = CancelRequestBuilder();
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
