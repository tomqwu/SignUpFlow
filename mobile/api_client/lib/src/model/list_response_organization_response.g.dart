// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'list_response_organization_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ListResponseOrganizationResponse
    extends ListResponseOrganizationResponse {
  @override
  final BuiltList<OrganizationResponse> items;
  @override
  final int limit;
  @override
  final int offset;
  @override
  final int total;

  factory _$ListResponseOrganizationResponse(
          [void Function(ListResponseOrganizationResponseBuilder)? updates]) =>
      (ListResponseOrganizationResponseBuilder()..update(updates))._build();

  _$ListResponseOrganizationResponse._(
      {required this.items,
      required this.limit,
      required this.offset,
      required this.total})
      : super._();
  @override
  ListResponseOrganizationResponse rebuild(
          void Function(ListResponseOrganizationResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ListResponseOrganizationResponseBuilder toBuilder() =>
      ListResponseOrganizationResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ListResponseOrganizationResponse &&
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
    return (newBuiltValueToStringHelper(r'ListResponseOrganizationResponse')
          ..add('items', items)
          ..add('limit', limit)
          ..add('offset', offset)
          ..add('total', total))
        .toString();
  }
}

class ListResponseOrganizationResponseBuilder
    implements
        Builder<ListResponseOrganizationResponse,
            ListResponseOrganizationResponseBuilder> {
  _$ListResponseOrganizationResponse? _$v;

  ListBuilder<OrganizationResponse>? _items;
  ListBuilder<OrganizationResponse> get items =>
      _$this._items ??= ListBuilder<OrganizationResponse>();
  set items(ListBuilder<OrganizationResponse>? items) => _$this._items = items;

  int? _limit;
  int? get limit => _$this._limit;
  set limit(int? limit) => _$this._limit = limit;

  int? _offset;
  int? get offset => _$this._offset;
  set offset(int? offset) => _$this._offset = offset;

  int? _total;
  int? get total => _$this._total;
  set total(int? total) => _$this._total = total;

  ListResponseOrganizationResponseBuilder() {
    ListResponseOrganizationResponse._defaults(this);
  }

  ListResponseOrganizationResponseBuilder get _$this {
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
  void replace(ListResponseOrganizationResponse other) {
    _$v = other as _$ListResponseOrganizationResponse;
  }

  @override
  void update(void Function(ListResponseOrganizationResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ListResponseOrganizationResponse build() => _build();

  _$ListResponseOrganizationResponse _build() {
    _$ListResponseOrganizationResponse _$result;
    try {
      _$result = _$v ??
          _$ListResponseOrganizationResponse._(
            items: items.build(),
            limit: BuiltValueNullFieldError.checkNotNull(
                limit, r'ListResponseOrganizationResponse', 'limit'),
            offset: BuiltValueNullFieldError.checkNotNull(
                offset, r'ListResponseOrganizationResponse', 'offset'),
            total: BuiltValueNullFieldError.checkNotNull(
                total, r'ListResponseOrganizationResponse', 'total'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'items';
        items.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'ListResponseOrganizationResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
