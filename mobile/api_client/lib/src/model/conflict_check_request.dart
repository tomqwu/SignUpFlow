//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'conflict_check_request.g.dart';

/// Request schema for checking conflicts.
///
/// Properties:
/// * [eventId] - Event ID to assign to
/// * [personId] - Person ID to check
@BuiltValue()
abstract class ConflictCheckRequest implements Built<ConflictCheckRequest, ConflictCheckRequestBuilder> {
  /// Event ID to assign to
  @BuiltValueField(wireName: r'event_id')
  String get eventId;

  /// Person ID to check
  @BuiltValueField(wireName: r'person_id')
  String get personId;

  ConflictCheckRequest._();

  factory ConflictCheckRequest([void updates(ConflictCheckRequestBuilder b)]) = _$ConflictCheckRequest;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(ConflictCheckRequestBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<ConflictCheckRequest> get serializer => _$ConflictCheckRequestSerializer();
}

class _$ConflictCheckRequestSerializer implements PrimitiveSerializer<ConflictCheckRequest> {
  @override
  final Iterable<Type> types = const [ConflictCheckRequest, _$ConflictCheckRequest];

  @override
  final String wireName = r'ConflictCheckRequest';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    ConflictCheckRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'event_id';
    yield serializers.serialize(
      object.eventId,
      specifiedType: const FullType(String),
    );
    yield r'person_id';
    yield serializers.serialize(
      object.personId,
      specifiedType: const FullType(String),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    ConflictCheckRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required ConflictCheckRequestBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'event_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.eventId = valueDes;
          break;
        case r'person_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.personId = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  ConflictCheckRequest deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = ConflictCheckRequestBuilder();
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

