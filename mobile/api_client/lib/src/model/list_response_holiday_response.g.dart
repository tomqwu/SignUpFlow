// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'list_response_holiday_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ListResponseHolidayResponse extends ListResponseHolidayResponse {
  @override
  final BuiltList<HolidayResponse> items;
  @override
  final int limit;
  @override
  final int offset;
  @override
  final int total;

  factory _$ListResponseHolidayResponse(
          [void Function(ListResponseHolidayResponseBuilder)? updates]) =>
      (ListResponseHolidayResponseBuilder()..update(updates))._build();

  _$ListResponseHolidayResponse._(
      {required this.items,
      required this.limit,
      required this.offset,
      required this.total})
      : super._();
  @override
  ListResponseHolidayResponse rebuild(
          void Function(ListResponseHolidayResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ListResponseHolidayResponseBuilder toBuilder() =>
      ListResponseHolidayResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ListResponseHolidayResponse &&
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
    return (newBuiltValueToStringHelper(r'ListResponseHolidayResponse')
          ..add('items', items)
          ..add('limit', limit)
          ..add('offset', offset)
          ..add('total', total))
        .toString();
  }
}

class ListResponseHolidayResponseBuilder
    implements
        Builder<ListResponseHolidayResponse,
            ListResponseHolidayResponseBuilder> {
  _$ListResponseHolidayResponse? _$v;

  ListBuilder<HolidayResponse>? _items;
  ListBuilder<HolidayResponse> get items =>
      _$this._items ??= ListBuilder<HolidayResponse>();
  set items(ListBuilder<HolidayResponse>? items) => _$this._items = items;

  int? _limit;
  int? get limit => _$this._limit;
  set limit(int? limit) => _$this._limit = limit;

  int? _offset;
  int? get offset => _$this._offset;
  set offset(int? offset) => _$this._offset = offset;

  int? _total;
  int? get total => _$this._total;
  set total(int? total) => _$this._total = total;

  ListResponseHolidayResponseBuilder() {
    ListResponseHolidayResponse._defaults(this);
  }

  ListResponseHolidayResponseBuilder get _$this {
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
  void replace(ListResponseHolidayResponse other) {
    _$v = other as _$ListResponseHolidayResponse;
  }

  @override
  void update(void Function(ListResponseHolidayResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ListResponseHolidayResponse build() => _build();

  _$ListResponseHolidayResponse _build() {
    _$ListResponseHolidayResponse _$result;
    try {
      _$result = _$v ??
          _$ListResponseHolidayResponse._(
            items: items.build(),
            limit: BuiltValueNullFieldError.checkNotNull(
                limit, r'ListResponseHolidayResponse', 'limit'),
            offset: BuiltValueNullFieldError.checkNotNull(
                offset, r'ListResponseHolidayResponse', 'offset'),
            total: BuiltValueNullFieldError.checkNotNull(
                total, r'ListResponseHolidayResponse', 'total'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'items';
        items.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'ListResponseHolidayResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
