// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'list_response_event_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ListResponseEventResponse extends ListResponseEventResponse {
  @override
  final BuiltList<EventResponse> items;
  @override
  final int limit;
  @override
  final int offset;
  @override
  final int total;

  factory _$ListResponseEventResponse(
          [void Function(ListResponseEventResponseBuilder)? updates]) =>
      (ListResponseEventResponseBuilder()..update(updates))._build();

  _$ListResponseEventResponse._(
      {required this.items,
      required this.limit,
      required this.offset,
      required this.total})
      : super._();
  @override
  ListResponseEventResponse rebuild(
          void Function(ListResponseEventResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ListResponseEventResponseBuilder toBuilder() =>
      ListResponseEventResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ListResponseEventResponse &&
        items == other.items &&
        limit == other.limit &&
        offset == other.offset &&
        total == other.total;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, items.hashCode);
    _$hash = $jc(_$hash, limit.hashCode);
    _$hash = $jc(_$hash, offset.hashCode);
    _$hash = $jc(_$hash, total.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'ListResponseEventResponse')
          ..add('items', items)
          ..add('limit', limit)
          ..add('offset', offset)
          ..add('total', total))
        .toString();
  }
}

class ListResponseEventResponseBuilder
    implements
        Builder<ListResponseEventResponse, ListResponseEventResponseBuilder> {
  _$ListResponseEventResponse? _$v;

  ListBuilder<EventResponse>? _items;
  ListBuilder<EventResponse> get items =>
      _$this._items ??= ListBuilder<EventResponse>();
  set items(ListBuilder<EventResponse>? items) => _$this._items = items;

  int? _limit;
  int? get limit => _$this._limit;
  set limit(int? limit) => _$this._limit = limit;

  int? _offset;
  int? get offset => _$this._offset;
  set offset(int? offset) => _$this._offset = offset;

  int? _total;
  int? get total => _$this._total;
  set total(int? total) => _$this._total = total;

  ListResponseEventResponseBuilder() {
    ListResponseEventResponse._defaults(this);
  }

  ListResponseEventResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _items = $v.items.toBuilder();
      _limit = $v.limit;
      _offset = $v.offset;
      _total = $v.total;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(ListResponseEventResponse other) {
    _$v = other as _$ListResponseEventResponse;
  }

  @override
  void update(void Function(ListResponseEventResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ListResponseEventResponse build() => _build();

  _$ListResponseEventResponse _build() {
    _$ListResponseEventResponse _$result;
    try {
      _$result = _$v ??
          _$ListResponseEventResponse._(
            items: items.build(),
            limit: BuiltValueNullFieldError.checkNotNull(
                limit, r'ListResponseEventResponse', 'limit'),
            offset: BuiltValueNullFieldError.checkNotNull(
                offset, r'ListResponseEventResponse', 'offset'),
            total: BuiltValueNullFieldError.checkNotNull(
                total, r'ListResponseEventResponse', 'total'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'items';
        items.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'ListResponseEventResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
