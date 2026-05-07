// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'list_response_constraint_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ListResponseConstraintResponse extends ListResponseConstraintResponse {
  @override
  final BuiltList<ConstraintResponse> items;
  @override
  final int limit;
  @override
  final int offset;
  @override
  final int total;

  factory _$ListResponseConstraintResponse(
          [void Function(ListResponseConstraintResponseBuilder)? updates]) =>
      (ListResponseConstraintResponseBuilder()..update(updates))._build();

  _$ListResponseConstraintResponse._(
      {required this.items,
      required this.limit,
      required this.offset,
      required this.total})
      : super._();
  @override
  ListResponseConstraintResponse rebuild(
          void Function(ListResponseConstraintResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ListResponseConstraintResponseBuilder toBuilder() =>
      ListResponseConstraintResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ListResponseConstraintResponse &&
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
    return (newBuiltValueToStringHelper(r'ListResponseConstraintResponse')
          ..add('items', items)
          ..add('limit', limit)
          ..add('offset', offset)
          ..add('total', total))
        .toString();
  }
}

class ListResponseConstraintResponseBuilder
    implements
        Builder<ListResponseConstraintResponse,
            ListResponseConstraintResponseBuilder> {
  _$ListResponseConstraintResponse? _$v;

  ListBuilder<ConstraintResponse>? _items;
  ListBuilder<ConstraintResponse> get items =>
      _$this._items ??= ListBuilder<ConstraintResponse>();
  set items(ListBuilder<ConstraintResponse>? items) => _$this._items = items;

  int? _limit;
  int? get limit => _$this._limit;
  set limit(int? limit) => _$this._limit = limit;

  int? _offset;
  int? get offset => _$this._offset;
  set offset(int? offset) => _$this._offset = offset;

  int? _total;
  int? get total => _$this._total;
  set total(int? total) => _$this._total = total;

  ListResponseConstraintResponseBuilder() {
    ListResponseConstraintResponse._defaults(this);
  }

  ListResponseConstraintResponseBuilder get _$this {
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
  void replace(ListResponseConstraintResponse other) {
    _$v = other as _$ListResponseConstraintResponse;
  }

  @override
  void update(void Function(ListResponseConstraintResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ListResponseConstraintResponse build() => _build();

  _$ListResponseConstraintResponse _build() {
    _$ListResponseConstraintResponse _$result;
    try {
      _$result = _$v ??
          _$ListResponseConstraintResponse._(
            items: items.build(),
            limit: BuiltValueNullFieldError.checkNotNull(
                limit, r'ListResponseConstraintResponse', 'limit'),
            offset: BuiltValueNullFieldError.checkNotNull(
                offset, r'ListResponseConstraintResponse', 'offset'),
            total: BuiltValueNullFieldError.checkNotNull(
                total, r'ListResponseConstraintResponse', 'total'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'items';
        items.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'ListResponseConstraintResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
