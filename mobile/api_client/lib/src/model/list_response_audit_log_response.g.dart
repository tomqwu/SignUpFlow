// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'list_response_audit_log_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ListResponseAuditLogResponse extends ListResponseAuditLogResponse {
  @override
  final BuiltList<AuditLogResponse> items;
  @override
  final int limit;
  @override
  final int offset;
  @override
  final int total;

  factory _$ListResponseAuditLogResponse(
          [void Function(ListResponseAuditLogResponseBuilder)? updates]) =>
      (ListResponseAuditLogResponseBuilder()..update(updates))._build();

  _$ListResponseAuditLogResponse._(
      {required this.items,
      required this.limit,
      required this.offset,
      required this.total})
      : super._();
  @override
  ListResponseAuditLogResponse rebuild(
          void Function(ListResponseAuditLogResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ListResponseAuditLogResponseBuilder toBuilder() =>
      ListResponseAuditLogResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ListResponseAuditLogResponse &&
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
    return (newBuiltValueToStringHelper(r'ListResponseAuditLogResponse')
          ..add('items', items)
          ..add('limit', limit)
          ..add('offset', offset)
          ..add('total', total))
        .toString();
  }
}

class ListResponseAuditLogResponseBuilder
    implements
        Builder<ListResponseAuditLogResponse,
            ListResponseAuditLogResponseBuilder> {
  _$ListResponseAuditLogResponse? _$v;

  ListBuilder<AuditLogResponse>? _items;
  ListBuilder<AuditLogResponse> get items =>
      _$this._items ??= ListBuilder<AuditLogResponse>();
  set items(ListBuilder<AuditLogResponse>? items) => _$this._items = items;

  int? _limit;
  int? get limit => _$this._limit;
  set limit(int? limit) => _$this._limit = limit;

  int? _offset;
  int? get offset => _$this._offset;
  set offset(int? offset) => _$this._offset = offset;

  int? _total;
  int? get total => _$this._total;
  set total(int? total) => _$this._total = total;

  ListResponseAuditLogResponseBuilder() {
    ListResponseAuditLogResponse._defaults(this);
  }

  ListResponseAuditLogResponseBuilder get _$this {
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
  void replace(ListResponseAuditLogResponse other) {
    _$v = other as _$ListResponseAuditLogResponse;
  }

  @override
  void update(void Function(ListResponseAuditLogResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ListResponseAuditLogResponse build() => _build();

  _$ListResponseAuditLogResponse _build() {
    _$ListResponseAuditLogResponse _$result;
    try {
      _$result = _$v ??
          _$ListResponseAuditLogResponse._(
            items: items.build(),
            limit: BuiltValueNullFieldError.checkNotNull(
                limit, r'ListResponseAuditLogResponse', 'limit'),
            offset: BuiltValueNullFieldError.checkNotNull(
                offset, r'ListResponseAuditLogResponse', 'offset'),
            total: BuiltValueNullFieldError.checkNotNull(
                total, r'ListResponseAuditLogResponse', 'total'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'items';
        items.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'ListResponseAuditLogResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
