// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'list_response_invitation_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ListResponseInvitationResponse extends ListResponseInvitationResponse {
  @override
  final BuiltList<InvitationResponse> items;
  @override
  final int limit;
  @override
  final int offset;
  @override
  final int total;

  factory _$ListResponseInvitationResponse(
          [void Function(ListResponseInvitationResponseBuilder)? updates]) =>
      (ListResponseInvitationResponseBuilder()..update(updates))._build();

  _$ListResponseInvitationResponse._(
      {required this.items,
      required this.limit,
      required this.offset,
      required this.total})
      : super._();
  @override
  ListResponseInvitationResponse rebuild(
          void Function(ListResponseInvitationResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ListResponseInvitationResponseBuilder toBuilder() =>
      ListResponseInvitationResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ListResponseInvitationResponse &&
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
    return (newBuiltValueToStringHelper(r'ListResponseInvitationResponse')
          ..add('items', items)
          ..add('limit', limit)
          ..add('offset', offset)
          ..add('total', total))
        .toString();
  }
}

class ListResponseInvitationResponseBuilder
    implements
        Builder<ListResponseInvitationResponse,
            ListResponseInvitationResponseBuilder> {
  _$ListResponseInvitationResponse? _$v;

  ListBuilder<InvitationResponse>? _items;
  ListBuilder<InvitationResponse> get items =>
      _$this._items ??= ListBuilder<InvitationResponse>();
  set items(ListBuilder<InvitationResponse>? items) => _$this._items = items;

  int? _limit;
  int? get limit => _$this._limit;
  set limit(int? limit) => _$this._limit = limit;

  int? _offset;
  int? get offset => _$this._offset;
  set offset(int? offset) => _$this._offset = offset;

  int? _total;
  int? get total => _$this._total;
  set total(int? total) => _$this._total = total;

  ListResponseInvitationResponseBuilder() {
    ListResponseInvitationResponse._defaults(this);
  }

  ListResponseInvitationResponseBuilder get _$this {
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
  void replace(ListResponseInvitationResponse other) {
    _$v = other as _$ListResponseInvitationResponse;
  }

  @override
  void update(void Function(ListResponseInvitationResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ListResponseInvitationResponse build() => _build();

  _$ListResponseInvitationResponse _build() {
    _$ListResponseInvitationResponse _$result;
    try {
      _$result = _$v ??
          _$ListResponseInvitationResponse._(
            items: items.build(),
            limit: BuiltValueNullFieldError.checkNotNull(
                limit, r'ListResponseInvitationResponse', 'limit'),
            offset: BuiltValueNullFieldError.checkNotNull(
                offset, r'ListResponseInvitationResponse', 'offset'),
            total: BuiltValueNullFieldError.checkNotNull(
                total, r'ListResponseInvitationResponse', 'total'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'items';
        items.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'ListResponseInvitationResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
