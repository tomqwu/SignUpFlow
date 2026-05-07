//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:signupflow_api/src/model/date.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'solve_request.g.dart';

/// Schema for solve request.
///
/// Properties:
/// * [changeMin] - Enable change minimization
/// * [fromDate] - Start date for schedule
/// * [mode] - Solve mode: strict or relaxed
/// * [orgId] - Organization ID
/// * [toDate] - End date for schedule
@BuiltValue()
abstract class SolveRequest implements Built<SolveRequest, SolveRequestBuilder> {
  /// Enable change minimization
  @BuiltValueField(wireName: r'change_min')
  bool? get changeMin;

  /// Start date for schedule
  @BuiltValueField(wireName: r'from_date')
  Date get fromDate;

  /// Solve mode: strict or relaxed
  @BuiltValueField(wireName: r'mode')
  String? get mode;

  /// Organization ID
  @BuiltValueField(wireName: r'org_id')
  String get orgId;

  /// End date for schedule
  @BuiltValueField(wireName: r'to_date')
  Date get toDate;

  SolveRequest._();

  factory SolveRequest([void updates(SolveRequestBuilder b)]) = _$SolveRequest;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(SolveRequestBuilder b) => b
      ..changeMin = false
      ..mode = 'strict';

  @BuiltValueSerializer(custom: true)
  static Serializer<SolveRequest> get serializer => _$SolveRequestSerializer();
}

class _$SolveRequestSerializer implements PrimitiveSerializer<SolveRequest> {
  @override
  final Iterable<Type> types = const [SolveRequest, _$SolveRequest];

  @override
  final String wireName = r'SolveRequest';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    SolveRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    if (object.changeMin != null) {
      yield r'change_min';
      yield serializers.serialize(
        object.changeMin,
        specifiedType: const FullType(bool),
      );
    }
    yield r'from_date';
    yield serializers.serialize(
      object.fromDate,
      specifiedType: const FullType(Date),
    );
    if (object.mode != null) {
      yield r'mode';
      yield serializers.serialize(
        object.mode,
        specifiedType: const FullType(String),
      );
    }
    yield r'org_id';
    yield serializers.serialize(
      object.orgId,
      specifiedType: const FullType(String),
    );
    yield r'to_date';
    yield serializers.serialize(
      object.toDate,
      specifiedType: const FullType(Date),
    );
  }

  @override
  Object serialize(
    Serializers serializers,
    SolveRequest object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required SolveRequestBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'change_min':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(bool),
          ) as bool;
          result.changeMin = valueDes;
          break;
        case r'from_date':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(Date),
          ) as Date;
          result.fromDate = valueDes;
          break;
        case r'mode':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.mode = valueDes;
          break;
        case r'org_id':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(String),
          ) as String;
          result.orgId = valueDes;
          break;
        case r'to_date':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(Date),
          ) as Date;
          result.toDate = valueDes;
          break;
        default:
          unhandled.add(key);
          unhandled.add(value);
          break;
      }
    }
  }

  @override
  SolveRequest deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = SolveRequestBuilder();
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

