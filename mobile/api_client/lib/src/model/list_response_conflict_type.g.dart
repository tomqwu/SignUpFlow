// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'list_response_conflict_type.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ListResponseConflictType extends ListResponseConflictType {
  @override
  final BuiltList<ConflictType> items;
  @override
  final int limit;
  @override
  final int offset;
  @override
  final int total;

  factory _$ListResponseConflictType(
          [void Function(ListResponseConflictTypeBuilder)? updates]) =>
      (ListResponseConflictTypeBuilder()..update(updates))._build();

  _$ListResponseConflictType._(
      {required this.items,
      required this.limit,
      required this.offset,
      required this.total})
      : super._();
  @override
  ListResponseConflictType rebuild(
          void Function(ListResponseConflictTypeBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ListResponseConflictTypeBuilder toBuilder() =>
      ListResponseConflictTypeBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ListResponseConflictType &&
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
    return (newBuiltValueToStringHelper(r'ListResponseConflictType')
          ..add('items', items)
          ..add('limit', limit)
          ..add('offset', offset)
          ..add('total', total))
        .toString();
  }
}

class ListResponseConflictTypeBuilder
    implements
        Builder<ListResponseConflictType, ListResponseConflictTypeBuilder> {
  _$ListResponseConflictType? _$v;

  ListBuilder<ConflictType>? _items;
  ListBuilder<ConflictType> get items =>
      _$this._items ??= ListBuilder<ConflictType>();
  set items(ListBuilder<ConflictType>? items) => _$this._items = items;

  int? _limit;
  int? get limit => _$this._limit;
  set limit(int? limit) => _$this._limit = limit;

  int? _offset;
  int? get offset => _$this._offset;
  set offset(int? offset) => _$this._offset = offset;

  int? _total;
  int? get total => _$this._total;
  set total(int? total) => _$this._total = total;

  ListResponseConflictTypeBuilder() {
    ListResponseConflictType._defaults(this);
  }

  ListResponseConflictTypeBuilder get _$this {
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
  void replace(ListResponseConflictType other) {
    _$v = other as _$ListResponseConflictType;
  }

  @override
  void update(void Function(ListResponseConflictTypeBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ListResponseConflictType build() => _build();

  _$ListResponseConflictType _build() {
    _$ListResponseConflictType _$result;
    try {
      _$result = _$v ??
          _$ListResponseConflictType._(
            items: items.build(),
            limit: BuiltValueNullFieldError.checkNotNull(
                limit, r'ListResponseConflictType', 'limit'),
            offset: BuiltValueNullFieldError.checkNotNull(
                offset, r'ListResponseConflictType', 'offset'),
            total: BuiltValueNullFieldError.checkNotNull(
                total, r'ListResponseConflictType', 'total'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'items';
        items.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'ListResponseConflictType', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
