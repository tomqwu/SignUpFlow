// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'holiday_bulk_import_error.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$HolidayBulkImportError extends HolidayBulkImportError {
  @override
  final String? label;
  @override
  final String message;
  @override
  final int row;

  factory _$HolidayBulkImportError(
          [void Function(HolidayBulkImportErrorBuilder)? updates]) =>
      (HolidayBulkImportErrorBuilder()..update(updates))._build();

  _$HolidayBulkImportError._(
      {this.label, required this.message, required this.row})
      : super._();
  @override
  HolidayBulkImportError rebuild(
          void Function(HolidayBulkImportErrorBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  HolidayBulkImportErrorBuilder toBuilder() =>
      HolidayBulkImportErrorBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is HolidayBulkImportError &&
        label == other.label &&
        message == other.message &&
        row == other.row;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, label.hashCode);
    _$hash = $jc(_$hash, message.hashCode);
    _$hash = $jc(_$hash, row.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'HolidayBulkImportError')
          ..add('label', label)
          ..add('message', message)
          ..add('row', row))
        .toString();
  }
}

class HolidayBulkImportErrorBuilder
    implements Builder<HolidayBulkImportError, HolidayBulkImportErrorBuilder> {
  _$HolidayBulkImportError? _$v;

  String? _label;
  String? get label => _$this._label;
  set label(String? label) => _$this._label = label;

  String? _message;
  String? get message => _$this._message;
  set message(String? message) => _$this._message = message;

  int? _row;
  int? get row => _$this._row;
  set row(int? row) => _$this._row = row;

  HolidayBulkImportErrorBuilder() {
    HolidayBulkImportError._defaults(this);
  }

  HolidayBulkImportErrorBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _label = $v.label;
      _message = $v.message;
      _row = $v.row;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(HolidayBulkImportError other) {
    _$v = other as _$HolidayBulkImportError;
  }

  @override
  void update(void Function(HolidayBulkImportErrorBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  HolidayBulkImportError build() => _build();

  _$HolidayBulkImportError _build() {
    final _$result = _$v ??
        _$HolidayBulkImportError._(
          label: label,
          message: BuiltValueNullFieldError.checkNotNull(
              message, r'HolidayBulkImportError', 'message'),
          row: BuiltValueNullFieldError.checkNotNull(
              row, r'HolidayBulkImportError', 'row'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
