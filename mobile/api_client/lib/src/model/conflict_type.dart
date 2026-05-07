//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'conflict_type.g.dart';

/// A detected scheduling conflict.
///
/// Properties:
/// * [conflictingEventId] 
/// * [endTime] 
/// * [message] - Human-readable conflict message
/// * [startTime] 
/// * [type] - Conflict type: already_assigned, time_off, double_booked
@BuiltValue()
abstract class ConflictType implements Built<ConflictType, ConflictTypeBuilder> {
  @BuiltValueField(wireName: r'conflicting_event_id')
  String? get conflictingEventId;

  @BuiltValueField(wireName: r'end_time')
  DateTime? get endTime;

  /// Human-readable conflict message
  @BuiltValueField(wireName: r'message')
  String get message;

  @BuiltValueField(wireName: r'start_time')
  DateTime? get startTime;

  /// Conflict type: already_assigned, time_off, double_booked
  @BuiltValueField(wireName: r'type')
  String get type;

  ConflictType._();

  factory ConflictType([void updates(ConflictTypeBuilder b)]) = _$ConflictType;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(ConflictTypeBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<ConflictType> get serializer => _$ConflictTypeSerializer();
}

class _$ConflictTypeSerializer implements PrimitiveSerializer<ConflictType> {
  @override
  final Iterable<Type> types = const [ConflictType, _$ConflictType];

  @override
  final String wireName = r'ConflictType';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    ConflictType object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    if (object.conflictingEventId != null) {
      yield r'conflicting_event_id';
      yield serializers.serialize(
        object.conflictingEventId,
        specifiedType: const FullType.nullable(String),
      );
    }
    if (object.endTime != null) {
      yield r'end_time';
      yield serializers.serialize(
        object.endTime,
        specifiedType: const FullType.nullable(DateTime),
      );
    }
    yield r'message';
    yield serializers.serialize(
      object.message,
      specifiedType: const FullType(String),
    );
    if (object.startTime != null) {
      yield r'start_time';
      yield serializers.serialize(
        object.startTime,
        specifiedType: const FullType.nullable(DateTime),
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
    ConflictType object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required ConflictTypeBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'conflicting_event_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(String),
          ) as String?;
          if (valueDes == null) continue;
          result.conflictingEventId = valueDes;
          break;
        case r'end_time':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(DateTime),
          ) as DateTime?;
          if (valueDes == null) continue;
          result.endTime = valueDes;
          break;
        case r'message':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.message = valueDes;
          break;
        case r'start_time':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType.nullable(DateTime),
          ) as DateTime?;
          if (valueDes == null) continue;
          result.startTime = valueDes;
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
  ConflictType deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = ConflictTypeBuilder();
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

