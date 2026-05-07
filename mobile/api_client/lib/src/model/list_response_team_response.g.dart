// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'list_response_team_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ListResponseTeamResponse extends ListResponseTeamResponse {
  @override
  final BuiltList<TeamResponse> items;
  @override
  final int limit;
  @override
  final int offset;
  @override
  final int total;

  factory _$ListResponseTeamResponse(
          [void Function(ListResponseTeamResponseBuilder)? updates]) =>
      (ListResponseTeamResponseBuilder()..update(updates))._build();

  _$ListResponseTeamResponse._(
      {required this.items,
      required this.limit,
      required this.offset,
      required this.total})
      : super._();
  @override
  ListResponseTeamResponse rebuild(
          void Function(ListResponseTeamResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ListResponseTeamResponseBuilder toBuilder() =>
      ListResponseTeamResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ListResponseTeamResponse &&
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
    return (newBuiltValueToStringHelper(r'ListResponseTeamResponse')
          ..add('items', items)
          ..add('limit', limit)
          ..add('offset', offset)
          ..add('total', total))
        .toString();
  }
}

class ListResponseTeamResponseBuilder
    implements
        Builder<ListResponseTeamResponse, ListResponseTeamResponseBuilder> {
  _$ListResponseTeamResponse? _$v;

  ListBuilder<TeamResponse>? _items;
  ListBuilder<TeamResponse> get items =>
      _$this._items ??= ListBuilder<TeamResponse>();
  set items(ListBuilder<TeamResponse>? items) => _$this._items = items;

  int? _limit;
  int? get limit => _$this._limit;
  set limit(int? limit) => _$this._limit = limit;

  int? _offset;
  int? get offset => _$this._offset;
  set offset(int? offset) => _$this._offset = offset;

  int? _total;
  int? get total => _$this._total;
  set total(int? total) => _$this._total = total;

  ListResponseTeamResponseBuilder() {
    ListResponseTeamResponse._defaults(this);
  }

  ListResponseTeamResponseBuilder get _$this {
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
  void replace(ListResponseTeamResponse other) {
    _$v = other as _$ListResponseTeamResponse;
  }

  @override
  void update(void Function(ListResponseTeamResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ListResponseTeamResponse build() => _build();

  _$ListResponseTeamResponse _build() {
    _$ListResponseTeamResponse _$result;
    try {
      _$result = _$v ??
          _$ListResponseTeamResponse._(
            items: items.build(),
            limit: BuiltValueNullFieldError.checkNotNull(
                limit, r'ListResponseTeamResponse', 'limit'),
            offset: BuiltValueNullFieldError.checkNotNull(
                offset, r'ListResponseTeamResponse', 'offset'),
            total: BuiltValueNullFieldError.checkNotNull(
                total, r'ListResponseTeamResponse', 'total'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'items';
        items.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'ListResponseTeamResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
