// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'bulk_import_item_error.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$BulkImportItemError extends BulkImportItemError {
  @override
  final String? id;
  @override
  final int index;
  @override
  final String reason;

  factory _$BulkImportItemError(
          [void Function(BulkImportItemErrorBuilder)? updates]) =>
      (BulkImportItemErrorBuilder()..update(updates))._build();

  _$BulkImportItemError._({this.id, required this.index, required this.reason})
      : super._();
  @override
  BulkImportItemError rebuild(
          void Function(BulkImportItemErrorBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  BulkImportItemErrorBuilder toBuilder() =>
      BulkImportItemErrorBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is BulkImportItemError &&
        id == other.id &&
        index == other.index &&
        reason == other.reason;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, index.hashCode);
    _$hash = $jc(_$hash, reason.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'BulkImportItemError')
          ..add('id', id)
          ..add('index', index)
          ..add('reason', reason))
        .toString();
  }
}

class BulkImportItemErrorBuilder
    implements Builder<BulkImportItemError, BulkImportItemErrorBuilder> {
  _$BulkImportItemError? _$v;

  String? _id;
  String? get id => _$this._id;
  set id(String? id) => _$this._id = id;

  int? _index;
  int? get index => _$this._index;
  set index(int? index) => _$this._index = index;

  String? _reason;
  String? get reason => _$this._reason;
  set reason(String? reason) => _$this._reason = reason;

  BulkImportItemErrorBuilder() {
    BulkImportItemError._defaults(this);
  }

  BulkImportItemErrorBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _id = $v.id;
      _index = $v.index;
      _reason = $v.reason;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(BulkImportItemError other) {
    _$v = other as _$BulkImportItemError;
  }

  @override
  void update(void Function(BulkImportItemErrorBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  BulkImportItemError build() => _build();

  _$BulkImportItemError _build() {
    final _$result = _$v ??
        _$BulkImportItemError._(
          id: id,
          index: BuiltValueNullFieldError.checkNotNull(
              index, r'BulkImportItemError', 'index'),
          reason: BuiltValueNullFieldError.checkNotNull(
              reason, r'BulkImportItemError', 'reason'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
