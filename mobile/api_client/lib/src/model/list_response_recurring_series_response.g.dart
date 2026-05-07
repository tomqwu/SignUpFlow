// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'list_response_recurring_series_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ListResponseRecurringSeriesResponse
    extends ListResponseRecurringSeriesResponse {
  @override
  final BuiltList<RecurringSeriesResponse> items;
  @override
  final int limit;
  @override
  final int offset;
  @override
  final int total;

  factory _$ListResponseRecurringSeriesResponse(
          [void Function(ListResponseRecurringSeriesResponseBuilder)?
              updates]) =>
      (ListResponseRecurringSeriesResponseBuilder()..update(updates))._build();

  _$ListResponseRecurringSeriesResponse._(
      {required this.items,
      required this.limit,
      required this.offset,
      required this.total})
      : super._();
  @override
  ListResponseRecurringSeriesResponse rebuild(
          void Function(ListResponseRecurringSeriesResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ListResponseRecurringSeriesResponseBuilder toBuilder() =>
      ListResponseRecurringSeriesResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ListResponseRecurringSeriesResponse &&
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
    return (newBuiltValueToStringHelper(r'ListResponseRecurringSeriesResponse')
          ..add('items', items)
          ..add('limit', limit)
          ..add('offset', offset)
          ..add('total', total))
        .toString();
  }
}

class ListResponseRecurringSeriesResponseBuilder
    implements
        Builder<ListResponseRecurringSeriesResponse,
            ListResponseRecurringSeriesResponseBuilder> {
  _$ListResponseRecurringSeriesResponse? _$v;

  ListBuilder<RecurringSeriesResponse>? _items;
  ListBuilder<RecurringSeriesResponse> get items =>
      _$this._items ??= ListBuilder<RecurringSeriesResponse>();
  set items(ListBuilder<RecurringSeriesResponse>? items) =>
      _$this._items = items;

  int? _limit;
  int? get limit => _$this._limit;
  set limit(int? limit) => _$this._limit = limit;

  int? _offset;
  int? get offset => _$this._offset;
  set offset(int? offset) => _$this._offset = offset;

  int? _total;
  int? get total => _$this._total;
  set total(int? total) => _$this._total = total;

  ListResponseRecurringSeriesResponseBuilder() {
    ListResponseRecurringSeriesResponse._defaults(this);
  }

  ListResponseRecurringSeriesResponseBuilder get _$this {
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
  void replace(ListResponseRecurringSeriesResponse other) {
    _$v = other as _$ListResponseRecurringSeriesResponse;
  }

  @override
  void update(
      void Function(ListResponseRecurringSeriesResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ListResponseRecurringSeriesResponse build() => _build();

  _$ListResponseRecurringSeriesResponse _build() {
    _$ListResponseRecurringSeriesResponse _$result;
    try {
      _$result = _$v ??
          _$ListResponseRecurringSeriesResponse._(
            items: items.build(),
            limit: BuiltValueNullFieldError.checkNotNull(
                limit, r'ListResponseRecurringSeriesResponse', 'limit'),
            offset: BuiltValueNullFieldError.checkNotNull(
                offset, r'ListResponseRecurringSeriesResponse', 'offset'),
            total: BuiltValueNullFieldError.checkNotNull(
                total, r'ListResponseRecurringSeriesResponse', 'total'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'items';
        items.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(r'ListResponseRecurringSeriesResponse',
            _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
