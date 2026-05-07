//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:built_collection/built_collection.dart';
import 'package:signupflow_api/src/model/recurring_series_response.dart';
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'list_response_recurring_series_response.g.dart';

/// ListResponseRecurringSeriesResponse
///
/// Properties:
/// * [items] 
/// * [limit] 
/// * [offset] 
/// * [total] 
@BuiltValue()
abstract class ListResponseRecurringSeriesResponse implements Built<ListResponseRecurringSeriesResponse, ListResponseRecurringSeriesResponseBuilder> {
  @BuiltValueField(wireName: r'items')
  BuiltList<RecurringSeriesResponse> get items;

  @BuiltValueField(wireName: r'limit')
  int get limit;

  @BuiltValueField(wireName: r'offset')
  int get offset;

  @BuiltValueField(wireName: r'total')
  int get total;

  ListResponseRecurringSeriesResponse._();

  factory ListResponseRecurringSeriesResponse([void updates(ListResponseRecurringSeriesResponseBuilder b)]) = _$ListResponseRecurringSeriesResponse;

  @BuiltValueHook(initializeBuilder: true)
  static void _defaults(ListResponseRecurringSeriesResponseBuilder b) => b;

  @BuiltValueSerializer(custom: true)
  static Serializer<ListResponseRecurringSeriesResponse> get serializer => _$ListResponseRecurringSeriesResponseSerializer();
}

class _$ListResponseRecurringSeriesResponseSerializer implements PrimitiveSerializer<ListResponseRecurringSeriesResponse> {
  @override
  final Iterable<Type> types = const [ListResponseRecurringSeriesResponse, _$ListResponseRecurringSeriesResponse];

  @override
  final String wireName = r'ListResponseRecurringSeriesResponse';

  Iterable<Object?> _serializeProperties(
    Serializers serializers,
    ListResponseRecurringSeriesResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) sync* {
    yield r'items';
    yield serializers.serialize(
      object.items,
      specifiedType: const FullType(BuiltList, [FullType(RecurringSeriesResponse)]),
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
    ListResponseRecurringSeriesResponse object, {
    FullType specifiedType = FullType.unspecified,
  }) {
    return _serializeProperties(serializers, object, specifiedType: specifiedType).toList();
  }

  void _deserializeProperties(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
    required List<Object?> serializedList,
    required ListResponseRecurringSeriesResponseBuilder result,
    required List<Object?> unhandled,
  }) {
    for (var i = 0; i < serializedList.length; i += 2) {
      final key = serializedList[i] as String;
      final value = serializedList[i + 1];
      switch (key) {
        case r'items':
          final valueDes = serializers.deserialize(
            value,
            specifiedType: const FullType(BuiltList, [FullType(RecurringSeriesResponse)]),
          ) as BuiltList<RecurringSeriesResponse>;
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
  ListResponseRecurringSeriesResponse deserialize(
    Serializers serializers,
    Object serialized, {
    FullType specifiedType = FullType.unspecified,
  }) {
    final result = ListResponseRecurringSeriesResponseBuilder();
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

