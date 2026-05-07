//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:signupflow_api/src/model/assignment_response.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'list_response_assignment_response.g.dart';

/// ListResponseAssignmentResponse
///
/// Properties:
/// * [items] 
/// * [limit] 
/// * [offset] 
/// * [total] 
@BuiltValue()
abstract class ListResponseAssignmentResponse implements Built<ListResponseAssignmentResponse, ListResponseAssignmentResponseBuilder> {
  @BuiltValueField(wireName: r'items')
  BuiltList<AssignmentResponse> get items;

  @BuiltValueField(wireName: r'limit')
  int get limit;

  @BuiltValueField(wireName: r'offset')
  int get offset;

  @BuiltValueField(wireName: r'total')
  int get total;

  ListResponseAssignmentResponse._();

  factory ListResponseAssignmentResponse([void updates(ListResponseAssignmentResponseBuilder b)]) = _$ListResponseAssignmentResponse;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(ListResponseAssignmentResponseBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<ListResponseAssignmentResponse> get serializer => _$ListResponseAssignmentResponseSerializer();
}

class _$ListResponseAssignmentResponseSerializer implements PrimitiveSerializer<ListResponseAssignmentResponse> {
  @override
  final Iterable<Type> types = const [ListResponseAssignmentResponse, _$ListResponseAssignmentResponse];

  @override
  final String wireName = r'ListResponseAssignmentResponse';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    ListResponseAssignmentResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'items';
    yield serializers.serialize(
      object.items,
      specifiedType: const FullType(BuiltList, [FullType(AssignmentResponse)]),
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
    ListResponseAssignmentResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required ListResponseAssignmentResponseBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'items':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(AssignmentResponse)]),
          ) as BuiltList<AssignmentResponse>;
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
  ListResponseAssignmentResponse deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = ListResponseAssignmentResponseBuilder();
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

