// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'list_response_solution_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ListResponseSolutionResponse extends ListResponseSolutionResponse {
  @override
  final BuiltList<SolutionResponse> items;
  @override
  final int limit;
  @override
  final int offset;
  @override
  final int total;

  factory _$ListResponseSolutionResponse(
          [void Function(ListResponseSolutionResponseBuilder)? updates]) =>
      (ListResponseSolutionResponseBuilder()..update(updates))._build();

  _$ListResponseSolutionResponse._(
      {required this.items,
      required this.limit,
      required this.offset,
      required this.total})
      : super._();
  @override
  ListResponseSolutionResponse rebuild(
          void Function(ListResponseSolutionResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ListResponseSolutionResponseBuilder toBuilder() =>
      ListResponseSolutionResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ListResponseSolutionResponse &&
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
    return (newBuiltValueToStringHelper(r'ListResponseSolutionResponse')
          ..add('items', items)
          ..add('limit', limit)
          ..add('offset', offset)
          ..add('total', total))
        .toString();
  }
}

class ListResponseSolutionResponseBuilder
    implements
        Builder<ListResponseSolutionResponse,
            ListResponseSolutionResponseBuilder> {
  _$ListResponseSolutionResponse? _$v;

  ListBuilder<SolutionResponse>? _items;
  ListBuilder<SolutionResponse> get items =>
      _$this._items ??= ListBuilder<SolutionResponse>();
  set items(ListBuilder<SolutionResponse>? items) => _$this._items = items;

  int? _limit;
  int? get limit => _$this._limit;
  set limit(int? limit) => _$this._limit = limit;

  int? _offset;
  int? get offset => _$this._offset;
  set offset(int? offset) => _$this._offset = offset;

  int? _total;
  int? get total => _$this._total;
  set total(int? total) => _$this._total = total;

  ListResponseSolutionResponseBuilder() {
    ListResponseSolutionResponse._defaults(this);
  }

  ListResponseSolutionResponseBuilder get _$this {
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
  void replace(ListResponseSolutionResponse other) {
    _$v = other as _$ListResponseSolutionResponse;
  }

  @override
  void update(void Function(ListResponseSolutionResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ListResponseSolutionResponse build() => _build();

  _$ListResponseSolutionResponse _build() {
    _$ListResponseSolutionResponse _$result;
    try {
      _$result = _$v ??
          _$ListResponseSolutionResponse._(
            items: items.build(),
            limit: BuiltValueNullFieldError.checkNotNull(
                limit, r'ListResponseSolutionResponse', 'limit'),
            offset: BuiltValueNullFieldError.checkNotNull(
                offset, r'ListResponseSolutionResponse', 'offset'),
            total: BuiltValueNullFieldError.checkNotNull(
                total, r'ListResponseSolutionResponse', 'total'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'items';
        items.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'ListResponseSolutionResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
