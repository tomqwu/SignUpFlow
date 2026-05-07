//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'violation_info.g.dart';

/// Schema for constraint violation.
///
/// Properties:
/// * [constraintKey] 
/// * [entities] 
/// * [message] 
/// * [severity] 
@BuiltValue()
abstract class ViolationInfo implements Built<ViolationInfo, ViolationInfoBuilder> {
  @BuiltValueField(wireName: r'constraint_key')
  String get constraintKey;

  @BuiltValueField(wireName: r'entities')
  BuiltList<String> get entities;

  @BuiltValueField(wireName: r'message')
  String get message;

  @BuiltValueField(wireName: r'severity')
  String get severity;

  ViolationInfo._();

  factory ViolationInfo([void updates(ViolationInfoBuilder b)]) = _$ViolationInfo;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(ViolationInfoBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<ViolationInfo> get serializer => _$ViolationInfoSerializer();
}

class _$ViolationInfoSerializer implements PrimitiveSerializer<ViolationInfo> {
  @override
  final Iterable<Type> types = const [ViolationInfo, _$ViolationInfo];

  @override
  final String wireName = r'ViolationInfo';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    ViolationInfo object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'constraint_key';
    yield serializers.serialize(
      object.constraintKey,
      specifiedType: const FullType(String),
    );
    yield r'entities';
    yield serializers.serialize(
      object.entities,
      specifiedType: const FullType(BuiltList, [FullType(String)]),
    );
    yield r'message';
    yield serializers.serialize(
      object.message,
      specifiedType: const FullType(String),
    );
    yield r'severity';
    yield serializers.serialize(
      object.severity,
      specifiedType: const FullType(String),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    ViolationInfo object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required ViolationInfoBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'constraint_key':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.constraintKey = valueDes;
          break;
        case r'entities':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(String)]),
          ) as BuiltList<String>;
          result.entities.replace(valueDes);
          break;
        case r'message':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.message = valueDes;
          break;
        case r'severity':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.severity = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  ViolationInfo deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = ViolationInfoBuilder();
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

