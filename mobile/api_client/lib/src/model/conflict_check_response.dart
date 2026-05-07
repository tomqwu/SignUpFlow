//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:signupflow_api/src/model/conflict_type.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'conflict_check_response.g.dart';

/// Response schema for conflict check.
///
/// Properties:
/// * [canAssign] - Whether assignment should be allowed despite conflicts
/// * [conflicts] - List of detected conflicts
/// * [hasConflicts] - Whether conflicts were detected
@BuiltValue()
abstract class ConflictCheckResponse implements Built<ConflictCheckResponse, ConflictCheckResponseBuilder> {
  /// Whether assignment should be allowed despite conflicts
  @BuiltValueField(wireName: r'can_assign')
  bool get canAssign;

  /// List of detected conflicts
  @BuiltValueField(wireName: r'conflicts')
  BuiltList<ConflictType>? get conflicts;

  /// Whether conflicts were detected
  @BuiltValueField(wireName: r'has_conflicts')
  bool get hasConflicts;

  ConflictCheckResponse._();

  factory ConflictCheckResponse([void updates(ConflictCheckResponseBuilder b)]) = _$ConflictCheckResponse;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(ConflictCheckResponseBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<ConflictCheckResponse> get serializer => _$ConflictCheckResponseSerializer();
}

class _$ConflictCheckResponseSerializer implements PrimitiveSerializer<ConflictCheckResponse> {
  @override
  final Iterable<Type> types = const [ConflictCheckResponse, _$ConflictCheckResponse];

  @override
  final String wireName = r'ConflictCheckResponse';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    ConflictCheckResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'can_assign';
    yield serializers.serialize(
      object.canAssign,
      specifiedType: const FullType(bool),
    );
    if (object.conflicts != null) {
      yield r'conflicts';
      yield serializers.serialize(
        object.conflicts,
        specifiedType: const FullType(BuiltList, [FullType(ConflictType)]),
      );
    }
    yield r'has_conflicts';
    yield serializers.serialize(
      object.hasConflicts,
      specifiedType: const FullType(bool),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    ConflictCheckResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required ConflictCheckResponseBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'can_assign':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(bool),
          ) as bool;
          result.canAssign = valueDes;
          break;
        case r'conflicts':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(ConflictType)]),
          ) as BuiltList<ConflictType>;
          result.conflicts.replace(valueDes);
          break;
        case r'has_conflicts':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(bool),
          ) as bool;
          result.hasConflicts = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  ConflictCheckResponse deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = ConflictCheckResponseBuilder();
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

