// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'list_response_person_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ListResponsePersonResponse extends ListResponsePersonResponse {
  @override
  final BuiltList<PersonResponse> items;
  @override
  final int limit;
  @override
  final int offset;
  @override
  final int total;

  factory _$ListResponsePersonResponse(
          [void Function(ListResponsePersonResponseBuilder)? updates]) =>
      (ListResponsePersonResponseBuilder()..update(updates))._build();

  _$ListResponsePersonResponse._(
      {required this.items,
      required this.limit,
      required this.offset,
      required this.total})
      : super._();
  @override
  ListResponsePersonResponse rebuild(
          void Function(ListResponsePersonResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ListResponsePersonResponseBuilder toBuilder() =>
      ListResponsePersonResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ListResponsePersonResponse &&
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
    return (newBuiltValueToStringHelper(r'ListResponsePersonResponse')
          ..add('items', items)
          ..add('limit', limit)
          ..add('offset', offset)
          ..add('total', total))
        .toString();
  }
}

class ListResponsePersonResponseBuilder
    implements
        Builder<ListResponsePersonResponse, ListResponsePersonResponseBuilder> {
  _$ListResponsePersonResponse? _$v;

  ListBuilder<PersonResponse>? _items;
  ListBuilder<PersonResponse> get items =>
      _$this._items ??= ListBuilder<PersonResponse>();
  set items(ListBuilder<PersonResponse>? items) => _$this._items = items;

  int? _limit;
  int? get limit => _$this._limit;
  set limit(int? limit) => _$this._limit = limit;

  int? _offset;
  int? get offset => _$this._offset;
  set offset(int? offset) => _$this._offset = offset;

  int? _total;
  int? get total => _$this._total;
  set total(int? total) => _$this._total = total;

  ListResponsePersonResponseBuilder() {
    ListResponsePersonResponse._defaults(this);
  }

  ListResponsePersonResponseBuilder get _$this {
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
  void replace(ListResponsePersonResponse other) {
    _$v = other as _$ListResponsePersonResponse;
  }

  @override
  void update(void Function(ListResponsePersonResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ListResponsePersonResponse build() => _build();

  _$ListResponsePersonResponse _build() {
    _$ListResponsePersonResponse _$result;
    try {
      _$result = _$v ??
          _$ListResponsePersonResponse._(
            items: items.build(),
            limit: BuiltValueNullFieldError.checkNotNull(
                limit, r'ListResponsePersonResponse', 'limit'),
            offset: BuiltValueNullFieldError.checkNotNull(
                offset, r'ListResponsePersonResponse', 'offset'),
            total: BuiltValueNullFieldError.checkNotNull(
                total, r'ListResponsePersonResponse', 'total'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'items';
        items.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'ListResponsePersonResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
