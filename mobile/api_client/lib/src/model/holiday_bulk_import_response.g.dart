// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'holiday_bulk_import_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$HolidayBulkImportResponse extends HolidayBulkImportResponse {
  @override
  final int created;
  @override
  final BuiltList<HolidayBulkImportError>? errors;
  @override
  final int skipped;

  factory _$HolidayBulkImportResponse(
          [void Function(HolidayBulkImportResponseBuilder)? updates]) =>
      (HolidayBulkImportResponseBuilder()..update(updates))._build();

  _$HolidayBulkImportResponse._(
      {required this.created, this.errors, required this.skipped})
      : super._();
  @override
  HolidayBulkImportResponse rebuild(
          void Function(HolidayBulkImportResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  HolidayBulkImportResponseBuilder toBuilder() =>
      HolidayBulkImportResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is HolidayBulkImportResponse &&
        created == other.created &&
        errors == other.errors &&
        skipped == other.skipped;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, created.hashCode);
    _$hash = $jc(_$hash, errors.hashCode);
    _$hash = $jc(_$hash, skipped.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'HolidayBulkImportResponse')
          ..add('created', created)
          ..add('errors', errors)
          ..add('skipped', skipped))
        .toString();
  }
}

class HolidayBulkImportResponseBuilder
    implements
        Builder<HolidayBulkImportResponse, HolidayBulkImportResponseBuilder> {
  _$HolidayBulkImportResponse? _$v;

  int? _created;
  int? get created => _$this._created;
  set created(int? created) => _$this._created = created;

  ListBuilder<HolidayBulkImportError>? _errors;
  ListBuilder<HolidayBulkImportError> get errors =>
      _$this._errors ??= ListBuilder<HolidayBulkImportError>();
  set errors(ListBuilder<HolidayBulkImportError>? errors) =>
      _$this._errors = errors;

  int? _skipped;
  int? get skipped => _$this._skipped;
  set skipped(int? skipped) => _$this._skipped = skipped;

  HolidayBulkImportResponseBuilder() {
    HolidayBulkImportResponse._defaults(this);
  }

  HolidayBulkImportResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _created = $v.created;
      _errors = $v.errors?.toBuilder();
      _skipped = $v.skipped;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(HolidayBulkImportResponse other) {
    _$v = other as _$HolidayBulkImportResponse;
  }

  @override
  void update(void Function(HolidayBulkImportResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  HolidayBulkImportResponse build() => _build();

  _$HolidayBulkImportResponse _build() {
    _$HolidayBulkImportResponse _$result;
    try {
      _$result = _$v ??
          _$HolidayBulkImportResponse._(
            created: BuiltValueNullFieldError.checkNotNull(
                created, r'HolidayBulkImportResponse', 'created'),
            errors: _errors?.build(),
            skipped: BuiltValueNullFieldError.checkNotNull(
                skipped, r'HolidayBulkImportResponse', 'skipped'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'errors';
        _errors?.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'HolidayBulkImportResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
