//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:signupflow_api/src/model/solution_response.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'list_response_solution_response.g.dart';

/// ListResponseSolutionResponse
///
/// Properties:
/// * [items] 
/// * [limit] 
/// * [offset] 
/// * [total] 
@BuiltValue()
abstract class ListResponseSolutionResponse implements Built<ListResponseSolutionResponse, ListResponseSolutionResponseBuilder> {
  @BuiltValueField(wireName: r'items')
  BuiltList<SolutionResponse> get items;

  @BuiltValueField(wireName: r'limit')
  int get limit;

  @BuiltValueField(wireName: r'offset')
  int get offset;

  @BuiltValueField(wireName: r'total')
  int get total;

  ListResponseSolutionResponse._();

  factory ListResponseSolutionResponse([void updates(ListResponseSolutionResponseBuilder b)]) = _$ListResponseSolutionResponse;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(ListResponseSolutionResponseBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<ListResponseSolutionResponse> get serializer => _$ListResponseSolutionResponseSerializer();
}

class _$ListResponseSolutionResponseSerializer implements PrimitiveSerializer<ListResponseSolutionResponse> {
  @override
  final Iterable<Type> types = const [ListResponseSolutionResponse, _$ListResponseSolutionResponse];

  @override
  final String wireName = r'ListResponseSolutionResponse';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    ListResponseSolutionResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'items';
    yield serializers.serialize(
      object.items,
      specifiedType: const FullType(BuiltList, [FullType(SolutionResponse)]),
    );
    yield r'limit';
    yield serializers.serialize(
      object.limit,
      specifiedType: const FullType(int),
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
    ListResponseSolutionResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required ListResponseSolutionResponseBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'items':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(SolutionResponse)]),
          ) as BuiltList<SolutionResponse>;
          result.items.replace(valueDes);
          break;
        case r'limit':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(int),
          ) as int;
          result.limit = valueDes;
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
  ListResponseSolutionResponse deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = ListResponseSolutionResponseBuilder();
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

