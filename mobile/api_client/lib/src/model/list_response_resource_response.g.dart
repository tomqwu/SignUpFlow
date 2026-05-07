// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'list_response_resource_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ListResponseResourceResponse extends ListResponseResourceResponse {
  @override
  final BuiltList<ResourceResponse> items;
  @override
  final int limit;
  @override
  final int offset;
  @override
  final int total;

  factory _$ListResponseResourceResponse(
          [void Function(ListResponseResourceResponseBuilder)? updates]) =>
      (ListResponseResourceResponseBuilder()..update(updates))._build();

  _$ListResponseResourceResponse._(
      {required this.items,
      required this.limit,
      required this.offset,
      required this.total})
      : super._();
  @override
  ListResponseResourceResponse rebuild(
          void Function(ListResponseResourceResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ListResponseResourceResponseBuilder toBuilder() =>
      ListResponseResourceResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ListResponseResourceResponse &&
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
    return (newBuiltValueToStringHelper(r'ListResponseResourceResponse')
          ..add('items', items)
          ..add('limit', limit)
          ..add('offset', offset)
          ..add('total', total))
        .toString();
  }
}

class ListResponseResourceResponseBuilder
    implements
        Builder<ListResponseResourceResponse,
            ListResponseResourceResponseBuilder> {
  _$ListResponseResourceResponse? _$v;

  ListBuilder<ResourceResponse>? _items;
  ListBuilder<ResourceResponse> get items =>
      _$this._items ??= ListBuilder<ResourceResponse>();
  set items(ListBuilder<ResourceResponse>? items) => _$this._items = items;

  int? _limit;
  int? get limit => _$this._limit;
  set limit(int? limit) => _$this._limit = limit;

  int? _offset;
  int? get offset => _$this._offset;
  set offset(int? offset) => _$this._offset = offset;

  int? _total;
  int? get total => _$this._total;
  set total(int? total) => _$this._total = total;

  ListResponseResourceResponseBuilder() {
    ListResponseResourceResponse._defaults(this);
  }

  ListResponseResourceResponseBuilder get _$this {
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
  void replace(ListResponseResourceResponse other) {
    _$v = other as _$ListResponseResourceResponse;
  }

  @override
  void update(void Function(ListResponseResourceResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ListResponseResourceResponse build() => _build();

  _$ListResponseResourceResponse _build() {
    _$ListResponseResourceResponse _$result;
    try {
      _$result = _$v ??
          _$ListResponseResourceResponse._(
            items: items.build(),
            limit: BuiltValueNullFieldError.checkNotNull(
                limit, r'ListResponseResourceResponse', 'limit'),
            offset: BuiltValueNullFieldError.checkNotNull(
                offset, r'ListResponseResourceResponse', 'offset'),
            total: BuiltValueNullFieldError.checkNotNull(
                total, r'ListResponseResourceResponse', 'total'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'items';
        items.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'ListResponseResourceResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
