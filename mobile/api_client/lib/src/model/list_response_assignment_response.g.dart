// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'list_response_assignment_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ListResponseAssignmentResponse extends ListResponseAssignmentResponse {
  @override
  final BuiltList<AssignmentResponse> items;
  @override
  final int limit;
  @override
  final int offset;
  @override
  final int total;

  factory _$ListResponseAssignmentResponse(
          [void Function(ListResponseAssignmentResponseBuilder)? updates]) =>
      (ListResponseAssignmentResponseBuilder()..update(updates))._build();

  _$ListResponseAssignmentResponse._(
      {required this.items,
      required this.limit,
      required this.offset,
      required this.total})
      : super._();
  @override
  ListResponseAssignmentResponse rebuild(
          void Function(ListResponseAssignmentResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ListResponseAssignmentResponseBuilder toBuilder() =>
      ListResponseAssignmentResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ListResponseAssignmentResponse &&
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
    return (newBuiltValueToStringHelper(r'ListResponseAssignmentResponse')
          ..add('items', items)
          ..add('limit', limit)
          ..add('offset', offset)
          ..add('total', total))
        .toString();
  }
}

class ListResponseAssignmentResponseBuilder
    implements
        Builder<ListResponseAssignmentResponse,
            ListResponseAssignmentResponseBuilder> {
  _$ListResponseAssignmentResponse? _$v;

  ListBuilder<AssignmentResponse>? _items;
  ListBuilder<AssignmentResponse> get items =>
      _$this._items ??= ListBuilder<AssignmentResponse>();
  set items(ListBuilder<AssignmentResponse>? items) => _$this._items = items;

  int? _limit;
  int? get limit => _$this._limit;
  set limit(int? limit) => _$this._limit = limit;

  int? _offset;
  int? get offset => _$this._offset;
  set offset(int? offset) => _$this._offset = offset;

  int? _total;
  int? get total => _$this._total;
  set total(int? total) => _$this._total = total;

  ListResponseAssignmentResponseBuilder() {
    ListResponseAssignmentResponse._defaults(this);
  }

  ListResponseAssignmentResponseBuilder get _$this {
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
  void replace(ListResponseAssignmentResponse other) {
    _$v = other as _$ListResponseAssignmentResponse;
  }

  @override
  void update(void Function(ListResponseAssignmentResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ListResponseAssignmentResponse build() => _build();

  _$ListResponseAssignmentResponse _build() {
    _$ListResponseAssignmentResponse _$result;
    try {
      _$result = _$v ??
          _$ListResponseAssignmentResponse._(
            items: items.build(),
            limit: BuiltValueNullFieldError.checkNotNull(
                limit, r'ListResponseAssignmentResponse', 'limit'),
            offset: BuiltValueNullFieldError.checkNotNull(
                offset, r'ListResponseAssignmentResponse', 'offset'),
            total: BuiltValueNullFieldError.checkNotNull(
                total, r'ListResponseAssignmentResponse', 'total'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'items';
        items.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'ListResponseAssignmentResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
